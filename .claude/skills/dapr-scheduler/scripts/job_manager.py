#!/usr/bin/env python3
"""
Dapr Jobs Manager

High-level utilities for managing Dapr jobs in FastAPI applications.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from schedule_job import DaprJobScheduler


logger = logging.getLogger(__name__)


class JobManager:
    """
    High-level job management for task reminders.

    Integrates with FastAPI to manage scheduled jobs for tasks.
    """

    def __init__(self, scheduler: Optional[DaprJobScheduler] = None):
        """
        Initialize JobManager.

        Args:
            scheduler: DaprJobScheduler instance (creates default if None)
        """
        self.scheduler = scheduler or DaprJobScheduler()

    def schedule_task_reminder(
        self,
        task_id: int,
        user_id: str,
        due_date: datetime
    ) -> Dict[str, Any]:
        """
        Schedule a reminder for a task's due date.

        Args:
            task_id: Task ID
            user_id: User ID
            due_date: Task due date

        Returns:
            Dict with job details
        """
        job_name = self.scheduler.schedule_job(
            task_id=task_id,
            user_id=user_id,
            due_date=due_date
        )

        return {
            "job_name": job_name,
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_for": due_date.isoformat(),
            "status": "scheduled"
        }

    def cancel_task_reminder(self, task_id: int, user_id: str) -> bool:
        """
        Cancel a task reminder.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            True if cancelled successfully
        """
        job_name = f"task-reminder-{task_id}-{user_id}"

        try:
            self.scheduler.delete_job(job_name)
            logger.info(f"Cancelled reminder for task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel reminder for task {task_id}: {e}")
            return False

    def reschedule_task_reminder(
        self,
        task_id: int,
        user_id: str,
        new_due_date: datetime
    ) -> Dict[str, Any]:
        """
        Reschedule a task reminder to a new due date.

        Args:
            task_id: Task ID
            user_id: User ID
            new_due_date: New due date

        Returns:
            Dict with updated job details
        """
        job_name = f"task-reminder-{task_id}-{user_id}"

        updated_job_name = self.scheduler.update_job(
            job_name=job_name,
            task_id=task_id,
            user_id=user_id,
            new_due_date=new_due_date
        )

        return {
            "job_name": updated_job_name,
            "task_id": task_id,
            "user_id": user_id,
            "rescheduled_for": new_due_date.isoformat(),
            "status": "rescheduled"
        }

    def list_user_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all scheduled reminders for a user.

        Args:
            user_id: User ID

        Returns:
            List of job details
        """
        try:
            all_jobs = self.scheduler.list_jobs()

            # Filter jobs for this user
            user_jobs = []
            if "jobs" in all_jobs:
                for job in all_jobs["jobs"]:
                    job_name = job.get("name", "")
                    if user_id in job_name:
                        user_jobs.append(job)

            return user_jobs

        except Exception as e:
            logger.error(f"Failed to list reminders for user {user_id}: {e}")
            return []

    def get_task_reminder(self, task_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get reminder details for a specific task.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            Job details or None if not found
        """
        job_name = f"task-reminder-{task_id}-{user_id}"

        try:
            job = self.scheduler.get_job(job_name)
            return job
        except Exception as e:
            logger.warning(f"Reminder not found for task {task_id}: {e}")
            return None


# Example integration with FastAPI
"""
from fastapi import FastAPI, Depends, HTTPException
from job_manager import JobManager
from datetime import datetime

app = FastAPI()
job_manager = JobManager()

@app.post("/api/tasks/{task_id}/schedule-reminder")
async def schedule_reminder(
    task_id: int,
    user_id: str,
    due_date: datetime
):
    try:
        result = job_manager.schedule_task_reminder(task_id, user_id, due_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}/reminder")
async def cancel_reminder(task_id: int, user_id: str):
    success = job_manager.cancel_task_reminder(task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder cancelled"}

@app.get("/api/users/{user_id}/reminders")
async def list_reminders(user_id: str):
    reminders = job_manager.list_user_reminders(user_id)
    return {"reminders": reminders}
"""
