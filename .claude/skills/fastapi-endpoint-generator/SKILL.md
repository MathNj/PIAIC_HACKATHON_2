---
name: "fastapi-endpoint-generator"
description: "Generates custom FastAPI endpoints with request validation, response models, error handling, and documentation. Use for non-CRUD endpoints like analytics, batch operations, complex queries, or business logic endpoints."
version: "1.0.0"
---

# FastAPI Endpoint Generator Skill

## When to Use
- User says "Create endpoint for..." or "Add API endpoint that..."
- Need custom business logic endpoint (not standard CRUD)
- Complex query operations (aggregations, joins, filters)
- Batch operations (bulk create, update, delete)
- Analytics endpoints (statistics, reports, dashboards)
- Action endpoints (send email, generate PDF, trigger workflow)
- Integration endpoints (webhooks, third-party API proxies)

## Context
This skill generates FastAPI endpoints following Todo App patterns:
- **Authentication**: JWT token validation with user_id extraction
- **Validation**: Pydantic schemas for request/response
- **Error Handling**: Proper HTTP status codes and error messages
- **Documentation**: OpenAPI/Swagger auto-docs
- **Testing**: Pytest test cases

## Workflow

### 1. Define Endpoint Requirements
- **Purpose**: What does this endpoint do?
- **Method**: GET, POST, PUT, PATCH, DELETE
- **Path**: URL structure with path parameters
- **Authentication**: Required or public?
- **Input**: Query params, path params, request body
- **Output**: Response model and status code
- **Business Logic**: What operations are performed?

### 2. Design Request/Response Models
Create Pydantic schemas if not exists in `backend/app/schemas/`

### 3. Implement Endpoint
Add to appropriate router in `backend/app/routers/`

### 4. Write Tests
Create test in `backend/tests/`

### 5. Update Documentation
Add to OpenAPI docs and update API reference

## Output Format

### Endpoint Template

```python
# backend/app/routers/[router_name].py
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlmodel import Session, select, func
from typing import Optional, List
from uuid import UUID

from app.database import get_session
from app.models.[model] import [Model]
from app.schemas.[schema] import [RequestSchema], [ResponseSchema]
from app.auth import get_current_user_id

router = APIRouter(
    prefix="/[resource]",
    tags=["[Tag]"]
)

@router.[method]("[path]", response_model=[ResponseSchema], status_code=status.HTTP_[CODE])
async def [function_name](
    # Path parameters
    [param]: [type] = Path(..., description="[Description]"),

    # Query parameters
    [param]: [type] = Query([default], description="[Description]"),

    # Request body
    [param]: [Schema] = Body(..., description="[Description]"),

    # Dependencies
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    [Endpoint description]

    - **[param]**: [Description]
    - **Returns**: [Description]
    """

    # Business logic here

    return response
```

## Examples

### Example 1: Statistics Endpoint (Aggregation)

**Requirement**: "Create endpoint to get task statistics (total, completed, pending) for current user"

**Output**:

```python
# backend/app/schemas/task_stats.py
from pydantic import BaseModel

class TaskStatsResponse(BaseModel):
    total: int
    completed: int
    pending: int
    in_progress: int
    completion_rate: float  # Percentage

# backend/app/routers/tasks.py
from sqlmodel import select, func
from app.schemas.task_stats import TaskStatsResponse

@router.get("/stats", response_model=TaskStatsResponse)
async def get_task_statistics(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get task statistics for the current user.

    Returns counts by status and overall completion rate.
    """
    # Get total count
    total_query = select(func.count(Task.id)).where(Task.user_id == user_id)
    total = session.exec(total_query).one()

    # Get counts by status
    completed_query = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.status == "completed"
    )
    completed = session.exec(completed_query).one()

    pending_query = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.status == "pending"
    )
    pending = session.exec(pending_query).one()

    in_progress_query = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.status == "in_progress"
    )
    in_progress = session.exec(in_progress_query).one()

    # Calculate completion rate
    completion_rate = (completed / total * 100) if total > 0 else 0.0

    return TaskStatsResponse(
        total=total,
        completed=completed,
        pending=pending,
        in_progress=in_progress,
        completion_rate=round(completion_rate, 2)
    )
```

