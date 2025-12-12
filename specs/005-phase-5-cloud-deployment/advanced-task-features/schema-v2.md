# Database Schema V2: Advanced Task Management

**Version**: 2.0
**Created**: 2025-12-11
**Migration From**: Schema V1 (basic task CRUD with users and tasks tables)
**Status**: Draft
**Related Spec**: [Advanced Task Management Features](spec.md)

## Overview

Schema V2 extends the existing database schema to support advanced task management features:
- **Priority Levels**: High, Medium, Low priority classification
- **Tags**: Flexible multi-dimensional categorization via many-to-many relationship
- **Due Dates**: DateTime-based deadline tracking
- **Recurring Tasks**: Automated task regeneration with recurrence patterns

## Schema Compatibility

- **SQLModel**: All tables and relationships defined using SQLModel ORM
- **SQLite**: Supported for local development
- **PostgreSQL**: Supported for production (Neon serverless)
- **Alembic**: Migration scripts required for production database updates
- **Backward Compatibility**: Existing tasks without new fields continue working (nullable columns)

## Entity Relationship Diagram (Text Format)

```
┌─────────────┐
│   users     │
│─────────────│
│ id (PK)     │──┐
│ email       │  │
│ name        │  │
│ created_at  │  │
└─────────────┘  │
                 │
                 │ 1:N (one user has many tasks)
                 │
┌────────────────▼──────────────┐
│           tasks               │
│───────────────────────────────│
│ id (PK)                       │
│ user_id (FK) → users.id       │──┐
│ title                         │  │
│ description                   │  │
│ completed                     │  │
│ priority_id (FK) → priorities │  │ N:M (many tasks have many tags)
│ due_date                      │  │
│ is_recurring                  │  │
│ recurrence_pattern            │  │
│ created_at                    │  │
│ updated_at                    │  │
└───────────────────────────────┘  │
         │                         │
         │ N:1                     │
         │                         │
         ▼                         │
┌─────────────────┐                │
│   priorities    │                │
│─────────────────│                │
│ id (PK)         │                │
│ name            │                │
│ level           │                │
│ color           │                │
└─────────────────┘                │
                                   │
                      ┌────────────▼─────────┐
                      │     task_tags        │
                      │──────────────────────│
                      │ task_id (PK, FK)     │
                      │ tag_id (PK, FK)      │
                      └───────┬──────────────┘
                              │
                              │ N:1
                              │
                              ▼
                      ┌─────────────┐
                      │    tags     │
                      │─────────────│
                      │ id (PK)     │
                      │ name (UQ)   │
                      │ created_at  │
                      └─────────────┘
```

## Table Definitions

### 1. priorities (NEW TABLE)

Lookup table for task priority levels.

| Column | Type        | Constraints               | Description                          |
|--------|-------------|---------------------------|--------------------------------------|
| id     | INTEGER     | PRIMARY KEY               | Unique identifier (1, 2, 3)          |
| name   | VARCHAR(50) | NOT NULL, UNIQUE          | Display name ("High", "Medium", "Low") |
| level  | INTEGER     | NOT NULL, UNIQUE          | Numeric level for sorting (1=highest) |
| color  | VARCHAR(7)  | NOT NULL                  | Hex color code for UI badges         |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE constraint on `name`
- UNIQUE constraint on `level`

**Seed Data** (inserted during migration):
```sql
INSERT INTO priorities (id, name, level, color) VALUES
  (1, 'High', 1, '#EF4444'),
  (2, 'Medium', 2, '#F59E0B'),
  (3, 'Low', 3, '#10B981');
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field

class Priority(SQLModel, table=True):
    __tablename__ = "priorities"

    id: int = Field(primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)
    level: int = Field(unique=True)
    color: str = Field(max_length=7)
```

---

### 2. tags (NEW TABLE)

User-scoped tag definitions for task categorization.

| Column     | Type         | Constraints                  | Description                     |
|------------|--------------|------------------------------|---------------------------------|
| id         | INTEGER      | PRIMARY KEY, AUTOINCREMENT   | Unique identifier               |
| name       | VARCHAR(30)  | NOT NULL, UNIQUE             | Tag name (lowercase, trimmed)   |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT NOW()      | Tag creation timestamp          |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE constraint on `name` (case-insensitive in PostgreSQL using LOWER() or CITEXT)
- INDEX on `name` for autocomplete queries

**Constraints**:
- Tag names normalized to lowercase before insertion
- Whitespace trimmed from tag names
- Maximum length: 30 characters
- Empty strings rejected

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=30, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 3. task_tags (NEW TABLE)

Junction table for many-to-many relationship between tasks and tags.

