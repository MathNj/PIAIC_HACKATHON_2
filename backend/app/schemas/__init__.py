"""
Pydantic schemas for request/response validation.

Defines data transfer objects (DTOs) for API endpoints.
Separates database models from API contracts.
"""

from app.schemas.task import TaskRead, TaskCreate, TaskUpdate
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse
)
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    SendMessageResponse
)

__all__ = [
    "TaskRead",
    "TaskCreate",
    "TaskUpdate",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationListResponse",
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
    "SendMessageResponse"
]
