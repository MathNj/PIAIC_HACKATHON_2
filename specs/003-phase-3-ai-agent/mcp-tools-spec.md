# Feature: MCP Tools for Task Management

## Overview

This feature implements the Model Context Protocol (MCP) tools that enable the AI agent to interact with the Task API. These tools serve as the exclusive interface between the stateless AI agent and the backend database, ensuring proper authentication, authorization, and data isolation.

## User Stories

- **US-1**: As an AI agent, I want to create tasks on behalf of authenticated users, so that I can execute user requests
- **US-2**: As an AI agent, I want to list tasks for authenticated users, so that I can provide task status and recommendations
- **US-3**: As an AI agent, I want to mark tasks as complete, so that I can help users manage their progress
- **US-4**: As an AI agent, I want to delete tasks on behalf of users, so that I can clean up completed or unwanted items
- **US-5**: As an AI agent, I want to update task details, so that I can modify titles, descriptions, priorities, and due dates
- **US-6**: As a developer, I want all MCP tools to validate JWT tokens, so that unauthorized access is prevented
- **US-7**: As a developer, I want all MCP tools to enforce user_id isolation, so that users can only access their own data

## Acceptance Criteria

- [ ] **AC-1**: All 5 core MCP tools are implemented with strict type hints
- [ ] **AC-2**: Each tool accepts user_token (JWT) as first parameter and validates it
- [ ] **AC-3**: Each tool extracts user_id from JWT and validates it matches the provided user_id parameter
- [ ] **AC-4**: Tools return structured strings/JSON that LLMs can interpret easily
- [ ] **AC-5**: Tool failures return user-friendly error messages, not raw exceptions
- [ ] **AC-6**: add_task creates tasks with title, description, priority, and due_date support
- [ ] **AC-7**: list_tasks supports filtering by status (all, pending, completed)
- [ ] **AC-8**: complete_task toggles task completion status
- [ ] **AC-9**: delete_task removes tasks and returns confirmation
- [ ] **AC-10**: update_task supports partial updates (only provided fields modified)
- [ ] **AC-11**: All tools have comprehensive docstrings (LLM-readable)
- [ ] **AC-12**: MCP server properly registers all tools
- [ ] **AC-13**: Tools handle database errors gracefully
- [ ] **AC-14**: Unit tests cover all tools with mock database
- [ ] **AC-15**: Integration tests verify tool behavior with real database

## MCP Tool Specifications

### Tool 1: add_task

**Purpose**: Create a new task for the authenticated user

**Function Signature**:
```python
@mcp.tool()
def add_task(
    user_token: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None
) -> str
```

**Docstring** (LLM-readable):
```
Create a new task for the user.

This tool creates a task with the specified title and optional details.
Priority defaults to "normal" if not specified. Due date accepts ISO format
(YYYY-MM-DD) or natural language expressions.

Args:
    user_token: JWT authentication token for the user
    title: Task title (required, 1-200 characters)
    description: Optional detailed description (max 1000 characters)
    priority: Task priority - "low", "normal" (default), or "high"
    due_date: Optional due date in ISO format (YYYY-MM-DD) or natural language

Returns:
    Success message with task ID and title, or error message

Examples:
    - add_task(token, "Buy groceries") → "Task 123 created: Buy groceries"
    - add_task(token, "Fix bug", "Critical production issue", "high", "2025-12-08")
      → "Task 124 created: Fix bug (high priority, due 2025-12-08)"
```

**Implementation Logic**:
1. Validate and decode JWT token to extract user_id
2. Validate title length (1-200 chars)
3. Parse due_date if provided (ISO format or natural language)
4. Set priority to "normal" if not provided
5. Create Task object with user_id from token
6. Save to database
7. Return formatted success message with task ID and details

**Return Format**:
```
Success: "Task {id} created: {title}" or "Task {id} created: {title} (high priority, due {date})"
Error: "Error creating task: {error_message}"
```

---

### Tool 2: list_tasks

**Purpose**: Retrieve all tasks for the authenticated user with optional filtering

**Function Signature**:
```python
@mcp.tool()
def list_tasks(
    user_token: str,
    status: Literal["all", "pending", "completed"] = "all",
    sort: Literal["created", "updated", "priority", "due_date"] = "created"
) -> str
```

