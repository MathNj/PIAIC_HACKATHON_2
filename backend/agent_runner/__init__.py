"""
AI Chat Agents module for Phase III.

This module provides the AI agent orchestration layer that enables
natural language interaction with the Task API through MCP tools.

Exports:
    - execute_agent: Main agent execution function (stub, for US-1 integration)
    - run_chat_turn: OpenAI agent runner with tool calling loop (Stage 3)
"""

from agent_runner.chat_agent import execute_agent
from agent_runner.runner import run_chat_turn

__all__ = ["execute_agent", "run_chat_turn"]
