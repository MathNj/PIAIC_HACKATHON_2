"""
MCP Tools for Phase III AI Chat Agent.

This module implements the 5 core task management tools that the AI agent
can use to interact with the Task API. Each tool validates the JWT token
independently and enforces user isolation.

Tools implemented:
1. list_tasks - Retrieve all tasks for the authenticated user
2. create_task - Create a new task from natural language description
3. update_task - Modify existing task properties
4. delete_task - Remove a task by ID
5. toggle_task_completion - Mark task as complete/incomplete

Architecture:
- Each tool receives a JWT token string (not user_id directly)
- Token validation happens inside each tool (stateless)
- Tools use database sessions via dependency injection
- All errors are raised as exceptions for agent handling
- Return structured data (dicts/lists), not HTTP responses
"""

from typing import Optional, Dict, Any, List, Literal
from uuid import UUID
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlmodel import Session, select
from dateutil import parser as date_parser
import re

from app.config import settings
from app.database import get_session, engine
from app.models.task import Task


class MCPToolError(Exception):
    """Base exception for MCP tool errors."""
    pass


class AuthenticationError(MCPToolError):
    """Raised when JWT token validation fails."""
    pass


class AuthorizationError(MCPToolError):
    """Raised when user tries to access resources they don't own."""
    pass


class NotFoundError(MCPToolError):
    """Raised when requested resource doesn't exist."""
    pass


class ValidationError(MCPToolError):
    """Raised when input validation fails."""
    pass


def validate_jwt_token(token: str) -> UUID:
    """
    Validate JWT token and extract user_id.

    Supports two formats:
    1. JWT token: Standard JWT with user_id in payload
    2. Direct user_id: Format "user_id:<uuid>" for development/testing

    Args:
        token: JWT token string OR "user_id:<uuid>" format

    Returns:
        UUID: Authenticated user's UUID

    Raises:
        AuthenticationError: If token is invalid, expired, or missing user_id
    """
    # Handle direct user_id format (development/testing)
    if token.startswith("user_id:"):
        user_id_str = token[8:]  # Strip "user_id:" prefix
        try:
            return UUID(user_id_str)
        except ValueError:
            raise AuthenticationError(f"Invalid user_id format: {user_id_str}")

    # Handle JWT token format
    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id from payload
        user_id_str: str = payload.get("user_id")
        if user_id_str is None:
            raise AuthenticationError("Invalid token: missing user_id")

        # Convert string user_id to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid token: malformed user_id")

        return user_id

    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


# ============================================================================
# Natural Language Processing Helpers (Phase III - US4 & US5)
# ============================================================================

def parse_due_date(natural_language: str) -> Optional[str]:
    """
    Parse natural language temporal expressions into ISO date format.

    Supports:
    - Relative dates: "tomorrow", "next week", "in 3 days"
    - Day names: "Monday", "next Friday"
    - ISO dates: "2025-12-25"
    - Fuzzy parsing: "by end of month", "sometime next week"

    Args:
        natural_language: Date description in natural language

    Returns:
        ISO format date string (YYYY-MM-DD) or None if parsing fails

    Examples:
        >>> parse_due_date("tomorrow")
        "2025-12-09"
        >>> parse_due_date("next week")
        "2025-12-15"
        >>> parse_due_date("2025-12-25")
        "2025-12-25"
    """
    if not natural_language or not natural_language.strip():
        return None

    text = natural_language.strip().lower()
    today = datetime.now().date()

    # Handle common relative expressions first (faster than parsing)
    if text in ["today", "now"]:
        return today.isoformat()
    elif text == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    elif text == "yesterday":
        return (today - timedelta(days=1)).isoformat()
    elif text in ["next week", "in a week", "1 week"]:
        return (today + timedelta(days=7)).isoformat()
    elif text in ["next month", "in a month", "1 month"]:
        return (today + timedelta(days=30)).isoformat()

    # Handle "in X days/weeks/months" pattern
    in_pattern = re.match(r'in (\d+) (day|days|week|weeks|month|months)', text)
    if in_pattern:
        count = int(in_pattern.group(1))
        unit = in_pattern.group(2)
        if 'day' in unit:
            return (today + timedelta(days=count)).isoformat()
        elif 'week' in unit:
            return (today + timedelta(days=count * 7)).isoformat()
        elif 'month' in unit:
            return (today + timedelta(days=count * 30)).isoformat()

    # Try fuzzy parsing with dateutil (handles complex expressions)
    try:
        parsed_date = date_parser.parse(text, fuzzy=True, default=datetime.now())
        return parsed_date.date().isoformat()
    except (ValueError, date_parser.ParserError):
        # Parsing failed - return None
        return None


