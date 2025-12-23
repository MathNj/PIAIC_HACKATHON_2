"""
Chat API routes for Phase III AI Chat Agent.

Endpoints for managing AI chat conversations with task management capabilities.
Implements spec-006 User Story 1: REST API endpoints for conversation and message CRUD.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from uuid import UUID
from typing import Annotated, Optional
from datetime import datetime
import logging

from app.database import get_session
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.auth.dependencies import get_current_user
from app.agents.context_manager import load_conversation_context
from app.agents.chat_agent import run_agent, get_openai_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# ============================================================================
# Helper Functions
# ============================================================================

def validate_conversation_ownership(
    conversation_id: str,
    user_id: UUID,
    session: Session
) -> Conversation:
    """
    Validate conversation exists, is active, and belongs to the user.

    Args:
        conversation_id: Conversation UUID as string
        user_id: User UUID from JWT token
        session: Database session

    Returns:
        Conversation: The validated conversation object

    Raises:
        HTTPException 404: If conversation not found or soft-deleted
        HTTPException 403: If conversation doesn't belong to user
        HTTPException 400: If conversation_id is invalid UUID
    """
    # Convert string to UUID
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        logger.warning(f"[Chat API] Invalid conversation UUID: {conversation_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID format: {conversation_id}"
        )

    # Query conversation by ID
    statement = select(Conversation).where(Conversation.id == conv_uuid)
    conversation = session.exec(statement).first()

    # Raise 404 if not found
    if not conversation:
        logger.warning(f"[Chat API] Conversation {conversation_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    # Raise 404 if soft-deleted
    if conversation.deleted_at is not None:
        logger.warning(f"[Chat API] Conversation {conversation_id} has been deleted")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    # Raise 403 if user_id doesn't match
    if conversation.user_id != user_id:
        logger.warning(
            f"[Chat API] User {user_id} attempted to access conversation {conversation_id} "
            f"belonging to user {conversation.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Conversation {conversation_id} does not belong to you"
        )

    return conversation


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> ConversationResponse:
    """
    Create a new conversation.

    Creates an empty conversation container. User can optionally provide a title,
    otherwise it will be auto-generated as "New Conversation".

    **Authentication**: Requires valid JWT token in Authorization header.

    **Request Body**:
    ```json
    {
        "title": "Task Planning Discussion"  // Optional
    }
    ```

    **Response**:
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Task Planning Discussion",
        "created_at": "2025-12-22T10:00:00Z",
        "updated_at": "2025-12-22T10:00:00Z",
        "message_count": 0,
        "last_message_preview": null
    }
    ```

    Args:
        conversation_data: ConversationCreate with optional title
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        ConversationResponse: Created conversation with metadata

    Raises:
        HTTPException 401: If JWT token is invalid
        HTTPException 500: If database operation fails
    """
    logger.info(f"[Chat API] POST /conversations - user: {current_user}")

    # Auto-generate title if not provided
    title = conversation_data.title or "New Conversation"

    # Create new conversation
    new_conversation = Conversation(
        user_id=current_user,
        title=title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        session.add(new_conversation)
        session.commit()
        session.refresh(new_conversation)

        logger.info(f"[Chat API] Created conversation {new_conversation.id} for user {current_user}")

    except Exception as e:
        session.rollback()
        logger.error(f"[Chat API] Failed to create conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )

    # Return ConversationResponse with message_count=0
    return ConversationResponse(
        id=str(new_conversation.id),
        user_id=str(new_conversation.user_id),
        title=new_conversation.title,
        created_at=new_conversation.created_at,
        updated_at=new_conversation.updated_at,
        message_count=0,
        last_message_preview=None
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> MessageResponse:
    """
    Send a message to a conversation and get AI agent response.

    This endpoint implements T025-T026 of User Story 2:
    1. Validates conversation ownership
    2. Saves user message to database
    3. Loads conversation context from database (stateless agent pattern)
    4. Executes AI agent with OpenAI integration
    5. Saves assistant response with tool_calls metadata
    6. Updates conversation timestamp
    7. Returns assistant response

    **Authentication**: Requires valid JWT token in Authorization header.

    **Environment Variables Required**:
    - OPENAI_API_KEY: OpenAI API key for agent execution

    **Request Body**:
    ```json
    {
        "content": "Help me organize my tasks for this week"
    }
    ```

    **Response**:
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
        "role": "assistant",
        "content": "I'll help you organize your tasks...",
        "tool_calls": {
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "status": "success",
                    "duration_ms": 245
                }
            ],
            "tokens_used": 450,
            "model": "gpt-4"
        },
        "created_at": "2025-12-22T10:15:03Z"
    }
    ```

    Args:
        conversation_id: UUID of the conversation (path parameter)
        message_data: MessageCreate with message content
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        MessageResponse: Assistant's response message

    Raises:
        HTTPException 400: If conversation_id is invalid UUID format
        HTTPException 401: If JWT token is invalid
        HTTPException 403: If conversation doesn't belong to user
        HTTPException 404: If conversation not found or soft-deleted
        HTTPException 500: If database operation fails or OpenAI API key missing

    Degraded Mode:
        If agent execution fails (API error, missing key, timeout), returns
        user message only with appropriate error logged.
    """
    logger.info(f"[Chat API] POST /conversations/{conversation_id}/messages - user: {current_user}")

    # Validate conversation ownership
    conversation = validate_conversation_ownership(
        conversation_id=conversation_id,
        user_id=current_user,
        session=session
    )

    logger.info(f"[Chat API] Validated conversation {conversation.id} ownership for user {current_user}")

    # Convert conversation_id string to UUID
    conv_uuid = UUID(conversation_id)

    # 1. Create and save user message with role='user'
    user_message = Message(
        conversation_id=conv_uuid,
        role=MessageRole.USER,
        content=message_data.content,
        tool_calls=None,  # User messages never have tool calls
        created_at=datetime.utcnow()
    )

    try:
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        logger.info(
            f"[Chat API] Created user message {user_message.id} in conversation {conversation_id}"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"[Chat API] Failed to save user message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save message: {str(e)}"
        )

    # 2. T025: Load conversation context from database (stateless agent pattern)
    try:
        history = await load_conversation_context(
            conversation_id=conv_uuid,
            session=session,
            limit=50  # Load last 50 messages for context
        )
        logger.info(
            f"[Chat API] Loaded {len(history)} messages for conversation context",
            extra={"conversation_id": conversation_id}
        )
    except Exception as e:
        logger.error(f"[Chat API] Failed to load conversation context: {str(e)}", exc_info=True)
        # Continue without history if loading fails (graceful degradation)
        history = []

    # 3. T025: Execute AI agent with conversation history
    agent_result = None
    try:
        # Verify OpenAI API key is configured
        try:
            get_openai_client()
        except ValueError as e:
            logger.error(f"[Chat API] OpenAI API key not configured: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI agent is not configured. Please set OPENAI_API_KEY environment variable."
            )

        # Run agent with user message and history
        agent_result = await run_agent(
            user_id=current_user,
            message=message_data.content,
            history=history
        )

        logger.info(
            f"[Chat API] Agent execution completed",
            extra={
                "conversation_id": conversation_id,
                "tokens_used": agent_result.get("tokens_used", 0),
                "tool_calls_count": len(agent_result.get("tool_calls", [])),
                "finish_reason": agent_result.get("finish_reason")
            }
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like missing API key)
        raise
    except Exception as e:
        # Log error but continue in degraded mode (return user message)
        logger.error(
            f"[Chat API] Agent execution failed: {str(e)}",
            exc_info=True,
            extra={"conversation_id": conversation_id, "user_id": str(current_user)}
        )
        logger.warning(
            f"[Chat API] Operating in degraded mode - returning user message without AI response"
        )

        # Return user message in degraded mode
        return MessageResponse(
            id=str(user_message.id),
            conversation_id=str(user_message.conversation_id),
            role=user_message.role.value,
            content=user_message.content,
            tool_calls=None,
            created_at=user_message.created_at
        )

    # 4. T026: Save assistant message to database
    assistant_message = Message(
        conversation_id=conv_uuid,
        role=MessageRole.ASSISTANT,
        content=agent_result.get("response", "I apologize, but I encountered an issue processing your request."),
        tool_calls={
            "tool_calls": agent_result.get("tool_calls", []),
            "model": agent_result.get("model", "gpt-4"),
            "tokens_used": agent_result.get("tokens_used", 0),
            "finish_reason": agent_result.get("finish_reason", "stop")
        } if agent_result.get("tool_calls") or agent_result.get("tokens_used") else None,
        created_at=datetime.utcnow()
    )

    try:
        session.add(assistant_message)

        # 5. Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        session.commit()
        session.refresh(assistant_message)

        logger.info(
            f"[Chat API] Created assistant message {assistant_message.id} in conversation {conversation_id}"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"[Chat API] Failed to save assistant message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save assistant response: {str(e)}"
        )

    # 6. Return assistant message
    return MessageResponse(
        id=str(assistant_message.id),
        conversation_id=str(assistant_message.conversation_id),
        role=assistant_message.role.value,  # Convert enum to string
        content=assistant_message.content,
        tool_calls=assistant_message.tool_calls,
        created_at=assistant_message.created_at
    )