**Docstring** (LLM-readable):
```
List all tasks for the authenticated user.

Returns a formatted list of tasks with filtering and sorting options.
Useful for checking task status, finding specific tasks, or providing
task summaries to the user.

Args:
    user_token: JWT authentication token for the user
    status: Filter by completion status - "all" (default), "pending", or "completed"
    sort: Sort order - "created" (default), "updated", "priority", or "due_date"

Returns:
    Formatted string with task list or error message

Examples:
    - list_tasks(token) → Returns all tasks sorted by creation date
    - list_tasks(token, "pending", "priority") → Returns incomplete tasks sorted by priority
    - list_tasks(token, "completed") → Returns only completed tasks
```

**Implementation Logic**:
1. Validate and decode JWT token to extract user_id
2. Build database query filtering by user_id and status
3. Apply sorting based on sort parameter
4. Execute query and retrieve tasks
5. Format tasks as readable string or JSON
6. Return formatted task list

**Return Format**:
```
Success:
"Found {count} tasks:
1. [ID: 1] Buy groceries (normal priority, due tomorrow, pending)
2. [ID: 2] Fix production bug (high priority, overdue, pending)
3. [ID: 3] Update documentation (low priority, completed)"

Empty: "No tasks found."
Error: "Error listing tasks: {error_message}"
```

---

### Tool 3: complete_task

**Purpose**: Mark a task as complete or toggle completion status

**Function Signature**:
```python
@mcp.tool()
def complete_task(
    user_token: str,
    task_id: int
) -> str
```

**Docstring** (LLM-readable):
```
Mark a task as complete (or toggle completion status).

If the task is currently incomplete, it will be marked as complete.
If the task is already complete, it will be marked as incomplete.
This allows users to undo task completion if needed.

Args:
    user_token: JWT authentication token for the user
    task_id: ID of the task to mark as complete

Returns:
    Confirmation message or error message

Examples:
    - complete_task(token, 123) → "Task 123 'Buy groceries' marked as complete"
    - complete_task(token, 124) → "Task 124 'Fix bug' marked as incomplete"
```

**Implementation Logic**:
1. Validate and decode JWT token to extract user_id
2. Query for task with task_id AND user_id (multi-user isolation)
3. If task not found, return error
4. Toggle task.completed status (True ↔ False)
5. Update task.updated_at timestamp
6. Save to database
7. Return confirmation with task title and new status

**Return Format**:
```
Success: "Task {id} '{title}' marked as complete" or "Task {id} '{title}' marked as incomplete"
Not Found: "Task {id} not found"
Error: "Error updating task: {error_message}"
```

---

### Tool 4: delete_task

**Purpose**: Permanently delete a task from the database

**Function Signature**:
```python
@mcp.tool()
def delete_task(
    user_token: str,
    task_id: int
) -> str
```

**Docstring** (LLM-readable):
```
Delete a task permanently.

Removes the task from the database. This action cannot be undone.
Use with caution - consider marking tasks as complete instead of deleting
them to maintain history.

Args:
    user_token: JWT authentication token for the user
    task_id: ID of the task to delete

Returns:
    Confirmation message or error message

Examples:
    - delete_task(token, 123) → "Task 123 'Buy groceries' deleted"
    - delete_task(token, 999) → "Task 999 not found"
```

**Implementation Logic**:
1. Validate and decode JWT token to extract user_id
2. Query for task with task_id AND user_id (multi-user isolation)
3. If task not found, return error
4. Store task title for confirmation message
5. Delete task from database
6. Return confirmation with task ID and title

**Return Format**:
```
Success: "Task {id} '{title}' deleted"
Not Found: "Task {id} not found"
Error: "Error deleting task: {error_message}"
```

---

### Tool 5: update_task

**Purpose**: Update task properties (partial updates supported)

**Function Signature**:
```python
@mcp.tool()
def update_task(
    user_token: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None
) -> str
```

