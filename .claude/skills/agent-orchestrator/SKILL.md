---
name: "agent-orchestrator"
description: "Orchestrates AI agent initialization with database context, JWT authentication, and session management. Use when wiring up new agents, implementing stateless AI workflows, or integrating agents with backend services in Phase III."
version: "1.0.0"
---

# Agent Orchestrator Skill

## When to Use
- User asks to "create an AI agent" or "wire up an agent"
- User says "Add an agent to handle..." or "Set up agent orchestration"
- Phase III: Agent-Augmented System implementation
- Building stateless AI assistants that need database access
- Integrating agents with FastAPI backend and MCP tools
- Setting up conversation persistence and chat history

## Context
This skill implements the Agent Orchestration pattern from the constitution:
- **Agent Type**: Stateless AI assistant (no in-memory conversation state)
- **Communication**: Model Context Protocol (MCP)
- **Frameworks**: OpenAI Agents SDK + MCP Python SDK
- **Architecture**: Agent layer sits above Phase II backend, consuming existing APIs
- **Security**: JWT authentication, strict user_id boundaries
- **Persistence**: All messages stored in database for ChatKit display

## Workflow
1. **Define Agent Purpose**: Identify the agent's role and capabilities
2. **Database Schema**: Ensure `conversations` and `messages` tables exist
3. **Agent Initialization**: Create agent class with database session injection
4. **JWT Integration**: Extract and validate user_id from JWT tokens
5. **MCP Tool Registration**: Register available MCP tools for the agent
6. **Conversation Management**: Implement conversation creation and message persistence
7. **State Management**: Ensure agent retrieves history from database, not memory
8. **Testing**: Test agent with sample conversations and verify persistence

## Output Format

### 1. Database Models: `backend/app/models/conversation.py`
```python
"""
Conversation and Message models for AI Agent persistence.

Enables stateless AI agents with database-backed conversation history.
"""

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index


class Conversation(SQLModel, table=True):
    """
    Conversation model for AI agent chat history.

    Stores conversation metadata for multi-user TODO application.
    Each user can have multiple conversations with the AI agent.

    Attributes:
        id: Unique conversation identifier
        user_id: Foreign key to User (UUID)
        title: Conversation title (auto-generated or user-defined)
        created_at: Creation timestamp
        updated_at: Last modification timestamp

    Indexes:
        - user_id: For efficient filtering by user
        - (user_id, updated_at): For sorting user's conversations

    Relations:
        messages: One-to-many relationship with Message model
    """

    __tablename__ = "conversations"

    # Primary key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False
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
        max_length=255,
        nullable=False,
        description="Conversation title (auto-generated or user-defined)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)"
    )

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")

    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
    )


class Message(SQLModel, table=True):
    """
    Message model for AI agent chat history.

    Stores individual messages (user and assistant) within conversations.

    Attributes:
        id: Unique message identifier
        conversation_id: Foreign key to Conversation
        role: Message role ("user" or "assistant")
        content: Message text content
        created_at: Creation timestamp

    Indexes:
        - conversation_id: For efficient conversation history retrieval
        - (conversation_id, created_at): For ordered message history

    Relations:
        conversation: Many-to-one relationship with Conversation model
    """

    __tablename__ = "messages"

    # Primary key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False
    )

    # Foreign key to conversations table
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    # Message data
    role: Literal["user", "assistant"] = Field(
        nullable=False,
        description="Message role: 'user' or 'assistant'"
    )

    content: str = Field(
        nullable=False,
        description="Message text content"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp (UTC)"
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

### 2. Agent Orchestrator: `backend/app/agents/orchestrator.py`
```python
"""
AI Agent Orchestrator for TODO application.

Manages stateless AI agent initialization, conversation persistence,
and integration with MCP tools.
"""

from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import Session, select

from app.database import get_session
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.auth.dependencies import verify_token
from app.mcp.server import get_mcp_server


