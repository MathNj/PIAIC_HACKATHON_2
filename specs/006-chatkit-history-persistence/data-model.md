# Data Model: OpenAI Chatkit Integration & History Persistence

**Phase**: 1 (Design & Contracts)
**Date**: 2025-12-19
**Status**: Complete

## Overview

This document defines the database schema and entity models for Phase III chat persistence. All models maintain strict tenant isolation via `user_id` foreign keys and support the constitutional requirement for stateless agent architecture.

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │ (Existing Phase II entity)
│─────────────────│
│ id (PK)         │
│ email           │
│ password_hash   │
│ created_at      │
└─────────────────┘
         │
         │ 1:N (owns)
         ▼
┌─────────────────────────┐
│     Conversation        │ (NEW)
│─────────────────────────│
│ id (PK)                 │
│ user_id (FK → User)     │──┐ (Tenant Isolation)
│ title                   │  │
│ created_at              │  │
│ updated_at              │  │
│ deleted_at (nullable)   │  │
└─────────────────────────┘  │
         │                    │
         │ 1:N (contains)     │
         ▼                    │
┌─────────────────────────┐  │
│       Message           │ (NEW)
│─────────────────────────│  │
│ id (PK)                 │  │
│ conversation_id (FK)    │  │
│ role (user|assistant)   │  │
│ content                 │  │
│ tool_calls (JSONB)      │  │
│ created_at              │  │
└─────────────────────────┘  │
                              │
Tenant Isolation Constraint: │
All queries MUST filter by    │
user_id extracted from JWT ───┘
```

## Database Tables

### 1. Conversation

**Purpose**: Represents a chat thread between user and AI assistant

**SQLModel Schema**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this conversation (tenant isolation)"
    )
    title: str = Field(
        max_length=200,
        description="Conversation title (auto-generated or user-set)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Last message timestamp (for sorting)"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Soft delete timestamp (null = active)"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True
    )
    user: "User" = Relationship(back_populates="conversations")
```

**Indexes**:
- Primary: `id` (UUID, clustered)
- Foreign Key: `user_id` (for tenant filtering)
- Query optimization: `(user_id, updated_at DESC)` (for conversation list)
- Soft delete: `(user_id, deleted_at)` (for filtering active conversations)

**Validation Rules**:
- `title`: Required, 1-200 characters, trimmed
- `user_id`: Must exist in `users` table (foreign key constraint)
- `deleted_at`: Must be >= `created_at` if not null

**State Transitions**:
1. **Created**: `deleted_at = NULL`
2. **Soft Deleted**: `deleted_at = NOW()`
3. **Hard Deleted**: Row removed (future cleanup job, >90 days)

### 2. Message

**Purpose**: Represents a single message in a conversation (user or assistant)

**SQLModel Schema**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation"
    )
    role: MessageRole = Field(
        description="Message author: 'user' or 'assistant'"
    )
    content: str = Field(
        max_length=10000,
        description="Message text content (markdown supported)"
    )
    tool_calls: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="MCP tool invocations (JSONB, assistant messages only)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message creation timestamp"
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Indexes**:
- Primary: `id` (UUID, clustered)
- Foreign Key: `conversation_id` (for fetching conversation history)
- Query optimization: `(conversation_id, created_at ASC)` (for chronological message retrieval)
- Tool usage analytics: `tool_calls USING GIN` (for JSONB queries)

**Validation Rules**:
- `content`: Required, 1-10,000 characters
- `conversation_id`: Must exist in `conversations` table (foreign key constraint)
- `role`: Must be 'user' or 'assistant' (enum constraint)
- `tool_calls`: Only allowed when `role = 'assistant'` (application-level validation)

**Tool Calls JSONB Structure**:
```json
{
  "tool_calls": [
    {
      "tool_name": "create_task",
      "arguments": {
        "title": "Buy groceries",
        "priority": "normal",
        "due_date": null
      },
      "result": {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "created"
      },
      "timestamp": "2025-12-19T10:30:00.000Z",
      "duration_ms": 245,
      "status": "success"
    }
  ]
}
```

**State Transitions**:
Messages are immutable after creation (no updates or deletions). Cascade delete when parent conversation is hard-deleted.

## Pydantic Schemas (Request/Response)

### Conversation Schemas

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConversationCreate(BaseModel):
    """Request: Create new conversation"""
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional title (auto-generated if omitted)"
    )