**Docstring** (LLM-readable):
```
Update an existing task's properties.

Supports partial updates - only provided fields will be modified.
All other fields remain unchanged. This allows targeted updates without
needing to provide all task details.

Args:
    user_token: JWT authentication token for the user
    task_id: ID of the task to update
    title: New task title (optional, 1-200 characters)
    description: New description (optional, max 1000 characters)
    priority: New priority level (optional, "low", "normal", or "high")
    due_date: New due date (optional, ISO format YYYY-MM-DD)

Returns:
    Confirmation message with updated fields or error message

Examples:
    - update_task(token, 123, title="Buy groceries and cook dinner")
      → "Task 123 updated: title changed"
    - update_task(token, 124, priority="high", due_date="2025-12-08")
      → "Task 124 updated: priority changed to high, due date set to 2025-12-08"
```

**Implementation Logic**:
1. Validate and decode JWT token to extract user_id
2. Query for task with task_id AND user_id (multi-user isolation)
3. If task not found, return error
4. Update only fields that were provided (not None)
5. Validate new values (title length, priority enum, due_date format)
6. Update task.updated_at timestamp
7. Save to database
8. Return confirmation listing changed fields

**Return Format**:
```
Success: "Task {id} updated: {changes}" where changes = "title changed, priority set to high"
Not Found: "Task {id} not found"
Error: "Error updating task: {error_message}"
```

---

## Additional Recommended Tools

### Tool 6: get_task_summary

**Purpose**: Get analytics and statistics about user's tasks

**Function Signature**:
```python
@mcp.tool()
def get_task_summary(
    user_token: str,
    timeframe: Literal["today", "this_week", "overdue", "all"] = "all"
) -> str
```

**Returns**: Summary with task counts, priorities, and upcoming deadlines

---

### Tool 7: suggest_task_prioritization

**Purpose**: AI-powered task ordering recommendations

**Function Signature**:
```python
@mcp.tool()
def suggest_task_prioritization(
    user_token: str
) -> str
```

**Returns**: Ordered list of tasks with prioritization reasoning based on due dates and priorities

---

## Implementation Details

### File Structure
```
backend/
├── mcp/
│   ├── __init__.py
│   ├── server.py           # MCP server initialization and tool registration
│   └── tools.py            # MCP tool implementations
├── app/
│   ├── auth/
│   │   └── dependencies.py # verify_token function
│   ├── models/
│   │   └── task.py         # Task SQLModel
│   └── database.py         # Database session management
```

### MCP Server Setup (`backend/mcp/server.py`)

```python
"""
MCP (Model Context Protocol) server for TODO application.

Exposes task management functionality as AI-callable tools.
"""

from mcp import MCPServer

# Initialize MCP server
mcp = MCPServer(name="todo-mcp-server")

# Import tools to register them
from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_task_summary,
    suggest_task_prioritization
)

def get_mcp_server():
    """Get the initialized MCP server instance."""
    return mcp
```

### Authentication Pattern

All tools MUST follow this authentication pattern:

```python
from app.auth.dependencies import verify_token
from fastapi import HTTPException

def tool_function(user_token: str, ...):
    try:
        # Extract user_id from JWT token
        user_id = verify_token(user_token)

        # Tool logic here...

    except HTTPException as e:
        return f"Authentication error: {e.detail}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Database Session Pattern

All tools MUST use this database session pattern:

```python
from app.database import get_session
from sqlmodel import Session

def tool_function(user_token: str, ...):
    user_id = verify_token(user_token)

    with Session(engine) as session:
        # Database operations here...
        session.commit()
```

### Error Handling Pattern

All tools MUST return user-friendly error messages:

```python
try:
    # Tool logic
    return "Task 123 created: Buy groceries"
except ValueError as e:
    return f"Validation error: {str(e)}"
except HTTPException as e:
    return f"Authentication error: {e.detail}"
except Exception as e:
    return f"Error: {str(e)}"
