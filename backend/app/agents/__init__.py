"""
AI Agent components for Phase III chat integration.

This package contains the stateless agent architecture for OpenAI chat integration:
- context_manager.py: Database-backed conversation history loading
- chat_agent.py: Stateless AI agent with OpenAI and MCP tools

CONSTITUTIONAL REQUIREMENT: All agents are stateless with database-backed
conversation persistence. NO in-memory conversation state allowed.
"""

from .context_manager import (
    load_conversation_context,
    get_new_messages,
    validate_conversation_access,
    truncate_history_for_tokens
)

from .chat_agent import run_agent

__all__ = [
    "load_conversation_context",
    "get_new_messages",
    "validate_conversation_access",
    "truncate_history_for_tokens",
    "run_agent"
]
