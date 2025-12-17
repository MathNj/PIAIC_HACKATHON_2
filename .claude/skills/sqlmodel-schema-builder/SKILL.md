# SQLModel Schema Builder Skill

## Metadata
```yaml
name: sqlmodel-schema-builder
description: Builds SQLModel database schemas with proper relationships, indexes, constraints, validators, and Alembic migrations. Specializes in FastAPI + SQLModel patterns for the Todo App backend.
version: 1.0.0
category: backend
tags: [sqlmodel, database, schema, orm, alembic, migrations, postgresql, relationships]
dependencies: [sqlmodel, alembic, pydantic]
```

## When to Use This Skill

Use this skill when:
- User says "Create database schema" or "Build SQLModel models"
- Need to design database tables and relationships
- Phase II: Implementing data persistence layer
- Adding new models to existing schema
- Need to create Alembic migrations
- Setting up relationships (one-to-many, many-to-many)
- Adding indexes and constraints for performance
- Implementing field validators

## What This Skill Provides

### 1. SQLModel Schema Design
- **Table models**: SQLModel classes with proper fields
- **Relationships**: One-to-many, many-to-many, self-referential
- **Field types**: Proper type mapping (str, int, datetime, JSON, etc.)
- **Constraints**: NOT NULL, UNIQUE, CHECK, DEFAULT
- **Indexes**: Single-column, composite, partial indexes

### 2. Pydantic Integration
- **Request schemas**: Create/Update models for API endpoints
- **Response schemas**: Read models with computed fields
- **Validators**: Custom field validation logic
- **Computed fields**: Properties derived from other fields
- **Config**: Model configuration (from_attributes, etc.)

### 3. Alembic Migrations
- **Auto-generation**: Generate migrations from model changes
- **Manual migrations**: Custom SQL for complex changes
- **Data migrations**: Populate/transform data during migration
- **Rollback**: Down migrations for safe rollback
- **Versioning**: Sequential migration versioning

### 4. Relationships
- **One-to-many**: User → Tasks (one user, many tasks)
- **Many-to-many**: Tasks ↔ Tags (tasks have tags, tags have tasks)
- **Self-referential**: Task → Subtasks (parent-child)
- **Back-references**: Automatic reverse relationships
- **Cascade**: ON DELETE CASCADE, SET NULL

### 5. Best Practices
- **Timestamps**: created_at, updated_at on all models
- **Soft deletes**: deleted_at for archiving
- **UUIDs vs Integers**: When to use which
- **Nullable fields**: Required vs optional
- **Default values**: Database defaults vs Python defaults

---

## Installation

### Core Dependencies
```bash
# Using uv (recommended)
uv add sqlmodel alembic psycopg2-binary

# Using pip
pip install sqlmodel alembic psycopg2-binary
```

### Optional
```bash
# PostgreSQL async support
uv add asyncpg

# SQLite (for development)
# Already included with Python
```

---

## Implementation Examples

### Example 1: Basic Task Model

```python
"""
Basic SQLModel schema for Todo App Task.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class TaskBase(SQLModel):
    """Base Task model with shared fields."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    due_date: Optional[datetime] = None

    # User relationship (foreign key)
    user_id: int = Field(foreign_key="user.id")

class Task(TaskBase, table=True):
    """Task table model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None  # Soft delete

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model="TaskTagLink")

    # Indexes (defined in migration)
    # INDEX idx_tasks_user_id ON tasks(user_id)
    # INDEX idx_tasks_status ON tasks(status)
    # INDEX idx_tasks_created_at ON tasks(created_at DESC)

class TaskCreate(TaskBase):
    """Schema for creating tasks (API request)."""
    pass

class TaskUpdate(SQLModel):
    """Schema for updating tasks (API request)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class TaskRead(TaskBase):
    """Schema for reading tasks (API response)."""
    id: int
    created_at: datetime
    updated_at: datetime

    # Include related data
    user: Optional["UserRead"] = None
    tags: list["TagRead"] = []

    class Config:
        from_attributes = True
```

---

### Example 2: User Model with Relationships