| Column  | Type    | Constraints                      | Description                    |
|---------|---------|----------------------------------|--------------------------------|
| task_id | INTEGER | PRIMARY KEY, FK → tasks.id       | Foreign key to tasks table     |
| tag_id  | INTEGER | PRIMARY KEY, FK → tags.id        | Foreign key to tags table      |

**Indexes**:
- PRIMARY KEY on `(task_id, tag_id)` composite
- INDEX on `task_id` for efficient task→tags queries
- INDEX on `tag_id` for efficient tag→tasks queries

**Constraints**:
- ON DELETE CASCADE for `task_id` (deleting task removes tag associations)
- ON DELETE CASCADE for `tag_id` (deleting tag removes all task associations)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field

class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True, ondelete="CASCADE")
    tag_id: int = Field(foreign_key="tags.id", primary_key=True, ondelete="CASCADE")
```

---

### 4. tasks (UPDATED TABLE)

Extended tasks table with new columns for priority, due date, and recurrence.

**New Columns Added**:

| Column             | Type        | Constraints                   | Description                              |
|--------------------|-------------|-------------------------------|------------------------------------------|
| priority_id        | INTEGER     | NULL, FK → priorities.id      | Foreign key to priorities (nullable)     |
| due_date           | TIMESTAMP   | NULL                          | Task deadline (nullable)                 |
| is_recurring       | BOOLEAN     | NOT NULL, DEFAULT FALSE       | Whether task regenerates on completion   |
| recurrence_pattern | VARCHAR(20) | NULL                          | Recurrence frequency ('daily', 'weekly', 'monthly', 'yearly') |

**Complete Table Schema** (V1 + V2 columns):

| Column             | Type         | Constraints                   | Description                              |
|--------------------|--------------|-------------------------------|------------------------------------------|
| id                 | INTEGER      | PRIMARY KEY, AUTOINCREMENT    | Unique identifier                        |
| user_id            | VARCHAR(255) | NOT NULL, FK → users.id       | Foreign key to users (owner)             |
| title              | VARCHAR(200) | NOT NULL                      | Task title/summary                       |
| description        | TEXT         | NULL                          | Optional detailed description            |
| completed          | BOOLEAN      | NOT NULL, DEFAULT FALSE       | Completion status                        |
| **priority_id**    | **INTEGER**  | **NULL, FK → priorities.id**  | **[V2] Priority level reference**        |
| **due_date**       | **TIMESTAMP**| **NULL**                      | **[V2] Task deadline**                   |
| **is_recurring**   | **BOOLEAN**  | **NOT NULL, DEFAULT FALSE**   | **[V2] Recurring task flag**             |
| **recurrence_pattern** | **VARCHAR(20)** | **NULL**              | **[V2] Recurrence pattern**              |
| created_at         | TIMESTAMP    | NOT NULL, DEFAULT NOW()       | Creation timestamp                       |
| updated_at         | TIMESTAMP    | NOT NULL, DEFAULT NOW()       | Last update timestamp                    |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (existing, for efficient user queries)
- INDEX on `completed` (existing, for filtered queries)
- **INDEX on `priority_id`** (new, for priority-based queries)
- **INDEX on `due_date`** (new, for date range queries)
- **INDEX on `is_recurring`** (new, for recurring task queries)

**Constraints**:
- `priority_id` NULLABLE (tasks can have no priority)
- `due_date` NULLABLE (tasks can have no due date)
- `recurrence_pattern` NULLABLE (only set when is_recurring=true)
- CHECK constraint: `recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly')` OR NULL
- Business logic validation: if `is_recurring=true`, then `due_date` MUST NOT be null

**SQLModel Definition** (Updated):
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Existing V1 columns
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # New V2 columns
    priority_id: Optional[int] = Field(default=None, foreign_key="priorities.id", index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    is_recurring: bool = Field(default=False, index=True)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=20)

    # Relationships (SQLModel)
    priority: Optional[Priority] = Relationship(back_populates="tasks")
    tags: list[Tag] = Relationship(back_populates="tasks", link_model=TaskTag)