**Test**:
```python
# backend/tests/test_task_stats.py
def test_get_task_statistics(auth_headers, db_session: Session, test_user):
    """Test task statistics endpoint."""
    user_id = test_user["id"]

    # Create test tasks
    tasks = [
        Task(user_id=user_id, title="Task 1", status="completed"),
        Task(user_id=user_id, title="Task 2", status="completed"),
        Task(user_id=user_id, title="Task 3", status="pending"),
        Task(user_id=user_id, title="Task 4", status="in_progress"),
    ]
    for task in tasks:
        db_session.add(task)
    db_session.commit()

    response = client.get("/tasks/stats", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["completed"] == 2
    assert data["pending"] == 1
    assert data["in_progress"] == 1
    assert data["completion_rate"] == 50.0
```

---

### Example 2: Batch Operation (Bulk Update)

**Requirement**: "Create endpoint to mark multiple tasks as completed"

**Output**:

```python
# backend/app/schemas/task.py
from pydantic import BaseModel
from typing import List

class TaskBulkCompleteRequest(BaseModel):
    task_ids: List[int]

class TaskBulkCompleteResponse(BaseModel):
    updated_count: int
    failed_ids: List[int]

# backend/app/routers/tasks.py
@router.post("/bulk-complete", response_model=TaskBulkCompleteResponse)
async def bulk_complete_tasks(
    request: TaskBulkCompleteRequest,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Mark multiple tasks as completed in a single operation.

    Only tasks belonging to the current user will be updated.
    Returns count of updated tasks and any IDs that failed.
    """
    from datetime import datetime

    updated_count = 0
    failed_ids = []

    for task_id in request.task_ids:
        # Fetch task with user validation
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if task:
            task.status = "completed"
            task.updated_at = datetime.utcnow()
            session.add(task)
            updated_count += 1
        else:
            failed_ids.append(task_id)

    session.commit()

    return TaskBulkCompleteResponse(
        updated_count=updated_count,
        failed_ids=failed_ids
    )
```

**Test**:
```python
def test_bulk_complete_tasks(auth_headers, db_session: Session, test_user):
    """Test bulk completing multiple tasks."""
    user_id = test_user["id"]

    # Create test tasks
    tasks = [
        Task(user_id=user_id, title=f"Task {i}", status="pending")
        for i in range(5)
    ]
    for task in tasks:
        db_session.add(task)
    db_session.commit()

    task_ids = [task.id for task in tasks[:3]]

    response = client.post(
        "/tasks/bulk-complete",
        json={"task_ids": task_ids},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["updated_count"] == 3
    assert len(data["failed_ids"]) == 0

    # Verify tasks are completed
    for task_id in task_ids:
        task = db_session.get(Task, task_id)
        assert task.status == "completed"
```

---

### Example 3: Search Endpoint (Complex Query)

**Requirement**: "Create endpoint to search tasks by title and description with filters"

**Output**:

```python
# backend/app/schemas/task.py
class TaskSearchRequest(BaseModel):
    query: str
    status: Optional[str] = None
    priority: Optional[str] = None

# backend/app/routers/tasks.py
@router.get("/search", response_model=TaskListResponse)
async def search_tasks(
    query: str = Query(..., min_length=1, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Search tasks by title and description with optional filters.

    - **query**: Search term (searches in title and description)
    - **status**: Filter by status (pending, in_progress, completed)
    - **priority**: Filter by priority (low, normal, high)
    """
    from sqlmodel import or_

    # Build base query with user scoping
    statement = select(Task).where(Task.user_id == user_id)

    # Add search filter (case-insensitive)
    search_filter = or_(
        Task.title.ilike(f"%{query}%"),
        Task.description.ilike(f"%{query}%")
    )
    statement = statement.where(search_filter)

    # Add optional filters
    if status:
        statement = statement.where(Task.status == status)
    if priority:
        statement = statement.where(Task.priority == priority)

    # Get total count
    count_statement = statement.with_only_columns(func.count(Task.id))
    total = session.exec(count_statement).one()

    # Apply pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size).order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()

    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )
```

---

### Example 4: Action Endpoint (Send Notification)

**Requirement**: "Create endpoint to send task reminder notification"

**Output**:

