"""
Message SQLModel for AI Chat Agent feature.

Represents a single message in a conversation (user, assistant, or system).
Messages are append-only and form the conversation history for stateless agent execution.
"""

from datetime import datetime
from typing import Optional, Literal, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Enum as SQLEnum, JSON
from pydantic import ConfigDict
import enum


class MessageRole(str, enum.Enum):
    """Message role enumeration for type safety"""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message model for Phase III AI Chat Agent.

    Represents a single message in a conversation. Can be from user or assistant.
    Messages are immutable (append-only) to maintain complete conversation audit trail.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Foreign key to Conversation (UUID)
        role: Message role - 'user' or 'assistant' (ENUM)
        content: Message text content (required, max 10,000 chars)
        tool_calls: Optional JSONB of tool executions (for assistant messages)
        created_at: Message creation timestamp

    Indexes:
        - conversation_id: For efficient conversation message retrieval
        - (conversation_id, created_at): Composite index for ordered queries
        - tool_calls: GIN index for JSONB queries (PostgreSQL only)

    Relations:
        conversation: Many-to-one relationship with Conversation model

    Lifecycle:
        - Created when user sends message or agent responds
        - Never updated after creation (immutable, append-only)
        - Deleted only via conversation cascade delete

    Tool Calls Format (JSONB in tool_calls column):
        [
          {
            "tool": "create_task",
            "arguments": {"title": "Buy groceries", "priority": "high"},
            "result": {"id": 789, "title": "Buy groceries", "created": true},
            "timestamp": "2025-12-07T10:30:00Z"
          }
        ]
    """

    __tablename__ = "messages"

    # Primary key (UUID)
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign key to conversations table
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    # Message metadata - using SQLAlchemy Column for ENUM
    role: MessageRole = Field(
        sa_column=Column(SQLEnum(MessageRole, name="message_role"), nullable=False),
        description="Message role: 'user' or 'assistant'"
    )

    # Message content
    content: str = Field(
        nullable=False,
        description="Message text content (max 10,000 characters)"
    )

    # Tool calls - using SQLAlchemy Column for JSONB (JSON for SQLite compatibility)
    tool_calls: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="JSONB of tool executions (for assistant messages)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Message creation timestamp (UTC)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                "role": "assistant",
                "content": "I've created a task for you.",
                "tool_calls": [{"tool": "create_task", "arguments": {"title": "Buy groceries"}, "result": {"id": 789}}],
                "created_at": "2025-12-07T10:30:00Z"
            }
        }
    )