```

---

### 5. users (UNCHANGED)

User table remains unchanged from V1.

| Column     | Type         | Constraints               | Description              |
|------------|--------------|---------------------------|--------------------------|
| id         | VARCHAR(255) | PRIMARY KEY               | User UUID                |
| email      | VARCHAR(255) | NOT NULL, UNIQUE          | User email address       |
| name       | VARCHAR(255) | NOT NULL                  | User display name        |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT NOW()   | Account creation date    |

---

## Migration Strategy

### Alembic Migration Script Structure

```python
"""Add advanced task features: priorities, tags, due dates, recurring tasks

Revision ID: 002_advanced_features
Revises: 001_initial_schema
Create Date: 2025-12-11
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Create priorities table
    op.create_table(
        'priorities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(7), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('level')
    )

    # Seed priorities data
    op.execute("""
        INSERT INTO priorities (id, name, level, color) VALUES
        (1, 'High', 1, '#EF4444'),
        (2, 'Medium', 2, '#F59E0B'),
        (3, 'Low', 3, '#10B981')
    """)

    # 2. Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_tags_name', 'tags', ['name'])

    # 3. Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )
    op.create_index('idx_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('idx_task_tags_tag_id', 'task_tags', ['tag_id'])

    # 4. Add new columns to tasks table
    op.add_column('tasks', sa.Column('priority_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(20), nullable=True))

    # 5. Create foreign key constraint
    op.create_foreign_key('fk_tasks_priority', 'tasks', 'priorities', ['priority_id'], ['id'])

    # 6. Create indexes on new columns
    op.create_index('idx_tasks_priority_id', 'tasks', ['priority_id'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_is_recurring', 'tasks', ['is_recurring'])

def downgrade():
    # Drop in reverse order
    op.drop_index('idx_tasks_is_recurring', 'tasks')
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_index('idx_tasks_priority_id', 'tasks')
    op.drop_constraint('fk_tasks_priority', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority_id')
    op.drop_table('task_tags')
    op.drop_table('tags')
    op.drop_table('priorities')
```

### Migration Execution

**Local Development (SQLite)**:
```bash
cd backend
alembic upgrade head
```

**Production (Neon PostgreSQL)**:
```bash
cd backend
export DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require"
alembic upgrade head
```

### Rollback Plan

If migration fails or needs to be reverted:
```bash
alembic downgrade -1  # Revert one migration
alembic downgrade 001_initial_schema  # Revert to specific revision
```

---

## Query Examples

### 1. Get Tasks with Priority and Tags

```sql
SELECT
    t.id,
    t.title,
    t.completed,
    t.due_date,
    t.is_recurring,
    t.recurrence_pattern,
    p.name AS priority_name,
    p.color AS priority_color,
    GROUP_CONCAT(tg.name, ', ') AS tags
FROM tasks t
LEFT JOIN priorities p ON t.priority_id = p.id
LEFT JOIN task_tags tt ON t.task_id = tt.task_id
LEFT JOIN tags tg ON tt.tag_id = tg.id
WHERE t.user_id = 'user123'
GROUP BY t.id
ORDER BY p.level ASC, t.due_date ASC;
```

### 2. Filter Tasks by Priority and Tags

```sql
SELECT DISTINCT t.*
FROM tasks t
INNER JOIN task_tags tt1 ON t.id = tt1.task_id
INNER JOIN tags tg1 ON tt1.tag_id = tg1.id
WHERE t.user_id = 'user123'
  AND t.priority_id IN (1, 2)  -- High or Medium
  AND tg1.name = 'work'
  AND t.due_date BETWEEN '2025-12-10' AND '2025-12-17'
ORDER BY t.due_date ASC;
```

### 3. Get Overdue Tasks

```sql
SELECT t.*, p.name AS priority_name
FROM tasks t
LEFT JOIN priorities p ON t.priority_id = p.id
WHERE t.user_id = 'user123'
  AND t.completed = false
  AND t.due_date < CURRENT_TIMESTAMP
ORDER BY t.due_date ASC;
```

### 4. Get Recurring Tasks Due for Regeneration

```sql
SELECT *
FROM tasks
WHERE is_recurring = true
  AND completed = true
  -- Tasks marked complete that need new instances created
ORDER BY updated_at DESC;
```

### 5. Tag Autocomplete Query

```sql
SELECT name
FROM tags
WHERE name LIKE 'wor%'  -- User typed "wor"
ORDER BY name ASC
LIMIT 10;
```

---

## Performance Considerations

### Index Strategy

**Existing Indexes (V1)**:
- `tasks(user_id)` - Critical for user-scoped queries
- `tasks(completed)` - Enables fast filtering by status

**New Indexes (V2)**:
- `tasks(priority_id)` - Enables fast priority filtering and joins
- `tasks(due_date)` - Enables fast date range queries and sorting
- `tasks(is_recurring)` - Enables fast recurring task queries
- `tags(name)` - Enables fast tag lookups and autocomplete
- `task_tags(task_id)` - Enables fast task→tags navigation
- `task_tags(tag_id)` - Enables fast tag→tasks navigation

### Query Optimization Tips

1. **Avoid N+1 Queries**: Use joins or eager loading for tasks + priority + tags
2. **Use Composite Indexes**: Consider composite index on `(user_id, due_date)` for date-filtered queries
3. **Limit Result Sets**: Always apply LIMIT for large task lists (pagination)
4. **Cache Priority Lookupstable**: Priorities table is static - cache in application memory
5. **Tag Normalization**: Normalize tag names (lowercase, trim) at application layer before querying

### Expected Performance

With proper indexes:
- **Single task query** (with priority + tags): < 10ms
- **User task list** (100 tasks with joins): < 50ms
- **Filtered query** (priority + tags + date range): < 100ms
- **Tag autocomplete**: < 50ms
- **Recurring task check** (cron job): < 100ms

---

## Data Validation Rules

### Application-Level Validations

1. **Priority**:
   - `priority_id` must exist in priorities table (1, 2, or 3) or be null
   - Backend validates FK constraint before INSERT/UPDATE

2. **Tags**:
   - Tag names normalized to lowercase before saving
   - Whitespace trimmed
   - Empty strings rejected
   - Maximum 10 tags per task enforced
   - Tag name length: 1-30 characters

3. **Due Date**:
   - Must be valid ISO 8601 DateTime format
   - Can be in past (for tracking overdue tasks)
   - Stored in UTC, converted to user timezone on frontend

4. **Recurring Tasks**:
   - If `is_recurring=true`, `due_date` MUST NOT be null (enforced in API)
   - `recurrence_pattern` must be one of: 'daily', 'weekly', 'monthly', 'yearly'
   - Backend validates pattern before saving

### Database-Level Constraints

- **Foreign Keys**: Enforced for `priority_id`, `task_id`, `tag_id`
- **NOT NULL**: Enforced for `title`, `user_id`, `completed`, `is_recurring`
- **UNIQUE**: Enforced for `tags.name`, `priorities.name`, `priorities.level`
- **CHECK** (if supported): `recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly')` OR NULL

---

## Backward Compatibility

### Existing Tasks

- All new columns are **nullable** (except `is_recurring` with default `false`)
- Existing tasks continue working without modification
- Queries without new fields remain unchanged

### API Compatibility

**Existing Endpoints** (unchanged behavior):
- `GET /api/{user_id}/tasks` - Returns tasks (new fields included but nullable)
- `POST /api/{user_id}/tasks` - Creates tasks (new fields optional)
- `PUT /api/{user_id}/tasks/{id}` - Updates tasks (new fields optional)

**New Query Parameters** (optional, backward compatible):
- `?priority[]=1&priority[]=2` - Filter by priority (optional)
- `?tags[]=work&tags[]=urgent` - Filter by tags (optional)
- `?due_date_from=2025-12-10&due_date_to=2025-12-17` - Filter by date range (optional)
- `?sort_by=due_date&sort_order=asc` - Sort by field (optional)

### Frontend Compatibility

- Existing frontend code displays tasks without new fields (gracefully degrades)
- New UI components (priority dropdown, tag input, date picker) are additive

---

## Testing Checklist

### Migration Testing

- [ ] Run migration on clean SQLite database
- [ ] Run migration on clean PostgreSQL database
- [ ] Verify all tables created with correct schema
- [ ] Verify indexes created
- [ ] Verify foreign key constraints enforced
- [ ] Verify seed data inserted (3 priorities)
- [ ] Test rollback (`alembic downgrade -1`)
- [ ] Test migration on database with existing tasks (backward compatibility)

### Data Integrity Testing

- [ ] Create task with priority - verify FK constraint
- [ ] Create task with invalid priority_id - expect FK violation
- [ ] Create task with tags - verify many-to-many relationship
- [ ] Delete task - verify tag associations removed (CASCADE)
- [ ] Delete tag - verify task associations removed (CASCADE)
- [ ] Create duplicate tag name - expect UNIQUE constraint violation
- [ ] Create task with recurring=true but no due_date - expect validation error

### Query Performance Testing

- [ ] Benchmark task list query with 100 tasks + priority + tags (target: < 50ms)
- [ ] Benchmark filtered query (priority + tags + date range) with 500 tasks (target: < 100ms)
- [ ] Benchmark tag autocomplete with 100 tags (target: < 50ms)
- [ ] Run EXPLAIN ANALYZE on complex queries - verify indexes used

---

## References

- **Specification**: [Advanced Task Management Features](spec.md)
- **Phase 2 Spec**: [Full-Stack Web TODO Application](../002-phase-2/spec.md)
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **PostgreSQL Foreign Keys**: https://www.postgresql.org/docs/current/ddl-constraints.html
