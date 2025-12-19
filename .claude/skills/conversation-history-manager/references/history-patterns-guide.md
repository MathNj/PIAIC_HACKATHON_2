# Conversation History Management Patterns

## Overview

This guide provides comprehensive patterns for managing conversation history in database-backed AI chat applications with stateless agent architecture.

## Core Principles

1. **Stateless Architecture**: No in-memory conversation state, all history fetched from database
2. **Tenant Isolation**: All queries filtered by user_id
3. **Performance**: Indexed queries with pagination and limits
4. **Scalability**: Cursor-based pagination, history truncation, archival strategies

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_conversations_deleted ON conversations(deleted_at) WHERE deleted_at IS NOT NULL;
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (length(content) <= 10000),
    tool_calls JSONB NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at ASC);
CREATE INDEX idx_messages_tool_calls ON messages USING GIN(tool_calls) WHERE tool_calls IS NOT NULL;
```

## Query Patterns

### Pattern 1: Load Conversation History for AI Context

**Purpose**: Load last N messages for stateless agent context

**SQLModel implementation**:
```python
from sqlmodel import Session, select
from app.models import Message

def load_conversation_context(
    conversation_id: str,
    db: Session,
    limit: int = 50
) -> list[Message]:
    """
    Load last 50 messages in chronological order for AI context.

    Args:
        conversation_id: UUID of conversation
        db: SQLModel session
        limit: Maximum messages to load (default 50)

    Returns:
        List of messages in chronological order (oldest first)
    """
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    # Reverse to get chronological order (oldest first)
    return list(reversed(messages))
```

**Performance**: Uses `idx_messages_conversation_created` index
**Scalability**: Limits context to prevent token overflow

### Pattern 2: Cursor-Based Conversation Pagination

**Purpose**: Efficient pagination for conversation list

**SQLModel implementation**:
```python
from sqlmodel import Session, select
from app.models import Conversation
from datetime import datetime

def list_conversations_paginated(
    user_id: str,
    db: Session,
    cursor: str | None = None,
    limit: int = 20
) -> dict:
    """
    List conversations with cursor-based pagination.

    Args:
        user_id: UUID of user (tenant isolation)
        db: SQLModel session
        cursor: ISO timestamp cursor for pagination
        limit: Page size (default 20)

    Returns:
        {
            "conversations": [...],
            "cursor": "2024-01-15T10:30:00Z" or None,
            "has_more": bool
        }
    """
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
        .order_by(Conversation.updated_at.desc())
    )

    if cursor:
        cursor_time = datetime.fromisoformat(cursor)
        query = query.where(Conversation.updated_at < cursor_time)

    # Fetch limit + 1 to check if there's more
    conversations = db.exec(query.limit(limit + 1)).all()

    has_more = len(conversations) > limit
    if has_more:
        conversations = conversations[:limit]

    next_cursor = None
    if has_more and conversations:
        next_cursor = conversations[-1].updated_at.isoformat()

    return {
        "conversations": conversations,
        "cursor": next_cursor,
        "has_more": has_more
    }
```

**Performance**: Uses `idx_conversations_user_updated` index
**Benefits**: Consistent results, handles concurrent inserts, no offset drift

### Pattern 3: Soft Delete with Audit Trail

**Purpose**: Mark conversations as deleted without losing data

**SQLModel implementation**:
```python
from sqlmodel import Session
from app.models import Conversation
from datetime import datetime

def soft_delete_conversation(
    conversation_id: str,
    user_id: str,
    db: Session
) -> bool:
    """
    Soft delete conversation (sets deleted_at timestamp).

    Args:
        conversation_id: UUID of conversation
        user_id: UUID of user (ownership validation)
        db: SQLModel session

    Returns:
        True if deleted, False if not found or access denied
    """
    conversation = db.get(Conversation, conversation_id)

    # Validate ownership
    if not conversation or conversation.user_id != user_id:
        return False

    # Prevent double-delete
    if conversation.deleted_at:
        return False

    conversation.deleted_at = datetime.utcnow()
    db.add(conversation)
    db.commit()

    return True

def restore_conversation(
    conversation_id: str,
    user_id: str,
    db: Session
) -> bool:
    """Restore soft-deleted conversation."""
    conversation = db.get(Conversation, conversation_id)

    if not conversation or conversation.user_id != user_id:
        return False

    if not conversation.deleted_at:
        return False  # Not deleted

    conversation.deleted_at = None
    conversation.updated_at = datetime.utcnow()
    db.add(conversation)
    db.commit()

    return True
