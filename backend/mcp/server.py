"""
MCP Server Initialization for Phase III AI Chat Agent.

This module initializes the Model Context Protocol (MCP) server and registers
all task management tools that the agent can use. The server enables the AI
agent to interact with the Task API through a standardized protocol.

Architecture:
- Stateless design: No in-memory conversation state (Phase III requirement)
- Tool-based: Each task operation exposed as an MCP tool
- Token-authenticated: All tools validate JWT tokens for user isolation
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Model Context Protocol (MCP) Server for AI Chat Agent.

    Manages the registration and execution of MCP tools that enable
    the agent to perform task management operations on behalf of the user.

    Design Principles:
    - Each tool validates JWT token independently (no shared session state)
    - Tools return structured data (not direct HTTP responses)
    - Errors are raised as exceptions for agent handling
    - All database operations use dependency injection for testability
    """

    def __init__(self):
        """Initialize MCP server with empty tool registry."""
        self.tools: Dict[str, Any] = {}
        logger.info("MCP Server initialized")

    def register_tool(self, name: str, tool_function: Any, schema: Dict[str, Any]) -> None:
        """
        Register an MCP tool with its schema.

        Args:
            name: Tool name (e.g., "list_tasks", "create_task")
            tool_function: Callable that implements the tool logic
            schema: JSON schema describing tool parameters and return type

        Example:
            server.register_tool(
                "list_tasks",
                list_tasks_tool,
                {
                    "name": "list_tasks",
                    "description": "List all tasks for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_token": {"type": "string"},
                            "status": {"type": "string", "enum": ["all", "pending", "completed"]}
                        },
                        "required": ["user_token"]
                    }
                }
            )
        """
        self.tools[name] = {
            "function": tool_function,
            "schema": schema
        }
        logger.info(f"Registered MCP tool: {name}")

    def get_tool(self, name: str) -> Any:
        """
        Retrieve a registered tool by name.

        Args:
            name: Tool name to retrieve

        Returns:
            Tool function

        Raises:
            ValueError: If tool not found
        """
        if name not in self.tools:
            raise ValueError(f"MCP tool '{name}' not found. Available tools: {list(self.tools.keys())}")

        return self.tools[name]["function"]

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all tool schemas for agent initialization.

        Returns:
            List of tool schemas in MCP format

        Example return:
            [
                {
                    "name": "list_tasks",
                    "description": "List all tasks...",
                    "parameters": {...}
                },
                ...
            ]
        """
        return [tool["schema"] for tool in self.tools.values()]

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())


# Global MCP server instance (singleton pattern)
# This ensures all tools are registered once and shared across the application
mcp_server = MCPServer()


def initialize_mcp_server() -> MCPServer:
    """
    Initialize and configure the MCP server with all task management tools.

    This function should be called once during application startup to register
    all MCP tools. It imports and registers tools from backend/mcp/tools.py.

    Returns:
        Configured MCPServer instance

    Usage:
        # In app/main.py startup event
        from app.mcp.server import initialize_mcp_server

        @app.on_event("startup")
        async def startup_event():
            initialize_mcp_server()
    """
    from mcp.tools import register_all_tools

    logger.info("Initializing MCP server with task management tools")

    # Register all MCP tools (list_tasks, create_task, etc.)
    register_all_tools(mcp_server)

    logger.info(f"MCP server initialized with {len(mcp_server.tools)} tools: {mcp_server.list_tools()}")

    return mcp_server


def get_mcp_server() -> MCPServer:
    """
    Get the global MCP server instance.

    Returns:
        Global MCPServer instance

    Usage:
        from app.mcp.server import get_mcp_server

        server = get_mcp_server()
        tool = server.get_tool("list_tasks")
        result = await tool(user_token="...", status="all")
    """
    return mcp_server
