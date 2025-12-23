"""
MCP (Model Context Protocol) module for Phase III AI Chat Agent.

This module provides the MCP server using the official FastMCP SDK from the
mcp package (>=1.9.4). It registers task management tools that enable the AI
agent to interact with the Task API through a standardized protocol.

CONSTITUTIONAL REQUIREMENT:
- Uses official mcp.server.FastMCP pattern (not custom implementation)
- Agent interacts with tasks ONLY via MCP tools, not direct API calls

Exports:
    - mcp_server: Global FastMCP server instance with registered tools
    - initialize_mcp_server: Server initialization function
    - get_mcp_server: Retrieve global server instance
    - execute_mcp_tool: Helper for executing tools by name
"""

from app_mcp.server import (
    mcp_server,
    initialize_mcp_server,
    get_mcp_server,
    execute_mcp_tool,
)

__all__ = [
    "mcp_server",
    "initialize_mcp_server",
    "get_mcp_server",
    "execute_mcp_tool",
]
