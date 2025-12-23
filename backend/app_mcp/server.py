"""
MCP Server using Official FastMCP SDK for Phase III AI Chat Agent.

This module implements the Model Context Protocol (MCP) server using the official
FastMCP SDK from the mcp package (>=1.9.4). It registers task management tools
that the AI agent can use to interact with the Task API.

CONSTITUTIONAL REQUIREMENT:
- Uses official mcp.server.FastMCP pattern (not custom implementation)
- Agent interacts with tasks ONLY via MCP tools (add_task, list_tasks, etc.)
- No direct API calls from agent - all task operations go through MCP

Architecture:
- FastMCP server with decorator-based tool registration
- Stateless design: No in-memory conversation state
- Token-authenticated: All tools validate JWT tokens for user isolation
- Tools return structured data (dicts/lists), not HTTP responses
"""

from typing import List, Dict, Any, Literal, Optional
from mcp.server import FastMCP
import logging

# Import tool functions from tools.py
from app_mcp.tools import (
    list_tasks,
    create_task,
    update_task,
    delete_task,
    toggle_task_completion,
    get_task_summary,
    suggest_task_prioritization
)

logger = logging.getLogger(__name__)


# ============================================================================
# FastMCP Server Instance (Official SDK Pattern)
# ============================================================================

# Initialize FastMCP server from official MCP SDK
# This replaces the custom MCPServer class with official implementation
mcp_server = FastMCP(
    name="Task Management MCP Server",
    instructions="AI agent tools for task management operations with JWT authentication",
    debug=False,
    log_level="INFO"
)

logger.info("Initialized FastMCP server from official MCP SDK")


# ============================================================================
# Tool Registration using Official @mcp_server.tool Decorator
# ============================================================================
# CONSTITUTIONAL REQUIREMENT: Use official FastMCP decorator pattern,
# not custom register_tool() method

@mcp_server.tool()
async def mcp_list_tasks(
    user_token: str,
    status: Literal["all", "pending", "completed"] = "all"
) -> List[Dict[str, Any]]:
    """
    List all tasks for the authenticated user.

    MCP Tool: list_tasks

    This tool retrieves all tasks for the authenticated user with optional filtering
    by completion status. The user_token is validated and the user_id is extracted
    to ensure tenant isolation.

    Args:
        user_token: JWT token for authentication
        status: Filter by completion status ("all", "pending", "completed")

    Returns:
        List of task dictionaries with fields:
        - id: Task ID
        - title: Task title
        - description: Task description (optional)
        - completed: Completion status
        - priority: Priority level (low/normal/high)
        - due_date: Due date timestamp (optional)
        - created_at: Creation timestamp
        - updated_at: Last update timestamp

    Raises:
        AuthenticationError: If token validation fails
        ValidationError: If status parameter is invalid

    Example:
        tasks = await mcp_list_tasks(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            status="pending"
        )
        # Returns: [{"id": 1, "title": "Buy groceries", ...}, ...]
    """
    # Delegate to tool function from tools.py
    # Tool functions handle JWT validation, database operations, and error handling
    return list_tasks(user_token=user_token, status=status)


@mcp_server.tool()
async def mcp_create_task(
    user_token: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task from natural language description.

    MCP Tool: create_task

    This tool supports natural language processing:
    - Priority inference: If priority is None, infers from description keywords
      (e.g., "URGENT task" → high, "maybe do this" → low)
    - Temporal parsing: Due dates can be natural language
      (e.g., "tomorrow", "next week", "2025-12-25")

    Args:
        user_token: JWT token for authentication
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)
        priority: Task priority ("low", "normal", "high") - if None, inferred from description
        due_date: Due date - supports natural language ("tomorrow", "next week") or ISO format

    Returns:
        Dictionary with created task fields (same as list_tasks)

    Raises:
        AuthenticationError: If token validation fails
        ValidationError: If title is empty, too long, or due_date is invalid

    Example:
        task = await mcp_create_task(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            title="Buy groceries",
            description="Milk, eggs, bread - URGENT!",
            due_date="tomorrow"
        )
        # Priority inferred as "high" from "URGENT"
        # Due date parsed from "tomorrow"
    """
    return create_task(
        user_token=user_token,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date
    )


@mcp_server.tool()
async def mcp_update_task(
    user_token: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing task's properties.

    MCP Tool: update_task

    Args:
        user_token: JWT token for authentication
        task_id: ID of the task to update
        title: Optional new title
        description: Optional new description
        priority: Optional new priority
        due_date: Optional new due date (ISO 8601 string)
        completed: Optional new completion status

    Returns:
        Dictionary with updated task fields

    Raises:
        AuthenticationError: If token validation fails
        AuthorizationError: If task doesn't belong to user
        NotFoundError: If task doesn't exist
        ValidationError: If any field validation fails

    Example:
        task = await mcp_update_task(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            task_id=123,
            title="Buy groceries (updated)",
            priority="high"
        )
    """
    return update_task(
        user_token=user_token,
        task_id=task_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        completed=completed
    )


