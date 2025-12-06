# Data Model: Console CRUD Operations

**Feature**: Console CRUD Operations
**Date**: 2025-12-05
**Status**: Complete

## Overview

This document defines the data structures and business logic for the TODO list application. All data is stored in-memory using Python data structures (no database, no file persistence).

## Entities

### Task

Represents a single TODO item.

**Attributes**:

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | int | Yes | auto | Unique auto-incrementing identifier (1, 2, 3, ...) |
| title | str | Yes | - | Task name/summary (non-empty) |
| description | str | No | "" | Optional detailed description (can be empty) |
| completed | bool | Yes | False | Completion status (False=pending, True=done) |

**Validation Rules**:
- `id`: Must be positive integer ≥ 1, assigned automatically by TaskManager
- `title`: Must be non-empty string (min length: 1 character)
- `description`: Can be empty string (length ≥ 0)
- `completed`: Boolean only (True or False)

**State Transitions**:
```
[New Task]
    ↓ (add_task)
[Incomplete] (completed=False)
    ↓ (mark_complete)
[Complete] (completed=True)
```

**Notes**:
- Tasks cannot transition from Complete back to Incomplete (no "unmark" operation)
- Task ID never changes after creation
- Tasks can be updated or deleted at any time regardless of completion status

**Python Implementation**:
```python
from dataclasses import dataclass

@dataclass
class Task:
    """Represents a TODO task.

    Attributes:
        id: Unique auto-incrementing identifier
        title: Task name (required, non-empty)
        description: Optional detailed description
        completed: Completion status (default False)
    """
    id: int
    title: str
    description: str
    completed: bool = False
```

## Business Logic

### TaskManager

Manages the in-memory collection of tasks and provides CRUD + completion operations.

**State**:
- `_tasks: dict[int, Task]` - Dictionary mapping task ID to Task object
- `_next_id: int` - Counter for auto-incrementing IDs (starts at 1)

**Operations**:

#### add_task(title: str, description: str) -> int

**Purpose**: Create a new task with auto-assigned ID

**Inputs**:
- `title` (str): Task name (must be non-empty, validated by caller)
- `description` (str): Task details (can be empty)

**Outputs**:
- Returns: Assigned task ID (int)

**Behavior**:
1. Create Task with `id=self._next_id`, `completed=False`
2. Store in `self._tasks[id]`
3. Increment `self._next_id`
4. Return assigned ID

**Complexity**: O(1)

**Example**:
```python
task_id = manager.add_task("Buy groceries", "Milk, eggs, bread")
# Returns: 1 (first task)
```

#### view_tasks() -> list[Task]

**Purpose**: Retrieve all tasks sorted by ID

**Inputs**: None

**Outputs**:
- Returns: List of Task objects sorted by ID (empty list if no tasks)

**Behavior**:
1. Get all tasks from `self._tasks.values()`
2. Sort by `task.id` ascending
3. Return sorted list

**Complexity**: O(n log n) where n = number of tasks

**Example**:
```python
tasks = manager.view_tasks()
# Returns: [Task(id=1, ...), Task(id=2, ...), Task(id=3, ...)]
```

#### update_task(task_id: int, title: Optional[str], description: Optional[str]) -> bool

**Purpose**: Update title and/or description of existing task

**Inputs**:
- `task_id` (int): ID of task to update (validated by caller)
- `title` (Optional[str]): New title, or None to keep current
- `description` (Optional[str]): New description, or None to keep current

**Outputs**:
- Returns: True if task found and updated, False if task ID not found

**Behavior**:
1. Look up task in `self._tasks[task_id]`
2. If not found: return False
3. If `title` is not None: update `task.title`
4. If `description` is not None: update `task.description`
5. Return True

**Side Effects**:
- Modifies task in-place (ID and completed status unchanged)
- If both title and description are None, task unchanged (but still returns True)

**Complexity**: O(1)

**Example**:
```python
success = manager.update_task(1, "Buy groceries and supplies", None)
# Returns: True (updates title, keeps original description)
```

#### delete_task(task_id: int) -> bool

**Purpose**: Remove task from collection

**Inputs**:
- `task_id` (int): ID of task to delete (validated by caller)

**Outputs**:
- Returns: True if task found and deleted, False if task ID not found

**Behavior**:
1. Check if `task_id` exists in `self._tasks`
2. If not found: return False
3. Delete from dictionary: `del self._tasks[task_id]`
4. Return True

**Side Effects**:
- Task permanently removed from memory
- Task ID is NOT reused (next_id counter continues incrementing)

**Complexity**: O(1)

**Example**:
```python
success = manager.delete_task(2)
# Returns: True (task 2 removed)
# Note: next task created will still be ID 3, not 2
```

#### mark_complete(task_id: int) -> bool

