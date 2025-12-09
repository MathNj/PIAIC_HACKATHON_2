"""
MCP (Model Context Protocol) module for Phase III AI Chat Agent.

This module provides the MCP server and tools that enable the AI agent
to interact with the Task API through a standardized protocol.

Exports:
    - MCPServer: Main MCP server class
    - mcp_server: Global singleton server instance
    - initialize_mcp_server: Server initialization function
    - get_mcp_server: Retrieve global server instance
"""

from mcp.server import (
    MCPServer,
    mcp_server,
    initialize_mcp_server,
    get_mcp_server,
)

__all__ = [
    "MCPServer",
    "mcp_server",
    "initialize_mcp_server",
    "get_mcp_server",
]
