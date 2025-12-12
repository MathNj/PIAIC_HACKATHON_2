# Phase 5: Data Model

**Branch**: `005-phase-5` | **Date**: 2025-12-11
**Phase**: Phase 1 - Design & Contracts
**Purpose**: Document data model changes and entity relationships for Phase 5

---

## Overview

Phase 5 (Event-Driven Architecture with Cloud Deployment) **does not introduce new database entities**. The data model was extended in **Component 2 (Advanced Task Features)** with priorities, tags, and recurring tasks. Component 4 (Cloud Deployment) focuses on infrastructure configuration and deployment strategy without database schema changes.

**Existing Database Entities** (from Phases 1-3 and Component 2):
1. **User**: User authentication and profile (Phase 2)
2. **Task**: Core task entity with CRUD operations (Phase 1-2)
3. **Priority**: Task priority levels (Component 2)
4. **Tag**: User-defined task labels (Component 2)
5. **TaskTag**: Many-to-many relationship between tasks and tags (Component 2)
6. **RecurringTask**: Templates for automated task generation (Component 2)
7. **Conversation**: AI chat conversation history (Phase 3)
8. **Message**: Individual chat messages (Phase 3)

---

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       │
       ├─────────────────┐
       │                 │
       ▼ 1:N             ▼ 1:N
┌─────────────┐    ┌──────────────┐
│    Task     │    │     Tag      │
└──────┬──────┘    └───────┬──────┘
       │                   │
       │ N:M               │
       └─────┐      ┌──────┘
             │      │
             ▼      ▼
        ┌─────────────┐
        │  TaskTag    │  (Junction)
        └─────────────┘

┌─────────────┐
│  Priority   │  (Lookup table, no user relationship)
└──────┬──────┘
       │ 1:N
       │
       ▼
┌─────────────┐
│    Task     │  (References priority_id)
└──────┬──────┘
       │ N:1
       │
       ▼
┌─────────────────┐
│ RecurringTask   │  (Templates for task generation)
└─────────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       │
       ▼
┌─────────────┐
│Conversation │  (AI chat history)
└──────┬──────┘
       │ 1:N
       │
       ▼
