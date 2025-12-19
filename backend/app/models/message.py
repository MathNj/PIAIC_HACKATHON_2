"""
Message SQLModel for AI Chat Agent feature.

Represents a single message in a conversation (user, assistant, or system).
Messages are append-only and form the conversation history for stateless agent execution.
"""

from datetime import datetime
from typing import Optional, Literal
from sqlmodel import Field, SQLModel, Index
from pydantic import ConfigDict


class Message(SQLModel, table=True):
    """
    Message model for Phase III AI Chat Agent.

    Represents a single message in a conversation. Can be from user, assistant, or system.
    Messages are immutable (append-only) to maintain complete conversation audit trail.

    Attributes:
        id: Unique message identifier (auto-incrementing integer)
        conversation_id: Foreign key to Conversation (int)
        role: Message role - 'user', 'assistant', or 'system'
        content: Message text content (required, max 10,000 chars)
        tool_calls: Optional JSON string of tool executions (for assistant messages)
        created_at: Message creation timestamp

    Indexes:
        - conversation_id: For efficient conversation message retrieval
        - (conversation_id, created_at): Composite index for ordered queries

    Relations:
        conversation: Many-to-one relationship with Conversation model

    Lifecycle:
        - Created when user sends message or agent responds
        - Never updated after creation (immutable, append-only)
        - Deleted only via conversation cascade delete

    Tool Calls Format (JSON in tool_calls column):
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

    # Primary key (auto-incrementing integer)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign key to conversations table
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    # Message metadata
    role: str = Field(
        nullable=False,
        max_length=20,
        description="Message role: 'user', 'assistant', or 'system'"
    )

    # Message content
    content: str = Field(
        nullable=False,
        description="Message text content (max 10,000 characters)"
    )

    tool_calls: Optional[str] = Field(
        default=None,
        nullable=True,
        description="JSON string of tool executions (for assistant messages)"
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
                "id": 456,
                "conversation_id": 123,
                "role": "assistant",
                "content": "I've created a task for you.",
                "tool_calls": "[{\"tool\":\"create_task\",\"arguments\":{\"title\":\"Buy groceries\"},\"result\":{\"id\":789}}]",
                "created_at": "2025-12-07T10:30:00Z"
            }
        }
    )


# Create composite index for efficient ordered message queries
# This is defined outside the class to ensure it's created in migrations
# Pattern: Query messages WHERE conversation_id = X ORDER BY created_at DESC
__table_args__ = (
    Index("idx_messages_conversation_created", "conversation_id", "created_at"),
)