```

**Benefits**: Auditability, recovery, compliance

### Pattern 4: Message Polling for Real-Time Updates

**Purpose**: Fetch new messages since last check

**SQLModel implementation**:
```python
from sqlmodel import Session, select
from app.models import Message
from datetime import datetime

def get_new_messages(
    conversation_id: str,
    user_id: str,
    since: str,
    db: Session
) -> list[Message]:
    """
    Get messages created after a specific timestamp.

    Args:
        conversation_id: UUID of conversation
        user_id: UUID of user (ownership validation)
        since: ISO timestamp of last known message
        db: SQLModel session

    Returns:
        List of new messages in chronological order
    """
    # Validate ownership
    from app.models import Conversation
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        return []

    since_time = datetime.fromisoformat(since)

    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.created_at > since_time)
        .order_by(Message.created_at.asc())
    ).all()

    return messages
```

**Performance**: Uses `idx_messages_conversation_created` index
**Use case**: HTTP polling for real-time updates (2-3 second interval)

### Pattern 5: Conversation Search and Filtering

**Purpose**: Search conversations by title or content

**SQLModel implementation**:
```python
from sqlmodel import Session, select, or_
from app.models import Conversation, Message

def search_conversations(
    user_id: str,
    query: str,
    db: Session,
    limit: int = 20
) -> list[Conversation]:
    """
    Search conversations by title or message content.

    Args:
        user_id: UUID of user
        query: Search query
        db: SQLModel session
        limit: Maximum results

    Returns:
        List of matching conversations
    """
    # Search by title
    conversations = db.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
        .where(Conversation.title.ilike(f"%{query}%"))
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    ).all()

    return conversations

def search_messages(
    user_id: str,
    query: str,
    db: Session,
    limit: int = 50
) -> list[Message]:
    """
    Full-text search across message content.

    Requires PostgreSQL full-text search index.
    """
    # Join with conversations for tenant isolation
    from sqlmodel import join

    messages = db.exec(
        select(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
        .where(Message.content.ilike(f"%{query}%"))
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    return messages
```

**Enhancement**: Add PostgreSQL full-text search for better performance:
```sql
CREATE INDEX idx_messages_content_fts ON messages USING GIN(to_tsvector('english', content));
```

### Pattern 6: Conversation Metadata Aggregation

**Purpose**: Get conversation stats (message count, last message preview)

**SQLModel implementation**:
```python
from sqlmodel import Session, select, func
from app.models import Conversation, Message

def get_conversation_with_metadata(
    conversation_id: str,
    user_id: str,
    db: Session
) -> dict | None:
    """
    Get conversation with computed metadata.

    Returns:
        {
            "id": str,
            "title": str,
            "created_at": datetime,
            "updated_at": datetime,
            "message_count": int,
            "last_message_preview": str | None
        }
    """
    conversation = db.get(Conversation, conversation_id)

    if not conversation or conversation.user_id != user_id:
        return None

    # Count messages
    message_count = db.exec(
        select(func.count(Message.id))
        .where(Message.conversation_id == conversation_id)
    ).one()

    # Get last message preview
    last_message = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(1)
    ).first()

    preview = None
    if last_message:
        preview = last_message.content[:100]  # First 100 chars
        if len(last_message.content) > 100:
            preview += "..."

    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "message_count": message_count,
        "last_message_preview": preview
    }
```

**Optimization**: Cache message_count in conversations table, update with trigger

### Pattern 7: History Archival and Cleanup

**Purpose**: Archive old conversations, clean up orphaned messages

**SQLModel implementation**:
```python
from sqlmodel import Session, select, delete
from app.models import Conversation, Message
from datetime import datetime, timedelta

