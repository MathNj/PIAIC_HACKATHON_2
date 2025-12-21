# Dapr Job Scheduling Patterns

Common patterns and best practices for task reminder scheduling with Dapr Jobs API.

## Table of Contents
- Task Reminder Patterns
- Integration Patterns
- Error Handling Patterns
- Performance Patterns
- Testing Patterns

## Task Reminder Patterns

### Pattern 1: Schedule on Task Creation

Schedule reminder when task is created with due date.

**Use Case:** User creates task with due date, wants automatic reminder

**Implementation:**
```python
from fastapi import APIRouter
from job_manager import JobManager

router = APIRouter()
job_manager = JobManager()

@router.post("/api/tasks")
async def create_task(task: TaskCreate):
    # Create task in database
    new_task = await db.create_task(task)

    # Schedule reminder if due_date is set
    if new_task.due_date:
        job_manager.schedule_task_reminder(
            task_id=new_task.id,
            user_id=new_task.user_id,
            due_date=new_task.due_date
        )

    return new_task
```

**Benefits:**
- Automatic reminders for all due dates
- No manual scheduling required
- Consistent user experience

### Pattern 2: Reschedule on Task Update

Update reminder when task due date changes.

**Use Case:** User edits task due date, reminder should reflect new time

**Implementation:**
```python
@router.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    # Get existing task
    existing_task = await db.get_task(task_id)

    # Update task
    updated_task = await db.update_task(task_id, task)

    # Handle due date changes
    if task.due_date:
        if task.due_date != existing_task.due_date:
            # Reschedule reminder
            job_manager.reschedule_task_reminder(
                task_id=task_id,
                user_id=updated_task.user_id,
                new_due_date=task.due_date
            )
    elif existing_task.due_date:
        # Due date removed, cancel reminder
        job_manager.cancel_task_reminder(task_id, updated_task.user_id)

    return updated_task
```

**Edge Cases Handled:**
- Due date added to task without one
- Due date changed to new time
- Due date removed from task

### Pattern 3: Cancel on Task Deletion

Remove reminder when task is deleted.

**Use Case:** User deletes task, reminder should not fire

**Implementation:**
```python
@router.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, user_id: str):
    # Delete task
    await db.delete_task(task_id)

    # Cancel reminder (ignore if not found)
    try:
        job_manager.cancel_task_reminder(task_id, user_id)
    except Exception as e:
        logger.warning(f"No reminder to cancel for task {task_id}: {e}")

    return {"message": "Task deleted"}
```

**Benefits:**
- Cleanup scheduled jobs
- Prevent orphaned reminders
- Resource efficiency

### Pattern 4: Batch Scheduling

Schedule multiple reminders efficiently.

**Use Case:** Import tasks in bulk, schedule all reminders at once

**Implementation:**
```python
@router.post("/api/tasks/batch")
async def create_tasks_batch(tasks: List[TaskCreate]):
    created_tasks = []
    scheduled_jobs = []

    for task in tasks:
        # Create task
        new_task = await db.create_task(task)
        created_tasks.append(new_task)

        # Schedule reminder if needed
        if new_task.due_date:
            try:
                job = job_manager.schedule_task_reminder(
                    task_id=new_task.id,
                    user_id=new_task.user_id,
                    due_date=new_task.due_date
                )
                scheduled_jobs.append(job)
            except Exception as e:
                logger.error(f"Failed to schedule for task {new_task.id}: {e}")

    return {
        "tasks": created_tasks,
        "scheduled_reminders": len(scheduled_jobs)
    }
```

**Optimization:**
- Process in parallel if possible
- Continue on individual failures
- Report summary statistics

## Integration Patterns

### Pattern 5: Notification Integration

Send notifications when job fires.

**Use Case:** Notify user via email, push, or SMS when task is due

