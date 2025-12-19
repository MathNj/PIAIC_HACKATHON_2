---
name: "db-migration-wizard"
description: "Automates Alembic database migrations: generates migration scripts, handles schema changes, converts data types, and ensures database-code alignment. Use when database schema needs to evolve."
version: "1.0.0"
---

# Database Migration Wizard Skill

## When to Use
- User asks to "add a new database column" or "change column type"
- User says "Run database migration" or "Fix schema mismatch"
- Backend models updated and database needs syncing
- Data type conversions needed (e.g., string → integer)
- Column renames or constraint changes
- Error messages show "column does not exist" or "type mismatch"

## Context
This skill handles database migrations following:
- **Migration Tool**: Alembic (SQLAlchemy-based)
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)
- **Databases**:
  - **Local**: SQLite (limited ALTER TABLE support)
  - **Production**: Neon Serverless PostgreSQL (full ALTER TABLE support)
- **Strategy**: Autogenerate migrations, review, test, apply

## Workflow
1. **Analyze Current State**: Check database schema vs SQLModel definitions
2. **Update Models**: Modify SQLModel classes in `backend/app/models/`
3. **Generate Migration**: Use `alembic revision --autogenerate`
4. **Review Migration**: Inspect generated SQL for correctness
5. **Add Data Migration**: Handle data conversions if needed
6. **Test Locally**: Apply migration to SQLite
7. **Apply to Production**: Run migration on Neon PostgreSQL
8. **Verify**: Check data integrity and API functionality

## Output Formats

### 1. Adding New Column (Nullable First)

**SQLModel Update**:
```python
# backend/app/models/task.py
from sqlmodel import Field, SQLModel
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Existing fields...

    # New field - nullable first
    is_recurring: Optional[bool] = Field(
        default=None,
        nullable=True,
        description="Whether task repeats on a schedule"
    )
```

