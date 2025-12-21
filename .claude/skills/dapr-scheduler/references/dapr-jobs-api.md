# Dapr Jobs API Reference

Complete reference for Dapr Jobs API for exact-time scheduling in Phase V.

## Table of Contents
- API Overview
- Job Scheduling
- Job Management
- Callback Handling
- Best Practices
- Troubleshooting

## API Overview

### What is Dapr Jobs API?

Dapr Jobs API provides exact-time job scheduling capabilities, replacing older Cron bindings with more precise and flexible scheduling.

**Key Features:**
- Exact datetime scheduling (not just cron patterns)
- One-time and recurring jobs
- Job persistence via state store
- Retry policies and error handling
- RESTful HTTP API

**Base URL:**
```
http://localhost:3500/v1.0/jobs
```

### Architecture

```
┌─────────────┐
│  FastAPI    │
│  Backend    │
└──────┬──────┘
       │ POST /v1.0/jobs/{job-name}
       ▼
┌─────────────┐
│    Dapr     │
│   Sidecar   │
└──────┬──────┘
       │ Persists job
       ▼
┌─────────────┐
│ State Store │
│   (Redis)   │
└─────────────┘

When job fires:
┌─────────────┐
│    Dapr     │
│   Sidecar   │
└──────┬──────┘
       │ POST /api/jobs/trigger
       ▼
┌─────────────┐
│  FastAPI    │
│  Callback   │
└─────────────┘
```

## Job Scheduling

### Create Job (POST /v1.0/jobs/{job-name})

Schedule a new job with exact datetime.

**Endpoint:**
```
POST http://localhost:3500/v1.0/jobs/{job-name}
```

**Request Body:**
```json
{
  "schedule": "",
  "repeats": 1,
  "dueTime": "2025-01-15T14:30:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user-xyz",
    "scheduled_at": "2025-01-14T10:00:00Z"
  }
}
```

**Fields:**
- `schedule` (string): Cron expression or empty for one-time jobs
- `repeats` (int): Number of times to repeat (1 = one-time)
- `dueTime` (string): ISO8601 datetime when job should fire
- `data` (object): Custom payload passed to callback

**Response:**
```json
{
  "status": "scheduled",
  "job_name": "task-reminder-123-user-xyz"
}
```

**Status Codes:**
- 200 OK - Job scheduled successfully
- 400 Bad Request - Invalid request format
- 409 Conflict - Job already exists
- 500 Internal Server Error - Dapr error

### One-Time Jobs

For exact-time task reminders:

```python
import requests
from datetime import datetime

job_name = "task-reminder-123-user-xyz"
due_date = datetime(2025, 1, 15, 14, 30, 0)

payload = {
    "schedule": "",  # Empty for one-time
    "repeats": 1,    # Fire once
    "dueTime": due_date.isoformat() + "Z",
    "data": {
        "task_id": 123,
        "user_id": "user-xyz"
    }
}

response = requests.post(
    f"http://localhost:3500/v1.0/jobs/{job_name}",
    json=payload
)
```

### Recurring Jobs

For periodic reminders (optional):

```json
{
  "schedule": "0 9 * * MON-FRI",  // Every weekday at 9 AM
  "repeats": 0,                    // Infinite repeats
  "dueTime": "2025-01-15T09:00:00Z",
  "data": {
    "reminder_type": "daily_standup"
  }
}
```

**Cron Expression Format:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

## Job Management

### List Jobs (GET /v1.0/jobs)

Retrieve all scheduled jobs.

**Endpoint:**
```
GET http://localhost:3500/v1.0/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "name": "task-reminder-123-user-xyz",
      "schedule": "",
      "repeats": 1,
      "dueTime": "2025-01-15T14:30:00Z",
      "data": {
        "task_id": 123,
        "user_id": "user-xyz"
      },
      "status": "scheduled"
    }
  ]
}
```

### Get Job (GET /v1.0/jobs/{job-name})

Retrieve specific job details.

**Endpoint:**
```
GET http://localhost:3500/v1.0/jobs/{job-name}
```

**Response:**
```json
{
  "name": "task-reminder-123-user-xyz",
  "schedule": "",
  "repeats": 1,
  "dueTime": "2025-01-15T14:30:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user-xyz"
  },
  "status": "scheduled"
}
```

**Status Codes:**
- 200 OK - Job found
- 404 Not Found - Job doesn't exist

### Delete Job (DELETE /v1.0/jobs/{job-name})

Cancel a scheduled job.

**Endpoint:**
```
DELETE http://localhost:3500/v1.0/jobs/{job-name}
```

**Response:**
```json
{
  "status": "deleted"
}
```

**Status Codes:**
- 200 OK - Job deleted successfully
- 404 Not Found - Job doesn't exist

## Callback Handling

### Job Trigger Callback

When a job fires, Dapr POSTs to your callback endpoint.