class ConversationUpdate(BaseModel):
    """Request: Update conversation title"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="New conversation title"
    )

class ConversationResponse(BaseModel):
    """Response: Conversation data"""
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int  # Computed field
    last_message_preview: Optional[str] = None  # First 100 chars of last message

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    """Response: Paginated conversation list"""
    conversations: List[ConversationResponse]
    nextCursor: Optional[str] = None  # ISO timestamp for cursor pagination
    hasMore: bool
```

### Message Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class MessageCreate(BaseModel):
    """Request: Send new message"""
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message text content"
    )

    @validator('content')
    def content_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be only whitespace')
        return v.strip()

class MessageResponse(BaseModel):
    """Response: Message data"""
    id: str
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str
    tool_calls: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    """Response: Conversation message history"""
    messages: List[MessageResponse]
    conversation_id: str
    total_count: int
```

## Database Migration (Alembic)

**File**: `backend/alembic/versions/xxxx_add_conversations_messages.py`

```python
"""Add conversations and messages tables for Phase III chat persistence

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-12-19 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = 'xxxx'
down_revision = 'yyyy'  # Previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
    )

    # Create indexes on conversations
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_user_updated', 'conversations', ['user_id', 'updated_at'], postgresql_ops={'updated_at': 'DESC'})
    op.create_index('ix_conversations_user_deleted', 'conversations', ['user_id', 'deleted_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='message_role'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # Create indexes on messages
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
    op.create_index('ix_messages_tool_calls', 'messages', ['tool_calls'], postgresql_using='gin')

    # Add check constraint for content length
    op.create_check_constraint(
        'ck_messages_content_length',
        'messages',
        'LENGTH(content) <= 10000'
    )

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
    op.execute('DROP TYPE message_role')
```

## Tenant Isolation Enforcement

**Critical Security Pattern**: All queries MUST enforce user_id filtering

### Backend Router Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/chat")

@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    cursor: Optional[str] = None
):
    """
    List conversations for authenticated user only.
    SECURITY: user_id from JWT token, NOT from query params.
    """
    query = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.deleted_at == None
    )

    if cursor:
        query = query.filter(Conversation.updated_at < cursor)

    conversations = query.order_by(
        Conversation.updated_at.desc()
    ).limit(limit + 1).all()

    # ...implementation
```

### Validation Pattern

```python
def validate_conversation_ownership(
    conversation_id: str,
    user_id: str,
    db: Session
) -> Conversation:
    """
    Verify user owns conversation before allowing access.
    Returns 403 if conversation exists but belongs to different user.
    Returns 404 if conversation doesn't exist.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if conversation.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Conversation deleted")

    return conversation
```

## Performance Considerations

### Expected Query Patterns

1. **List conversations** (most frequent):
   - Query: `SELECT * FROM conversations WHERE user_id = ? AND deleted_at IS NULL ORDER BY updated_at DESC LIMIT 20`
   - Index: `(user_id, updated_at DESC)`
   - Expected rows: 10-50 per user
   - Performance: <10ms

2. **Load conversation history** (frequent):
   - Query: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT 50`
   - Index: `(conversation_id, created_at ASC)`
   - Expected rows: 10-100 per conversation
   - Performance: <20ms

3. **Create message** (frequent):
   - Query: `INSERT INTO messages (...) VALUES (...)` + `UPDATE conversations SET updated_at = NOW() WHERE id = ?`
   - Transaction: Required (both operations atomic)
   - Performance: <50ms

4. **Tool usage analytics** (infrequent, admin only):
   - Query: `SELECT tool_calls->>'tool_name', COUNT(*) FROM messages WHERE tool_calls IS NOT NULL GROUP BY tool_calls->>'tool_name'`
   - Index: `tool_calls USING GIN`
   - Performance: Variable (depends on dataset size)

### Capacity Planning

- **Storage**: ~500 bytes per message (average)
- **Expected scale**: 10,000 users × 10 conversations × 50 messages = 5M messages = ~2.5GB
- **Index overhead**: ~30% of data size = ~750MB
- **Total database size**: ~3.5GB (well within Neon free tier limits)

## Data Lifecycle

### Retention Policy

- **Active conversations**: No limit (retained indefinitely)
- **Soft-deleted conversations**: Retained for 90 days
- **Hard-deleted conversations**: Permanently removed after 90 days (future cleanup job)

### Cleanup Job (Future Implementation)

```python
# backend/app/jobs/cleanup_deleted_conversations.py
def cleanup_old_deleted_conversations():
    """
    Hard delete conversations that have been soft-deleted for >90 days.
    Run daily via cron job.
    """
    threshold = datetime.utcnow() - timedelta(days=90)

    deleted_count = db.query(Conversation).filter(
        Conversation.deleted_at < threshold
    ).delete()

    db.commit()
    return deleted_count
```

## Testing Strategy

### Unit Tests

- Conversation CRUD operations
- Message CRUD operations
- Tenant isolation validation
- Soft delete behavior
- Tool call JSON serialization

### Integration Tests

- Full conversation flow (create → send messages → load history → delete)
- Pagination edge cases (empty list, single page, multiple pages)
- Concurrent message sends (race condition handling)
- Cross-user access attempts (security validation)

### Performance Tests

- Load 1000 conversations (pagination performance)
- Load 100 messages (history retrieval performance)
- Concurrent message sends (database contention)

## Summary

This data model provides:
- ✅ Stateless agent architecture support (all history in database)
- ✅ Strict tenant isolation (user_id filtering on all queries)
- ✅ Efficient querying (indexes on common access patterns)
- ✅ Auditability (soft delete, tool call tracking)
- ✅ Scalability (cursor-based pagination, JSONB for flexible schema)
- ✅ Constitutional compliance (Phase III requirements satisfied)