**Implementation:**
```python
async def process_task_reminder(task_id: int, user_id: str):
    """Process reminder and send notification."""
    # Fetch task details
    task = await db.get_task(task_id)

    # Fetch user preferences
    user = await db.get_user(user_id)

    # Send notification based on user preferences
    if user.email_notifications:
        await send_email(
            to=user.email,
            subject=f"Task Reminder: {task.title}",
            body=f"Your task '{task.title}' is due now!"
        )

    if user.push_notifications:
        await send_push_notification(
            user_id=user_id,
            title="Task Reminder",
            body=f"{task.title} is due",
            data={"task_id": task_id}
        )

    # Log notification
    await db.create_notification_log(
        user_id=user_id,
        task_id=task_id,
        sent_at=datetime.now()
    )
```

**Channels:**
- Email (SendGrid, AWS SES)
- Push notifications (Firebase, OneSignal)
- SMS (Twilio, AWS SNS)
- In-app notifications (WebSocket, SSE)

### Pattern 6: Webhook Integration

Trigger external systems when reminder fires.

**Use Case:** Integrate with third-party task management tools

**Implementation:**
```python
async def process_task_reminder(task_id: int, user_id: str):
    task = await db.get_task(task_id)
    user = await db.get_user(user_id)

    # Trigger webhook if configured
    if user.webhook_url:
        await trigger_webhook(
            url=user.webhook_url,
            payload={
                "event": "task_reminder",
                "task_id": task_id,
                "task_title": task.title,
                "due_date": task.due_date.isoformat(),
                "user_id": user_id
            }
        )
```

**Webhook Retry:**
```python
async def trigger_webhook(url: str, payload: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = await httpx.post(
                url,
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Webhook failed after {max_retries} attempts: {e}")
                return False
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Pattern 7: Event Publishing

Publish events for event-driven architecture.

**Use Case:** Notify other microservices when reminder fires

**Implementation:**
```python
from dapr.clients import DaprClient

async def process_task_reminder(task_id: int, user_id: str):
    task = await db.get_task(task_id)

    # Publish event via Dapr pub/sub
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="task-reminders",
            data=json.dumps({
                "task_id": task_id,
                "user_id": user_id,
                "task_title": task.title,
                "due_date": task.due_date.isoformat()
            })
        )

    logger.info(f"Published reminder event for task {task_id}")
```

**Subscribers:**
- Notification service
- Analytics service
- Audit logging service

## Error Handling Patterns

### Pattern 8: Graceful Degradation

Continue task operations even if scheduling fails.

**Use Case:** Don't block task creation if reminder scheduling fails

**Implementation:**
```python
@router.post("/api/tasks")
async def create_task(task: TaskCreate):
    # Create task (critical operation)
    new_task = await db.create_task(task)

    # Schedule reminder (non-critical, best-effort)
    if new_task.due_date:
        try:
            job_manager.schedule_task_reminder(
                task_id=new_task.id,
                user_id=new_task.user_id,
                due_date=new_task.due_date
            )
        except Exception as e:
            # Log error but don't fail request
            logger.error(f"Failed to schedule reminder: {e}")
            # Optionally queue for retry
            await retry_queue.enqueue("schedule_reminder", new_task)

    return new_task