```python
# backend/app/schemas/notification.py
from pydantic import BaseModel

class SendReminderRequest(BaseModel):
    task_id: int
    notification_type: str  # "email", "sms", "push"

class SendReminderResponse(BaseModel):
    success: bool
    message: str

# backend/app/routers/notifications.py
from app.services.email import send_email  # Hypothetical email service

@router.post("/send-reminder", response_model=SendReminderResponse)
async def send_task_reminder(
    request: SendReminderRequest,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Send a reminder notification for a specific task.

    - **task_id**: ID of the task to remind about
    - **notification_type**: Delivery method (email, sms, push)
    """
    # Fetch task with user validation
    statement = select(Task).where(
        Task.id == request.task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get user details
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Send notification based on type
    try:
        if request.notification_type == "email":
            send_email(
                to=user.email,
                subject=f"Reminder: {task.title}",
                body=f"Don't forget about your task: {task.title}"
            )
        elif request.notification_type == "sms":
            # SMS sending logic
            pass
        elif request.notification_type == "push":
            # Push notification logic
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification type: {request.notification_type}"
            )

        return SendReminderResponse(
            success=True,
            message=f"Reminder sent via {request.notification_type}"
        )

    except Exception as e:
        return SendReminderResponse(
            success=False,
            message=f"Failed to send reminder: {str(e)}"
        )
```

---

### Example 5: Analytics Endpoint (Time-based Report)

**Requirement**: "Create endpoint for weekly task completion report"

**Output**:

```python
# backend/app/schemas/reports.py
from pydantic import BaseModel
from datetime import date
from typing import List

class DailyStats(BaseModel):
    date: date
    completed: int

class WeeklyReportResponse(BaseModel):
    week_start: date
    week_end: date
    total_completed: int
    daily_breakdown: List[DailyStats]
    average_per_day: float

# backend/app/routers/reports.py
from datetime import datetime, timedelta

@router.get("/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(
    week_offset: int = Query(0, description="Weeks ago (0=current, 1=last week)"),
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get weekly task completion report.

    - **week_offset**: Number of weeks in the past (0 for current week)

    Returns daily completion counts and weekly summary.
    """
    # Calculate week boundaries
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday() + (week_offset * 7))
    week_end = week_start + timedelta(days=6)

    # Get completed tasks for the week
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.status == "completed",
        Task.updated_at >= datetime.combine(week_start, datetime.min.time()),
        Task.updated_at <= datetime.combine(week_end, datetime.max.time())
    )
    tasks = session.exec(statement).all()

    # Group by day
    daily_counts = {}
    for task in tasks:
        day = task.updated_at.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1

    # Build daily breakdown
    daily_breakdown = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        daily_breakdown.append(DailyStats(
            date=day,
            completed=daily_counts.get(day, 0)
        ))

    total_completed = len(tasks)
    average_per_day = total_completed / 7

    return WeeklyReportResponse(
        week_start=week_start,
        week_end=week_end,
        total_completed=total_completed,
        daily_breakdown=daily_breakdown,
        average_per_day=round(average_per_day, 2)
    )
```

## Common Patterns

### 1. Pagination Helper
```python
def paginate_query(statement, page: int, page_size: int):
    """Helper to apply pagination to any query."""
    offset = (page - 1) * page_size
    return statement.offset(offset).limit(page_size)
```

### 2. Error Handling Decorator
```python
from functools import wraps

def handle_errors(func):
    """Decorator for consistent error handling."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

@router.get("/example")
@handle_errors
async def example_endpoint():
    # Endpoint logic
    pass
```

### 3. Background Tasks
```python
from fastapi import BackgroundTasks

def send_email_background(to: str, subject: str):
    """Background task for sending email."""
    # Email sending logic
    pass

@router.post("/send-notification")
async def send_notification(
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(get_current_user_id)
):
    """Endpoint with background task."""
    background_tasks.add_task(send_email_background, "user@example.com", "Notification")
    return {"message": "Notification queued"}
```

## Quality Checklist

Before finalizing endpoint:
- [ ] HTTP method matches operation (GET for read, POST for create, etc.)
- [ ] Path follows RESTful conventions
- [ ] Request schema validates all inputs
- [ ] Response schema includes all necessary fields
- [ ] Authentication required (unless explicitly public)
- [ ] User_id used for data scoping
- [ ] Proper HTTP status codes (200, 201, 204, 400, 404, etc.)
- [ ] Error messages are clear and actionable
- [ ] OpenAPI documentation complete (description, parameters)
- [ ] Tests cover success and error cases
- [ ] Edge cases handled (empty results, invalid input, not found)
- [ ] Performance considerations (pagination, indexing)

## Post-Creation

After generating endpoint:
1. **Test Manually**: Use Swagger UI at http://localhost:8000/docs
2. **Run Tests**: `pytest backend/tests/test_[module].py -v`
3. **Update API Docs**: Add to `@specs/api/rest-endpoints.md`
4. **Create Frontend Types**: Use api-schema-sync skill
5. **Update PHR**: Document the endpoint creation
