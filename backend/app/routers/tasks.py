"""
Task API routes.

Endpoints for task CRUD operations with multi-user isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated, Literal

from app.database import get_session
from app.models.task import Task
from app.schemas.task import TaskRead, TaskCreate, TaskUpdate
from app.auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get("/{user_id}/tasks", response_model=list[TaskRead])
async def get_tasks(
    user_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    status_filter: Literal["all", "pending", "completed"] = Query(
        "all",
        alias="status",
        description="Filter tasks by completion status"
    ),
    sort: Literal["created", "updated", "title"] = Query(
        "created",
        description="Sort tasks by field (created=ASC, updated=DESC, title=alphabetical)"
    )
) -> list[TaskRead]:
    """
    Get all tasks for a user with filtering and sorting.

    **Authorization**: User can only access their own tasks.
    Path user_id must match authenticated user from JWT.

    **Filtering**:
    - status=all: Return all tasks (default)
    - status=pending: Return only incomplete tasks (completed=False)
    - status=completed: Return only completed tasks (completed=True)

    **Sorting**:
    - sort=created: Sort by creation date (oldest first)
    - sort=updated: Sort by update date (newest first)
    - sort=title: Sort alphabetically by title (A-Z)

    **Example**:
    ```
    GET /api/{user_id}/tasks?status=pending&sort=created
    ```

    Args:
        user_id: UUID from URL path (user whose tasks to retrieve)
        current_user: UUID from JWT token (authenticated user)
        session: Database session
        status_filter: Filter by completion status
        sort: Sort field and direction

    Returns:
        List of tasks matching filters, sorted as specified

    Raises:
        HTTPException 403: If path user_id doesn't match authenticated user
        HTTPException 500: If database query fails
    """
    # Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot access tasks for user {user_id}"
        )

    # Build base query filtering by user_id
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filtering
    if status_filter == "pending":
        statement = statement.where(Task.completed == False)
    elif status_filter == "completed":
        statement = statement.where(Task.completed == True)
    # status_filter == "all": no additional filter needed

    # Apply sorting
    if sort == "created":
        # Sort by creation date (oldest first)
        statement = statement.order_by(Task.created_at.asc())
    elif sort == "updated":
        # Sort by update date (newest first)
        statement = statement.order_by(Task.updated_at.desc())
    elif sort == "title":
        # Sort alphabetically by title (A-Z)
        statement = statement.order_by(Task.title.asc())

    # Execute query
    try:
        tasks = session.exec(statement).all()
        # Convert to response schemas with string user_id
        return [
            TaskRead(
                id=task.id,
                user_id=str(task.user_id),
                title=task.title,
                description=task.description,
                completed=task.completed,
                priority=task.priority,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Create a new task for a user.

    **Authorization**: User can only create tasks for themselves.
    Path user_id must match authenticated user from JWT.

    **Request Body**:
    ```json
    {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }
    ```

    **Validation**:
    - title: Required, 1-200 characters
    - description: Optional, max 1000 characters

    **Response**: Returns the created task with all fields including:
    - id: Auto-generated task ID
    - user_id: Owner UUID (from JWT)
    - completed: Defaults to False
    - created_at: Timestamp when task was created
    - updated_at: Timestamp when task was last modified

    Args:
        user_id: UUID from URL path (user to create task for)
        task_data: TaskCreate schema with title and optional description
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        TaskRead: The newly created task with all fields

    Raises:
        HTTPException 403: If path user_id doesn't match authenticated user
        HTTPException 422: If validation fails (missing/invalid title or description)
        HTTPException 500: If database insertion fails
    """
    # Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot create tasks for user {user_id}"
        )

    # Create Task object with user_id from JWT (not from request body)
    # completed, created_at, updated_at will be set by SQLModel defaults
    new_task = Task(
        user_id=current_user,  # Use JWT user_id, not path parameter
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority or "normal",
        due_date=task_data.due_date,
        # completed defaults to False
        # created_at and updated_at default to datetime.utcnow()
    )

    # Insert into database
    try:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)  # Populate auto-generated fields (id, timestamps)

        # Convert to response schema with string user_id
        return TaskRead(
            id=new_task.id,
            user_id=str(new_task.user_id),
            title=new_task.title,
            description=new_task.description,
            completed=new_task.completed,
            priority=new_task.priority,
            due_date=new_task.due_date,
            created_at=new_task.created_at,
            updated_at=new_task.updated_at
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task_by_id(
    user_id: UUID,
    task_id: int,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Get a single task by ID for a user.

    **Authorization**: User can only access their own tasks.
    Path user_id must match authenticated user from JWT.

    **Response**: Returns the task with all fields.

    **Example**:
    ```
    GET /api/{user_id}/tasks/1
    ```

    Args:
        user_id: UUID from URL path (user whose task to retrieve)
        task_id: Task ID to retrieve
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        TaskRead: The requested task

    Raises:
        HTTPException 403: If path user_id doesn't match authenticated user
        HTTPException 404: If task not found or doesn't belong to user
    """
    # Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot access tasks for user {user_id}"
        )

    # Query for task with both id AND user_id (multi-user isolation)
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    # Return 404 if not found (don't expose whether task exists for other users)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Convert to response schema with string user_id
    return TaskRead(
        id=task.id,
        user_id=str(task.user_id),
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: UUID,
    task_id: int,
    task_update: TaskUpdate,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Update an existing task.

    **Authorization**: User can only update their own tasks.
    Path user_id must match authenticated user from JWT.

    **Request Body** (all fields optional):
    ```json
    {
        "title": "Updated title",
        "description": "Updated description",
        "completed": true
    }
    ```

    **Validation**:
    - title: 1-200 characters (if provided)
    - description: max 1000 characters (if provided)
    - completed: boolean (if provided)

    **Behavior**:
    - Only provided fields are updated
    - updated_at is automatically refreshed
    - created_at remains unchanged

    Args:
        user_id: UUID from URL path (user whose task to update)
        task_id: Task ID to update
        task_update: TaskUpdate schema with optional fields
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        TaskRead: The updated task with all fields

    Raises:
        HTTPException 403: If path user_id doesn't match authenticated user
        HTTPException 404: If task not found or doesn't belong to user
        HTTPException 422: If validation fails (empty title, too long, etc.)
        HTTPException 500: If database update fails
    """
    # Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot update tasks for user {user_id}"
        )

    # Fetch task for this user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    # Return 404 if not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Update only provided fields (partial update)
    update_data = task_update.dict(exclude_unset=True)  # Pydantic v1 syntax

    for field, value in update_data.items():
        setattr(task, field, value)

    # Always update updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Save to database
    try:
        session.add(task)
        session.commit()
        session.refresh(task)

        # Convert to response schema with string user_id
        return TaskRead(
            id=task.id,
            user_id=str(task.user_id),
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    user_id: UUID,
    task_id: int,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a task.

    **Authorization**: User can only delete their own tasks.
    Path user_id must match authenticated user from JWT.

    **Behavior**: Permanently removes the task from the database (hard delete).

    **Response**:
    ```json
    {
        "detail": "Task deleted"
    }
    ```

    Args:
        user_id: UUID from URL path (user whose task to delete)
        task_id: Task ID to delete
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException 403: If path user_id doesn't match authenticated user
        HTTPException 404: If task not found or doesn't belong to user
        HTTPException 500: If database deletion fails
    """
    # Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot delete tasks for user {user_id}"
        )

    # Fetch task for this user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    # Return 404 if not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Delete from database (hard delete)
    try:
        session.delete(task)
        session.commit()
        return {"detail": "Task deleted"}
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: UUID,
    task_id: int,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Toggle task completion status.

    **Authorization**: User can only toggle their own tasks.
    Path user_id must match authenticated user from JWT.

    **Behavior**: Toggles the completed field (True → False, False → True).
    No request body required.

    **Response**: Returns the updated task with toggled completed status.

    **Example**:
    ```
    PATCH /api/{user_id}/tasks/1/complete

    # If task.completed was False, it becomes True
    # If task.completed was True, it becomes False
    ```

    Args:
        user_id: UUID from URL path (user whose task to toggle)
        task_id: Task ID to toggle
        current_user: UUID from JWT token (authenticated user)
        session: Database session

    Returns:
        TaskRead: The updated task with toggled completion status

    Raises:
        HTTPException 403: If path user_id doesn't match authenticated user
        HTTPException 404: If task not found or doesn't belong to user
        HTTPException 422: If task_id is not a valid integer
        HTTPException 500: If database update fails
    """
    # Authorization: Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot toggle tasks for user {user_id}"
        )

    # Fetch task for this user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    # Return 404 if not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Save to database
    try:
        session.add(task)
        session.commit()
        session.refresh(task)

        # Convert to response schema with string user_id
        return TaskRead(
            id=task.id,
            user_id=str(task.user_id),
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle task completion: {str(e)}"
        )
