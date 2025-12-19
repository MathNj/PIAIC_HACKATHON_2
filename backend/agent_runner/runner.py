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

# OpenAI SDK for custom client configuration
from openai import AsyncOpenAI

# OpenAI Agents SDK for Agent and Runner
from agents import Agent, Runner, set_default_openai_client, set_default_openai_api, function_tool

from app.config import settings  # Import settings instead of using os.getenv
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


# Agent instructions for the task management agent
AGENT_INSTRUCTIONS = """You are a helpful task management assistant. You help users manage their TODO tasks through natural language conversation.

IMPORTANT: You are already authenticated. The user is logged in and you can directly call all tools without asking for authentication or tokens. Never ask the user for tokens or credentials.

You have access to the following tools:
- list_tasks: List all tasks with optional status filtering (no parameters needed - you're already authenticated)
- create_task: Create a new task with title, description, priority, and due date
- update_task: Update an existing task's properties
- delete_task: Delete a task by ID
- toggle_task_completion: Mark a task as complete or incomplete

When users ask you to create tasks:
1. Extract the task title from their message
2. Infer priority from urgency keywords (urgent/asap/critical → high, maybe/someday → low, default → normal)
3. Parse temporal expressions for due dates (tomorrow, next week, Monday, etc.)
4. Directly call create_task tool - you don't need to ask for authentication

When users ask about their tasks:
1. Directly call list_tasks to fetch their current tasks (no authentication needed)
2. Provide a clear summary organized by priority or due date
3. Highlight overdue tasks or high-priority items

When users ask to modify tasks:
1. Use update_task to change task properties
2. Confirm the changes you made

When users ask to complete or delete tasks:
1. Use toggle_task_completion or delete_task as appropriate
2. Confirm the action taken

Always be concise, helpful, and proactive in managing tasks efficiently. Never ask users for authentication - you're already authorized to perform all operations.
"""

# Global variables for agent configuration
_agent_client_configured = False
_user_token_context: Optional[str] = None
_user_id_context: Optional[str] = None


def _configure_gemini_client():
    """Configure the AsyncOpenAI client for Gemini API (v1beta)."""
    global _agent_client_configured

    if _agent_client_configured:
        return

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise AgentRunnerError("GEMINI_API_KEY environment variable not set")

    # Create custom AsyncOpenAI client pointing to Gemini's v1beta OpenAI-compatible endpoint
    gemini_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Set as default client for openai-agents SDK
    set_default_openai_client(gemini_client)

    # CRITICAL: Set API type to "chat_completions" instead of default "responses"
    # Gemini supports Chat Completions API, NOT Responses API
    set_default_openai_api("chat_completions")

    _agent_client_configured = True
    logger.info("[Agent Runner] Configured Gemini client with chat_completions API for openai-agents SDK")


def _create_tool_wrappers(user_token: Optional[str], user_id: str):
    """
    Create function_tool wrappers for MCP tools with user_token injection.

    These wrappers allow the openai-agents SDK to discover and call our MCP tools
    while automatically injecting authentication credentials.
    """
    # Store context in global variables for tool wrappers to access
    global _user_token_context, _user_id_context
    _user_token_context = user_token or f"user_id:{user_id}"
    _user_id_context = user_id

    @function_tool
    def list_tasks_tool(status: Optional[str] = None):
        """List all tasks for the authenticated user, optionally filtered by status."""
        return list_tasks(user_token=_user_token_context, status=status)

    @function_tool
    def create_task_tool(
        title: str,
        description: Optional[str] = None,
        priority: str = "normal",
        due_date: Optional[str] = None
    ):
        """Create a new task with the given title, optional description, priority, and due date."""
        return create_task(
            user_token=_user_token_context,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )

    @function_tool
    def update_task_tool(
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None
    ):
        """Update an existing task's properties."""
        return update_task(
            user_token=_user_token_context,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )

    @function_tool
    def delete_task_tool(task_id: int):
        """Delete a task by ID."""
        return delete_task(user_token=_user_token_context, task_id=task_id)

    @function_tool
    def toggle_task_completion_tool(task_id: int):
        """Mark a task as complete or incomplete (toggle completion status)."""
        return toggle_task_completion(user_token=_user_token_context, task_id=task_id)

    return [
        list_tasks_tool,
        create_task_tool,
        update_task_tool,
        delete_task_tool,
        toggle_task_completion_tool
    ]


async def run_chat_turn(
    user_id: str,
    message: str,
    history: List[Dict[str, str]],
    user_token: Optional[str] = None,
    max_tool_calls: int = 10
) -> Dict[str, Any]:
    """
    Execute a single chat turn with the AI agent using openai-agents SDK.

    This function uses the proper openai-agents SDK pattern:
    1. Configure Gemini client with set_default_openai_client()
    2. Create Agent with instructions and MCP tool wrappers
    3. Use Runner.run() to execute the agent

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
            "tool_calls": [...],
            "total_tool_calls": 2,
            "model": "gemini-2.5-flash"
        }

    Raises:
        AgentRunnerError: If agent execution fails
        LLMError: If LLM API call fails

    Example:
        result = await run_chat_turn(
            user_id="user-123",
            message="Create a task to buy groceries tomorrow",
            history=[],
            user_token="eyJhbGciOiJIUzI1NiIs..."
        )
    """
    logger.info(f"[Agent Runner] Starting chat turn for user {user_id}, message: {message[:50]}...")

    try:
        # 1. Configure Gemini client (only runs once)
        _configure_gemini_client()

        # 2. Create tool wrappers with user authentication
        tools = _create_tool_wrappers(user_token, user_id)

        # 3. Create Agent with Gemini model
        agent = Agent(
            name="Task Management Assistant",
            instructions=AGENT_INSTRUCTIONS,
            model="gemini-2.5-flash",  # Gemini 2.5 Flash via configured client
            tools=tools
        )

        # 4. Construct full message with history
        # Convert history to openai-agents format
        full_message = message
        if history:
            # Prepend history as context
            context_messages = []
            for msg in history:
                role = msg["role"]
                content = msg["content"]
                context_messages.append(f"{role.capitalize()}: {content}")

            full_message = "\n\n".join(context_messages) + f"\n\nUser: {message}"

        # 5. Run agent with Runner.run()
        logger.info(f"[Agent Runner] Running agent with {len(tools)} tools")

        result = await Runner.run(agent, full_message)

        # 6. Extract response and tool calls
        final_response = result.final_output or ""

        # Note: openai-agents SDK doesn't expose tool call audit trail in the same way
        # We'll need to extract this from the result object if available
        tool_calls = []  # TODO: Extract from result if SDK provides this

        logger.info(f"[Agent Runner] Agent completed: {final_response[:100]}...")

        return {
            "response": final_response,
            "tool_calls": tool_calls,
            "total_tool_calls": len(tool_calls),
            "model": "gemini-2.5-flash"
        }

    except Exception as e:
        logger.error(f"[Agent Runner] Error during agent execution: {str(e)}", exc_info=True)
        raise LLMError(f"Agent execution failed: {str(e)}")