def infer_priority(description: str) -> Literal["low", "normal", "high"]:
    """
    Infer task priority from urgency keywords in the description.

    Priority Detection:
    - HIGH: urgent, asap, critical, important, emergency, crucial, vital, high priority
    - LOW: maybe, sometime, eventually, when possible, low priority, nice to have
    - NORMAL: default if no keywords match

    Args:
        description: Task description text

    Returns:
        Priority level: "low", "normal", or "high"

    Examples:
        >>> infer_priority("URGENT: Fix production bug")
        "high"
        >>> infer_priority("Maybe clean up the code sometime")
        "low"
        >>> infer_priority("Write documentation")
        "normal"
    """
    if not description:
        return "normal"

    text = description.lower()

    # High priority keywords
    high_keywords = [
        "urgent", "asap", "critical", "important", "emergency",
        "crucial", "vital", "high priority", "right away", "immediately",
        "blocker", "p0", "p1", "must", "required"
    ]

    # Low priority keywords
    low_keywords = [
        "maybe", "sometime", "eventually", "when possible", "low priority",
        "nice to have", "optional", "if time", "p3", "p4", "someday"
    ]

    # Check for high priority
    for keyword in high_keywords:
        if keyword in text:
            return "high"

    # Check for low priority
    for keyword in low_keywords:
        if keyword in text:
            return "low"

    # Default to normal
    return "normal"


