---
name: dapr-scheduler
description: Implement exact-time task reminder scheduling using Dapr Jobs API for Phase V event-driven architecture. Use when: (1) Scheduling task reminders for specific due dates, (2) Implementing precise job scheduling (not cron patterns), (3) Replacing older Cron bindings with modern Jobs API, (4) Integrating job scheduling with FastAPI backend, (5) Managing scheduled jobs (create, list, cancel, update), (6) Handling job callbacks when reminders fire, or (7) Building event-driven reminder systems with Dapr. Provides production-ready Python code, Dapr component configuration, FastAPI endpoints, and scheduling patterns.
---

# Dapr Scheduler

Exact-time task reminder scheduling using Dapr Jobs API for Phase V event-driven architecture.

## Overview

This skill provides complete Dapr Jobs API integration for scheduling precise task reminders. Replaces older Cron bindings with modern job scheduling that supports exact datetimes (not just cron patterns).

**Key Features:**
- Exact datetime scheduling via POST /v1.0/jobs
- One-time job scheduling for task due dates
- Complete job lifecycle management (create, list, cancel, update)
- FastAPI callback endpoint for job execution
- Job state persistence via Redis
- Idempotent callback handling
- Production-ready error handling

**Phase V Requirement:** Must use Dapr Jobs API for all reminder scheduling.

## Quick Start

### 1. Deploy Dapr Component

```bash
# Copy component configuration
kubectl apply -f assets/dapr-components/job-scheduler.yaml
```

### 2. Integrate with FastAPI

```python
# Add to your main.py
from assets.fastapi_endpoints.job_routes import router as job_router
from assets.fastapi_endpoints.job_callback import router as callback_router

app.include_router(job_router)
app.include_router(callback_router)
```

### 3. Schedule a Reminder

```python
from scripts.job_manager import JobManager

job_manager = JobManager()

# Schedule reminder for task due date
job_manager.schedule_task_reminder(
    task_id=123,
    user_id="user-xyz",
    due_date=datetime(2025, 1, 15, 14, 30, 0)
)
```

## Core Workflows

### Workflow 1: Task Creation with Reminder

When user creates task with due date:

```python
@router.post("/api/tasks")
async def create_task(task: TaskCreate):
    # Create task in database
    new_task = await db.create_task(task)

    # Schedule reminder if due_date set
    if new_task.due_date:
        job_manager.schedule_task_reminder(
            task_id=new_task.id,
            user_id=new_task.user_id,
            due_date=new_task.due_date
        )

    return new_task
```

### Workflow 2: Task Update with Reschedule

When user changes task due date:

```python
@router.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    existing = await db.get_task(task_id)
    updated = await db.update_task(task_id, task)

    # Handle due date changes
    if task.due_date and task.due_date != existing.due_date:
        job_manager.reschedule_task_reminder(
            task_id=task_id,
            user_id=updated.user_id,
            new_due_date=task.due_date
        )

    return updated
```

### Workflow 3: Task Deletion with Cancel

When user deletes task:

```python
@router.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, user_id: str):
    await db.delete_task(task_id)

    # Cancel reminder
    job_manager.cancel_task_reminder(task_id, user_id)

    return {"message": "Task deleted"}
```

### Workflow 4: Reminder Callback

When job fires at due time:

```python
@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    body = await request.json()

    task_id = body["data"]["task_id"]
    user_id = body["data"]["user_id"]

    # Fetch current task state
    task = await db.get_task(task_id)

    # Send notification
    await send_notification(
        user_id=user_id,
        title=f"Task Reminder: {task.title}",
        message=f"Your task '{task.title}' is due now!"
    )

    return {"status": "success"}
```

## Bundled Resources

### Scripts

**`scripts/schedule_job.py`**
- `DaprJobScheduler` class wrapping Dapr Jobs API
- Methods: `schedule_job()`, `list_jobs()`, `get_job()`, `delete_job()`, `update_job()`
- Uses: Direct job scheduling via HTTP POST /v1.0/jobs

