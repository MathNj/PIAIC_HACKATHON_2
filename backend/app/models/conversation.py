"""
Conversation SQLModel for AI Chat Agent feature.

Represents a persistent chat conversation between a user and the AI agent.
Each conversation belongs to one user and contains multiple messages.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from pydantic import ConfigDict


class Conversation(SQLModel, table=True):
    """
    Conversation model for Phase III AI Chat Agent.

    Represents a conversation container that holds messages between user and agent.
    All conversation history is persisted in the database to ensure stateless agent design.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Foreign key to User (UUID) - owner of the conversation
        title: Conversation title (required, max 200 chars)
        created_at: Conversation creation timestamp
        updated_at: Last message timestamp (updated on each new message)
        deleted_at: Soft delete timestamp (null if active)

    Indexes:
        - user_id: For efficient filtering by user
        - (user_id, updated_at DESC): For sorting by most recent conversations
        - (user_id, deleted_at): For filtering soft-deleted conversations

    Relations:
        user: Many-to-one relationship with User model
        messages: One-to-many relationship with Message model (cascade delete)

    Lifecycle:
        - Created when user starts new conversation (conversation_id = null in chat API)
        - updated_at refreshed on every new message
        - Soft deleted when user explicitly deletes conversation (sets deleted_at)
    """

    __tablename__ = "conversations"

    # Primary key (UUID)
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # Foreign key to users table
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation"
    )

    # Conversation metadata
    title: str = Field(
        max_length=200,
        nullable=False,
        description="Conversation title (auto-generated or user-set)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,  # Index for sorting by most recent
        description="Last message timestamp (UTC) - updated on each message"
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Soft delete timestamp (null if active, UTC when deleted)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Task Management - Dec 7",
                "created_at": "2025-12-07T10:00:00Z",
                "updated_at": "2025-12-07T11:30:00Z",
                "deleted_at": None
            }
        }
    )