class AgentOrchestrator:
    """
    Orchestrates AI agent interactions with database-backed persistence.

    This class implements the stateless agent pattern:
    - NO in-memory conversation state
    - ALL messages stored in database immediately
    - Agent retrieves history from database on each request
    - JWT authentication enforced
    - Strict user_id boundaries
    """

    def __init__(self, db: Session):
        """
        Initialize agent orchestrator.

        Args:
            db: Database session for persistence
        """
        self.db = db
        self.mcp_server = get_mcp_server()

    @staticmethod
    def verify_user(user_token: str) -> UUID:
        """
        Verify JWT token and extract user_id.

        Args:
            user_token: JWT authentication token

        Returns:
            user_id: UUID of authenticated user

        Raises:
            HTTPException: If token is invalid
        """
        return verify_token(user_token)

    def create_conversation(
        self,
        user_token: str,
        title: Optional[str] = None
    ) -> Dict:
        """
        Create a new conversation for the authenticated user.

        Args:
            user_token: JWT authentication token
            title: Optional conversation title (auto-generated if None)

        Returns:
            Dict with conversation details
        """
        try:
            user_id = self.verify_user(user_token)

            # Auto-generate title if not provided
            if not title:
                # Count existing conversations for this user
                count = len(self.db.exec(
                    select(Conversation).where(Conversation.user_id == user_id)
                ).all())
                title = f"Conversation {count + 1}"

            # Create conversation
            conversation = Conversation(
                user_id=user_id,
                title=title
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            return {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "message_count": 0
            }

        except Exception as e:
            self.db.rollback()
            return {"error": str(e), "created": False}

    def get_conversations(self, user_token: str) -> List[Dict]:
        """
        Get all conversations for the authenticated user.

        Args:
            user_token: JWT authentication token

        Returns:
            List of conversation summaries
        """
        try:
            user_id = self.verify_user(user_token)

            # Fetch conversations ordered by updated_at DESC
            conversations = self.db.exec(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
            ).all()

            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": len(conv.messages)
                }
                for conv in conversations
            ]

        except Exception as e:
            return {"error": str(e)}

    def get_conversation_history(
        self,
        user_token: str,
        conversation_id: int
    ) -> List[Dict]:
        """
        Get full message history for a conversation.

        CRITICAL: This is how the agent retrieves context.
        The agent MUST NOT store conversation state in memory.

        Args:
            user_token: JWT authentication token
            conversation_id: Conversation ID to retrieve

        Returns:
            List of messages ordered by created_at ASC
        """
        try:
            user_id = self.verify_user(user_token)

            # Verify conversation belongs to user
            conversation = self.db.exec(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            ).first()

            if not conversation:
                return {"error": "Conversation not found", "messages": []}

            # Fetch messages ordered chronologically
            messages = self.db.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
            ).all()

            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]

        except Exception as e:
            return {"error": str(e)}

    def add_message(
        self,
        user_token: str,
        conversation_id: int,
        role: str,
        content: str
    ) -> Dict:
        """
        Add a message to a conversation.

        CRITICAL: Messages MUST be persisted immediately.
        This ensures conversation survives browser refresh.

        Args:
            user_token: JWT authentication token
            conversation_id: Conversation to add message to
            role: "user" or "assistant"
            content: Message text

        Returns:
            Dict with message details
        """
        try:
            user_id = self.verify_user(user_token)

            # Verify conversation belongs to user
            conversation = self.db.exec(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            ).first()

            if not conversation:
                return {"error": "Conversation not found", "saved": False}

            # Create message
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content
            )
            self.db.add(message)

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            self.db.add(conversation)

            self.db.commit()
            self.db.refresh(message)

            return {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "saved": True
            }

        except Exception as e:
            self.db.rollback()
            return {"error": str(e), "saved": False}

    def process_user_message(
        self,
        user_token: str,
        conversation_id: int,
        user_message: str
    ) -> Dict:
        """
        Process a user message and generate AI response.

        This is the main orchestration method:
        1. Verify user authentication
        2. Save user message to database
        3. Retrieve conversation history
        4. Call AI with history and MCP tools
        5. Save AI response to database
        6. Return response

        Args:
            user_token: JWT authentication token
            conversation_id: Active conversation ID
            user_message: User's message text

        Returns:
            Dict with AI response and metadata
        """
        try:
            # 1. Save user message
            user_msg_result = self.add_message(
                user_token,
                conversation_id,
                role="user",
                content=user_message
            )
            if not user_msg_result.get("saved"):
                return {"error": "Failed to save user message"}

            # 2. Retrieve conversation history
            history = self.get_conversation_history(user_token, conversation_id)
            if isinstance(history, dict) and "error" in history:
                return history

            # 3. Call AI with history and MCP tools
            # TODO: Integrate with OpenAI Agents SDK
            # For now, simple placeholder response
            ai_response = f"I received your message: '{user_message}'. I have access to {len(self.mcp_server.list_tools())} MCP tools."

            # 4. Save AI response
            ai_msg_result = self.add_message(
                user_token,
                conversation_id,
                role="assistant",
                content=ai_response
            )
            if not ai_msg_result.get("saved"):
                return {"error": "Failed to save AI response"}

            return {
                "user_message_id": user_msg_result["id"],
                "assistant_message_id": ai_msg_result["id"],
                "assistant_response": ai_response,
                "success": True
            }

        except Exception as e:
            return {"error": str(e), "success": False}
