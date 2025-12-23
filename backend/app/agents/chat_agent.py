"""
Stateless AI chat agent with OpenAI integration and MCP tools.

This module implements a stateless AI agent that accepts conversation history
as a parameter (constitutional requirement for horizontal scaling).

CONSTITUTIONAL REQUIREMENT:
- Agent interacts with tasks ONLY via MCP tools (mcp_list_tasks, mcp_create_task, etc.)
- Uses official FastMCP SDK from mcp package (>= 1.9.4)
- NO direct API calls from agent - all task operations go through MCP

Functions:
    - run_agent: Execute stateless AI agent with conversation history and MCP tools
    - _execute_tool: Execute a single MCP tool (internal)
    - _convert_mcp_tools_to_openai_format: Convert FastMCP tools to OpenAI function format
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
import json
import time
import logging
import os

from openai import OpenAI, OpenAIError
from jose import jwt

# Import MCP server and tool execution (official FastMCP SDK)
from app_mcp.server import get_mcp_server, execute_mcp_tool
from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# OpenAI Client and JWT Token Generation
# ============================================================================

def get_openai_client() -> OpenAI:
    """
    Get OpenAI client instance.

    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required for AI agent"
        )
    return OpenAI(api_key=api_key)


def _generate_jwt_token(user_id: UUID) -> str:
    """
    Generate JWT token for MCP tool authentication.

    MCP tools require JWT authentication with user_id in the token payload.
    This function generates a short-lived token for tool execution context.

    Args:
        user_id: User UUID to encode in token

    Returns:
        JWT token string

    Example:
        token = _generate_jwt_token(user_id)
        # Token payload: {"user_id": "550e8400-...", "exp": 1735...}
    """
    payload = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=5),  # 5-minute expiry for tool execution
        "iat": datetime.utcnow(),
        "purpose": "mcp_tool_execution"
    }

    token = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )

    return token


