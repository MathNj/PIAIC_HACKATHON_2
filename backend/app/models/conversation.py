"""
Conversation SQLModel for AI Chat Agent feature.

Represents a persistent chat conversation between a user and the AI agent.
Each conversation belongs to one user and contains multiple messages.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model for Phase III AI Chat Agent.

    Represents a conversation container that holds messages between user and agent.
    All conversation history is persisted in the database to ensure stateless agent design.

    Attributes:
        id: Unique conversation identifier (auto-incrementing integer)
        user_id: Foreign key to User (UUID) - owner of the conversation
        title: Optional conversation title (auto-generated or user-set, max 200 chars)
        created_at: Conversation creation timestamp
        updated_at: Last message timestamp (updated on each new message)

    Indexes:
        - user_id: For efficient filtering by user
        - updated_at: For sorting by most recent conversations

    Relations:
        user: Many-to-one relationship with User model
        messages: One-to-many relationship with Message model (cascade delete)

    Lifecycle:
        - Created when user starts new conversation (conversation_id = null in chat API)
        - updated_at refreshed on every new message
        - Deleted when user explicitly deletes conversation (cascades to messages)
    """

    __tablename__ = "conversations"

    # Primary key (auto-incrementing integer)
    id: Optional[int] = Field(
        default=None,
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
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        nullable=True,
        description="Optional conversation title (auto-generated or user-set)"
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

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": 123,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Task Management - Dec 7",
                "created_at": "2025-12-07T10:00:00Z",
                "updated_at": "2025-12-07T11:30:00Z"
            }
        }