def list_tasks(
    user_token: str,
    status: Literal["all", "pending", "completed"] = "all"
) -> List[Dict[str, Any]]:
    """
    List all tasks for the authenticated user.

    MCP Tool: list_tasks

    Args:
        user_token: JWT token for authentication
        status: Filter by completion status ("all", "pending", "completed")

    Returns:
        List of task dictionaries with fields:
        - id: Task ID
        - title: Task title
        - description: Task description (optional)
        - completed: Completion status
        - priority: Priority level (low/normal/high)
        - due_date: Due date timestamp (optional)
        - created_at: Creation timestamp
        - updated_at: Last update timestamp

    Raises:
        AuthenticationError: If token validation fails
        ValidationError: If status parameter is invalid

    Example:
        tasks = await list_tasks(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            status="pending"
        )
        # Returns: [{"id": 1, "title": "Buy groceries", ...}, ...]
    """
    # Validate JWT and extract user_id
    user_id = validate_jwt_token(user_token)

    # Validate status parameter
    if status not in ["all", "pending", "completed"]:
        raise ValidationError(f"Invalid status filter: {status}. Must be 'all', 'pending', or 'completed'")

    # Create database session
    with Session(engine) as session:
        # Build base query filtering by user_id
        statement = select(Task).where(Task.user_id == user_id)

        # Apply status filtering
        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        # Sort by creation date (oldest first)
        statement = statement.order_by(Task.created_at.asc())

        # Execute query
        tasks = session.exec(statement).all()

        # Convert to dictionaries
        return [
            {
                "id": task.id,
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]


def create_task(
    user_token: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task from natural language description.

    MCP Tool: create_task

    This tool supports natural language processing:
    - Priority inference: If priority is None, infers from description keywords
      (e.g., "URGENT task" → high, "maybe do this" → low)
    - Temporal parsing: Due dates can be natural language
      (e.g., "tomorrow", "next week", "2025-12-25")

    Args:
        user_token: JWT token for authentication
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)
        priority: Task priority ("low", "normal", "high") - if None, inferred from description
        due_date: Due date - supports natural language ("tomorrow", "next week") or ISO format

    Returns:
        Dictionary with created task fields (same as list_tasks)

    Raises:
        AuthenticationError: If token validation fails
        ValidationError: If title is empty, too long, or due_date is invalid

    Example:
        task = create_task(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            title="Buy groceries",
            description="Milk, eggs, bread - URGENT!",
            due_date="tomorrow"
        )
        # Priority inferred as "high" from "URGENT"
        # Due date parsed from "tomorrow"
    """
    # Validate JWT and extract user_id
    user_id = validate_jwt_token(user_token)

    # Validate title
    if not title or not title.strip():
        raise ValidationError("Task title cannot be empty")
    if len(title) > 200:
        raise ValidationError(f"Task title too long: {len(title)} characters (max 200)")

    # Validate description
    if description and len(description) > 1000:
        raise ValidationError(f"Task description too long: {len(description)} characters (max 1000)")

    # Infer priority from description if not provided (Phase III - US5)
    if priority is None:
        combined_text = f"{title} {description or ''}"
        priority = infer_priority(combined_text)

    # Validate priority
    if priority not in ["low", "normal", "high"]:
        raise ValidationError(f"Invalid priority: {priority}. Must be 'low', 'normal', or 'high'")

    # Parse due_date with natural language support (Phase III - US4)
    due_date_obj = None
    if due_date:
        # First try to parse as natural language
        parsed_iso_date = parse_due_date(due_date)
        if parsed_iso_date:
            # Convert ISO date string to datetime object at midnight
            due_date_obj = datetime.fromisoformat(parsed_iso_date + "T00:00:00")
        else:
            # Fallback: try parsing as ISO 8601 datetime
            try:
                due_date_obj = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError(f"Could not parse due_date: {due_date}. Use natural language (tomorrow, next week) or ISO format.")

    # Create database session
    with Session(engine) as session:
        # Create Task object
        new_task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority,
            due_date=due_date_obj,
            completed=False
        )

        # Insert into database
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Convert to dictionary
        return {
            "id": new_task.id,
            "user_id": str(new_task.user_id),
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.completed,
            "priority": new_task.priority,
            "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
            "created_at": new_task.created_at.isoformat(),
            "updated_at": new_task.updated_at.isoformat()
        }


def update_task(
    user_token: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing task's properties.

    MCP Tool: update_task

    Args:
        user_token: JWT token for authentication
        task_id: ID of the task to update
        title: Optional new title
        description: Optional new description
        priority: Optional new priority
        due_date: Optional new due date (ISO 8601 string)
        completed: Optional new completion status

    Returns:
        Dictionary with updated task fields

    Raises:
        AuthenticationError: If token validation fails
        AuthorizationError: If task doesn't belong to user
        NotFoundError: If task doesn't exist
        ValidationError: If any field validation fails

    Example:
        task = await update_task(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            task_id=123,
            title="Buy groceries (updated)",
            priority="high"
        )
    """
    # Validate JWT and extract user_id
    user_id = validate_jwt_token(user_token)

    # Validate at least one field is provided
    if all(v is None for v in [title, description, priority, due_date, completed]):
        raise ValidationError("At least one field must be provided for update")

    # Create database session
    with Session(engine) as session:
        # Fetch task for this user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        # Return 404 if not found
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        # Update fields if provided
        if title is not None:
            if not title.strip():
                raise ValidationError("Task title cannot be empty")
            if len(title) > 200:
                raise ValidationError(f"Task title too long: {len(title)} characters (max 200)")
            task.title = title.strip()

        if description is not None:
            if len(description) > 1000:
                raise ValidationError(f"Task description too long: {len(description)} characters (max 1000)")
            task.description = description.strip() if description else None

        if priority is not None:
            if priority not in ["low", "normal", "high"]:
                raise ValidationError(f"Invalid priority: {priority}. Must be 'low', 'normal', or 'high'")
            task.priority = priority

        if due_date is not None:
            try:
                task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError(f"Invalid due_date format: {due_date}. Expected ISO 8601 format")

        if completed is not None:
            task.completed = completed

        # Update updated_at timestamp
        task.updated_at = datetime.utcnow()

        # Save to database
        session.add(task)
        session.commit()
        session.refresh(task)

        # Convert to dictionary
        return {
            "id": task.id,
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }


def delete_task(
    user_token: str,
    task_id: int
) -> Dict[str, str]:
    """
    Delete a task by ID.

    MCP Tool: delete_task

    Args:
        user_token: JWT token for authentication
        task_id: ID of the task to delete

    Returns:
        Dictionary with success message:
        {"detail": "Task {id} deleted"}

    Raises:
        AuthenticationError: If token validation fails
        AuthorizationError: If task doesn't belong to user
        NotFoundError: If task doesn't exist

    Example:
        result = await delete_task(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            task_id=123
        )
        # Returns: {"detail": "Task 123 deleted"}
    """
    # Validate JWT and extract user_id
    user_id = validate_jwt_token(user_token)

    # Create database session
    with Session(engine) as session:
        # Fetch task for this user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        # Return 404 if not found
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        # Delete from database
        session.delete(task)
        session.commit()

        return {"detail": f"Task {task_id} deleted"}


def toggle_task_completion(
    user_token: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Toggle task completion status (True ↔ False).

    MCP Tool: toggle_task_completion

    Args:
        user_token: JWT token for authentication
        task_id: ID of the task to toggle

    Returns:
        Dictionary with updated task fields (completed status toggled)

    Raises:
        AuthenticationError: If token validation fails
        AuthorizationError: If task doesn't belong to user
        NotFoundError: If task doesn't exist

    Example:
        task = await toggle_task_completion(
            user_token="eyJhbGciOiJIUzI1NiIs...",
            task_id=123
        )
        # If task.completed was False, returns task with completed=True
        # If task.completed was True, returns task with completed=False
    """
    # Validate JWT and extract user_id
    user_id = validate_jwt_token(user_token)

    # Create database session
    with Session(engine) as session:
        # Fetch task for this user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        # Return 404 if not found
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        # Toggle completion status
        task.completed = not task.completed

        # Update updated_at timestamp
        task.updated_at = datetime.utcnow()

        # Save to database
        session.add(task)
        session.commit()
        session.refresh(task)

        # Convert to dictionary
        return {
            "id": task.id,
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }


# ============================================================================
# Advanced MCP Tools (Phase III - US6)
# ============================================================================

def get_task_summary(
    user_token: str,
    timeframe: Literal["all", "today", "week", "overdue"] = "all"
) -> Dict[str, Any]:
    """Get task statistics and summary."""
    user_id = validate_jwt_token(user_token)
    today = datetime.now().date()

    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)
        all_tasks = session.exec(statement).all()

        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.completed)
        pending = total - completed
        high_priority = sum(1 for t in all_tasks if t.priority == "high" and not t.completed)
        overdue = sum(1 for t in all_tasks if t.due_date and t.due_date.date() < today and not t.completed)
        due_today = sum(1 for t in all_tasks if t.due_date and t.due_date.date() == today and not t.completed)
        due_this_week = sum(1 for t in all_tasks if t.due_date and today <= t.due_date.date() <= today + timedelta(days=7) and not t.completed)

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority": high_priority,
            "overdue": overdue,
            "due_today": due_today,
            "due_this_week": due_this_week
        }


def suggest_task_prioritization(user_token: str) -> List[Dict[str, Any]]:
    """Suggest task prioritization based on urgency and importance."""
    user_id = validate_jwt_token(user_token)
    today = datetime.now().date()

    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id, Task.completed == False)
        tasks = session.exec(statement).all()

        scored_tasks = []
        for task in tasks:
            score = 0
            reasons = []

            if task.priority == "high":
                score += 30
                reasons.append("High Priority")
            elif task.priority == "normal":
                score += 15
            else:
                score += 5

            if task.due_date:
                due = task.due_date.date()
                if due < today:
                    score += 100
                    reasons.append("OVERDUE")
                elif due == today:
                    score += 50
                    reasons.append("Due Today")
                elif due <= today + timedelta(days=7):
                    score += 25
                    reasons.append("Due This Week")

            scored_tasks.append({
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                },
                "score": score,
                "reasoning": " + ".join(reasons) if reasons else "Normal"
            })

        scored_tasks.sort(key=lambda x: x["score"], reverse=True)
        return scored_tasks


def register_all_tools(server) -> None:
    """
    Register all MCP tools with the server.

    This function is called by initialize_mcp_server() to register
    all 5 task management tools with their schemas.

    Args:
        server: MCPServer instance to register tools with

    Example:
        from backend.mcp.server import mcp_server
        register_all_tools(mcp_server)
    """
    # Tool 1: list_tasks
    server.register_tool(
        "list_tasks",
        list_tasks,
        {
            "name": "list_tasks",
            "description": "List all tasks for the authenticated user with optional status filtering",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by completion status (default: 'all')"
                    }
                },
                "required": ["user_token"]
            }
        }
    )

    # Tool 2: create_task
    server.register_tool(
        "create_task",
        create_task,
        {
            "name": "create_task",
            "description": "Create a new task from natural language description with optional priority and due date",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description (max 1000 characters)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high"],
                        "description": "Task priority level (default: 'normal')"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional due date in ISO 8601 format (e.g., '2025-12-08T10:00:00Z')"
                    }
                },
                "required": ["user_token", "title"]
            }
        }
    )

    # Tool 3: update_task
    server.register_tool(
        "update_task",
        update_task,
        {
            "name": "update_task",
            "description": "Update an existing task's properties (title, description, priority, due_date, completed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional new title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional new description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high"],
                        "description": "Optional new priority"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional new due date (ISO 8601 format)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Optional new completion status"
                    }
                },
                "required": ["user_token", "task_id"]
            }
        }
    )

    # Tool 4: delete_task
    server.register_tool(
        "delete_task",
        delete_task,
        {
            "name": "delete_task",
            "description": "Permanently delete a task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["user_token", "task_id"]
            }
        }
    )

    # Tool 5: toggle_task_completion
    server.register_tool(
        "toggle_task_completion",
        toggle_task_completion,
        {
            "name": "toggle_task_completion",
            "description": "Toggle task completion status (mark as complete if pending, or pending if complete)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to toggle"
                    }
                },
                "required": ["user_token", "task_id"]
            }
        }
    )

    # Tool 6: get_task_summary (optional advanced tool)
    server.register_tool(
        "get_task_summary",
        get_task_summary,
        {
            "name": "get_task_summary",
            "description": "Get task statistics and summary with counts by status, priority, and timeframe",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["all", "today", "week", "overdue"],
                        "description": "Filter timeframe for summary (default: 'all')"
                    }
                },
                "required": ["user_token"]
            }
        }
    )

    # Tool 7: suggest_task_prioritization (optional advanced tool)
    server.register_tool(
        "suggest_task_prioritization",
        suggest_task_prioritization,
        {
            "name": "suggest_task_prioritization",
            "description": "Get AI-powered task prioritization suggestions based on urgency and due dates",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "JWT authentication token"
                    }
                },
                "required": ["user_token"]
            }
        }
    )