```python
"""
User model with one-to-many relationship to Tasks.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import re

class UserBase(SQLModel):
    """Base User model."""
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")
        return email.lower()

class User(UserBase, table=True):
    """User table model."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Authentication
    hashed_password: str = Field(exclude=True)  # Never return in API

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")

    # Indexes:
    # UNIQUE INDEX idx_users_email ON users(email)
    # UNIQUE INDEX idx_users_username ON users(username)

class UserCreate(SQLModel):
    """Schema for user registration."""
    email: str
    username: str
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = None

class UserUpdate(SQLModel):
    """Schema for updating user profile."""
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)

class UserRead(SQLModel):
    """Schema for reading user data."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    # Optionally include task count
    task_count: Optional[int] = None

    class Config:
        from_attributes = True
```

---

### Example 3: Many-to-Many Relationship (Tasks ↔ Tags)

```python
"""
Many-to-many relationship between Tasks and Tags.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# Link table for many-to-many
class TaskTagLink(SQLModel, table=True):
    """Link table for Task-Tag many-to-many relationship."""
    __tablename__ = "task_tag_links"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

    # Optional: Add metadata to the relationship
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TagBase(SQLModel):
    """Base Tag model."""
    name: str = Field(min_length=1, max_length=50, unique=True)
    color: str = Field(default="#808080", regex=r'^#[0-9A-Fa-f]{6}$')

class Tag(TagBase, table=True):
    """Tag table model."""
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)

    # Indexes:
    # UNIQUE INDEX idx_tags_name ON tags(name)

class TagCreate(TagBase):
    """Schema for creating tags."""
    pass

class TagUpdate(SQLModel):
    """Schema for updating tags."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, regex=r'^#[0-9A-Fa-f]{6}$')

class TagRead(TagBase):
    """Schema for reading tags."""
    id: int
    created_at: datetime

    # Optionally include task count
    task_count: Optional[int] = None

    class Config:
        from_attributes = True

# Usage in API
def add_tags_to_task(session, task_id: int, tag_ids: List[int]):
    """Add multiple tags to a task."""
    task = session.get(Task, task_id)

    for tag_id in tag_ids:
        tag = session.get(Tag, tag_id)
        if tag:
            # Create link
            link = TaskTagLink(task_id=task_id, tag_id=tag_id)
            session.add(link)

    session.commit()
```

---

### Example 4: Self-Referential Relationship (Subtasks)

```python
"""
Self-referential relationship for task hierarchy (parent-child).
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Task(TaskBase, table=True):
    """Task with optional parent task (subtasks)."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Self-referential foreign key
    parent_id: Optional[int] = Field(default=None, foreign_key="tasks.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")

    # Parent-child relationships
    parent: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={
            "remote_side": "Task.id"  # Important for self-referential
        }
    )
    subtasks: List["Task"] = Relationship(back_populates="parent")

    # Indexes:
    # INDEX idx_tasks_parent_id ON tasks(parent_id)

# API usage
def get_task_with_subtasks(session, task_id: int) -> TaskRead:
    """Get task with all subtasks."""
    task = session.get(Task, task_id)

    # Recursively load subtasks
    def load_subtasks(t: Task) -> dict:
        return {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "subtasks": [load_subtasks(st) for st in t.subtasks]
        }

    return load_subtasks(task)
```

---

### Example 5: Advanced Validators and Computed Fields

```python
"""
Advanced field validators and computed properties.
"""

from sqlmodel import SQLModel, Field
from pydantic import field_validator, computed_field
from typing import Optional
from datetime import datetime, timedelta

class TaskBase(SQLModel):
    """Task with advanced validation."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0, le=1000)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate due date is in the future."""
        if v and v < datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return v

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Remove excessive whitespace from description."""
        if v:
            # Remove leading/trailing whitespace and collapse multiple spaces
            v = ' '.join(v.split())
        return v if v else None

class TaskRead(TaskBase):
    """Task read schema with computed fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.utcnow() > self.due_date
        return False

    @computed_field
    @property
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date."""
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None

    @computed_field
    @property
    def age_days(self) -> int:
        """Calculate task age in days."""
        delta = datetime.utcnow() - self.created_at
        return delta.days

    class Config:
        from_attributes = True
```

---

### Example 6: Alembic Migration Generation

