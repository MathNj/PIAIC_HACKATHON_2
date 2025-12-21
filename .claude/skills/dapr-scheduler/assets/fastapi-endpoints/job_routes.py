"""
FastAPI Job Management Routes

CRUD operations for managing Dapr scheduled jobs.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import logging

# Import from your scripts (adjust path as needed)
import sys
sys.path.append("scripts")
from job_manager import JobManager


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["job-management"])

# Initialize job manager (singleton pattern)
job_manager = JobManager()


class ScheduleReminderRequest(BaseModel):
    """Request to schedule a task reminder."""
    task_id: int
    user_id: str
    due_date: datetime


class RescheduleReminderRequest(BaseModel):
    """Request to reschedule a task reminder."""
    task_id: int
    user_id: str
    new_due_date: datetime


class ReminderResponse(BaseModel):
    """Reminder details response."""
    job_name: str
    task_id: int
    user_id: str
    scheduled_for: str
    status: str


@router.post("/schedule", response_model=ReminderResponse)
async def schedule_task_reminder(request: ScheduleReminderRequest):
    """
    Schedule a reminder for a task's due date.

    Creates a Dapr job that will fire at the exact due date time.

    Args:
        request: ScheduleReminderRequest with task_id, user_id, due_date

    Returns:
        ReminderResponse with job details

    Raises:
        HTTPException 500: If scheduling fails
    """
    try:
        result = job_manager.schedule_task_reminder(
            task_id=request.task_id,
            user_id=request.user_id,
            due_date=request.due_date
        )

        logger.info(
            f"Scheduled reminder for task {request.task_id} "
            f"at {request.due_date.isoformat()}"
        )

        return ReminderResponse(**result)

    except Exception as e:
        logger.error(f"Failed to schedule reminder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule reminder: {str(e)}"
        )


@router.delete("/tasks/{task_id}/reminder")
async def cancel_task_reminder(task_id: int, user_id: str):
    """
    Cancel a scheduled task reminder.

    Deletes the Dapr job associated with the task.

    Args:
        task_id: Task ID
        user_id: User ID

    Returns:
        Success message

    Raises:
        HTTPException 404: If reminder not found
        HTTPException 500: If cancellation fails
    """
    try:
        success = job_manager.cancel_task_reminder(task_id, user_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Reminder not found for task {task_id}"
            )

        return {
            "message": f"Reminder cancelled for task {task_id}",
            "task_id": task_id,
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel reminder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel reminder: {str(e)}"
        )


@router.put("/reschedule", response_model=ReminderResponse)
async def reschedule_task_reminder(request: RescheduleReminderRequest):
    """
    Reschedule a task reminder to a new due date.

    Updates the Dapr job with a new schedule time.

    Args:
        request: RescheduleReminderRequest with task_id, user_id, new_due_date

    Returns:
        ReminderResponse with updated job details

    Raises:
        HTTPException 500: If rescheduling fails
    """
    try:
        result = job_manager.reschedule_task_reminder(
            task_id=request.task_id,
            user_id=request.user_id,
            new_due_date=request.new_due_date
        )

        logger.info(
            f"Rescheduled reminder for task {request.task_id} "
            f"to {request.new_due_date.isoformat()}"
        )

        return ReminderResponse(**result)

    except Exception as e:
        logger.error(f"Failed to reschedule reminder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reschedule reminder: {str(e)}"
        )


@router.get("/users/{user_id}/reminders")
async def list_user_reminders(user_id: str):
    """
    List all scheduled reminders for a user.

    Returns all Dapr jobs associated with the user.

    Args:
        user_id: User ID

    Returns:
        List of reminder details

    Raises:
        HTTPException 500: If listing fails
    """
    try:
        reminders = job_manager.list_user_reminders(user_id)

        return {
            "user_id": user_id,
            "reminders": reminders,
            "count": len(reminders)
        }

    except Exception as e:
        logger.error(f"Failed to list reminders: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list reminders: {str(e)}"
        )


@router.get("/tasks/{task_id}/reminder")
async def get_task_reminder(task_id: int, user_id: str):
    """
    Get reminder details for a specific task.

    Args:
        task_id: Task ID
        user_id: User ID

    Returns:
        Reminder details or 404 if not found

    Raises:
        HTTPException 404: If reminder not found
        HTTPException 500: If retrieval fails
    """
    try:
        reminder = job_manager.get_task_reminder(task_id, user_id)

        if not reminder:
            raise HTTPException(
                status_code=404,
                detail=f"Reminder not found for task {task_id}"
            )

        return reminder

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reminder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get reminder: {str(e)}"
        )


# Integration example for task endpoints
"""
Add to your existing task routes:

from job_routes import job_manager

@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    # Create task in database
    new_task = await create_task_in_db(task)

    # Schedule reminder if due_date is set
    if new_task.due_date:
        try:
            job_manager.schedule_task_reminder(
                task_id=new_task.id,
                user_id=new_task.user_id,
                due_date=new_task.due_date
            )
        except Exception as e:
            logger.error(f"Failed to schedule reminder: {e}")

    return new_task

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    # Update task in database
    updated_task = await update_task_in_db(task_id, task)

    # Reschedule reminder if due_date changed
    if task.due_date and task.due_date != updated_task.due_date:
        try:
            job_manager.reschedule_task_reminder(
                task_id=task_id,
                user_id=updated_task.user_id,
                new_due_date=task.due_date
            )
        except Exception as e:
            logger.error(f"Failed to reschedule reminder: {e}")

    return updated_task

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, user_id: str):
    # Delete task from database
    await delete_task_from_db(task_id)

    # Cancel reminder
    try:
        job_manager.cancel_task_reminder(task_id, user_id)
    except Exception as e:
        logger.error(f"Failed to cancel reminder: {e}")

    return {"message": "Task deleted"}
"""