```

### 3. FastAPI Router: `backend/app/routers/chat.py`
```python
"""
Chat router for AI agent conversations.

Exposes agent orchestration as REST endpoints for frontend.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.agents.orchestrator import AgentOrchestrator


router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ConversationCreate(BaseModel):
    """Request body for creating a conversation."""
    title: Optional[str] = None


class MessageSend(BaseModel):
    """Request body for sending a message."""
    message: str


@router.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_session),
    user_token: str = Depends(get_auth_token)
) -> Dict:
    """
    Create a new conversation.

    Returns conversation ID and metadata.
    """
    orchestrator = AgentOrchestrator(db)
    result = orchestrator.create_conversation(user_token, data.title)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/conversations")
async def list_conversations(
    db: Session = Depends(get_session),
    user_token: str = Depends(get_auth_token)
) -> List[Dict]:
    """
    List all conversations for authenticated user.

    Returns conversations ordered by updated_at DESC.
    """
    orchestrator = AgentOrchestrator(db)
    return orchestrator.get_conversations(user_token)


@router.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_session),
    user_token: str = Depends(get_auth_token)
) -> List[Dict]:
    """
    Get full message history for a conversation.

    Used by ChatKit to display history on page load.
    """
    orchestrator = AgentOrchestrator(db)
    return orchestrator.get_conversation_history(user_token, conversation_id)


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    data: MessageSend,
    db: Session = Depends(get_session),
    user_token: str = Depends(get_auth_token)
) -> Dict:
    """
    Send a message to the AI agent.

    Processes message, generates AI response, and persists both to database.
    """
    orchestrator = AgentOrchestrator(db)
    result = orchestrator.process_user_message(
        user_token,
        conversation_id,
        data.message
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


def get_auth_token() -> str:
    """
    Extract JWT token from Authorization header.

    TODO: Implement proper header extraction.
    """
    # Placeholder - implement actual token extraction
    return "token"
```

### 4. Database Migration: `backend/alembic/versions/XXX_add_conversations.py`
```python
"""Add conversations and messages tables

Revision ID: XXX
Revises: YYY
Create Date: 2025-12-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = 'XXX'
down_revision = 'YYY'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_user_updated', 'conversations', ['user_id', 'updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_messages_conversation_created', 'messages')
    op.drop_index('ix_messages_conversation_id', 'messages')
    op.drop_table('messages')

    op.drop_index('ix_conversations_user_updated', 'conversations')
    op.drop_index('ix_conversations_user_id', 'conversations')
    op.drop_table('conversations')
```

## Agent Orchestration Best Practices

### 1. Stateless Design
```python
# ❌ BAD: Storing state in memory
class StatefulAgent:
    def __init__(self):
        self.conversations = {}  # In-memory state - LOST on restart

# ✅ GOOD: Database-backed state
class StatelessAgent:
    def __init__(self, db: Session):
        self.db = db  # All state in database
```

### 2. JWT Validation
```python
# Always verify user_id before database operations
user_id = self.verify_user(user_token)
conversation = db.exec(
    select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # ✅ Enforces tenant isolation
    )
).first()
```

### 3. Immediate Persistence
```python
# ✅ Save messages immediately after creation
message = Message(conversation_id=id, role="user", content=text)
db.add(message)
db.commit()  # Persist NOW, not later
db.refresh(message)  # Get ID for response
```

### 4. History Retrieval
```python
# ✅ Agent retrieves history from database on EVERY request
history = db.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
).all()
```

## Post-Creation Steps
1. **Create Migration**: Run `alembic revision --autogenerate -m "Add conversations"`
2. **Apply Migration**: Run `alembic upgrade head`
3. **Register Router**: Add to `main.py`:
   ```python
   from app.routers import chat
   app.include_router(chat.router)
   ```
4. **Test Endpoints**: Use `/docs` to test conversation creation and message persistence
5. **Frontend Integration**: Connect ChatKit to `/api/chat` endpoints
6. **Create PHR**:
   - Title: "Agent Orchestrator - Stateless AI Setup"
   - Stage: `green`
   - Feature: `ai-agent`

## Example
**Input**: "Set up an AI agent to help manage tasks via chat"

**Output**:
1. `backend/app/models/conversation.py` - Conversation and Message models
2. `backend/app/agents/orchestrator.py` - AgentOrchestrator class
3. `backend/app/routers/chat.py` - FastAPI chat endpoints
4. Database migration for conversations and messages tables
5. JWT authentication integrated
6. All messages persisted to database
7. Agent retrieves history on each request (stateless)

## Quality Checklist
Before finalizing:
- [ ] Database models created with proper indexes
- [ ] AgentOrchestrator class implements stateless pattern
- [ ] JWT authentication enforced in all methods
- [ ] Messages persisted immediately after creation
- [ ] Conversation history retrieved from database (no memory state)
- [ ] User_id boundaries enforced (tenant isolation)
- [ ] FastAPI router exposes agent endpoints
- [ ] Database migration created and applied
- [ ] Error handling with user-friendly messages
- [ ] No sensitive data in responses
- [ ] Integration tested with sample conversations
- [ ] ChatKit frontend can retrieve history on page load
