# Data Model: AI Chat Agent with MCP Integration

**Feature**: AI Chat Agent with MCP Integration
**Date**: 2025-12-07
**Phase**: III (Agent-Augmented System)

## Overview

This document defines the database schema, entity relationships, validation rules, and state transitions for the AI Chat Agent feature. The data model extends the existing Phase II schema with conversation persistence tables while maintaining full compatibility with existing users and tasks tables.

## Entity Relationship Diagram

```
┌──────────────┐
│    users     │
│              │
│ id (UUID, PK)│
│ email        │
│ name         │
│ created_at   │
└──────┬───────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐
│   conversations      │
│                      │
│ id (INT, PK)         │◄────────┐
│ user_id (UUID, FK)   │         │
│ title (VARCHAR 200)  │         │
│ created_at           │         │ 1:N
│ updated_at           │         │
└──────────────────────┘         │
                                 │
                                 │
                          ┌──────┴──────────┐
                          │    messages     │
                          │                 │
                          │ id (INT, PK)    │
                          │ conversation_id │
                          │ role (ENUM)     │
                          │ content (TEXT)  │
                          │ tool_calls (JSONB)│
                          │ created_at      │
                          └─────────────────┘

┌──────────────┐
│    tasks     │ (Existing Phase II table - no changes)
│              │
│ id (INT, PK) │
│ user_id (UUID, FK) → References users.id
│ title        │
│ description  │
│ priority     │
│ due_date     │
│ completed    │
│ created_at   │
│ updated_at   │
└──────────────┘
```

## Entities

### 1. Conversation

**Purpose**: Represents a persistent chat conversation between a user and the AI agent. Stores conversation metadata and serves as the parent container for messages.

**Table Name**: `conversations`

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing conversation identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users.id | Owner of the conversation |
| title | VARCHAR(200) | NULL | Auto-generated conversation summary (e.g., "Task Management - Dec 7") |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Conversation creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp (updated on each message) |

**Indexes**:
- `PRIMARY KEY (id)` - Clustered index for conversation lookup
- `INDEX idx_conversations_user_id (user_id)` - Fast user conversation listing
- `INDEX idx_conversations_updated_at (updated_at DESC)` - Recent conversations first

**Foreign Keys**:
- `user_id` → `users.id` ON DELETE CASCADE
  - When user is deleted, all their conversations are deleted
  - Maintains referential integrity

**Validation Rules**:
- `title` length: 0-200 characters (NULL allowed for untitled conversations)
- `updated_at` must be >= `created_at`
- `user_id` must exist in `users` table

**Lifecycle**:
1. **Creation**: Auto-created on first message if no conversation_id provided
2. **Update**: `updated_at` updated on every new message
3. **Deletion**: User can explicitly delete; cascades to delete all messages

---

### 2. Message

**Purpose**: Represents a single message in a conversation. Can be from user, assistant, or system. Stores message content, role, and optional tool call audit trail.

**Table Name**: `messages`

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing message identifier |
| conversation_id | INT | NOT NULL, FOREIGN KEY → conversations.id | Parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant', 'system') | Message role |
| content | TEXT | NOT NULL | Message text content |
| tool_calls | TEXT | NULL | JSON string of tool executions (for assistant messages) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes**:
- `PRIMARY KEY (id)` - Clustered index for message lookup
- `INDEX idx_messages_conversation_id (conversation_id)` - Fast conversation message retrieval
- `INDEX idx_messages_conversation_created (conversation_id, created_at)` - Ordered message queries (most efficient)

**Foreign Keys**:
- `conversation_id` → `conversations.id` ON DELETE CASCADE
  - When conversation is deleted, all messages are deleted
  - Maintains referential integrity

**Validation Rules**:
- `role` must be one of: `'user'`, `'assistant'`, `'system'`
- `content` length: 1-10000 characters (non-empty, reasonable limit)
- `tool_calls`: Valid JSON string or NULL (validated at application layer)
- `created_at` must be >= parent conversation's `created_at`

**Role Semantics**:
- **user**: Messages sent by the authenticated user
- **assistant**: Responses generated by the AI agent
- **system**: Internal system messages (optional, e.g., "Conversation started")

