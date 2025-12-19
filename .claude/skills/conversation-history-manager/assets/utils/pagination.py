# Cursor-based pagination utilities for conversation history
# Copy this file to: backend/app/utils/pagination.py

from sqlmodel import Session, select
from typing import TypeVar, Generic, List
from pydantic import BaseModel
from datetime import datetime
from app.models import Conversation

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    cursor: str | None
    has_more: bool


def paginate_conversations(
    user_id: str,
    db: Session,
    cursor: str | None = None,
    limit: int = 20
) -> dict:
    """
    Paginate conversations using cursor-based pagination.

    Benefits over offset pagination:
    - Consistent results with concurrent inserts
    - No offset drift issues
    - Better performance (no COUNT query needed)

    Args:
        user_id: UUID of user (tenant isolation)
        db: SQLModel database session
        cursor: ISO timestamp cursor from previous page
        limit: Page size (default 20)

    Returns:
        {
            "conversations": List[Conversation],
            "cursor": str | None,  # Next page cursor
            "has_more": bool
        }

    Performance: Uses idx_conversations_user_updated index
    Expected query time: <20ms for 20 conversations
    """
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
        .order_by(Conversation.updated_at.desc())
    )

    if cursor:
        try:
            cursor_time = datetime.fromisoformat(cursor)
            query = query.where(Conversation.updated_at < cursor_time)
        except ValueError:
            # Invalid cursor, return empty results
            return {
                "conversations": [],
                "cursor": None,
                "has_more": False
            }

    # Fetch limit + 1 to check if there's more
    conversations = db.exec(query.limit(limit + 1)).all()

    has_more = len(conversations) > limit
    if has_more:
        conversations = conversations[:limit]

    next_cursor = None
    if has_more and conversations:
        next_cursor = conversations[-1].updated_at.isoformat()

    return {
        "conversations": conversations,
        "cursor": next_cursor,
        "has_more": has_more
    }


def paginate_with_offset(
    user_id: str,
    db: Session,
    offset: int = 0,
    limit: int = 20
) -> dict:
    """
    Paginate conversations using offset-based pagination.

    WARNING: Offset pagination has issues with concurrent inserts.
             Prefer cursor-based pagination (paginate_conversations).

    Use only when:
    - You need random page access (e.g., page 5 directly)
    - Total count is required
    - Data is relatively static

    Args:
        user_id: UUID of user
        db: SQLModel database session
        offset: Number of items to skip
        limit: Page size

    Returns:
        {
            "conversations": List[Conversation],
            "offset": int,
            "limit": int,
            "total": int
        }
    """
    from sqlmodel import func

    # Get total count
    total = db.exec(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
    ).one()

    # Get page of conversations
    conversations = db.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "conversations": conversations,
        "offset": offset,
        "limit": limit,
        "total": total
    }