```

**Benefits:**
- Task creation always succeeds
- Reminder scheduling is best-effort
- Retry mechanism for failures

### Pattern 9: Dead Letter Queue

Handle failed job callbacks.

**Use Case:** Job fires but callback fails, need to retry or log

**Implementation:**
```python
@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    body = await request.json()

    try:
        await process_task_reminder(
            body["data"]["task_id"],
            body["data"]["user_id"]
        )
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Job callback failed: {e}")

        # Send to dead letter queue
        await dlq.enqueue({
            "job_name": body["job_name"],
            "data": body["data"],
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

        # Return 500 to trigger Dapr retry
        raise HTTPException(status_code=500, detail=str(e))
```

**DLQ Processing:**
```python
async def process_dlq():
    """Retry failed job callbacks."""
    while True:
        item = await dlq.dequeue()

        try:
            await process_task_reminder(
                item["data"]["task_id"],
                item["data"]["user_id"]
            )
            logger.info(f"Successfully retried job {item['job_name']}")

        except Exception as e:
            logger.error(f"DLQ retry failed: {e}")
            # Re-queue or send alert
```

## Performance Patterns

### Pattern 10: Lazy Loading

Load task details only when reminder fires.

**Use Case:** Avoid storing full task data in job payload

**Implementation:**
```python
# When scheduling - store only IDs
job_manager.schedule_task_reminder(
    task_id=123,
    user_id="user-xyz",
    due_date=due_date
)

# When callback fires - fetch fresh data
@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    body = await request.json()
    task_id = body["data"]["task_id"]

    # Fetch current task state
    task = await db.get_task(task_id)

    # Task might have been updated since scheduling
    if task.completed:
        logger.info(f"Task {task_id} already completed, skipping reminder")
        return {"status": "skipped"}

    # Send reminder with current data
    await send_notification(task)
```

**Benefits:**
- Always use current task data
- Handle task updates/deletions
- Smaller job payloads

### Pattern 11: Batch Cleanup

Periodically clean up expired jobs.

**Use Case:** Remove old one-time jobs to save storage

**Implementation:**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2)  # Run at 2 AM daily
async def cleanup_expired_jobs():
    """Delete jobs that have already fired."""
    all_jobs = job_manager.scheduler.list_jobs()

    deleted_count = 0
    for job in all_jobs.get("jobs", []):
        due_time = datetime.fromisoformat(job["dueTime"].rstrip("Z"))

        # Delete if one-time job and past due time
        if job["repeats"] == 1 and due_time < datetime.now():
            try:
                job_manager.scheduler.delete_job(job["name"])
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete job {job['name']}: {e}")

    logger.info(f"Cleaned up {deleted_count} expired jobs")

scheduler.start()
```

## Testing Patterns

### Pattern 12: Mock Dapr in Tests

Test job scheduling without running Dapr.

**Implementation:**
```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_scheduler():
    with patch('job_manager.DaprJobScheduler') as mock:
        yield mock

def test_create_task_schedules_reminder(mock_scheduler):
    # Arrange
    task = TaskCreate(
        title="Test Task",
        due_date=datetime(2025, 1, 15, 14, 30)
    )

    # Act
    response = client.post("/api/tasks", json=task.dict())

    # Assert
    assert response.status_code == 201
    mock_scheduler.schedule_job.assert_called_once_with(
        task_id=response.json()["id"],
        user_id=task.user_id,
        due_date=task.due_date
    )
```

### Pattern 13: Integration Tests

Test full flow with test Dapr instance.

**Implementation:**
```python
import pytest
import asyncio

@pytest.mark.integration
async def test_reminder_e2e():
    # Schedule job for 5 seconds from now
    due_date = datetime.now() + timedelta(seconds=5)

    task = await create_task(
        title="Test Reminder",
        due_date=due_date
    )

    # Wait for job to fire
    await asyncio.sleep(6)

    # Verify notification was sent
    notifications = await get_notifications(task.user_id)
    assert len(notifications) == 1
    assert notifications[0]["task_id"] == task.id
```

### Pattern 14: Time Travel Testing

Test scheduling logic without waiting.

**Implementation:**
```python
from freezegun import freeze_time

@freeze_time("2025-01-15 14:00:00")
def test_schedule_reminder():
    # Schedule for 30 minutes from now
    due_date = datetime(2025, 1, 15, 14, 30)

    job = job_manager.schedule_task_reminder(
        task_id=123,
        user_id="user-xyz",
        due_date=due_date
    )

    assert job["scheduled_for"] == "2025-01-15T14:30:00"

    # Fast forward to due time
    with freeze_time("2025-01-15 14:30:00"):
        # Simulate callback
        response = client.post("/api/jobs/trigger", json={
            "job_name": job["job_name"],
            "data": {"task_id": 123, "user_id": "user-xyz"}
        })

        assert response.status_code == 200
```

## Summary

**Task Lifecycle:**
1. Create → Schedule reminder
2. Update → Reschedule reminder
3. Delete → Cancel reminder
4. Due time → Fire reminder → Send notification

**Key Principles:**
- Always use exact datetimes (not cron patterns)
- Handle edge cases (task updates, deletions)
- Implement idempotent callbacks
- Graceful degradation on failures
- Cleanup expired jobs periodically
