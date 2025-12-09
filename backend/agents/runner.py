"""
Agent Runner for Phase III AI Chat Agent.

This module implements the OpenAI agent execution logic with tool calling support.
It orchestrates the conversation flow between the user, the LLM, and MCP tools.

Architecture:
- Stateless execution (no in-memory conversation state)
- Tool calling loop (LLM → Tool → LLM → Response)
- JWT token propagation to all MCP tools
- Comprehensive error handling and logging
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json
import os

from openai import AsyncOpenAI

from mcp.server import get_mcp_server
from mcp.tools import (
    list_tasks,
    create_task,
    update_task,
    delete_task,
    toggle_task_completion,
    MCPToolError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class AgentRunnerError(Exception):
    """Base exception for agent runner errors."""
    pass


class LLMError(AgentRunnerError):
    """Raised when LLM execution fails."""
    pass


class ToolExecutionError(AgentRunnerError):
    """Raised when tool execution fails."""
    pass


# System prompt for the task management agent
SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their TODO tasks through natural language conversation.

You have access to the following tools:
- list_tasks: List all tasks with optional status filtering
- create_task: Create a new task with title, description, priority, and due date
- update_task: Update an existing task's properties
- delete_task: Delete a task by ID
- toggle_task_completion: Mark a task as complete or incomplete

When users ask you to create tasks:
1. Extract the task title from their message
2. Infer priority from urgency keywords (urgent/asap/critical → high, maybe/someday → low, default → normal)
3. Parse temporal expressions for due dates (tomorrow, next week, Monday, etc.)
4. Create the task using the create_task tool

When users ask about their tasks:
1. Use list_tasks to fetch their current tasks
2. Provide a clear summary organized by priority or due date
3. Highlight overdue tasks or high-priority items

When users ask to modify tasks:
1. Use update_task to change task properties
2. Confirm the changes you made

When users ask to complete or delete tasks:
1. Use toggle_task_completion or delete_task as appropriate
2. Confirm the action taken

Always be concise, helpful, and proactive in managing tasks efficiently.
"""


async def run_chat_turn(
    user_id: str,
    message: str,
    history: List[Dict[str, str]],
    user_token: Optional[str] = None,
    max_tool_calls: int = 10
) -> Dict[str, Any]:
    """
    Execute a single chat turn with the AI agent.

    This function implements the complete agent execution loop:
    1. Initialize OpenAI client with gpt-4o model
    2. Construct conversation context (system prompt + history + user message)
    3. Send request to LLM with available MCP tools
    4. Handle tool calling loop:
       - If LLM requests tool call → Execute tool → Send result back to LLM
       - If LLM returns text response → Return to caller
    5. Return final response with tool call audit trail

    Args:
        user_id: User ID for authentication (used as fallback if no JWT token)
        message: User's current message
        history: Previous conversation messages in format:
            [{"role": "user"|"assistant", "content": "..."}, ...]
        user_token: Optional JWT token for MCP tool authentication.
            If not provided, user_id will be used directly (less secure).
        max_tool_calls: Maximum number of tool calls to prevent infinite loops (default: 10)

    Returns:
        Dictionary with agent response and tool execution audit trail:
        {
            "response": "Agent's final text response",
            "tool_calls": [
                {
                    "tool": "create_task",
                    "arguments": {"title": "Buy groceries", "priority": "normal"},
                    "result": {"id": 123, "title": "Buy groceries", ...},
                    "timestamp": "2025-12-08T10:00:00Z",
                    "success": True
                },
                ...
            ],
            "total_tool_calls": 2,
            "model": "gpt-4o"
        }

    Raises:
        AgentRunnerError: If agent execution fails
        LLMError: If LLM API call fails
        ToolExecutionError: If tool execution fails critically

    Example:
        result = run_chat_turn(
            user_id="user-123",
            message="Create a task to buy groceries tomorrow",
            history=[
                {"role": "user", "content": "Show me my tasks"},
                {"role": "assistant", "content": "You have 5 tasks..."}
            ],
            user_token="eyJhbGciOiJIUzI1NiIs..."
        )
        print(result["response"])  # "I've created a task 'Buy groceries' due tomorrow."
        print(result["tool_calls"])  # [{"tool": "create_task", ...}]
    """
    logger.info(f"[Agent Runner] Starting chat turn for user {user_id}, message: {message[:50]}...")

    # 1. Initialize AsyncOpenAI Client for Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AgentRunnerError("GEMINI_API_KEY environment variable not set")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    model = "gemini-2.5-flash"  # Using Gemini 2.5 Flash (not deprecated versions)

    # 2. Get MCP tools and convert to OpenAI tool format
    mcp_server = get_mcp_server()
    tool_schemas = _convert_mcp_tools_to_openai_format(mcp_server.get_tool_schemas())

    logger.info(f"[Agent Runner] Loaded {len(tool_schemas)} MCP tools")

    # 3. Construct conversation context
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Add conversation history
    messages.extend(history)

    # Add current user message
    messages.append({"role": "user", "content": message})

    logger.info(f"[Agent Runner] Conversation context: {len(messages)} messages")

    # 4. Execute agent loop with tool calling support
    tool_call_audit = []
    tool_call_count = 0

    try:
        while tool_call_count < max_tool_calls:
            logger.info(f"[Agent Runner] Sending request to LLM (iteration {tool_call_count + 1})")

            # Call Gemini API via AsyncOpenAI client
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                tool_choice="auto"  # Let LLM decide when to use tools
            )

            assistant_message = response.choices[0].message

            # Check if LLM wants to call tools
            if assistant_message.tool_calls:
                logger.info(f"[Agent Runner] LLM requested {len(assistant_message.tool_calls)} tool calls")

                # Add assistant's tool call message to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args_str = tool_call.function.arguments
                    tool_call_id = tool_call.id

                    logger.info(f"[Agent Runner] Executing tool: {tool_name}")

                    # Execute tool and capture result
                    tool_result = _execute_tool(
                        tool_name=tool_name,
                        arguments=tool_args_str,
                        user_token=user_token,
                        user_id=user_id
                    )

                    # Add tool result to audit trail
                    tool_call_audit.append({
                        "tool": tool_name,
                        "arguments": json.loads(tool_args_str),
                        "result": tool_result["result"],
                        "success": tool_result["success"],
                        "error": tool_result.get("error"),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })

                    # Add tool result to conversation for LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps(tool_result["result"]) if tool_result["success"] else tool_result["error"]
                    })

                    tool_call_count += 1

                # Continue loop to get LLM's response after tool execution

            else:
                # LLM returned final text response (no more tool calls)
                final_response = assistant_message.content or ""
                logger.info(f"[Agent Runner] Agent returned final response: {final_response[:100]}...")

                return {
                    "response": final_response,
                    "tool_calls": tool_call_audit,
                    "total_tool_calls": len(tool_call_audit),
                    "model": model
                }

        # Max tool calls reached without final response
        logger.warning(f"[Agent Runner] Max tool calls ({max_tool_calls}) reached")
        return {
            "response": "I apologize, but I've reached the maximum number of tool calls. Please try rephrasing your request or breaking it into smaller steps.",
            "tool_calls": tool_call_audit,
            "total_tool_calls": len(tool_call_audit),
            "model": model,
            "error": "max_tool_calls_exceeded"
        }

    except Exception as e:
        logger.error(f"[Agent Runner] Error during agent execution: {str(e)}", exc_info=True)
        raise LLMError(f"LLM execution failed: {str(e)}")