```

---

## Non-Functional Requirements

**Security**:
- All tools MUST validate JWT token before any operation
- All tools MUST verify user_id from token matches requested user_id
- Failed authentication returns error string, not exception
- Database queries MUST filter by user_id (multi-user isolation)
- No tool can access data belonging to different users

**Performance**:
- Tool execution time: < 500ms for simple operations
- Tool execution time: < 2s for list_tasks with large datasets
- Database queries optimized with indexes on user_id

**Reliability**:
- Tools MUST handle all exceptions gracefully
- Tools MUST return structured strings (never raise exceptions)
- Database transaction failures rollback automatically
- Tools MUST validate input before database operations

**Testing**:
- Unit tests for each tool with mock database
- Unit tests for authentication failure scenarios
- Unit tests for user_id isolation (cross-user access blocked)
- Integration tests with real database
- Mock LLM calls to test tool responses

**Observability**:
- Tool calls logged in messages.tool_calls for audit trail
- Errors logged with context (user_id, task_id, operation)
- Tool execution time tracked for performance monitoring

---

## Dependencies & Integration

**Existing Features**:
- Phase II Task API (database models and CRUD logic)
- Phase II Authentication (JWT token validation)
- SQLModel session management

**New Dependencies**:
- MCP Python SDK (Official Model Context Protocol)
- OpenAI Agents SDK (for agent orchestration)

**Integration Points**:
- Tools consume existing Task model from `app/models/task.py`
- Tools use existing `verify_token` from `app/auth/dependencies.py`
- Tools use existing database session from `app/database.py`
- Agent calls tools via MCP protocol

---

## Testing Strategy

### Unit Tests (`backend/tests/test_mcp_tools.py`)

```python
import pytest
from mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task

class TestMCPTools:
    def test_add_task_creates_task(self, mock_token, mock_db):
        result = add_task(mock_token, "Test Task", "Description")
        assert "Task" in result
        assert "created" in result

    def test_add_task_validates_token(self, invalid_token):
        result = add_task(invalid_token, "Test")
        assert "Authentication error" in result

    def test_list_tasks_filters_by_user(self, user1_token, user2_token, mock_db):
        # User 1 creates task
        add_task(user1_token, "User 1 Task")

        # User 2 should not see User 1's task
        result = list_tasks(user2_token)
        assert "User 1 Task" not in result

    # ... more tests
```

### Integration Tests

```python
class TestMCPToolsIntegration:
    def test_full_task_lifecycle(self, auth_token, real_db):
        # Create
        result = add_task(auth_token, "Lifecycle Test")
        assert "created" in result

        # List
        result = list_tasks(auth_token)
        assert "Lifecycle Test" in result

        # Complete
        result = complete_task(auth_token, task_id)
        assert "complete" in result

        # Delete
        result = delete_task(auth_token, task_id)
        assert "deleted" in result
```

---

## Implementation Phases

### Phase 1: Core MCP Infrastructure
- Install MCP Python SDK
- Create `backend/mcp/` directory structure
- Initialize MCP server in `server.py`
- Set up tool registration pattern

### Phase 2: Authentication Integration
- Integrate `verify_token` from existing auth module
- Create authentication helper for tools
- Test token validation and user_id extraction

### Phase 3: Implement Core Tools (add, list, complete, delete, update)
- Implement each tool following specification
- Add comprehensive docstrings (LLM-readable)
- Implement error handling pattern
- Test each tool independently

### Phase 4: Implement Advanced Tools (summary, prioritization)
- Implement get_task_summary with analytics
- Implement suggest_task_prioritization with scoring
- Test recommendation logic

### Phase 5: Testing & Validation
- Write unit tests for all tools
- Write integration tests for tool interactions
- Test multi-user isolation
- Test error scenarios

### Phase 6: Documentation & Integration
- Document MCP tool usage in ADR
- Update API documentation
- Integrate tools with agent orchestration layer

---

## Out of Scope

- Batch operations (create multiple tasks at once)
- Task sharing or collaboration features
- Task templates or recurring tasks
- Advanced search or filtering beyond status
- Task attachments or file uploads
- Task history or change tracking (beyond tool_calls logging)

---

## References

- Constitution: `.specify/memory/constitution.md` (Phase III MCP compliance)
- AI Chat Spec: `specs/003-phase-3-ai-agent/spec.md`
- MCP Tool Maker Skill: `.claude/skills/mcp-tool-maker/SKILL.md`
- Phase II Task Model: `backend/app/models/task.py`
- Authentication: `backend/app/auth/dependencies.py`
