"""
Pydantic schemas for Message API requests and responses.

Schemas:
- MessageCreate: Send new message (user input)
- MessageResponse: Message data output
- MessageListResponse: Conversation message history
- SendMessageResponse: Response after sending message (for future use)
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any


class MessageCreate(BaseModel):
    """
    Schema for creating a new message.

    Content is validated to ensure it's not empty or only whitespace.
    Role (user/assistant) and conversation_id are handled server-side.
    """
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message text content"
    )

    @field_validator('content')
    @classmethod
    def content_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure content is not only whitespace and trim it."""
        if not v.strip():
            raise ValueError('Content cannot be only whitespace')
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "Help me organize my tasks for this week"
            }
        }
    )


class MessageResponse(BaseModel):
    """
    Schema for message data in API responses.

    Includes optional tool_calls metadata for AI agent transparency.
    """
    id: str = Field(..., description="Unique message ID (UUID)")
    conversation_id: str = Field(..., description="Parent conversation ID")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    tool_calls: Optional[Dict[str, Any]] = Field(
        None,
        description="MCP tool execution metadata (for assistant messages)"
    )
    created_at: datetime = Field(..., description="Message creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLModel compatibility (Pydantic v2)
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                "role": "user",
                "content": "Help me organize my tasks for this week",
                "tool_calls": None,
                "created_at": "2025-12-22T10:15:00Z"
            }
        }
    )


class MessageListResponse(BaseModel):
    """
    Schema for conversation message history responses.

    Returns messages in chronological order with total count for pagination.
    """
    messages: list[MessageResponse] = Field(
        ...,
        description="List of messages in chronological order"
    )
    conversation_id: str = Field(
        ...,
        description="Conversation ID for these messages"
    )
    total_count: int = Field(
        ...,
        description="Total number of messages in conversation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "messages": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440002",
                        "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                        "role": "user",
                        "content": "Help me organize my tasks",
                        "tool_calls": None,
                        "created_at": "2025-12-22T10:15:00Z"
                    },
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                        "role": "assistant",
                        "content": "I'll help you with that. Let me fetch your current tasks.",
                        "tool_calls": {
                            "tool_name": "list_tasks",
                            "status": "success",
                            "duration_ms": 245
                        },
                        "created_at": "2025-12-22T10:15:03Z"
                    }
                ],
                "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                "total_count": 2
            }
        }
    )


class SendMessageResponse(BaseModel):
    """
    Schema for response after sending a message.

    For future use: may include streaming tokens, partial responses, or status updates.
    Currently returns the created user message and assistant response.
    """
    user_message: MessageResponse = Field(
        ...,
        description="The user message that was saved"
    )
    assistant_message: Optional[MessageResponse] = Field(
        None,
        description="The AI assistant's response (if generated)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_message": {
                    "id": "550e8400-e29b-41d4-a716-446655440002",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                    "role": "user",
                    "content": "Help me organize my tasks",
                    "tool_calls": None,
                    "created_at": "2025-12-22T10:15:00Z"
                },
                "assistant_message": {
                    "id": "550e8400-e29b-41d4-a716-446655440003",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
                    "role": "assistant",
                    "content": "I'll help you with that. Let me fetch your current tasks.",
                    "tool_calls": {
                        "tool_name": "list_tasks",
                        "status": "success"
                    },
                    "created_at": "2025-12-22T10:15:03Z"
                }
            }
        }
    )