**Tool Calls Format** (JSON in `tool_calls` column):
```json
[
  {
    "tool": "create_task",
    "arguments": {
      "title": "Buy groceries",
      "priority": "normal",
      "due_date": "2025-12-08"
    },
    "result": {
      "id": 789,
      "title": "Buy groceries",
      "created": true
    },
    "timestamp": "2025-12-07T10:30:00Z"
  },
  {
    "tool": "list_tasks",
    "arguments": {
      "status": "pending"
    },
    "result": "Found 5 tasks...",
    "timestamp": "2025-12-07T10:30:01Z"
  }
]
```

**Lifecycle**:
1. **Creation**: Inserted when user sends message or agent responds
2. **Immutable**: Messages never updated after creation (append-only log)
3. **Deletion**: Only via conversation deletion (cascade)

---

### 3. User (Existing - No Changes)

**Purpose**: Existing Phase II user entity. No schema changes required.

**Referenced By**:
- `conversations.user_id` (new foreign key)
- `tasks.user_id` (existing foreign key)

**Note**: Phase III adds conversations relationship but does not modify users table schema.

---

### 4. Task (Existing - No Changes)

**Purpose**: Existing Phase II task entity. No schema changes required. Accessed via MCP tools only (not directly by agent).

**Integration with Phase III**:
- MCP tools (`create_task`, `list_tasks`, etc.) operate on tasks table
- Agent never directly queries tasks (must use MCP tools)
- User isolation enforced at MCP tool layer (JWT validation)

---

## Relationships

### Conversation → User (Many-to-One)

- **Cardinality**: Many conversations belong to one user
- **Foreign Key**: `conversations.user_id` → `users.id`
- **Cascade**: ON DELETE CASCADE (user deletion removes all conversations)
- **Enforcement**: Database-level foreign key constraint

**Business Rules**:
- User can have 0 to many conversations
- Conversation belongs to exactly 1 user
- Conversation ownership never changes (no transfer)
- User deletion permanently removes all conversation history

### Message → Conversation (Many-to-One)

- **Cardinality**: Many messages belong to one conversation
- **Foreign Key**: `messages.conversation_id` → `conversations.id`
- **Cascade**: ON DELETE CASCADE (conversation deletion removes all messages)
- **Enforcement**: Database-level foreign key constraint

**Business Rules**:
- Conversation can have 1 to many messages (minimum 1 message at creation)
- Message belongs to exactly 1 conversation
- Message cannot be moved between conversations
- Messages ordered by `created_at` (append-only log)

### Implicit: Message → User (via Conversation)

- **Cardinality**: Many messages belong to one user (transitive through conversation)
- **No Direct FK**: Relationship derived via `messages.conversation_id → conversations.user_id`
- **Multi-User Isolation**: Enforced by querying messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id)

**Business Rules**:
- Messages indirectly scoped to user via parent conversation
- User can only access messages in their own conversations
- No cross-user message visibility

---

## State Transitions

### Conversation State Machine

```
┌─────────────┐
│   Created   │ (Initial state)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Active    │ ◄───┐ (Has messages, can receive new messages)
└──────┬──────┘     │
       │            │
       │ (timeout   │ (new message)
       │  or         │
       │  inactivity)│
       ▼            │
┌─────────────┐     │
│   Stale     │ ────┘ (No messages for > 7 days)
└──────┬──────┘
       │
       │ (user delete)
       ▼
┌─────────────┐
│   Deleted   │ (Terminal state - cascades to messages)
└─────────────┘
```

**State Definitions**:
- **Created**: Conversation just initialized (first message not yet saved)
- **Active**: Has >= 1 message, `updated_at` within last 7 days
- **Stale**: No messages for > 7 days (considered inactive)
- **Deleted**: User explicitly deleted (cascades to all messages)

**Note**: State is derived from `updated_at` and message count, not stored explicitly. "Stale" state is for UI indication only (conversation remains functional).

### Message State (Immutable)

Messages are **append-only** and have no state transitions. Once created, messages are never modified or deleted (except via conversation cascade delete).

**Immutability Benefits**:
- Complete conversation audit trail
- Simplified data model (no update logic)
- Tool call history preserved for debugging
- Conversation integrity guaranteed

---

## Indexes and Query Optimization

### Index Strategy

