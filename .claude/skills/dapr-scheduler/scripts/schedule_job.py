#!/usr/bin/env python3
"""
Dapr Jobs API - Job Scheduler

Schedule exact-time jobs using Dapr Jobs API (POST /v1.0/jobs).
Replaces older Cron bindings with precise job scheduling.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class JobSchedule(BaseModel):
    """Job schedule configuration."""
    task_id: int
    user_id: str
    due_date: datetime
    job_name: Optional[str] = None

    def get_job_name(self) -> str:
        """Generate unique job name."""
        if self.job_name:
            return self.job_name
        return f"task-reminder-{self.task_id}-{self.user_id}"


class DaprJobScheduler:
    """
    Dapr Jobs API scheduler for exact-time task reminders.

    Usage:
        scheduler = DaprJobScheduler(dapr_host="localhost", dapr_port=3500)

        # Schedule a job
        job_id = scheduler.schedule_job(
            task_id=123,
            user_id="user-xyz",
            due_date=datetime(2025, 1, 15, 14, 30, 0)
        )

        # List jobs
        jobs = scheduler.list_jobs()

        # Delete job
        scheduler.delete_job(job_id)
    """

    def __init__(
        self,
        dapr_host: str = "localhost",
        dapr_port: int = 3500,
        callback_url: str = "/api/jobs/trigger"
    ):
        """
        Initialize Dapr Job Scheduler.

        Args:
            dapr_host: Dapr sidecar host
            dapr_port: Dapr HTTP port
            callback_url: FastAPI endpoint to invoke when job fires
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port
        self.callback_url = callback_url
        self.base_url = f"http://{dapr_host}:{dapr_port}/v1.0/jobs"

    def schedule_job(
        self,
        task_id: int,
        user_id: str,
        due_date: datetime,
        job_name: Optional[str] = None
    ) -> str:
        """
        Schedule a one-time job for exact due date.

        Args:
            task_id: Task ID to remind about
            user_id: User ID to notify
            due_date: Exact datetime to fire the job
            job_name: Optional custom job name

        Returns:
            job_name: Unique job identifier

        Raises:
            requests.HTTPError: If job scheduling fails
        """
        schedule = JobSchedule(
            task_id=task_id,
            user_id=user_id,
            due_date=due_date,
            job_name=job_name
        )

        job_name = schedule.get_job_name()

        # Dapr Jobs API payload
        payload = {
            "schedule": self._format_schedule(due_date),
            "repeats": 1,  # One-time job
            "dueTime": due_date.isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "scheduled_at": datetime.now().isoformat()
            }
        }

        # POST /v1.0/jobs/{job-name}
        url = f"{self.base_url}/{job_name}"

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            response.raise_for_status()

            logger.info(
                f"Scheduled job '{job_name}' for task {task_id} "
                f"at {due_date.isoformat()}"
            )
            return job_name

        except requests.HTTPError as e:
            logger.error(f"Failed to schedule job '{job_name}': {e}")
            raise

    def _format_schedule(self, due_date: datetime) -> str:
        """
        Format datetime as schedule expression.

        For one-time jobs, use ISO8601 duration format or just rely on dueTime.
        For recurring jobs, use cron expression.

        Args:
            due_date: Target datetime

        Returns:
            Schedule expression (can be empty for one-time with dueTime)
        """
        # For one-time jobs, dueTime is sufficient
        # Return empty string or use '@once' if supported
        return ""

    def list_jobs(self) -> Dict[str, Any]:
        """
        List all scheduled jobs.

        Returns:
            Dict with jobs metadata

        Raises:
            requests.HTTPError: If request fails
        """
        url = self.base_url

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.error(f"Failed to list jobs: {e}")
            raise

    def get_job(self, job_name: str) -> Dict[str, Any]:
        """
        Get specific job details.

        Args:
            job_name: Job identifier

        Returns:
            Job metadata

        Raises:
            requests.HTTPError: If job not found
        """
        url = f"{self.base_url}/{job_name}"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.error(f"Failed to get job '{job_name}': {e}")
            raise

    def delete_job(self, job_name: str) -> bool:
        """
        Delete (cancel) a scheduled job.

        Args:
            job_name: Job identifier

        Returns:
            True if deleted successfully

        Raises:
            requests.HTTPError: If deletion fails
        """
        url = f"{self.base_url}/{job_name}"

        try:
            response = requests.delete(url, timeout=5)
            response.raise_for_status()

            logger.info(f"Deleted job '{job_name}'")
            return True

        except requests.HTTPError as e:
            logger.error(f"Failed to delete job '{job_name}': {e}")
            raise

    def update_job(
        self,
        job_name: str,
        task_id: int,
        user_id: str,
        new_due_date: datetime
    ) -> str:
        """
        Update job schedule by deleting and recreating.

        Dapr Jobs API doesn't support PATCH, so we delete and recreate.

        Args:
            job_name: Existing job name
            task_id: Task ID
            user_id: User ID
            new_due_date: New datetime

        Returns:
            job_name: Updated job identifier
        """
        # Delete existing job
        try:
            self.delete_job(job_name)
        except requests.HTTPError:
            logger.warning(f"Job '{job_name}' not found, creating new one")

        # Schedule new job with same name
        return self.schedule_job(
            task_id=task_id,
            user_id=user_id,
            due_date=new_due_date,
            job_name=job_name
        )


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scheduler = DaprJobScheduler()

    # Schedule a job
    job_name = scheduler.schedule_job(
        task_id=123,
        user_id="user-abc",
        due_date=datetime(2025, 12, 25, 9, 0, 0)
    )

    print(f"Scheduled job: {job_name}")

    # List jobs
    jobs = scheduler.list_jobs()
    print(f"All jobs: {json.dumps(jobs, indent=2)}")

    # Delete job
    scheduler.delete_job(job_name)
    print(f"Deleted job: {job_name}")