**Dapr Configuration:**
Configure callback URL in component metadata or via app annotation.

**Callback Request:**
```http
POST /api/jobs/trigger
Content-Type: application/json

{
  "job_name": "task-reminder-123-user-xyz",
  "data": {
    "task_id": 123,
    "user_id": "user-xyz",
    "scheduled_at": "2025-01-14T10:00:00Z"
  },
  "scheduled_time": "2025-01-15T14:30:00Z",
  "actual_time": "2025-01-15T14:30:02Z"
}
```

**Expected Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "message": "Reminder processed"
}
```

**Retry Behavior:**
- Non-2xx response triggers retry
- Retry policy defined in component metadata
- Max retries and retry interval configurable

### Callback Implementation

```python
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    body = await request.json()

    job_name = body["job_name"]
    task_id = body["data"]["task_id"]
    user_id = body["data"]["user_id"]

    # Process reminder
    await send_notification(task_id, user_id)

    return {"status": "success"}
```

## Best Practices

### Job Naming Convention

Use descriptive, unique job names:

```
{resource}-{action}-{id}-{user}

Examples:
- task-reminder-123-user-xyz
- report-generate-daily-user-abc
- backup-database-weekly-system
```

### Idempotency

Ensure callbacks are idempotent:

```python
processed_jobs = set()  # Use Redis in production

@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    body = await request.json()
    job_name = body["job_name"]

    if job_name in processed_jobs:
        return {"status": "already_processed"}

    # Process job
    await process_reminder(body["data"])

    processed_jobs.add(job_name)
    return {"status": "success"}
```

### Error Handling

Handle errors gracefully:

```python
@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    try:
        body = await request.json()
        await process_job(body)
        return {"status": "success"}

    except ValidationError as e:
        # Non-retryable error
        logger.error(f"Invalid payload: {e}")
        return {"status": "failed", "error": str(e)}

    except TemporaryError as e:
        # Retryable error
        logger.warning(f"Temporary failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### State Store Configuration

Use persistent state store for production:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-cluster.svc.cluster.local:6379"
    - name: enableTTL
      value: "true"
    - name: ttlInSeconds
      value: "86400"  # 24 hours
```

### Job Cleanup

Implement cleanup for old jobs:

```python
async def cleanup_expired_jobs():
    """Delete jobs that have already fired."""
    all_jobs = scheduler.list_jobs()

    for job in all_jobs["jobs"]:
        due_time = datetime.fromisoformat(job["dueTime"])

        if due_time < datetime.now() and job["repeats"] == 1:
            scheduler.delete_job(job["name"])
```

## Troubleshooting

### Job Not Firing

**Symptoms:** Job scheduled but callback never invoked

**Checks:**
1. Verify Dapr sidecar is running: `dapr list`
2. Check component configuration: `kubectl get components`
3. Verify callback endpoint is accessible from Dapr sidecar
4. Check Dapr logs: `kubectl logs <pod> -c daprd`

**Solution:**
```bash
# Test callback endpoint directly
curl -X POST http://localhost:8000/api/jobs/trigger \
  -H "Content-Type: application/json" \
  -d '{"job_name": "test", "data": {}}'
```

### Job Already Exists (409 Conflict)

**Symptoms:** 409 error when creating job

**Cause:** Job with same name already scheduled

**Solution:**
```python
# Delete existing job first
try:
    scheduler.delete_job(job_name)
except:
    pass

# Then create new job
scheduler.schedule_job(...)
```

### State Store Connection Failed

**Symptoms:** Jobs not persisting, lost on restart

**Checks:**
1. Verify Redis is running
2. Check Redis password in secret
3. Test Redis connection: `redis-cli -h <host> -a <password> ping`

**Solution:**
Update component with correct Redis credentials

### Callback Timeout

**Symptoms:** Jobs fail with timeout errors

**Cause:** Callback processing takes too long

**Solution:**
```yaml
# Increase timeout in component
metadata:
  - name: jobTimeout
    value: "10m"  # Increase from default 5m
```

Or process asynchronously:

```python
@router.post("/api/jobs/trigger")
async def job_callback(request: Request):
    body = await request.json()

    # Queue for async processing
    await task_queue.enqueue(process_reminder, body["data"])

    # Return immediately
    return {"status": "queued"}
```

## Migration from Cron Bindings

### Old Approach (Cron)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "0 9 * * *"  # Fixed schedule only
```

### New Approach (Jobs API)

```python
# Dynamic, exact-time scheduling
scheduler.schedule_job(
    task_id=123,
    user_id="user-xyz",
    due_date=datetime(2025, 1, 15, 14, 30, 0)  # Exact time
)
```

**Benefits:**
- Exact datetime scheduling (not just cron patterns)
- Dynamic job creation via API
- Job persistence and management
- Better error handling and retries