**Conversations Table**:
1. `PRIMARY KEY (id)` - Single conversation lookup (O(1))
2. `INDEX idx_conversations_user_id (user_id)` - List user's conversations
3. `INDEX idx_conversations_updated_at (updated_at DESC)` - Recent conversations first

**Query Patterns**:
```sql
-- List user's conversations (ordered by most recent)
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 20;

-- Get single conversation
SELECT * FROM conversations WHERE id = :id AND user_id = :user_id;
```

**Messages Table**:
1. `PRIMARY KEY (id)` - Single message lookup (O(1))
2. `INDEX idx_messages_conversation_id (conversation_id)` - All messages in conversation
3. `INDEX idx_messages_conversation_created (conversation_id, created_at)` - **Composite index** for ordered retrieval (most efficient)

**Query Patterns**:
```sql
-- Load last 20 messages in conversation (most common query)
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at DESC
LIMIT 20;

-- Load messages with pagination
SELECT * FROM messages
WHERE conversation_id = :conversation_id
  AND created_at < :before_timestamp
ORDER BY created_at DESC
LIMIT 20;
```

**Index Justification**:
- Composite index `(conversation_id, created_at)` covers the WHERE and ORDER BY, eliminating full table scan
- Estimated query time: < 10ms for 1000 messages, < 100ms for 100k messages
- Index size: ~2MB per 10k messages (acceptable overhead)

---

## Data Constraints and Validation

### Database-Level Constraints

**Conversations**:
```sql
ALTER TABLE conversations
  ADD CONSTRAINT chk_title_length CHECK (LENGTH(title) <= 200),
  ADD CONSTRAINT chk_updated_after_created CHECK (updated_at >= created_at);
```

**Messages**:
```sql
ALTER TABLE messages
  ADD CONSTRAINT chk_role_valid CHECK (role IN ('user', 'assistant', 'system')),
  ADD CONSTRAINT chk_content_not_empty CHECK (LENGTH(content) >= 1),
  ADD CONSTRAINT chk_content_max_length CHECK (LENGTH(content) <= 10000);
```

### Application-Level Validation (SQLModel)

**Conversation Model**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Validation
    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v) > 200:
            raise ValueError('Title must be <= 200 characters')
        return v

    @validator('updated_at')
    def validate_updated_at(cls, v, values):
        if 'created_at' in values and v < values['created_at']:
            raise ValueError('updated_at must be >= created_at')
        return v
```

**Message Model**:
```python
from typing import Literal

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: Literal["user", "assistant", "system"] = Field(nullable=False)
    content: str = Field(nullable=False, min_length=1, max_length=10000)
    tool_calls: Optional[str] = Field(default=None, description="JSON string of tool executions")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Validation
    @validator('tool_calls')
    def validate_tool_calls(cls, v):
        if v is not None:
            try:
                json.loads(v)  # Validate JSON format
            except json.JSONDecodeError:
                raise ValueError('tool_calls must be valid JSON')
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v or len(v) < 1:
            raise ValueError('Content cannot be empty')
        if len(v) > 10000:
            raise ValueError('Content must be <= 10000 characters')
        return v
