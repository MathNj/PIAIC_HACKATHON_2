"""
Task API routes.

Endpoints for task CRUD operations with multi-user isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated, Literal, Optional
from datetime import datetime

from app.database import get_session
from app.models.task import Task
from app.models.task_tag import TaskTag
from app.schemas.task import TaskRead, TaskCreate, TaskUpdate
from app.auth.dependencies import get_current_user
from app.dapr.client import dapr_client

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
    priority_ids: Optional[list[int]] = Query(
        None,
        alias="priority",
        description="Filter by priority IDs (1=High, 2=Medium, 3=Low)"
    ),
    tag_ids: Optional[list[int]] = Query(
        None,
        alias="tags",
        description="Filter by tag IDs"
    ),
    due_date_from: Optional[datetime] = Query(
        None,
        description="Filter tasks with due date >= this date"
    ),
    due_date_to: Optional[datetime] = Query(
        None,
        description="Filter tasks with due date <= this date"
    ),
    is_recurring: Optional[bool] = Query(
        None,
        description="Filter by recurring status"
    ),
    sort: Literal["created", "updated", "title", "due_date", "priority"] = Query(
        "created",
        description="Sort tasks by field"
    ),
    sort_order: Literal["asc", "desc"] = Query(
        "asc",
        description="Sort order (asc or desc)"
    )
) -> list[TaskRead]:
    """
    Get all tasks for a user with advanced filtering and sorting.

    **Authorization**: User can only access their own tasks.
    Path user_id must match authenticated user from JWT.

    **Filtering**:
    - status=all|pending|completed: Filter by completion status
    - priority=[1,2,3]: Filter by priority IDs (1=High, 2=Medium, 3=Low)
    - tags=[1,2,3]: Filter by tag IDs (tasks with ANY of these tags)
    - due_date_from/due_date_to: Filter by due date range
    - is_recurring=true|false: Filter recurring tasks

    **Sorting**:
    - sort=created|updated|title|due_date|priority
    - sort_order=asc|desc

    **Example**:
    ```
    GET /api/{user_id}/tasks?status=pending&priority=1&priority=2&sort=due_date&sort_order=asc
    ```

    Args:
        user_id: UUID from URL path
        current_user: UUID from JWT token
        session: Database session
        status_filter: Filter by completion status
        priority_ids: Filter by priority IDs
        tag_ids: Filter by tag IDs
        due_date_from: Filter tasks with due date >= this
        due_date_to: Filter tasks with due date <= this
        is_recurring: Filter by recurring status
        sort: Sort field
        sort_order: Sort direction (asc/desc)

    Returns:
        List of tasks matching filters

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

    # Apply priority filtering
    if priority_ids:
        statement = statement.where(Task.priority_id.in_(priority_ids))

    # Apply tag filtering (tasks with ANY of the specified tags)
    if tag_ids:
        # Join with task_tags to filter by tags
        statement = statement.join(TaskTag).where(TaskTag.tag_id.in_(tag_ids)).distinct()

    # Apply due date range filtering
    if due_date_from:
        statement = statement.where(Task.due_date >= due_date_from)
    if due_date_to:
        statement = statement.where(Task.due_date <= due_date_to)

    # Apply recurring filter
    if is_recurring is not None:
        statement = statement.where(Task.is_recurring == is_recurring)

    # Apply sorting
    sort_column = {
        "created": Task.created_at,
        "updated": Task.updated_at,
        "title": Task.title,
        "due_date": Task.due_date,
        "priority": Task.priority_id
    }[sort]

    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    # Execute query
    try:
        tasks = session.exec(statement).all()

        # For each task, fetch its tag IDs
        result_tasks = []
        for task in tasks:
            tag_statement = select(TaskTag.tag_id).where(TaskTag.task_id == task.id)
            task_tag_ids = session.exec(tag_statement).all()

            result_tasks.append(TaskRead(
                id=task.id,
                user_id=str(task.user_id),
                title=task.title,
                description=task.description,
                completed=task.completed,
                priority_id=task.priority_id,
                due_date=task.due_date,
                is_recurring=task.is_recurring,
                recurrence_pattern=task.recurrence_pattern,
                tag_ids=list(task_tag_ids),
                created_at=task.created_at,
                updated_at=task.updated_at
            ))

        return result_tasks
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
    new_task = Task(
        user_id=current_user,  # Use JWT user_id, not path parameter
        title=task_data.title,
        description=task_data.description,
        priority_id=task_data.priority_id,
        due_date=task_data.due_date,
        is_recurring=task_data.is_recurring,
        recurrence_pattern=task_data.recurrence_pattern,
        # completed defaults to False
        # created_at and updated_at default to datetime.utcnow()
    )

    # Insert into database
    try:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)  # Populate auto-generated fields (id, timestamps)

        # Create tag associations
        for tag_id in task_data.tag_ids:
            task_tag = TaskTag(task_id=new_task.id, tag_id=tag_id)
            session.add(task_tag)

        session.commit()

        # Publish task_created event to Dapr pub/sub
        try:
            event_data = {
                "event_type": "task_created",
                "task_id": new_task.id,
                "user_id": str(new_task.user_id),
                "title": new_task.title,
                "description": new_task.description,
                "completed": new_task.completed,
                "priority_id": new_task.priority_id,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "is_recurring": new_task.is_recurring,
                "recurrence_pattern": new_task.recurrence_pattern,
                "tag_ids": task_data.tag_ids,
                "created_at": new_task.created_at.isoformat(),
                "updated_at": new_task.updated_at.isoformat()
            }

            dapr_client.publish_event(
                pubsub_name="kafka-pubsub",
                topic_name="task-events",
                data=event_data
            )
        except Exception as pub_error:
            # Log the error but don't fail the request - event publishing is non-critical
            print(f"Warning: Failed to publish task_created event: {str(pub_error)}")

        # Convert to response schema with string user_id
        return TaskRead(
            id=new_task.id,
            user_id=str(new_task.user_id),
            title=new_task.title,
            description=new_task.description,
            completed=new_task.completed,
            priority_id=new_task.priority_id,
            due_date=new_task.due_date,
            is_recurring=new_task.is_recurring,
            recurrence_pattern=new_task.recurrence_pattern,
            tag_ids=task_data.tag_ids,
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

    # Fetch tag IDs for this task
    tag_statement = select(TaskTag.tag_id).where(TaskTag.task_id == task.id)
    task_tag_ids = session.exec(tag_statement).all()

    # Convert to response schema with string user_id
    return TaskRead(
        id=task.id,
        user_id=str(task.user_id),
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority_id=task.priority_id,
        due_date=task.due_date,
        is_recurring=task.is_recurring,
        recurrence_pattern=task.recurrence_pattern,
        tag_ids=list(task_tag_ids),
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
    update_data = task_update.model_dump(exclude_unset=True)  # Pydantic v2 syntax

    # Handle tag_ids separately
    new_tag_ids = update_data.pop("tag_ids", None)

    for field, value in update_data.items():
        setattr(task, field, value)

    # Always update updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Save to database
    try:
        session.add(task)
        session.commit()
        session.refresh(task)

        # Update tag associations if provided
        if new_tag_ids is not None:
            # Remove existing tag associations
            delete_statement = select(TaskTag).where(TaskTag.task_id == task.id)
            existing_task_tags = session.exec(delete_statement).all()
            for task_tag in existing_task_tags:
                session.delete(task_tag)

            # Add new tag associations
            for tag_id in new_tag_ids:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)

            session.commit()

        # Fetch current tag IDs
        tag_statement = select(TaskTag.tag_id).where(TaskTag.task_id == task.id)
        task_tag_ids = session.exec(tag_statement).all()

        # Convert to response schema with string user_id
        return TaskRead(
            id=task.id,
            user_id=str(task.user_id),
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority_id=task.priority_id,
            due_date=task.due_date,
            is_recurring=task.is_recurring,
            recurrence_pattern=task.recurrence_pattern,
            tag_ids=list(task_tag_ids),
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

        # Fetch tag IDs for this task
        tag_statement = select(TaskTag.tag_id).where(TaskTag.task_id == task.id)
        task_tag_ids = session.exec(tag_statement).all()

        # Convert to response schema with string user_id
        return TaskRead(
            id=task.id,
            user_id=str(task.user_id),
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority_id=task.priority_id,
            due_date=task.due_date,
            is_recurring=task.is_recurring,
            recurrence_pattern=task.recurrence_pattern,
            tag_ids=list(task_tag_ids),
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle task completion: {str(e)}"
        )