@mcp_server.tool()
async def mcp_delete_task(
    user_token: str,
    task_id: int
) -> Dict[str, str]:
    """
    Delete a task by ID.

    MCP Tool: delete_task

    Args:
        user_token: JWT token for authentication
        task_id: ID of the task to delete

    Returns:
        Dictionary with success message:
        {"detail": "Task {id} deleted"}

    Raises:
        AuthenticationError: If token validation fails
        AuthorizationError: If task doesn't belong to user
        NotFoundError: If task doesn't exist

    Example:
        result = await mcp_delete_task(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            task_id=123
        )
        # Returns: {"detail": "Task 123 deleted"}
    """
    return delete_task(user_token=user_token, task_id=task_id)


@mcp_server.tool()
async def mcp_toggle_task_completion(
    user_token: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Toggle task completion status (True ↔ False).

    MCP Tool: toggle_task_completion

    Args:
        user_token: JWT token for authentication
        task_id: ID of the task to toggle

    Returns:
        Dictionary with updated task fields (completed status toggled)

    Raises:
        AuthenticationError: If token validation fails
        AuthorizationError: If task doesn't belong to user
        NotFoundError: If task doesn't exist

    Example:
        task = await mcp_toggle_task_completion(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            task_id=123
        )
        # If task.completed was False, returns task with completed=True
        # If task.completed was True, returns task with completed=False
    """
    return toggle_task_completion(user_token=user_token, task_id=task_id)


@mcp_server.tool()
async def mcp_get_task_summary(
    user_token: str,
    timeframe: Literal["all", "today", "week", "overdue"] = "all"
) -> Dict[str, Any]:
    """
    Get task statistics and summary.

    MCP Tool: get_task_summary (Advanced Analytics)

    Returns aggregated statistics about user's tasks including:
    - Total count, completed count, pending count
    - High priority task count
    - Overdue task count
    - Due today count
    - Due this week count

    Args:
        user_token: JWT token for authentication
        timeframe: Filter timeframe for summary (default: 'all')

    Returns:
        Dictionary with task statistics

    Example:
        summary = await mcp_get_task_summary(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            timeframe="week"
        )
        # Returns: {"total": 10, "completed": 5, "pending": 5, ...}
    """
    return get_task_summary(user_token=user_token, timeframe=timeframe)


@mcp_server.tool()
async def mcp_suggest_task_prioritization(
    user_token: str
) -> List[Dict[str, Any]]:
    """
    Get AI-powered task prioritization suggestions.

    MCP Tool: suggest_task_prioritization (Advanced AI Feature)

    Analyzes pending tasks and suggests prioritization based on:
    - Task priority level
    - Due date urgency (overdue, today, this week)
    - Scoring algorithm

    Args:
        user_token: JWT token for authentication

    Returns:
        List of tasks with prioritization scores and reasoning

    Example:
        suggestions = await mcp_suggest_task_prioritization(
            user_token="eyJhbGciOiJIUzI1NiIs..."
        )
        # Returns: [
        #     {
        #         "task": {"id": 1, "title": "...", ...},
        #         "score": 100,
        #         "reasoning": "OVERDUE + High Priority"
        #     },
        #     ...
        # ]
    """
    return suggest_task_prioritization(user_token=user_token)


# ============================================================================
# Server Management Functions (Compatibility Layer)
# ============================================================================

def initialize_mcp_server() -> FastMCP:
    """
    Initialize and configure the MCP server with all task management tools.

    NOTE: With FastMCP decorator pattern, tools are registered at import time
    via @mcp_server.tool() decorators above. This function exists for
    compatibility with existing startup code.

    Returns:
        Configured FastMCP instance

    Usage:
        # In app/main.py startup event
        from app.mcp.server import initialize_mcp_server

        @app.on_event("startup")
        async def startup_event():
            initialize_mcp_server()
    """
    # Tools are already registered via decorators
    # Just log initialization
    tool_count = len(mcp_server.list_tools())
    tool_names = [tool.name for tool in mcp_server.list_tools()]

    logger.info(
        f"MCP server initialized with {tool_count} tools using official FastMCP SDK: {tool_names}"
    )

    return mcp_server


def get_mcp_server() -> FastMCP:
    """
    Get the global FastMCP server instance.

    Returns:
        Global FastMCP instance

    Usage:
        from app.mcp.server import get_mcp_server

        server = get_mcp_server()
        # Use server.call_tool() to execute tools
    """
    return mcp_server


# ============================================================================
# Tool Execution Helper (for Agent Integration)
# ============================================================================

async def execute_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute an MCP tool by name with arguments.

    This is a helper function for agent integration. The agent can call this
    function to execute tools without directly accessing the FastMCP server.

    Args:
        tool_name: Name of the tool to execute (e.g., "mcp_list_tasks")
        arguments: Tool arguments as dictionary

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool not found
        Exception: Any exception raised by the tool

    Example:
        result = await execute_mcp_tool(
            tool_name="mcp_list_tasks",
            arguments={"user_token": "...", "status": "pending"}
        )
    """
    try:
        # Call tool using FastMCP's call_tool method
        result = await mcp_server.call_tool(tool_name, arguments)
        return result
    except Exception as e:
        logger.error(f"MCP tool execution failed: {tool_name} - {str(e)}", exc_info=True)
        raise


# Log server initialization on module import
logger.info("FastMCP server module loaded with official SDK pattern")
