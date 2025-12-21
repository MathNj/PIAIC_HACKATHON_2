"""
FastAPI Job Callback Endpoint

Handles job execution events from Dapr Jobs API.
This endpoint is invoked when a scheduled job fires.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobPayload(BaseModel):
    """Payload received from Dapr when job fires."""
    task_id: int
    user_id: str
    scheduled_at: str


class JobTriggerRequest(BaseModel):
    """Dapr job trigger request structure."""
    job_name: str
    data: JobPayload
    scheduled_time: Optional[str] = None


@router.post("/trigger")
async def job_trigger_callback(request: Request):
    """
    Job callback endpoint invoked by Dapr when a scheduled job fires.

    Dapr will POST to this endpoint with job details and payload.

    Request body structure:
    {
        "job_name": "task-reminder-123-user-xyz",
        "data": {
            "task_id": 123,
            "user_id": "user-xyz",
            "scheduled_at": "2025-01-15T14:30:00"
        },
        "scheduled_time": "2025-01-15T14:30:00"
    }

    Returns:
        200 OK if processed successfully
        500 if processing fails (Dapr will retry based on retry policy)
    """
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"Job trigger received: {body}")

        # Extract job data
        job_name = body.get("job_name")
        data = body.get("data", {})
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        if not task_id or not user_id:
            raise HTTPException(
                status_code=400,
                detail="Missing task_id or user_id in job payload"
            )

        # Process the reminder
        await process_task_reminder(task_id, user_id)

        logger.info(
            f"Successfully processed reminder for task {task_id}, user {user_id}"
        )

        return {
            "status": "success",
            "message": f"Reminder processed for task {task_id}",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to process job trigger: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process job: {str(e)}"
        )


async def process_task_reminder(task_id: int, user_id: str):
    """
    Process task reminder logic.

    Implement your reminder logic here:
    1. Fetch task details from database
    2. Send notification (email, push, SMS)
    3. Update task status if needed
    4. Log reminder activity

    Args:
        task_id: Task ID to remind about
        user_id: User ID to notify

    Raises:
        Exception: If processing fails
    """
    # TODO: Implement your reminder logic
    # Example:
    # 1. Fetch task from database
    # task = await get_task(task_id, user_id)

    # 2. Send notification
    # await send_notification(
    #     user_id=user_id,
    #     title=f"Task Reminder: {task.title}",
    #     message=f"Task '{task.title}' is due now!",
    #     task_id=task_id
    # )

    # 3. Log activity
    # await log_reminder_sent(task_id, user_id)

    logger.info(f"TODO: Implement reminder for task {task_id}, user {user_id}")


# Optional: Idempotency support
# Store processed job IDs to prevent duplicate processing
processed_jobs = set()  # In production, use Redis or database


@router.post("/trigger-idempotent")
async def job_trigger_idempotent(request: Request):
    """
    Idempotent job callback endpoint.

    Ensures jobs are processed exactly once even if Dapr retries.
    """
    try:
        body = await request.json()
        job_name = body.get("job_name")

        # Check if already processed
        if job_name in processed_jobs:
            logger.info(f"Job {job_name} already processed, skipping")
            return {"status": "skipped", "message": "Already processed"}

        # Process job
        data = body.get("data", {})
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        await process_task_reminder(task_id, user_id)

        # Mark as processed
        processed_jobs.add(job_name)

        return {
            "status": "success",
            "message": f"Reminder processed for task {task_id}"
        }

    except Exception as e:
        logger.error(f"Failed to process job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Optional: Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for job callback service."""
    return {
        "status": "healthy",
        "service": "dapr-job-callback",
        "timestamp": datetime.now().isoformat()
    }