**`scripts/job_manager.py`**
- `JobManager` high-level utilities for FastAPI integration
- Methods: `schedule_task_reminder()`, `cancel_task_reminder()`, `reschedule_task_reminder()`
- Uses: Simplified task reminder management

### Assets

**`assets/dapr-components/job-scheduler.yaml`**
- Complete Dapr component configuration
- Includes job scheduler, state store (Redis), and secrets
- Ready for kubectl apply

**`assets/fastapi-endpoints/job_callback.py`**
- FastAPI callback endpoint `/api/jobs/trigger`
- Handles job execution events from Dapr
- Includes idempotency support

**`assets/fastapi-endpoints/job_routes.py`**
- FastAPI job management routes
- Endpoints: `/api/jobs/schedule`, `/api/jobs/reschedule`, `/api/jobs/tasks/{id}/reminder`
- Complete CRUD for scheduled jobs

### References

**`references/dapr-jobs-api.md`**
- Complete Dapr Jobs API reference
- API endpoints, request/response formats
- Troubleshooting guide
- Migration from Cron bindings

**`references/scheduling-patterns.md`**
- Common scheduling patterns
- Integration patterns (notifications, webhooks, events)
- Error handling patterns
- Testing patterns

## Usage Patterns

### Pattern: Schedule on Task Creation

```python
from scripts.job_manager import JobManager

job_manager = JobManager()

@router.post("/api/tasks")
async def create_task(task: TaskCreate):
    new_task = await db.create_task(task)

    if new_task.due_date:
        job_manager.schedule_task_reminder(
            task_id=new_task.id,
            user_id=new_task.user_id,
            due_date=new_task.due_date
        )

    return new_task
```

### Pattern: Graceful Degradation

Don't block task creation if scheduling fails:

```python
if new_task.due_date:
    try:
        job_manager.schedule_task_reminder(...)
    except Exception as e:
        logger.error(f"Failed to schedule reminder: {e}")
        # Task creation still succeeds
```

### Pattern: Notification Integration

```python
async def process_task_reminder(task_id: int, user_id: str):
    task = await db.get_task(task_id)
    user = await db.get_user(user_id)

    # Send email
    if user.email_notifications:
        await send_email(
            to=user.email,
            subject=f"Task Reminder: {task.title}",
            body=f"Your task '{task.title}' is due now!"
        )

    # Send push notification
    if user.push_notifications:
        await send_push(
            user_id=user_id,
            title="Task Reminder",
            body=f"{task.title} is due"
        )
```

## Configuration

### Environment Variables

```env
# Dapr sidecar configuration
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# Redis state store
REDIS_HOST=localhost:6379
REDIS_PASSWORD=your-password

# Job configuration
JOB_TIMEOUT=5m
MAX_CONCURRENT_JOBS=10
```

### Dapr Component Metadata

```yaml
metadata:
  - name: stateStore
    value: "statestore"

  - name: jobTimeout
    value: "5m"

  - name: maxConcurrentJobs
    value: "10"

  - name: retryPolicy
    value: |
      {
        "maxRetries": 3,
        "retryInterval": "1m"
      }
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_scheduler():
    with patch('job_manager.DaprJobScheduler') as mock:
        yield mock

def test_schedule_reminder(mock_scheduler):
    task = TaskCreate(
        title="Test Task",
        due_date=datetime(2025, 1, 15, 14, 30)
    )

    response = client.post("/api/tasks", json=task.dict())

    assert response.status_code == 201
    mock_scheduler.schedule_job.assert_called_once()
```

### Integration Tests

```python
@pytest.mark.integration
async def test_reminder_e2e():
    # Schedule job for 5 seconds from now
    due_date = datetime.now() + timedelta(seconds=5)

    task = await create_task(title="Test", due_date=due_date)

    # Wait for job to fire
    await asyncio.sleep(6)

    # Verify notification sent
    notifications = await get_notifications(task.user_id)
    assert len(notifications) == 1
```