```python
"""
Generate and apply Alembic migrations.
"""

# Step 1: Initialize Alembic (one-time)
# Command: alembic init alembic

# Step 2: Configure alembic.ini
"""
# alembic.ini
sqlalchemy.url = postgresql://user:pass@localhost/todo_db
"""

# Step 3: Configure env.py
"""
# alembic/env.py
from app.models import SQLModel
from app.database import engine

target_metadata = SQLModel.metadata

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()
"""

# Step 4: Generate migration
"""
# After creating/modifying models:
alembic revision --autogenerate -m "Add tasks and users tables"

# This creates: alembic/versions/xxxx_add_tasks_and_users_tables.py
"""

# Step 5: Review and edit migration
"""
# alembic/versions/xxxx_add_tasks_and_users_tables.py

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(), nullable=False, server_default='normal'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_tasks_parent_id', 'tasks', ['parent_id'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False, server_default='#808080'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tags_name', 'tags', ['name'], unique=True)

    # Create many-to-many link table
    op.create_table(
        'task_tag_links',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('task_tag_links')
    op.drop_table('tags')
    op.drop_table('tasks')
    op.drop_table('users')
"""

# Step 6: Apply migration
"""
alembic upgrade head
"""

# Step 7: Rollback if needed
"""
alembic downgrade -1  # Go back one version
alembic downgrade base  # Go back to beginning
"""
```

---

### Example 7: Data Migration

```python
"""
Custom data migration for transforming existing data.
"""

# alembic/versions/xxxx_migrate_task_priorities.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # Add new priority column
    op.add_column('tasks', sa.Column('priority_v2', sa.String(), nullable=True))

    # Create temporary table reference
    tasks = table('tasks',
        column('id', sa.Integer),
        column('priority_old', sa.Integer),
        column('priority_v2', sa.String)
    )

    # Migrate data: integer priorities to string enum
    # 1 -> 'low', 2 -> 'normal', 3 -> 'high'
    op.execute(
        tasks.update()
        .where(tasks.c.priority_old == 1)
        .values(priority_v2='low')
    )
    op.execute(
        tasks.update()
        .where(tasks.c.priority_old == 2)
        .values(priority_v2='normal')
    )
    op.execute(
        tasks.update()
        .where(tasks.c.priority_old == 3)
        .values(priority_v2='high')
    )

    # Drop old column
    op.drop_column('tasks', 'priority_old')

    # Rename new column
    op.alter_column('tasks', 'priority_v2', new_column_name='priority')

    # Set default
    op.alter_column('tasks', 'priority', server_default='normal')

def downgrade():
    # Reverse migration
    op.add_column('tasks', sa.Column('priority_old', sa.Integer(), nullable=True))

    tasks = table('tasks',
        column('priority', sa.String),
        column('priority_old', sa.Integer)
    )

    # Convert back
    op.execute(tasks.update().where(tasks.c.priority == 'low').values(priority_old=1))
    op.execute(tasks.update().where(tasks.c.priority == 'normal').values(priority_old=2))
    op.execute(tasks.update().where(tasks.c.priority == 'high').values(priority_old=3))

    op.drop_column('tasks', 'priority')
    op.alter_column('tasks', 'priority_old', new_column_name='priority')
```

---

## Database Patterns

### Pattern 1: Soft Delete
```python
class BaseModel(SQLModel):
    """Base model with soft delete support."""
    deleted_at: Optional[datetime] = None

    def soft_delete(self):
        """Mark as deleted without removing from database."""
        self.deleted_at = datetime.utcnow()

    @classmethod
    def active_only(cls, session):
        """Query only non-deleted records."""
        return session.query(cls).filter(cls.deleted_at.is_(None))
```

### Pattern 2: Timestamps
```python
class TimestampMixin(SQLModel):
    """Mixin for automatic timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
```

### Pattern 3: UUID Primary Keys
```python
import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

class Task(SQLModel, table=True):
    """Task with UUID primary key."""
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=True))
    )
```

### Pattern 4: JSON Fields
```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON

class Task(SQLModel, table=True):
    """Task with JSON metadata field."""
    metadata_json: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )

    # Usage:
    # task.metadata_json = {"labels": ["urgent", "bug"], "assignee": "john"}
```

### Pattern 5: Composite Indexes
```python
# In Alembic migration
def upgrade():
    # Composite index for common query pattern
    op.create_index(
        'idx_tasks_user_status',
        'tasks',
        ['user_id', 'status']
    )

    # Partial index (PostgreSQL)
    op.create_index(
        'idx_tasks_active',
        'tasks',
        ['user_id'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
```