def _convert_mcp_tools_to_openai_format(mcp_schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert MCP tool schemas to OpenAI function calling format.

    OpenAI expects tools in this format:
    {
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "Tool description",
            "parameters": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
    }

    Args:
        mcp_schemas: List of MCP tool schemas from mcp_server.get_tool_schemas()

    Returns:
        List of OpenAI-formatted tool schemas
    """
    openai_tools = []

    for mcp_schema in mcp_schemas:
        openai_tool = {
            "type": "function",
            "function": {
                "name": mcp_schema["name"],
                "description": mcp_schema["description"],
                "parameters": mcp_schema["parameters"]
            }
        }
        openai_tools.append(openai_tool)

    return openai_tools


def _execute_tool(
    tool_name: str,
    arguments: str,
    user_token: Optional[str],
    user_id: str
) -> Dict[str, Any]:
    """
    Execute an MCP tool with error handling.

    Args:
        tool_name: Name of the tool to execute
        arguments: JSON string of tool arguments
        user_token: JWT token for authentication
        user_id: User ID (fallback if no token)

    Returns:
        Dictionary with execution result:
        {
            "success": True,
            "result": {...}  # Tool return value
        }
        OR
        {
            "success": False,
            "error": "Error message"
        }
    """
    try:
        # Parse arguments
        args = json.loads(arguments)

        # Add user_token to arguments if not present
        if "user_token" not in args and user_token:
            args["user_token"] = user_token
        elif "user_token" not in args:
            # Fallback: use user_id directly (less secure, for development)
            logger.warning(f"[Tool Execution] No user_token provided, using user_id directly")
            args["user_id"] = user_id

        # Get tool function from MCP server
        mcp_server = get_mcp_server()
        tool_func = mcp_server.get_tool(tool_name)

        # Execute tool
        result = tool_func(**args)

        return {
            "success": True,
            "result": result
        }

    except AuthenticationError as e:
        logger.error(f"[Tool Execution] Authentication error: {str(e)}")
        return {
            "success": False,
            "error": f"Authentication failed: {str(e)}"
        }

    except AuthorizationError as e:
        logger.error(f"[Tool Execution] Authorization error: {str(e)}")
        return {
            "success": False,
            "error": f"Access denied: {str(e)}"
        }

    except NotFoundError as e:
        logger.error(f"[Tool Execution] Resource not found: {str(e)}")
        return {
            "success": False,
            "error": f"Not found: {str(e)}"
        }

    except ValidationError as e:
        logger.error(f"[Tool Execution] Validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid input: {str(e)}"
        }

    except MCPToolError as e:
        logger.error(f"[Tool Execution] MCP tool error: {str(e)}")
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }

    except Exception as e:
        logger.error(f"[Tool Execution] Unexpected error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Internal error: {str(e)}"
        }
