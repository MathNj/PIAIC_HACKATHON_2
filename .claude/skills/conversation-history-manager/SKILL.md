---
name: conversation-history-manager
description: Implement conversation history management patterns for database-backed AI chat applications with stateless agent architecture. Use when implementing: (1) Stateless AI agent context loading (no in-memory state), (2) Cursor-based conversation pagination, (3) Message history querying and filtering, (4) Soft delete patterns with audit trails, (5) Conversation metadata aggregation, (6) History archival and cleanup strategies, (7) Tenant isolation and security patterns, or (8) Performance optimization with database indexes. This skill provides SQLModel query patterns, pagination utilities, and production-ready conversation management code.
---

# Conversation History Manager

This skill provides comprehensive patterns for managing conversation history in database-backed AI chat applications with stateless agent architecture.

## Core Principles

1. **Stateless Architecture**: No in-memory conversation state, all history fetched from database
2. **Tenant Isolation**: All queries filtered by user_id to prevent cross-tenant data leakage
3. **Performance**: Indexed queries with pagination and limits
4. **Scalability**: Cursor-based pagination, history truncation, archival strategies

## Quick Start Workflow

### Step 1: Review Patterns Guide

Read the comprehensive patterns guide:
```bash
.claude/skills/conversation-history-manager/references/history-patterns-guide.md
```

This guide provides:
- 7 core query patterns (context loading, pagination, soft delete, polling, search, metadata, archival)
- Database schema with performance indexes
- Security best practices
- Performance optimization strategies
- Testing patterns

### Step 2: Copy Utility Functions

**Context manager** - Copy `assets/utils/context_manager.py` to `backend/app/agents/context_manager.py`:
- `load_conversation_context()` - Load last 50 messages for AI (stateless requirement)
- `get_new_messages()` - Polling for real-time updates
- `validate_conversation_access()` - Tenant isolation enforcement
- `truncate_history_for_tokens()` - Token budget management

**Pagination utilities** - Copy `assets/utils/pagination.py` to `backend/app/utils/pagination.py`:
- `paginate_conversations()` - Cursor-based pagination (recommended)
- `paginate_with_offset()` - Offset-based pagination (legacy)

### Step 3: Implement Query Patterns

Use the patterns from the reference guide:

**Pattern 1: Load Conversation History for AI Context**
```python
from app.agents.context_manager import load_conversation_context

async def run_agent(conversation_id: str, user_message: str, db: Session):
    # Load last 50 messages (stateless - fetch from DB every request)
    history = load_conversation_context(conversation_id, db, limit=50)

    # Build messages for AI
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": user_message})

    # Call AI model with full context
    response = await ai_client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response
```

**Pattern 2: Cursor-Based Conversation Pagination**
```python
from app.utils.pagination import paginate_conversations

@router.get("/api/chat/conversations")
async def list_conversations(
    cursor: str | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    result = paginate_conversations(
        user_id=current_user.id,
        db=db,
        cursor=cursor,
        limit=limit
    )

    return result  # {"conversations": [...], "cursor": "...", "has_more": bool}
```

**Pattern 3: Soft Delete with Audit Trail**
```python
from datetime import datetime

@router.delete("/api/chat/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    conversation = db.get(Conversation, conversation_id)

    # Validate ownership
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404)

    # Soft delete (set timestamp)
    conversation.deleted_at = datetime.utcnow()
    db.add(conversation)
    db.commit()

    return {"message": "Conversation deleted"}
```

**Pattern 4: Message Polling for Real-Time Updates**
```python
from app.agents.context_manager import get_new_messages

@router.get("/api/chat/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    since: str | None = None,  # ISO timestamp
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if since:
        # Polling mode: get new messages since timestamp
        messages = get_new_messages(
            conversation_id=conversation_id,
            user_id=current_user.id,
            since=since,
            db=db
        )
    else:
        # Initial load: get full history
        messages = load_conversation_context(conversation_id, db)

    return {"messages": messages, "conversation_id": conversation_id}
```

### Step 4: Create Database Indexes

**Critical indexes for performance**:

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
```

**Create with Alembic migration**:
```python
def upgrade():
    op.create_index(
        'idx_conversations_user_updated',
        'conversations',
        ['user_id', sa.text('updated_at DESC')],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at']
    )
```

### Step 5: Implement Security Patterns

**Always validate conversation access**:
```python
from app.agents.context_manager import validate_conversation_access