---

## CLI Tool for Schema Management

```python
"""
CLI for database schema operations.
"""

import typer
from rich.console import Console
from sqlmodel import SQLModel, create_engine
from alembic.config import Config
from alembic import command

app = typer.Typer(name="db", help="Database Schema Manager")
console = Console()

@app.command("init")
def init_database(url: str = typer.Option(..., help="Database URL")):
    """Initialize database with all tables."""
    engine = create_engine(url)
    SQLModel.metadata.create_all(engine)
    console.print("[green]✓ Database initialized[/green]")

@app.command("migrate")
def create_migration(message: str = typer.Argument(..., help="Migration message")):
    """Generate new Alembic migration."""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    console.print(f"[green]✓ Migration created: {message}[/green]")

@app.command("upgrade")
def upgrade_database(revision: str = typer.Option("head", help="Target revision")):
    """Apply migrations."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, revision)
    console.print(f"[green]✓ Upgraded to {revision}[/green]")

@app.command("downgrade")
def downgrade_database(revision: str = typer.Option("-1", help="Target revision")):
    """Rollback migrations."""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    console.print(f"[yellow]⚠ Downgraded to {revision}[/yellow]")

@app.command("current")
def show_current():
    """Show current migration version."""
    alembic_cfg = Config("alembic.ini")
    command.current(alembic_cfg)

@app.command("history")
def show_history():
    """Show migration history."""
    alembic_cfg = Config("alembic.ini")
    command.history(alembic_cfg)

if __name__ == "__main__":
    app()
```

Usage:
```bash
# Initialize database
python db_manager.py init --url postgresql://user:pass@localhost/todo_db

# Create migration
python db_manager.py migrate "Add tags table"

# Apply migrations
python db_manager.py upgrade

# Rollback one version
python db_manager.py downgrade -1

# Show current version
python db_manager.py current

# Show migration history
python db_manager.py history
```

---

## Best Practices

### 1. Schema Design
- Use descriptive table and column names
- Add indexes for foreign keys
- Use UNIQUE constraints for business keys
- Set appropriate field lengths (don't use TEXT for everything)
- Use ENUM types for fixed choices

### 2. Relationships
- Define back_populates for bidirectional relationships
- Use cascade options appropriately
- Lazy load vs eager load (select vs joined)
- Consider using link models for many-to-many with metadata

### 3. Migrations
- Always review auto-generated migrations
- Test migrations on staging first
- Write down migrations for rollback
- Use data migrations for transforming data
- Version migrations sequentially

### 4. Performance
- Add indexes for commonly queried fields
- Use composite indexes for multi-column queries
- Avoid N+1 queries (use joinedload)
- Use partial indexes for filtered queries
- Monitor slow queries

### 5. Validation
- Validate at both database and application level
- Use Pydantic validators for business logic
- Set database constraints for data integrity
- Handle constraint violations gracefully

---

## Quality Checklist

Before considering schema complete:
- [ ] All models have timestamps (created_at, updated_at)
- [ ] Foreign keys have appropriate indexes
- [ ] Relationships properly defined with back_populates
- [ ] Field constraints match business requirements
- [ ] Validators implemented for complex rules
- [ ] Alembic migrations generated and tested
- [ ] Down migrations written for rollback
- [ ] Indexes added for common query patterns
- [ ] Soft delete implemented if needed
- [ ] API schemas (Create/Update/Read) defined
- [ ] Database constraints match Pydantic validation

---

## Integration with Todo App

### Complete Schema for Todo App

```python
# app/models/__init__.py
from .user import User, UserCreate, UserUpdate, UserRead
from .task import Task, TaskCreate, TaskUpdate, TaskRead
from .tag import Tag, TagCreate, TagUpdate, TagRead
from .task_tag_link import TaskTagLink

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserRead",
    "Task", "TaskCreate", "TaskUpdate", "TaskRead",
    "Tag", "TagCreate", "TagUpdate", "TagRead",
    "TaskTagLink"
]
```

### Database Setup
```python
# app/database.py
from sqlmodel import create_engine, SQLModel, Session
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

def init_db():
    """Initialize database (development only)."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session (dependency injection)."""
    with Session(engine) as session:
        yield session
```

This creates a complete, production-ready database schema for the Todo App with proper relationships, indexes, and migrations.
