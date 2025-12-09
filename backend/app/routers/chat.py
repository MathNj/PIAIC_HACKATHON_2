"""
Chat API routes for Phase III AI Chat Agent.

Endpoints for managing AI chat conversations with task management capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated, Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
import json
import logging

from app.database import get_session
from app.models.conversation import Conversation
from app.models.message import Message
from app.auth.dependencies import get_current_user
from agent_runner.runner import run_chat_turn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Attributes:
        conversation_id: Optional ID of existing conversation to continue.
            If null, a new conversation will be created.
        message: User's message to the AI agent.
    """
    conversation_id: Optional[int] = Field(
        default=None,
        description="Existing conversation ID (null for new conversation)",
        example=123
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message to the AI agent",
        example="Create a task to buy groceries tomorrow"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": 123,
                "message": "Create a task to buy groceries tomorrow"
            }
        }
    )


class MessageResponse(BaseModel):
    """
    Response schema for a single message.

    Attributes:
        id: Message ID
        role: Message role (user/assistant/system)
        content: Message text content
        tool_calls: Optional list of tool executions
        created_at: Message timestamp
    """
    id: int
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 456,
                "role": "assistant",
                "content": "I've created a task 'Buy groceries' due tomorrow.",
                "tool_calls": [
                    {
                        "tool": "create_task",
                        "arguments": {"title": "Buy groceries", "priority": "normal"},
                        "result": {"id": 789, "title": "Buy groceries"},
                        "timestamp": "2025-12-08T10:00:00Z"
                    }
                ],
                "created_at": "2025-12-08T10:00:01Z"
            }
        }
    )


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Attributes:
        conversation_id: ID of the conversation (new or existing)
        message: Assistant's response message
        user_message_id: ID of the saved user message
        assistant_message_id: ID of the saved assistant message
    """
    conversation_id: int
    message: MessageResponse
    user_message_id: int
    assistant_message_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": 123,
                "message": {
                    "id": 456,
                    "role": "assistant",
                    "content": "I've created a task for you.",
                    "tool_calls": [],
                    "created_at": "2025-12-08T10:00:00Z"
                },
                "user_message_id": 455,
                "assistant_message_id": 456
            }
        }
    )


# ============================================================================
# Helper Functions
# ============================================================================

def load_conversation_history(
    conversation_id: int,
    session: Session,
    limit: int = 10
) -> List[Dict[str, str]]:
    """
    Load conversation history from database.

    Retrieves the most recent messages from a conversation for providing
    context to the AI agent. Messages are loaded in chronological order
    (oldest first) to maintain conversation flow.

    Args:
        conversation_id: ID of the conversation to load
        session: Database session
        limit: Maximum number of recent messages to load (default: 10)

    Returns:
        List of message dictionaries in format:
        [
            {"role": "user", "content": "Show me my tasks"},
            {"role": "assistant", "content": "You have 5 tasks..."},
            ...
        ]

    Example:
        history = load_conversation_history(
            conversation_id=123,
            session=session,
            limit=10
        )
    """
    # Query last N messages ordered by created_at DESC, then reverse for chronological order
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    messages = session.exec(statement).all()

    # Reverse to get chronological order (oldest first)
    messages = list(reversed(messages))

    # Convert to format expected by run_chat_turn()
    history = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in messages
    ]

    logger.info(f"[Chat API] Loaded {len(history)} messages from conversation {conversation_id}")

    return history


def save_message(
    conversation_id: int,
    role: str,
    content: str,
    session: Session,
    tool_calls: Optional[List[Dict[str, Any]]] = None
) -> int:
    """
    Save a message to the conversation history in the database.

    This function persists a message (user or assistant) to the messages table,
    optionally including tool call audit information for assistant messages.

    Args:
        conversation_id: ID of the conversation this message belongs to
        role: Message role ("user", "assistant", or "system")
        content: Message text content
        session: Database session
        tool_calls: Optional list of tool execution records (for assistant messages)

    Returns:
        int: ID of the created message

    Raises:
        HTTPException: If message creation fails

    Example:
        message_id = save_message(
            conversation_id=123,
            role="user",
            content="Create a task to buy groceries",
            session=session
        )
    """
    # Validate role
    if role not in ["user", "assistant", "system"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message role: {role}. Must be 'user', 'assistant', or 'system'"
        )

    # Convert tool_calls to JSON string if provided
    tool_calls_json = None
    if tool_calls:
        tool_calls_json = json.dumps(tool_calls)

    # Create Message object
    new_message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls_json,
        created_at=datetime.utcnow()
    )

    # Save to database
    try:
        session.add(new_message)
        session.commit()
        session.refresh(new_message)

        logger.info(f"[Chat API] Saved {role} message {new_message.id} to conversation {conversation_id}")

        return new_message.id

    except Exception as e:
        session.rollback()
        logger.error(f"[Chat API] Failed to save message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save message: {str(e)}"
        )


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> List[Dict[str, Any]]:
    """List all conversations for the user."""
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
    conversations = session.exec(statement).all()

    return [{
        "id": conv.id,
        "title": conv.title or "New Conversation",
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat()
    } for conv in conversations]


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> ChatResponse:
    """
    Send a message to the AI chat agent.

    This endpoint handles the complete chat flow:
    1. Verify JWT authentication and user authorization
    2. Create new conversation or retrieve existing conversation
    3. Load conversation history from database
    4. Save user message to database
    5. Execute AI agent with conversation history and MCP tools
    6. Save assistant response to database
    7. Update conversation timestamp
    8. Return assistant response with tool execution audit trail

    **Authorization**: User can only chat in their own conversations.
    Path user_id must match authenticated user from JWT.

    **Request Body**:
    ```json
    {
        "conversation_id": 123,  // null for new conversation
        "message": "Create a task to buy groceries tomorrow"
    }
    ```

    **Response**:
    ```json
    {
        "conversation_id": 123,
        "message": {
            "id": 456,
            "role": "assistant",
            "content": "I've created a task 'Buy groceries' due tomorrow.",
            "tool_calls": [...],
            "created_at": "2025-12-08T10:00:00Z"
        },
        "user_message_id": 455,
        "assistant_message_id": 456
    }
    ```

    Args:
        user_id: UUID from URL path (user to chat as)
        request: ChatRequest with conversation_id (optional) and message
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        ChatResponse: Assistant's response with conversation metadata

    Raises:
        HTTPException 400: If message validation fails
        HTTPException 401: If JWT token is invalid
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If conversation not found or doesn't belong to user
        HTTPException 500: If agent execution or database operation fails
    """
    logger.info(f"[Chat API] POST /{user_id}/chat - message: {request.message[:50]}...")

    # 1. Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        logger.warning(f"[Chat API] Authorization failed: user_id {user_id} != current_user {current_user}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot chat as user {user_id}"
        )

    # 2. Conversation Handling
    conversation: Conversation

    if request.conversation_id is not None:
        # Retrieve existing conversation
        logger.info(f"[Chat API] Retrieving existing conversation {request.conversation_id}")

        statement = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            logger.warning(f"[Chat API] Conversation {request.conversation_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )

        logger.info(f"[Chat API] Found conversation {conversation.id}")

    else:
        # Create new conversation
        logger.info(f"[Chat API] Creating new conversation for user {user_id}")

        conversation = Conversation(
            user_id=user_id,
            title=None,  # Will be auto-generated later (future enhancement)
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        try:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

            logger.info(f"[Chat API] Created new conversation {conversation.id}")

        except Exception as e:
            session.rollback()
            logger.error(f"[Chat API] Failed to create conversation: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create conversation: {str(e)}"
            )

    # 3. Load conversation history (last 10 messages)
    conversation_history = load_conversation_history(
        conversation_id=conversation.id,
        session=session,
        limit=10
    )

    # 4. Save user message to database
    user_message_id = save_message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
        session=session
    )

    # 5. Execute AI agent with run_chat_turn()
    logger.info(f"[Chat API] Executing agent for conversation {conversation.id}")

    try:
        # For Phase III, we use user_id directly for M CP tools instead of JWT token
        # Setting user_token=None will trigger the fallback in runner.py to use user_id
        user_token = None

        agent_result = await run_chat_turn(
            user_id=str(user_id),
            message=request.message,
            history=conversation_history,
            user_token=user_token,
            max_tool_calls=10
        )

        logger.info(f"[Chat API] Agent execution completed: {len(agent_result['tool_calls'])} tool calls")

    except Exception as e:
        logger.error(f"[Chat API] Agent execution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

    # 6. Save assistant response to database
    assistant_message_id = save_message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_result["response"],
        session=session,
        tool_calls=agent_result.get("tool_calls", [])
    )

    # 7. Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    logger.info(f"[Chat API] Updated conversation {conversation.id} timestamp")

    # 8. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageResponse(
            id=assistant_message_id,
            role="assistant",
            content=agent_result["response"],
            tool_calls=agent_result.get("tool_calls", []),
            created_at=datetime.utcnow()
        ),
        user_message_id=user_message_id,
        assistant_message_id=assistant_message_id
    )
