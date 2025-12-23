"""
Conversation context manager for stateless AI agent architecture.

Fetches conversation history from database on every request to enable
stateless agent design (constitutional requirement).

Functions:
    - load_conversation_context: Load last N messages for AI context
    - get_new_messages: Polling for real-time message updates
    - validate_conversation_access: Tenant isolation enforcement
    - truncate_history_for_tokens: Token budget management
"""

from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException
import logging
import tiktoken

from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens in
        model: OpenAI model name (default: gpt-4)

    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token counting failed: {e}, using estimate")
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4


async def load_conversation_context(
    conversation_id: UUID,
    session: Session,
    limit: int = 50,
    since: Optional[datetime] = None
) -> List[Dict[str, str]]:
    """
    Load conversation history from database for agent context.

    CONSTITUTIONAL REQUIREMENT: ALWAYS fetch from database (NO in-memory caching).
    This enables stateless agent architecture and horizontal scaling.

    Args:
        conversation_id: UUID of conversation
        session: Database session
        limit: Maximum messages to load (default: 50)
        since: Optional datetime for pagination (load messages after this timestamp)

    Returns:
        List of dicts: [{"role": "user", "content": "..."},...]
        Ordered chronologically (oldest first)

    Example:
        >>> history = await load_conversation_context(conv_id, session, limit=50)
        >>> messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    """
    logger.info(
        f"Loading conversation context",
        extra={
            "conversation_id": str(conversation_id),
            "limit": limit,
            "since": since
        }
    )

    # Build query: filter by conversation_id, order by created_at ASC
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    # Add since filter for pagination
    if since:
        statement = statement.where(Message.created_at > since)

    # Limit results
    statement = statement.limit(limit)

    # Execute query
    messages_db = session.exec(statement).all()

    # Convert to OpenAI format
    messages = []
    for msg in messages_db:
        message_dict = {
            "role": msg.role.value,  # Convert enum to string
            "content": msg.content
        }
        messages.append(message_dict)

    logger.info(
        f"Loaded {len(messages)} messages for conversation",
        extra={"conversation_id": str(conversation_id)}
    )

    return messages


async def get_new_messages(
    conversation_id: UUID,
    user_id: UUID,
    since: datetime,
    session: Session
) -> List[Dict[str, str]]:
    """
    Get new messages since a timestamp (polling pattern).

    Used for real-time message updates via HTTP polling.

    Args:
        conversation_id: UUID of conversation
        user_id: Current user ID (for tenant isolation)
        since: ISO timestamp - only return messages after this
        session: Database session

    Returns:
        List of new messages in OpenAI format

    Security:
        Validates conversation ownership before returning messages
    """
    # Validate conversation access (tenant isolation)
    conversation = await validate_conversation_access(
        conversation_id=conversation_id,
        user_id=user_id,
        session=session
    )

    if not conversation:
        return []

    # Load messages since timestamp
    messages = await load_conversation_context(
        conversation_id=conversation_id,
        session=session,
        limit=100,  # Reasonable limit for polling
        since=since
    )

    return messages


async def validate_conversation_access(
    conversation_id: UUID,
    user_id: UUID,
    session: Session
) -> Optional[Conversation]:
    """
    Validate user has access to conversation (tenant isolation).

    SECURITY: Always validate conversation ownership before operations.

    Args:
        conversation_id: UUID of conversation to access
        user_id: Current user ID
        session: Database session

    Returns:
        Conversation object if authorized, None otherwise

    Raises:
        HTTPException 404 if conversation not found or unauthorized
    """
    # Query conversation with user_id filter (tenant isolation)
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None)  # Exclude soft-deleted
    )

    conversation = session.exec(statement).first()

    if not conversation:
        logger.warning(
            f"Unauthorized conversation access attempt",
            extra={
                "conversation_id": str(conversation_id),
                "user_id": str(user_id)
            }
        )
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or access denied"
        )

    return conversation


async def truncate_history_for_tokens(
    history: List[Dict[str, str]],
    max_tokens: int = 8000,
    model: str = "gpt-4"
) -> List[Dict[str, str]]:
    """
    Truncate conversation history to fit within token budget.

    Removes oldest messages until total tokens <= max_tokens.
    Useful for preventing context length errors.

    Args:
        history: List of messages in OpenAI format
        max_tokens: Maximum total tokens allowed (default: 8000)
        model: OpenAI model name for token counting

    Returns:
        Truncated history (oldest messages removed if needed)

    Note:
        Always keeps at least the last message if possible.
    """
    if not history:
        return history

    # Count tokens for each message
    message_tokens = [
        count_tokens(msg.get("content", ""), model=model)
        for msg in history
    ]

    total_tokens = sum(message_tokens)

    # If within budget, return as-is
    if total_tokens <= max_tokens:
        logger.info(
            f"History within token budget",
            extra={"total_tokens": total_tokens, "max_tokens": max_tokens}
        )
        return history

    # Truncate from the beginning (remove oldest messages)
    truncated_history = history.copy()
    removed_count = 0

    while total_tokens > max_tokens and len(truncated_history) > 1:
        # Remove oldest message (first in list)
        removed_msg_tokens = message_tokens.pop(0)
        truncated_history.pop(0)
        total_tokens -= removed_msg_tokens
        removed_count += 1

    logger.warning(
        f"History truncated to fit token budget",
        extra={
            "removed_messages": removed_count,
            "remaining_messages": len(truncated_history),
            "final_tokens": total_tokens,
            "max_tokens": max_tokens
        }
    )

    return truncated_history