def archive_old_conversations(
    user_id: str,
    days_old: int,
    db: Session
) -> int:
    """
    Hard delete soft-deleted conversations older than N days.

    Returns: Number of conversations archived
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)

    old_conversations = db.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_not(None))
        .where(Conversation.deleted_at < cutoff_date)
    ).all()

    count = len(old_conversations)

    for conversation in old_conversations:
        # Cascade delete will remove messages
        db.delete(conversation)

    db.commit()

    return count

def cleanup_orphaned_messages(db: Session) -> int:
    """
    Remove messages for deleted conversations.

    Only needed if CASCADE delete not configured.
    """
    result = db.exec(
        delete(Message)
        .where(
            Message.conversation_id.in_(
                select(Conversation.id)
                .where(Conversation.deleted_at.is_not(None))
            )
        )
    )

    db.commit()

    return result.rowcount
```

**Best practice**: Run archival as scheduled job (e.g., weekly cron)

## Performance Optimization

### 1. Database Indexes

**Critical indexes**:
```sql
-- Conversation list (user's conversations sorted by update time)
CREATE INDEX idx_conversations_user_updated
ON conversations(user_id, updated_at DESC)
WHERE deleted_at IS NULL;

-- Message history (chronological order for AI context)
CREATE INDEX idx_messages_conversation_created
ON messages(conversation_id, created_at ASC);

-- Tool call analytics
CREATE INDEX idx_messages_tool_calls
ON messages USING GIN(tool_calls)
WHERE tool_calls IS NOT NULL;

-- Full-text search
CREATE INDEX idx_messages_content_fts
ON messages USING GIN(to_tsvector('english', content));
```

### 2. Query Optimization

**Use EXPLAIN ANALYZE** to verify index usage:
```sql
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE conversation_id = 'uuid-here'
ORDER BY created_at ASC
LIMIT 50;
```

Expected: Index Scan using `idx_messages_conversation_created`

### 3. Connection Pooling

**FastAPI with SQLModel**:
```python
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

### 4. Caching Strategy

**Cache conversation metadata**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_conversation_title(conversation_id: str) -> str:
    # Cache conversation titles to avoid repeated DB queries
    ...
```

**Redis for session caching**:
```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_conversation_metadata(conversation_id: str) -> dict:
    # Check cache first
    cached = redis_client.get(f"conv:{conversation_id}")
    if cached:
        return json.loads(cached)

    # Query database
    metadata = query_database(conversation_id)

    # Cache for 5 minutes
    redis_client.setex(
        f"conv:{conversation_id}",
        300,
        json.dumps(metadata)
    )

    return metadata
```

## Security Best Practices

### 1. Tenant Isolation

**Always validate user ownership**:
```python
def validate_conversation_access(
    conversation_id: str,
    user_id: str,
    db: Session
) -> Conversation | None:
    """
    Validate user has access to conversation.

    Returns conversation if access granted, None otherwise.
    """
    conversation = db.get(Conversation, conversation_id)

    if not conversation:
        return None

    if conversation.user_id != user_id:
        # Log unauthorized access attempt
        logger.warning(
            f"Unauthorized access attempt: user {user_id} "
            f"tried to access conversation {conversation_id}"
        )
        return None

    return conversation
```

### 2. Input Validation

**Sanitize user input**:
```python
from pydantic import BaseModel, Field, validator

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

    @validator('content')
    def sanitize_content(cls, v):
        # Remove null bytes
        v = v.replace('\x00', '')
        # Strip excessive whitespace
        v = ' '.join(v.split())
        return v
```

### 3. Rate Limiting

**Prevent abuse**:
```python
from fastapi import HTTPException
from datetime import datetime, timedelta

def check_rate_limit(user_id: str, db: Session):
    """
    Limit to 100 messages per hour per user.
    """
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    message_count = db.exec(
        select(func.count(Message.id))
        .join(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Message.created_at > one_hour_ago)
    ).one()

    if message_count >= 100:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
```

## Testing Patterns

### Unit Tests

```python
import pytest
from sqlmodel import Session, create_engine
from app.models import Conversation, Message

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    with Session(engine) as session:
        yield session

def test_load_conversation_context(session):
    # Create test data
    conversation = Conversation(user_id="user-1", title="Test")
    session.add(conversation)
    session.commit()

    for i in range(60):
        msg = Message(
            conversation_id=conversation.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )
        session.add(msg)
    session.commit()

    # Load context (limit 50)
    context = load_conversation_context(conversation.id, session)

    assert len(context) == 50
    assert context[0].content == "Message 10"  # Oldest of last 50
    assert context[-1].content == "Message 59"  # Newest
```

## Common Issues and Solutions

**Issue**: Out of memory errors with large conversation histories
**Solution**: Implement pagination and limits (max 50 messages for AI context)

**Issue**: Slow conversation list queries
**Solution**: Ensure `idx_conversations_user_updated` index exists and is used

**Issue**: Race conditions on concurrent message creation
**Solution**: Use database transactions and optimistic locking

**Issue**: Deleted conversations still appear in searches
**Solution**: Always filter by `deleted_at IS NULL` in queries