```

---

## Migration Strategy

### Alembic Migration Script

**File**: `backend/alembic/versions/{timestamp}_add_conversation_tables.py`

```python
"""Add conversation and message tables for AI chat agent

Revision ID: {hash}
Revises: {previous_revision}
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Revision identifiers
revision = '{hash}'
down_revision = '{previous_revision}'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for conversations
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', [sa.text('updated_at DESC')])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='chk_role_valid'),
        sa.CheckConstraint("LENGTH(content) >= 1", name='chk_content_not_empty'),
        sa.CheckConstraint("LENGTH(content) <= 10000", name='chk_content_max_length'),
    )

    # Create indexes for messages
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_index('idx_conversations_updated_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')

    # Drop tables (CASCADE handles foreign keys)
    op.drop_table('messages')
    op.drop_table('conversations')
```

**Migration Execution**:
```bash
# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables"

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

---

## Data Retention and Archival

### Retention Policy

**Conversations**:
- **Active Retention**: Indefinite (user controls deletion)
- **Stale Conversations**: Not auto-deleted (user may resume after months)
- **User Deletion**: All conversations CASCADE deleted immediately

**Messages**:
- **Retention**: Same as parent conversation (cascade delete only)
- **Immutable**: Never modified after creation
- **Audit Trail**: Tool calls preserved for debugging and analytics

### Future Archival Strategy (Out of Scope for Phase III)

**Potential Enhancements**:
- Auto-archive conversations inactive for > 90 days to cheaper storage
- Export conversation history to JSON (user download)
- Compress old message content (gzip TEXT column)
- Partition messages table by created_at for faster queries

---

## Security Considerations

### Multi-User Isolation

**Enforcement Points**:
1. **API Layer**: JWT validates user_id, query filters by user_id
2. **Database Layer**: Foreign key constraints prevent orphaned data
3. **MCP Tool Layer**: Each tool re-validates user_id from JWT

**Query Pattern** (Safe):
```sql
-- ✅ SAFE: Query scoped to authenticated user
SELECT c.* FROM conversations c
WHERE c.user_id = :authenticated_user_id
ORDER BY c.updated_at DESC;

-- ✅ SAFE: Message access via user's conversation
SELECT m.* FROM messages m
INNER JOIN conversations c ON m.conversation_id = c.id
WHERE c.user_id = :authenticated_user_id
  AND m.conversation_id = :conversation_id
ORDER BY m.created_at DESC;
```

**Anti-Pattern** (Unsafe):
```sql
-- ❌ UNSAFE: No user_id filter (exposes all conversations)
SELECT * FROM conversations WHERE id = :conversation_id;

-- ❌ UNSAFE: No join to verify user ownership
SELECT * FROM messages WHERE conversation_id = :conversation_id;
```

### PII and Data Sensitivity

**Personal Information**:
- `messages.content` may contain PII (user tasks, names, dates)
- `tool_calls` may log sensitive task details
- `conversations.title` auto-generated from first message (may contain PII)

**Protection Measures**:
- Encrypt database at rest (Neon default)
- TLS for all database connections
- Never log message content in application logs
- Mask user_id in error messages
- Conversation export requires authentication

---

## Testing Data Model

### Unit Tests (SQLModel Validation)

```python
def test_conversation_title_max_length():
    """Conversation title must be <= 200 characters."""
    with pytest.raises(ValidationError):
        Conversation(user_id=user_id, title="x" * 201)

def test_message_role_enum():
    """Message role must be user, assistant, or system."""
    with pytest.raises(ValidationError):
        Message(conversation_id=1, role="admin", content="Test")

def test_message_content_not_empty():
    """Message content cannot be empty."""
    with pytest.raises(ValidationError):
        Message(conversation_id=1, role="user", content="")
```

### Integration Tests (Database)

```python
def test_conversation_cascade_delete(session, user):
    """Deleting conversation deletes all messages."""
    conversation = Conversation(user_id=user.id)
    session.add(conversation)
    session.commit()

    message = Message(conversation_id=conversation.id, role="user", content="Test")
    session.add(message)
    session.commit()

    # Delete conversation
    session.delete(conversation)
    session.commit()

    # Verify message was cascade deleted
    assert session.query(Message).filter_by(conversation_id=conversation.id).count() == 0

def test_multi_user_isolation(session, user1, user2):
    """User cannot access another user's conversations."""
    conv1 = Conversation(user_id=user1.id, title="User 1 conv")
    conv2 = Conversation(user_id=user2.id, title="User 2 conv")
    session.add_all([conv1, conv2])
    session.commit()

    # User 1 query
    user1_convs = session.query(Conversation).filter_by(user_id=user1.id).all()
    assert len(user1_convs) == 1
    assert user1_convs[0].title == "User 1 conv"
```

---

## Summary

This data model provides:
- ✅ **Stateless Agent Support**: Database-backed conversation history
- ✅ **Multi-User Isolation**: Foreign keys and query filters enforce user scoping
- ✅ **Audit Trail**: Immutable message log with tool call history
- ✅ **Performance**: Composite indexes optimize common queries
- ✅ **Data Integrity**: Foreign key constraints with CASCADE deletes
- ✅ **Scalability**: Indexed queries support 100k+ conversations per user
- ✅ **Phase II Compatibility**: No changes to existing users or tasks tables

**Alembic Migration**: Single migration adds both tables with indexes and constraints. Rollback supported.