┌─────────────┐
│   Message   │  (Individual chat messages)
└─────────────┘
```

---

## Database Schema (PostgreSQL)

**No schema changes in Phase 5 Component 4 (Cloud Deployment)**.

The following schema was added in **Component 2 (Advanced Task Features)** and is already implemented:

### priorities Table (Component 2)
```sql
CREATE TABLE priorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,  -- Low, Medium, High, Critical
    level INT NOT NULL UNIQUE,         -- 1 (lowest) to 5 (highest)
    color VARCHAR(7) NOT NULL,         -- Hex color (#FF5733)
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Seed Data**:
```sql
INSERT INTO priorities (name, level, color) VALUES
('Low', 1, '#6B7280'),
('Medium', 2, '#3B82F6'),
('High', 3, '#F59E0B'),
('Critical', 4, '#EF4444');
```

### tags Table (Component 2)
```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)  -- Prevent duplicate tag names per user
);

CREATE INDEX idx_tags_user_id ON tags(user_id);
```

### task_tags Junction Table (Component 2)
```sql
CREATE TABLE task_tags (
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

### recurring_tasks Table (Component 2)
```sql
CREATE TABLE recurring_tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_title VARCHAR(200) NOT NULL,
    template_description TEXT,
    recurrence_pattern VARCHAR(50) NOT NULL,  -- daily, weekly, monthly, custom
    cron_expression VARCHAR(100),              -- For custom patterns (e.g., "0 9 * * MON")
    next_occurrence TIMESTAMP NOT NULL,
    priority_id INT REFERENCES priorities(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recurring_tasks_user_id ON recurring_tasks(user_id);
CREATE INDEX idx_recurring_tasks_next_occurrence ON recurring_tasks(next_occurrence) WHERE is_active = true;
```

### tasks Table (Updated in Component 2)
```sql
-- Added columns:
ALTER TABLE tasks
ADD COLUMN priority_id INT REFERENCES priorities(id) DEFAULT 2,  -- Default to Medium
ADD COLUMN recurring_task_id INT REFERENCES recurring_tasks(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_priority_id ON tasks(priority_id);
CREATE INDEX idx_tasks_recurring_task_id ON tasks(recurring_task_id) WHERE recurring_task_id IS NOT NULL;
```

---

## Event-Driven Data Patterns (Component 1 & 3)

Phase 5 introduces **event-driven data flows** that do not change the database schema but alter how data is propagated:

### Event Publishing (Component 1 - Implemented)

**When tasks are created/updated**, the backend publishes events to Kafka via Dapr:

```python
# Example: Task creation event
{
    "event_type": "task.created",
    "task_id": 123,
    "user_id": "uuid-string",
    "title": "Complete Phase 5 deployment",
    "description": "Deploy to DOKS with Redpanda Cloud",
    "completed": false,
    "priority_id": 3,  # High
    "due_date": "2025-12-15T12:00:00Z",
    "is_recurring": false,
    "recurrence_pattern": null,
    "tag_ids": [1, 5, 8],
    "created_at": "2025-12-11T22:00:00Z",
    "updated_at": "2025-12-11T22:00:00Z",
    "timestamp": "2025-12-11T22:00:00.123456Z"
}
```

**Event Types**:
- `task.created`: New task added
- `task.updated`: Task modified
- `task.completed`: Task marked as done
- `task.deleted`: Task removed
- `task.due.approaching`: Task due date within 24 hours (generated by notification-service)

### State Store (Distributed Cache - Component 1)

**Redis state store** (via Dapr) caches conversation history and temporary workflow state:

**State Key Pattern**: `todo-app::<entity-type>::<entity-id>`

Examples:
- `todo-app::conversation::uuid-123`: Full conversation history for AI chat (Phase 3)
- `todo-app::reminder-sent::task-456`: Deduplication flag for reminder notifications (Component 3)
- `todo-app::recurring-task-processed::template-789`: Last processed timestamp for recurring tasks (Component 3)

**State Operations** (via Dapr HTTP API):
```python
# Save state
POST http://localhost:3500/v1.0/state/statestore
{
    "key": "todo-app::conversation::uuid-123",
    "value": {
        "messages": [...],
        "context": {...}
    },
    "metadata": {
        "ttl": "3600"  # 1 hour expiration
    }
}

# Get state
GET http://localhost:3500/v1.0/state/statestore/todo-app::conversation::uuid-123

# Delete state
DELETE http://localhost:3500/v1.0/state/statestore/todo-app::conversation::uuid-123
```

---

## Data Flow Diagrams

### Task Creation Flow (with Event Publishing)

```
┌─────────────┐   1. POST /api/tasks   ┌─────────────┐
│   Frontend  │ ───────────────────────►│   Backend   │
│  (Next.js)  │                         │  (FastAPI)  │
└─────────────┘                         └──────┬──────┘
                                               │
                                   2. Save to PostgreSQL
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Neon      │
                                        │ PostgreSQL  │
                                        └─────────────┘
                                               │
                             3. Publish event (non-blocking)
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │Dapr Sidecar │
                                        │(localhost:  │
                                        │   3500)     │
                                        └──────┬──────┘
                                               │
                                    4. Kafka pub/sub
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Redpanda   │
                                        │   Cloud     │
                                        │(task-events)│
                                        └──────┬──────┘
                                               │
                                    5. Event delivery
                                               │
                     ┌─────────────────────────┼─────────────────────────┐
                     │                         │                         │
                     ▼                         ▼                         ▼
              ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
              │Notification │         │  Recurring  │         │   Future    │
              │  Service    │         │ Task Service│         │  Consumers  │
              │(Subscriber) │         │(Subscriber) │         │             │
              └──────┬──────┘         └─────────────┘         └─────────────┘
                     │
         6. Send email/push notification
                     │
                     ▼
              ┌─────────────┐
              │  SendGrid/  │
              │   FCM       │
              └─────────────┘
```

### Conversation State Management (Redis Cache)

```
┌─────────────┐   1. POST /api/chat   ┌─────────────┐
│   Frontend  │ ───────────────────────►│   Backend   │
│  (Next.js)  │                         │  (FastAPI)  │
└─────────────┘                         └──────┬──────┘
                                               │
                                  2. Get conversation history
                                     (via Dapr state store)
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │Dapr Sidecar │
                                        │(localhost:  │
                                        │   3500)     │
                                        └──────┬──────┘
                                               │
                                    3. State retrieval
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │DO Managed   │
                                        │   Redis     │
                                        │  (TLS)      │
                                        └──────┬──────┘
                                               │
                                   4. Return cached history
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Backend   │
                                        │  (FastAPI)  │
                                        └──────┬──────┘
                                               │
                             5. Call AI with full context
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Gemini 2.5 │
                                        │    Flash    │
                                        └──────┬──────┘
                                               │
                                6. Save updated conversation
                                     (back to Redis via Dapr)
                                               │
                                               ▼
                                     Response to frontend
```

---

## Summary

**Phase 5 Component 4 (Cloud Deployment)**:
- ✅ **No new database entities**
- ✅ **No schema migrations required**
- ✅ **Existing entities used**: User, Task, Priority, Tag, TaskTag, RecurringTask, Conversation, Message
- ✅ **Data patterns introduced**: Event publishing (Kafka), distributed caching (Redis state store)

**Database Operations**:
- **Writes**: Tasks, Conversations, Messages saved to PostgreSQL (Neon) as before
- **Reads**: Tasks queried from PostgreSQL, Conversations optionally cached in Redis
- **Events**: Task operations trigger Kafka events (asynchronous, non-blocking)
- **Cache**: Redis stores conversation history with TTL for fast retrieval

**Next Steps**:
- Generate Kubernetes Secret manifests for Redpanda and Redis credentials
- Generate Dapr component YAMLs for production (kafka-pubsub-prod, statestore-prod)
- Generate Helm values overrides for DOKS deployment (values-prod.yaml)

---

**Created**: 2025-12-11
**Author**: Claude Sonnet 4.5
**Phase**: Phase 1 - Design & Contracts
**Status**: ✅ Complete
