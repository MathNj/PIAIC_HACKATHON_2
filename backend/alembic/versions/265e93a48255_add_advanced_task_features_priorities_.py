"""Add advanced task features - priorities tags recurring

Revision ID: 265e93a48255
Revises: bcde77eeb26a
Create Date: 2025-12-11 21:09:49.656042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '265e93a48255'
down_revision: Union[str, None] = 'bcde77eeb26a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create priorities table with seed data
    op.create_table(
        'priorities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('level')
    )
    op.create_index(op.f('ix_priorities_name'), 'priorities', ['name'], unique=False)

    # Seed priority data
    op.execute("""
        INSERT INTO priorities (id, name, level, color) VALUES
        (1, 'High', 1, '#EF4444'),
        (2, 'Medium', 2, '#F59E0B'),
        (3, 'Low', 3, '#10B981')
    """)

    # 2. Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)

    # 3. Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

    # 4. Drop old priority column from tasks (string-based)
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_column('tasks', 'priority')

    # 5. Add new columns to tasks table
    op.add_column('tasks', sa.Column('priority_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(length=20), nullable=True))

    # 6. Create foreign key and indexes
    op.create_foreign_key('fk_tasks_priority_id', 'tasks', 'priorities', ['priority_id'], ['id'])
    op.create_index(op.f('ix_tasks_priority_id'), 'tasks', ['priority_id'], unique=False)
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)
    op.create_index(op.f('ix_tasks_is_recurring'), 'tasks', ['is_recurring'], unique=False)

    # 7. Create composite indexes for efficient filtering
    op.create_index('idx_tasks_user_priority', 'tasks', ['user_id', 'priority_id'], unique=False)


def downgrade() -> None:
    # Reverse the changes
    op.drop_index('idx_tasks_user_priority', table_name='tasks')
    op.drop_index(op.f('ix_tasks_is_recurring'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_due_date'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_priority_id'), table_name='tasks')
    op.drop_constraint('fk_tasks_priority_id', 'tasks', type_='foreignkey')

    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')
    op.drop_column('tasks', 'priority_id')

    # Restore old priority string column
    op.add_column('tasks', sa.Column('priority', sa.String(), nullable=False, server_default='normal'))
    op.create_index('ix_tasks_priority', 'tasks', ['priority'], unique=False)

    op.drop_table('task_tags')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_priorities_name'), table_name='priorities')
    op.drop_table('priorities')