**Purpose**: Set task's completed status to True

**Inputs**:
- `task_id` (int): ID of task to mark complete (validated by caller)

**Outputs**:
- Returns: True if task found and marked, False if task ID not found

**Behavior**:
1. Look up task in `self._tasks[task_id]`
2. If not found: return False
3. Set `task.completed = True`
4. Return True

**Side Effects**:
- Modifies task in-place (completed flag set to True)
- Idempotent: can call multiple times on same task (always returns True if exists)

**Complexity**: O(1)

**Example**:
```python
success = manager.mark_complete(1)
# Returns: True (task 1 marked as complete)
```

#### get_task(task_id: int) -> Optional[Task]

**Purpose**: Retrieve single task by ID

**Inputs**:
- `task_id` (int): ID of task to retrieve

**Outputs**:
- Returns: Task object if found, None if not found

**Behavior**:
1. Look up and return `self._tasks.get(task_id)`

**Complexity**: O(1)

**Example**:
```python
task = manager.get_task(1)
# Returns: Task(id=1, title="Buy groceries", ...) or None
```

## Storage Structure

**In-Memory Storage**:
```python
# TaskManager internal state:
self._tasks = {
    1: Task(id=1, title="Buy groceries", description="Milk, eggs", completed=False),
    2: Task(id=2, title="Call dentist", description="", completed=True),
    3: Task(id=3, title="Finish report", description="Q4 summary", completed=False)
}
self._next_id = 4
```

**Memory Characteristics**:
- Dictionary overhead: ~240 bytes + 8 bytes per entry
- Task object size: ~56 bytes + string lengths
- Expected capacity: 100 tasks ≈ 10-20 KB total memory
- No persistence: all data lost on application exit

## Data Flow

### Add Task Flow
```
User Input (title, description)
    ↓
Presentation Layer validates title non-empty
    ↓
TaskManager.add_task(title, description)
    ↓
Create Task with next_id
    ↓
Store in _tasks dict
    ↓
Increment _next_id
    ↓
Return task_id to Presentation Layer
    ↓
Display "Task added with ID {task_id}"
```

### View Tasks Flow
```
User selects "View Tasks"
    ↓
TaskManager.view_tasks()
    ↓
Get all tasks from _tasks.values()
    ↓
Sort by task.id
    ↓
Return list to Presentation Layer
    ↓
Format each task as "[ID] [Status] Title"
    ↓
Display to user
```

### Update Task Flow
```
User Input (task_id, new_title, new_description)
    ↓
Presentation Layer validates task_id is numeric
    ↓
TaskManager.update_task(task_id, title, description)
    ↓
Lookup task by ID
    ↓
If found: update fields, return True
If not found: return False
    ↓
Presentation Layer displays success or "Task ID {id} not found"
```

### Delete Task Flow
```
User Input (task_id)
    ↓
Presentation Layer validates task_id is numeric
    ↓
TaskManager.delete_task(task_id)
    ↓
Check if task exists
    ↓
If found: delete from dict, return True
If not found: return False
    ↓
Presentation Layer displays success or "Task ID {id} not found"
```

### Mark Complete Flow
```
User Input (task_id)
    ↓
Presentation Layer validates task_id is numeric
    ↓
TaskManager.mark_complete(task_id)
    ↓
Lookup task by ID
    ↓
If found: set completed=True, return True
If not found: return False
    ↓
Presentation Layer displays success or "Task ID {id} not found"
```

## Invariants

**System Invariants** (must always be true):
1. All task IDs in `_tasks` dictionary are positive integers ≥ 1
2. `_next_id` is always greater than any existing task ID
3. All task IDs are unique within `_tasks`
4. No task has an empty title (ensured by validation)
5. All tasks have exactly 4 attributes: id, title, description, completed

**Operational Invariants**:
1. After `add_task()`: task exists in `_tasks` with assigned ID
2. After `delete_task(id)` returns True: task with `id` no longer in `_tasks`
3. After `mark_complete(id)` returns True: task with `id` has `completed=True`
4. `view_tasks()` always returns list sorted by ID (ascending)

## Constraints

**Phase I Constraints**:
- NO database connections
- NO file I/O (no saving/loading)
- NO external serialization libraries
- In-memory only (data lost on exit)
- Single-user (no concurrency control needed)

**Performance Constraints**:
- All operations O(1) except view_tasks which is O(n log n)
- Target: <100ms response time for all operations
- Scale: Support up to 100 tasks efficiently

**Data Constraints**:
- Task title max length: unlimited (practical limit: console width ~80 chars)
- Task description max length: unlimited
- Max tasks: no hard limit (practical limit: memory and usability ~100-1000)
- ID range: 1 to 2^31-1 (Python int max, effectively unlimited for use case)
