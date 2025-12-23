"""
Pydantic schemas for Conversation API requests and responses.

Schemas:
- ConversationCreate: Create new conversation (optional title)
- ConversationUpdate: Update conversation title
- ConversationResponse: Conversation data output
- ConversationListResponse: Paginated conversation list
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ConversationCreate(BaseModel):
    """
    Schema for creating a new conversation.

    Title is optional and will be auto-generated from first message if omitted.
    User ID will be extracted from JWT token, not provided in request body.
    """
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional title (auto-generated if omitted)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Task Planning Discussion"
            }
        }
    )


class ConversationUpdate(BaseModel):
    """
    Schema for updating an existing conversation.

    Currently only supports updating the title.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="New conversation title"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Conversation Title"
            }
        }
    )


class ConversationResponse(BaseModel):
    """
    Schema for conversation data in API responses.

    Includes computed fields for message_count and last_message_preview.
    """
    id: str = Field(..., description="Unique conversation ID (UUID)")
    user_id: str = Field(..., description="Owner user ID (UUID)")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Total message count in conversation")
    last_message_preview: Optional[str] = Field(
        None,
        description="First 100 chars of last message"
    )

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLModel compatibility (Pydantic v2)
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Task Planning Discussion",
                "created_at": "2025-12-22T10:00:00Z",
                "updated_at": "2025-12-22T10:15:00Z",
                "message_count": 5,
                "last_message_preview": "I'll help you organize those tasks. Let me create them for you..."
            }
        }
    )


class ConversationListResponse(BaseModel):
    """
    Schema for paginated conversation list responses.

    Uses cursor-based pagination with ISO timestamp for efficient scrolling.
    """
    conversations: list[ConversationResponse] = Field(
        ...,
        description="List of conversations"
    )
    nextCursor: Optional[str] = Field(
        None,
        description="ISO timestamp for cursor pagination (pass to next request)"
    )
    hasMore: bool = Field(
        ...,
        description="Whether more conversations are available"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Task Planning Discussion",
                        "created_at": "2025-12-22T10:00:00Z",
                        "updated_at": "2025-12-22T10:15:00Z",
                        "message_count": 5,
                        "last_message_preview": "I'll help you organize those tasks..."
                    }
                ],
                "nextCursor": "2025-12-22T10:00:00Z",
                "hasMore": True
            }
        }
    )