def _convert_mcp_tools_to_openai_format() -> List[Dict[str, Any]]:
    """
    Convert FastMCP tool schemas to OpenAI function calling format.

    FastMCP uses MCP protocol schemas, but OpenAI requires a different format.
    This function bridges the two formats.

    Returns:
        List of OpenAI-compatible tool definitions

    Example:
        [
            {
                "type": "function",
                "function": {
                    "name": "mcp_list_tasks",
                    "description": "List all tasks for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["all", "pending", "completed"]}
                        },
                        "required": []  # user_token is injected, not required from agent
                    }
                }
            },
            ...
        ]

    NOTE: user_token parameter is REMOVED from OpenAI schema since it's
    injected automatically during tool execution.
    """
    mcp_server = get_mcp_server()
    mcp_tools_list = mcp_server.list_tools()

    openai_tools = []

    # Manually define tool schemas in OpenAI format (user_token parameter excluded)
    # These mirror the MCP tools but are compatible with OpenAI function calling
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "mcp_list_tasks",
                "description": "List all tasks for the authenticated user with optional status filtering (all, pending, completed)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by completion status (default: all)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_create_task",
                "description": "Create a new task from natural language description. Supports priority inference from keywords (URGENT→high, maybe→low) and natural language due dates (tomorrow, next week, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description (max 1000 characters)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high"],
                            "description": "Task priority level. If omitted, will be inferred from description keywords."
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date - supports natural language (tomorrow, next week, in 3 days) or ISO format (2025-12-25)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_update_task",
                "description": "Update an existing task's properties (title, description, priority, due_date, completed status)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional new title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high"],
                            "description": "Optional new priority"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Optional new due date (ISO 8601 format)"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Optional new completion status"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_delete_task",
                "description": "Permanently delete a task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_toggle_task_completion",
                "description": "Toggle task completion status (mark as complete if pending, or pending if complete)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to toggle"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_get_task_summary",
                "description": "Get task statistics and summary with counts by status, priority, and timeframe (total, completed, pending, high_priority, overdue, due_today, due_this_week)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeframe": {
                            "type": "string",
                            "enum": ["all", "today", "week", "overdue"],
                            "description": "Filter timeframe for summary (default: all)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_suggest_task_prioritization",
                "description": "Get AI-powered task prioritization suggestions based on urgency, due dates, and priority levels. Returns tasks sorted by computed priority score with reasoning.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    logger.info(f"Converted {len(tool_definitions)} MCP tools to OpenAI function calling format")

    return tool_definitions


async def run_agent(
    user_id: UUID,
    message: str,
    history: List[Dict[str, str]],
    mcp_tools: Optional[List[Dict[str, Any]]] = None,
    max_tool_calls: int = 10,
    model: str = "gpt-4",
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute stateless AI agent with conversation history and MCP tools.

    CONSTITUTIONAL REQUIREMENT:
    - No class-level state. Accept history parameter.
    - Agent must be restartable without losing context.
    - Agent interacts with tasks ONLY via MCP tools (official FastMCP SDK)

    Args:
        user_id: Current user ID (for MCP tool authentication and tenant isolation)
        message: User's new message to process
        history: Conversation history from database (list of {"role": str, "content": str})
        mcp_tools: DEPRECATED - MCP tools are auto-loaded from FastMCP server
        max_tool_calls: Maximum tool execution iterations (default: 10)
        model: OpenAI model to use (default: gpt-4)
        system_prompt: Optional system prompt override

    Returns:
        {
            "response": str,  # AI assistant response text
            "tool_calls": [   # Audit trail of tool executions
                {
                    "tool_name": str,
                    "arguments": dict,
                    "result": dict,
                    "timestamp": str,  # ISO 8601
                    "duration_ms": int,
                    "status": "success" | "error"
                }
            ],
            "model": str,  # Model used
            "tokens_used": int,  # Total tokens consumed
            "finish_reason": str  # "stop", "length", "tool_calls", etc.
        }

    Raises:
        OpenAIError: If OpenAI API call fails
        ValueError: If OPENAI_API_KEY not set

    Example:
        >>> history = await load_conversation_context(conv_id, session)
        >>> result = await run_agent(
        ...     user_id=user.id,
        ...     message="Create a task for groceries",
        ...     history=history
        ... )
        >>> print(result["response"])
        "I've created a task for groceries with ID 123"
    """
    start_time = time.time()

    logger.info(
        f"Agent execution started with MCP tools",
        extra={
            "user_id": str(user_id),
            "message_length": len(message),
            "history_length": len(history),
            "model": model
        }
    )

    # Initialize OpenAI client
    try:
        client = get_openai_client()
    except ValueError as e:
        logger.error(f"OpenAI client initialization failed: {e}")
        raise

    # Generate JWT token for MCP tool authentication
    # This token is injected into all tool calls for user authentication
    user_token = _generate_jwt_token(user_id)
    logger.debug(f"Generated JWT token for MCP tool execution")

    # Load MCP tools from FastMCP server and convert to OpenAI format
    openai_tools = _convert_mcp_tools_to_openai_format()
    logger.info(f"Loaded {len(openai_tools)} MCP tools for agent")

    # Build messages array for OpenAI
    messages = []

    # Add system prompt (if not already in history)
    if system_prompt or (not history or history[0].get("role") != "system"):
        default_system_prompt = (
            "You are a helpful AI assistant for a task management application. "
            "You have access to tools that let you create, update, list, delete, and manage tasks. "
            "When users ask to create tasks, use the mcp_create_task tool with natural language support "
            "(e.g., 'tomorrow' for due dates, 'URGENT' in description sets high priority). "
            "Be concise, friendly, and proactive in offering assistance. "
            "Always confirm task operations with the user by describing what you did."
        )
        messages.append({
            "role": "system",
            "content": system_prompt or default_system_prompt
        })

    # Add conversation history
    messages.extend(history)

    # Add new user message
    messages.append({
        "role": "user",
        "content": message
    })

    # Tool execution tracking
    tool_calls_audit = []
    total_tokens = 0
    iteration = 0

    # Agent execution loop (for multi-turn tool calling)
    while iteration < max_tool_calls:
        iteration += 1

        try:
            # Call OpenAI API with MCP tools (official FastMCP SDK integration)
            logger.debug(f"OpenAI API call (iteration {iteration}) with {len(openai_tools)} tools")

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=openai_tools,  # MCP tools in OpenAI function calling format
                tool_choice="auto",  # Let model decide when to use tools
                temperature=0.7,
                max_tokens=2000
            )

            # Extract response
            assistant_message = completion.choices[0].message
            finish_reason = completion.choices[0].finish_reason
            total_tokens += completion.usage.total_tokens

            # No tool calls - return final response
            if not hasattr(assistant_message, 'tool_calls') or not assistant_message.tool_calls:
                response_text = assistant_message.content or ""

                duration_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    f"Agent execution completed",
                    extra={
                        "user_id": str(user_id),
                        "iterations": iteration,
                        "tool_calls": len(tool_calls_audit),
                        "tokens_used": total_tokens,
                        "duration_ms": duration_ms,
                        "finish_reason": finish_reason
                    }
                )

                return {
                    "response": response_text,
                    "tool_calls": tool_calls_audit,
                    "model": model,
                    "tokens_used": total_tokens,
                    "finish_reason": finish_reason
                }

            # Tool calls present - execute them
            logger.info(
                f"Agent requested {len(assistant_message.tool_calls)} tool calls"
            )

            # Add assistant message with tool calls to conversation
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
                tool_start = time.time()
                tool_name = tool_call.function.name
                tool_arguments_str = tool_call.function.arguments

                try:
                    # Parse arguments
                    tool_arguments = json.loads(tool_arguments_str)

                    logger.debug(
                        f"Executing tool: {tool_name}",
                        extra={"arguments": tool_arguments}
                    )

                    # Execute MCP tool via FastMCP SDK (with injected JWT token)
                    tool_result = await _execute_tool(
                        tool_name=tool_name,
                        arguments=tool_arguments,
                        user_token=user_token  # Inject JWT token for authentication
                    )

                    tool_status = "success"

                except json.JSONDecodeError as e:
                    logger.error(f"Tool arguments JSON decode failed: {e}")
                    tool_result = {
                        "error": "Invalid tool arguments format",
                        "details": str(e)
                    }
                    tool_status = "error"

                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    tool_result = {
                        "error": "Tool execution failed",
                        "details": str(e)
                    }
                    tool_status = "error"

                # Record tool execution
                tool_duration_ms = int((time.time() - tool_start) * 1000)
                tool_calls_audit.append({
                    "tool_name": tool_name,
                    "arguments": tool_arguments if isinstance(tool_arguments, dict) else {},
                    "result": tool_result,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "duration_ms": tool_duration_ms,
                    "status": tool_status
                })

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise

    # Exceeded max iterations
    logger.warning(
        f"Agent exceeded max tool call iterations",
        extra={"max_tool_calls": max_tool_calls}
    )

    return {
        "response": "I apologize, but I've reached the maximum number of tool calls. Please try breaking down your request.",
        "tool_calls": tool_calls_audit,
        "model": model,
        "tokens_used": total_tokens,
        "finish_reason": "max_iterations"
    }


async def _execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    user_token: str
) -> Dict[str, Any]:
    """
    Execute a single MCP tool via official FastMCP SDK.

    CONSTITUTIONAL REQUIREMENT: Agent interacts with tasks ONLY via MCP tools.
    This function calls the MCP server which uses the official FastMCP SDK pattern.

    Args:
        tool_name: Name of the MCP tool to execute (e.g., "mcp_list_tasks")
        arguments: Tool arguments from OpenAI (user_token excluded)
        user_token: JWT token for authentication (injected, not from OpenAI)

    Returns:
        Tool execution result as dictionary

    Raises:
        Exception: If tool execution fails

    Example:
        result = await _execute_tool(
            tool_name="mcp_create_task",
            arguments={"title": "Buy groceries", "due_date": "tomorrow"},
            user_token="eyJhbGciOiJIUzI1NiIs..."
        )
        # Returns: {"id": 123, "title": "Buy groceries", ...}
    """
    logger.info(
        f"Executing MCP tool via FastMCP SDK: {tool_name}",
        extra={
            "tool_name": tool_name,
            "arguments": arguments
        }
    )

    # Inject user_token into arguments (required by all MCP tools)
    # This ensures JWT authentication for tenant isolation
    tool_arguments_with_token = {
        "user_token": user_token,
        **arguments
    }

    try:
        # Call MCP tool via FastMCP's execute_mcp_tool helper
        # This uses the official FastMCP SDK pattern
        result = await execute_mcp_tool(
            tool_name=tool_name,
            arguments=tool_arguments_with_token
        )

        logger.info(
            f"MCP tool executed successfully: {tool_name}",
            extra={"tool_name": tool_name, "result_type": type(result).__name__}
        )

        return result

    except Exception as e:
        logger.error(
            f"MCP tool execution failed: {tool_name} - {str(e)}",
            exc_info=True,
            extra={
                "tool_name": tool_name,
                "arguments": arguments,
                "error": str(e)
            }
        )
        # Re-raise to be caught by run_agent's error handling
        raise
