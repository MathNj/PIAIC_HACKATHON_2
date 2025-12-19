# Conversation context management utilities for stateless AI agents
# Copy this file to: backend/app/agents/context_manager.py

from sqlmodel import Session, select
from typing import List
from app.models import Message, Conversation
from datetime import datetime


def load_conversation_context(
    conversation_id: str,
    db: Session,
    limit: int = 50
) -> List[Message]:
    """
    Load last N messages for stateless agent context.

    This function implements the stateless architecture requirement:
    - No in-memory conversation state
    - Full history fetched from database every request
    - Enables horizontal scaling and load balancing

    Args:
        conversation_id: UUID of conversation
        db: SQLModel database session
        limit: Maximum messages to load (default 50 for token management)

    Returns:
        List of messages in chronological order (oldest first)

    Performance: Uses idx_messages_conversation_created index
    Expected query time: <20ms for 50 messages
    """
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    # Reverse to get chronological order (oldest first) for AI context
    return list(reversed(messages))


def get_new_messages(
    conversation_id: str,
    user_id: str,
    since: str,
    db: Session
) -> List[Message]:
    """
    Get messages created after a specific timestamp (for polling).

    Args:
        conversation_id: UUID of conversation
        user_id: UUID of user (for ownership validation)
        since: ISO timestamp of last known message
        db: SQLModel database session

    Returns:
        List of new messages in chronological order

    Raises:
        None (returns empty list if conversation not found or access denied)
    """
    # Validate ownership
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        return []

    since_time = datetime.fromisoformat(since)

    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.created_at > since_time)
        .order_by(Message.created_at.asc())
    ).all()

    return messages


def validate_conversation_access(
    conversation_id: str,
    user_id: str,
    db: Session
) -> Conversation | None:
    """
    Validate user has access to conversation (tenant isolation).

    Args:
        conversation_id: UUID of conversation
        user_id: UUID of user
        db: SQLModel database session

    Returns:
        Conversation object if access granted, None otherwise

    Security: Prevents cross-tenant data leakage
    """
    conversation = db.get(Conversation, conversation_id)

    if not conversation:
        return None

    if conversation.user_id != user_id:
        # Log unauthorized access attempt (optional)
        import logging
        logging.warning(
            f"Unauthorized access: user {user_id} -> conversation {conversation_id}"
        )
        return None

    if conversation.deleted_at is not None:
        # Don't allow access to deleted conversations
        return None

    return conversation


def truncate_history_for_tokens(
    messages: List[Message],
    max_tokens: int = 8000,
    chars_per_token: float = 4.0
) -> List[Message]:
    """
    Truncate message history to fit within token budget.

    Args:
        messages: List of messages in chronological order
        max_tokens: Maximum tokens allowed (default 8000)
        chars_per_token: Approximate characters per token (default 4.0)

    Returns:
        Truncated list of messages that fits within token budget

    Note: This is a simple character-based estimation.
          For production, use tiktoken for accurate token counting.
    """
    max_chars = int(max_tokens * chars_per_token)
    total_chars = 0
    truncated_messages = []

    # Start from most recent and work backwards
    for message in reversed(messages):
        message_chars = len(message.content)

        if total_chars + message_chars > max_chars:
            break

        truncated_messages.insert(0, message)
        total_chars += message_chars

    return truncated_messages