**Generate Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add is_recurring column to tasks"
```

**Migration File** (`alembic/versions/xxxx_add_is_recurring.py`):
```python
"""Add is_recurring column to tasks

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-12-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None


def upgrade():
    # Add column as nullable
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=True))

    # Set default value for existing rows
    op.execute("UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL")

    # Make non-nullable after setting defaults
    op.alter_column('tasks', 'is_recurring', nullable=False)


def downgrade():
    op.drop_column('tasks', 'is_recurring')
```

**Apply Migration**:
```bash
# Local testing
alembic upgrade head

# Production (via kubectl)
kubectl exec <backend-pod> -c backend -- alembic upgrade head
```

### 2. Renaming Column (Preserve Data)

**Problem**: Backend expects `priority_id` but database has `priority`

**SQLModel Update**:
```python
# backend/app/models/task.py
class Task(SQLModel, table=True):
    # OLD: priority: str
    # NEW: priority_id: Optional[int]

    priority_id: Optional[int] = Field(
        default=None,
        nullable=True,
        foreign_key="priorities.id",
        description="Task priority level (1=High, 2=Normal, 3=Low)"
    )
```

**Migration File**:
```python
def upgrade():
    # Rename column (preserves data)
    op.alter_column('tasks', 'priority', new_column_name='priority_id')


def downgrade():
    op.alter_column('tasks', 'priority_id', new_column_name='priority')
```

**Direct SQL** (when migration not feasible):
```python
# Via kubectl exec
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE tasks RENAME COLUMN priority TO priority_id'))
    conn.commit()
"
```

### 3. Converting Data Type (String → Integer)

**Problem**: Column has string data ('high', 'normal', 'low') but needs integers (1, 2, 3)

**Migration Strategy**:
```python
def upgrade():
    # Step 1: Clear incompatible data
    op.execute("UPDATE tasks SET priority_id = NULL")

    # Step 2: Change column type
    op.alter_column('tasks', 'priority_id',
                    type_=sa.Integer(),
                    existing_type=sa.String(),
                    nullable=True)


def downgrade():
    op.alter_column('tasks', 'priority_id',
                    type_=sa.String(),
                    existing_type=sa.Integer())
```

**With Data Conversion**:
```python
def upgrade():
    # Map string values to integers
    op.execute("""
        UPDATE tasks
        SET priority_id = CASE priority_id
            WHEN 'high' THEN 1
            WHEN 'normal' THEN 2
            WHEN 'low' THEN 3
            ELSE NULL
        END
    """)

    # Change column type
    op.alter_column('tasks', 'priority_id',
                    type_=sa.Integer(),
                    existing_type=sa.String())
```

### 4. Making Column Nullable/Non-Nullable

**Add NOT NULL Constraint**:
```python
def upgrade():
    # First, ensure no NULL values exist
    op.execute("UPDATE tasks SET completed = FALSE WHERE completed IS NULL")

    # Then add NOT NULL constraint
    op.alter_column('tasks', 'completed', nullable=False)


def downgrade():
    op.alter_column('tasks', 'completed', nullable=True)
```

**Remove NOT NULL Constraint**:
```python
def upgrade():
    # Allow NULL values
    op.alter_column('tasks', 'priority_id', nullable=True)


def downgrade():
    op.alter_column('tasks', 'priority_id', nullable=False)
```

### 5. Adding Foreign Key Constraint

**Create Reference Table First**:
```python
# Migration 1: Create priorities table
def upgrade():
    op.create_table('priorities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(20), nullable=False),
        sa.Column('color', sa.String(7), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default values
    op.execute("""
        INSERT INTO priorities (id, name, color) VALUES
        (1, 'High', '#ef4444'),
        (2, 'Normal', '#3b82f6'),
        (3, 'Low', '#10b981')
    """)


# Migration 2: Add FK constraint
def upgrade():
    op.create_foreign_key(
        'fk_tasks_priority_id',
        'tasks', 'priorities',
        ['priority_id'], ['id'],
        ondelete='SET NULL'
    )
```

### 6. Adding Index for Performance

**Migration File**:
```python
def upgrade():
    # Add index for faster queries
    op.create_index(
        'ix_tasks_user_id_completed',
        'tasks',
        ['user_id', 'completed']
    )


def downgrade():
    op.drop_index('ix_tasks_user_id_completed', table_name='tasks')
```

## Direct Database Access (Emergency)

### Via Kubernetes Pod

```bash
# Execute SQL directly
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    # Your SQL here
    result = conn.execute(text('SELECT * FROM tasks LIMIT 5'))
    for row in result:
        print(row)
"
```

### Common Emergency Fixes

**Add missing column**:
```python
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE NOT NULL'))
    conn.commit()
"
```

**Rename column**:
```python
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE tasks RENAME COLUMN priority TO priority_id'))
    conn.commit()
"
```

**Clear data before type change**:
```python
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('UPDATE tasks SET priority_id = NULL'))
    conn.execute(text('ALTER TABLE tasks ALTER COLUMN priority_id DROP NOT NULL'))
    conn.execute(text('ALTER TABLE tasks ALTER COLUMN priority_id TYPE INTEGER USING NULL'))
    conn.commit()
"
```

## Migration Checklist

Before applying migrations:
- [ ] Backup production database (Neon has automatic backups)
- [ ] Test migration on local SQLite
- [ ] Review generated SQL in migration file
- [ ] Check for data loss scenarios
- [ ] Test rollback procedure (downgrade)
- [ ] Update SQLModel models to match new schema
- [ ] Update Pydantic schemas in `backend/app/schemas/`
- [ ] Verify API endpoints still work
- [ ] Check frontend compatibility (TypeScript types)
- [ ] Document breaking changes in commit message

After applying migrations:
- [ ] Verify data integrity (check row counts, values)
- [ ] Test all CRUD operations via API
- [ ] Check for database locks or performance issues
- [ ] Monitor error logs for 500 errors
- [ ] Update API documentation if schema changed

## Common Pitfalls

1. **NOT NULL Constraints**: Always add nullable first, set defaults, then make non-nullable
   ```python
   # ❌ WRONG - Will fail if existing rows have NULL
   op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False))

   # ✅ CORRECT - Three-step process
   op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=True))
   op.execute("UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL")
   op.alter_column('tasks', 'is_recurring', nullable=False)
   ```

2. **Column Renames**: Use `alter_column()`, not drop + add (preserves data)
   ```python
   # ❌ WRONG - Loses data
   op.drop_column('tasks', 'priority')
   op.add_column('tasks', sa.Column('priority_id', sa.Integer()))

   # ✅ CORRECT - Preserves data
   op.alter_column('tasks', 'priority', new_column_name='priority_id')
   ```

3. **Type Changes**: May require data conversion or clearing
   ```python
   # ❌ WRONG - Fails if data incompatible
   op.alter_column('tasks', 'priority_id', type_=sa.Integer())

   # ✅ CORRECT - Clear or convert first
   op.execute("UPDATE tasks SET priority_id = NULL")
   op.alter_column('tasks', 'priority_id', type_=sa.Integer(), postgresql_using='priority_id::integer')
   ```

4. **Foreign Keys**: Create referenced table before adding FK constraint

5. **Indexes**: Add indexes AFTER data migration for better performance

6. **SQLite Limitations**: Limited ALTER TABLE support (may need table recreation)

## Example Usage

**Scenario**: Backend returns "column tasks.priority_id does not exist"

**Steps**:
1. Check database: Column is named `priority` (string)
2. Check model: Expects `priority_id` (integer FK)
3. Update SQLModel to use `priority_id: Optional[int]`
4. Generate migration: `alembic revision --autogenerate -m "Rename priority to priority_id"`
5. Review migration: Ensure it uses `alter_column` rename
6. Clear data: `UPDATE tasks SET priority = NULL` (if type incompatible)
7. Apply migration: `alembic upgrade head`
8. Update frontend TypeScript types to use `priority_id: number | null`
9. Test API: Create task, verify priority_id works

## Quality Checklist
Before finalizing:
- [ ] Migration file has both `upgrade()` and `downgrade()`
- [ ] Data preservation strategy in place
- [ ] NULL handling for new columns
- [ ] Type conversions handle existing data
- [ ] Foreign key constraints reference existing tables
- [ ] Indexes added for query optimization
- [ ] Migration tested locally before production
- [ ] Rollback plan documented
- [ ] API and frontend updated to match schema
- [ ] No hardcoded values (use environment variables)