@router.post("/api/chat/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Validate ownership (tenant isolation)
    conversation = validate_conversation_access(
        conversation_id=conversation_id,
        user_id=current_user.id,
        db=db
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Proceed with message creation
    ...
```

## Key Implementation Details

### Stateless Agent Pattern

**Critical**: Agent runtime MUST NOT store conversation state in memory.

**Why**: Enables horizontal scaling, load balancing, and constitutional compliance.

**Implementation**:
```python
# CORRECT: Load history from database every request
async def run_agent(conversation_id: str, user_message: str, db: Session):
    history = load_conversation_context(conversation_id, db)  # ✅ DB fetch
    # ... use history

# WRONG: Store conversation in memory
class Agent:
    def __init__(self):
        self.conversations = {}  # ❌ In-memory state

    async def run(self, conversation_id: str, user_message: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []  # ❌ WRONG
```

### Cursor-Based vs Offset Pagination

**Use cursor-based pagination** (recommended):
- Consistent results with concurrent inserts
- No offset drift issues
- Better performance (no COUNT query)

**Offset pagination issues**:
- New conversations can shift results between pages
- Requires COUNT query (slower)
- Can show duplicates or miss items

### Tenant Isolation Pattern

**All conversation queries MUST filter by user_id**:

```python
# ✅ CORRECT: Filters by user_id
conversations = db.exec(
    select(Conversation)
    .where(Conversation.user_id == current_user.id)
    .where(Conversation.deleted_at.is_(None))
).all()

# ❌ WRONG: Missing user_id filter (security vulnerability)
conversations = db.exec(
    select(Conversation)
    .where(Conversation.deleted_at.is_(None))
).all()
```

### Soft Delete Benefits

1. **Auditability**: Track when conversations were deleted
2. **Recovery**: Users can restore accidentally deleted conversations
3. **Compliance**: Meet data retention requirements
4. **Analytics**: Analyze deletion patterns

**Implementation**: Set `deleted_at` timestamp instead of DELETE

### History Truncation for Token Budget

**Limit messages loaded for AI context**:

```python
# Load last 50 messages (prevents token overflow)
history = load_conversation_context(conversation_id, db, limit=50)

# Or truncate by token count
from app.agents.context_manager import truncate_history_for_tokens

truncated = truncate_history_for_tokens(history, max_tokens=8000)
```

## Performance Optimization

### 1. Database Indexes

Verify indexes are used with EXPLAIN ANALYZE:
```sql
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE conversation_id = 'uuid-here'
ORDER BY created_at ASC
LIMIT 50;
```

Expected: Index Scan using `idx_messages_conversation_created`

### 2. Connection Pooling

Configure FastAPI database connection pool:
```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Max connections
    max_overflow=10,        # Extra connections under load
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
)
```

### 3. Query Optimization

- Use `limit()` on all queries
- Filter by `deleted_at IS NULL` with partial index
- Use `select()` instead of loading entire models when only need counts

## Common Patterns

### Conversation Metadata

Get message count and last message preview:
```python
from sqlmodel import func

# Count messages
message_count = db.exec(
    select(func.count(Message.id))
    .where(Message.conversation_id == conversation_id)
).one()

# Get last message
last_message = db.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(1)
).first()
```

### Conversation Search

Search by title or content:
```python
# Search by title
conversations = db.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .where(Conversation.deleted_at.is_(None))
    .where(Conversation.title.ilike(f"%{query}%"))
    .order_by(Conversation.updated_at.desc())
).all()
```

### History Archival

Hard delete old soft-deleted conversations:
```python
from datetime import datetime, timedelta

cutoff_date = datetime.utcnow() - timedelta(days=90)

old_conversations = db.exec(
    select(Conversation)
    .where(Conversation.deleted_at.is_not(None))
    .where(Conversation.deleted_at < cutoff_date)
).all()

for conversation in old_conversations:
    db.delete(conversation)  # CASCADE deletes messages

db.commit()
```

## Testing

**Unit test for context loading**:
```python
def test_load_conversation_context(session):
    # Create conversation with 60 messages
    conversation = Conversation(user_id="user-1", title="Test")
    session.add(conversation)
    session.commit()

    for i in range(60):
        msg = Message(conversation_id=conversation.id, role="user", content=f"Message {i}")
        session.add(msg)
    session.commit()

    # Load context (limit 50)
    context = load_conversation_context(conversation.id, session)

    assert len(context) == 50
    assert context[0].content == "Message 10"  # Oldest of last 50
```

## Common Issues

**Out of memory errors**: Implement pagination and limits (max 50 messages for AI)

**Slow queries**: Verify indexes exist and are being used (EXPLAIN ANALYZE)

**Race conditions**: Use database transactions for concurrent operations

**Deleted conversations in searches**: Always filter by `deleted_at IS NULL`

## Reference Files

- **Patterns Guide**: `references/history-patterns-guide.md` - Complete query patterns, security, performance
- **Context Manager**: `assets/utils/context_manager.py` - Stateless context loading utilities
- **Pagination**: `assets/utils/pagination.py` - Cursor-based pagination implementation