## Troubleshooting

### Job Not Firing

**Symptoms:** Job scheduled but callback never invoked

**Checks:**
1. Dapr sidecar running: `dapr list`
2. Component configuration: `kubectl get components`
3. Callback endpoint accessible from Dapr
4. Dapr logs: `kubectl logs <pod> -c daprd`

**Solution:**
```bash
# Test callback directly
curl -X POST http://localhost:8000/api/jobs/trigger \
  -H "Content-Type: application/json" \
  -d '{"job_name": "test", "data": {"task_id": 123, "user_id": "xyz"}}'
```

### State Store Connection Failed

**Symptoms:** Jobs not persisting

**Checks:**
1. Redis running: `redis-cli ping`
2. Check Redis password in secret
3. Verify component configuration

**Solution:** Update Redis credentials in `job-scheduler.yaml`

## Best Practices

1. **Use exact datetimes** - Not cron patterns for task reminders
2. **Implement idempotency** - Handle duplicate callbacks gracefully
3. **Graceful degradation** - Don't block task creation on scheduling failure
4. **Cleanup expired jobs** - Periodically delete old one-time jobs
5. **Monitor job health** - Track scheduling success/failure rates
6. **Test thoroughly** - Mock Dapr in unit tests, use real Dapr in integration tests

## Advanced Features

### Batch Scheduling

```python
@router.post("/api/tasks/batch")
async def create_tasks_batch(tasks: List[TaskCreate]):
    scheduled_count = 0

    for task in tasks:
        new_task = await db.create_task(task)

        if new_task.due_date:
            try:
                job_manager.schedule_task_reminder(
                    task_id=new_task.id,
                    user_id=new_task.user_id,
                    due_date=new_task.due_date
                )
                scheduled_count += 1
            except Exception as e:
                logger.error(f"Failed to schedule: {e}")

    return {"scheduled_reminders": scheduled_count}
```

### Webhook Integration

```python
async def process_task_reminder(task_id: int, user_id: str):
    user = await db.get_user(user_id)

    if user.webhook_url:
        await trigger_webhook(
            url=user.webhook_url,
            payload={
                "event": "task_reminder",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            }
        )
```

### Event Publishing

```python
from dapr.clients import DaprClient

async def process_task_reminder(task_id: int, user_id: str):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="task-reminders",
            data=json.dumps({
                "task_id": task_id,
                "user_id": user_id
            })
        )
```

## Migration from Cron Bindings

### Old Approach (Cron)

```yaml
# Fixed schedule only, not exact times
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  metadata:
    - name: schedule
      value: "0 9 * * *"  # Every day at 9 AM
```

### New Approach (Jobs API)

```python
# Exact datetime, dynamic scheduling
job_manager.schedule_task_reminder(
    task_id=123,
    user_id="user-xyz",
    due_date=datetime(2025, 1, 15, 14, 30, 0)  # Exact time
)
```

**Benefits:**
- Exact datetime scheduling (not limited to cron patterns)
- Dynamic job creation via API
- Job persistence and state management
- Better error handling and retries
- RESTful job management (list, get, delete)

## Reference Documentation

For detailed information:
- **API Reference**: See `references/dapr-jobs-api.md` for complete Dapr Jobs API documentation
- **Patterns**: See `references/scheduling-patterns.md` for common scheduling patterns and best practices

## Phase V Compliance

✅ **Jobs API First:** Always use Dapr Jobs API (not Cron bindings)
✅ **Exact-Time Scheduling:** Support precise due date reminders
✅ **FastAPI Integration:** Complete FastAPI endpoints for job management
✅ **State Persistence:** Jobs persist via Redis state store
✅ **Production-Ready:** Error handling, idempotency, graceful degradation
✅ **Event-Driven:** Integrates with Dapr pub/sub for notifications
✅ **Testing Support:** Mock and integration testing patterns included
