---
name: "dapr-event-flow"
description: "Automates Dapr event-driven architecture: configures pub/sub components, implements event publishers, creates subscribers, and tests event flow. Use for Phase V microservices communication."
version: "1.0.0"
---

# Dapr Event Flow Skill

## When to Use
- User asks to "publish events" or "subscribe to events"
- User says "Set up Dapr pub/sub" or "Configure Kafka/Redpanda"
- Building microservices that need to communicate
- Creating notification or recurring task services
- Testing event-driven workflows
- Migrating from local Kafka to Redpanda Cloud

## Context
This skill handles event-driven architecture following:
- **Service Mesh**: Dapr 1.13+ (localhost:3500 sidecar)
- **Event Streaming**:
  - **Local**: Kafka/Redpanda (docker-compose)
  - **Production**: Redpanda Cloud (SASL/SSL)
- **State Store**:
  - **Local**: Redis
  - **Production**: DigitalOcean Managed Redis (Valkey)
- **Protocol**: HTTP (Dapr API over localhost)
- **Event Format**: CloudEvents specification

## Workflow
1. **Define Event Schema**: Create event type and payload structure
2. **Configure Dapr Components**: Set up pub/sub and state store YAMLs
3. **Implement Publisher**: Add event publishing to backend endpoints
4. **Create Subscriber**: Build microservice with event handler
5. **Test Locally**: Verify end-to-end event flow on Minikube
6. **Deploy to Production**: Configure cloud components (Redpanda Cloud, DO Redis)
7. **Monitor**: Check Dapr sidecar logs and event metrics

## Output Formats

### 1. Event Schema Definition

**Event Types** (`backend/app/schemas/events.py`):
```python
"""
Event schemas for Dapr pub/sub.

All events follow CloudEvents specification.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreatedEvent(BaseModel):
    """Event published when a task is created."""
    task_id: int
    user_id: str
    title: str
    priority_id: Optional[int] = None
    due_date: Optional[str] = None  # ISO 8601 datetime
    created_at: str


class TaskUpdatedEvent(BaseModel):
    """Event published when a task is updated."""
    task_id: int
    user_id: str
    title: str
    completed: bool
    priority_id: Optional[int] = None
    updated_at: str


class TaskCompletedEvent(BaseModel):
    """Event published when a task is marked complete."""
    task_id: int
    user_id: str
    completed: bool
    completed_at: str


class TaskDeletedEvent(BaseModel):
    """Event published when a task is deleted."""
    task_id: int
    user_id: str
    deleted_at: str
```

### 2. Dapr Client Wrapper

**Publisher Utility** (`backend/app/utils/dapr_client.py`):
```python
"""
Dapr client wrapper for event publishing.

Uses httpx to publish events to Dapr sidecar.
"""

import httpx
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"
TOPIC_PREFIX = "task-events"


async def publish_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Publish event to Dapr pub/sub.

    Args:
        event_type: Event type (e.g., 'task_created', 'task_updated')
        data: Event payload dictionary

    Raises:
        httpx.HTTPError: If publishing fails
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_PREFIX}.{event_type}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=5.0)
            response.raise_for_status()
            logger.info(f"Published event: {event_type} - {data}")
    except httpx.HTTPError as e:
        logger.error(f"Failed to publish event {event_type}: {str(e)}")
        raise


async def save_state(key: str, value: Dict[str, Any]) -> None:
    """
    Save state to Dapr state store.

    Args:
        key: State key
        value: State value (dict)
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore"
    payload = [{
        "key": key,
        "value": value
    }]

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=5.0)
        response.raise_for_status()


async def get_state(key: str) -> Dict[str, Any]:
    """
    Get state from Dapr state store.

    Args:
        key: State key

    Returns:
        State value dict
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore/{key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        return response.json()
```

### 3. Event Publishing in Backend

**Update Task Endpoint** (`backend/app/routers/tasks.py`):
```python
"""
Task API routes with event publishing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.dapr_client import publish_event
from app.schemas.events import TaskCreatedEvent


@router.post("/{user_id}/tasks", status_code=201)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> TaskRead:
    """
    Create a new task and publish task_created event.
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Create task in database
    new_task = Task(user_id=current_user, **task_data.dict())
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    # Publish event (async, non-blocking)
    try:
        event = TaskCreatedEvent(
            task_id=new_task.id,
            user_id=str(new_task.user_id),
            title=new_task.title,
            priority_id=new_task.priority_id,
            due_date=new_task.due_date.isoformat() if new_task.due_date else None,
            created_at=new_task.created_at.isoformat()
        )
        await publish_event("task_created", event.dict())
    except Exception as e:
        # Log error but don't fail request
        logger.error(f"Failed to publish task_created event: {str(e)}")

    return TaskRead.from_orm(new_task)
```

### 4. Event Subscriber Microservice

**Notification Service** (`notification-service/app/main.py`):
```python
"""
Notification microservice that subscribes to task events.

Listens for task_created, task_updated, task_completed events.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")


class CloudEvent(BaseModel):
    """
    Dapr CloudEvent format.

    Dapr wraps all events in CloudEvents specification.
    """
    id: str
    source: str
    type: str
    datacontenttype: str
    data: Dict[str, Any]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns list of topics to subscribe to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events.task_created",
            "route": "/events/task-created"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events.task_updated",
            "route": "/events/task-updated"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events.task_completed",
            "route": "/events/task-completed"
        }
    ]


@app.post("/events/task-created")
async def handle_task_created(event: CloudEvent):
    """
    Handle task_created event.

    Send notification to user about new task.
    """
    task_data = event.data
    logger.info(f"📨 NEW TASK: {task_data['title']} (User: {task_data['user_id']})")

    # TODO: Send email notification
    # TODO: Send push notification
    # TODO: Update notification state in Dapr state store

    return {"status": "SUCCESS"}


@app.post("/events/task-updated")
async def handle_task_updated(event: CloudEvent):
    """Handle task_updated event."""
    task_data = event.data
    logger.info(f"📝 TASK UPDATED: ID {task_data['task_id']}")

    # TODO: Update notification status
    return {"status": "SUCCESS"}


@app.post("/events/task-completed")
async def handle_task_completed(event: CloudEvent):
    """Handle task_completed event."""
    task_data = event.data
    logger.info(f"✅ TASK COMPLETED: ID {task_data['task_id']}")

    # TODO: Send completion notification
    return {"status": "SUCCESS"}
```

### 5. Dapr Component Configurations

**Kafka Pub/Sub (Local)** (`infrastructure/dapr/components/kafka-pubsub.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda:9092"
  - name: clientID
    value: "todo-backend"
  - name: consumerGroup
    value: "notification-service"
  - name: authType
    value: "none"
```

**Redpanda Cloud Pub/Sub (Production)** (`infrastructure/dapr/components/kafka-pubsub-prod.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "seed-<cluster-id>.seed.cloud.redpanda.com:9092"
  - name: authType
    value: "sasl"
  - name: saslUsername
    secretKeyRef:
      name: redpanda-credentials
      key: username
  - name: saslPassword
    secretKeyRef:
      name: redpanda-credentials
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-256"
  - name: enableTLS
    value: "true"
```

**Redis State Store (Local)** (`infrastructure/dapr/components/statestore.yaml`):
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
    value: "redis:6379"
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

**DigitalOcean Redis (Production)** (`infrastructure/dapr/components/statestore-prod.yaml`):
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
    secretKeyRef:
      name: redis-credentials
      key: host
  - name: redisPassword
    secretKeyRef:
      name: redis-credentials
      key: password
  - name: enableTLS
    value: "true"
```

### 6. Kubernetes Deployment with Dapr

**Backend with Dapr Sidecar** (`infrastructure/kubernetes/backend-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        # Dapr sidecar configuration
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/sidecar-cpu-limit: "200m"
        dapr.io/sidecar-memory-limit: "256Mi"
    spec:
      containers:
      - name: backend
        image: registry.digitalocean.com/todo-chatbot-reg/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: DATABASE_URL
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

**Notification Service with Dapr** (`infrastructure/kubernetes/notification-service-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  labels:
    app: notification-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: notification-service
        image: registry.digitalocean.com/todo-chatbot-reg/notification-service:latest
        ports:
        - containerPort: 8001
```

## Testing Event Flow

### 1. Publish Event via API
```bash
# Create a task (triggers task_created event)
curl -X POST "http://174.138.120.69/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event Flow",
    "priority_id": 1
  }'
```

### 2. Check Backend Logs
```bash
# Check if event was published
kubectl logs deployment/backend -c backend | grep "Published event"
```

### 3. Check Dapr Sidecar Logs
```bash
# Check Dapr pub/sub activity
kubectl logs deployment/backend -c daprd | grep "pubsub"
```

### 4. Check Subscriber Logs
```bash
# Check if notification service received event
kubectl logs deployment/notification-service -c notification-service | grep "NEW TASK"
```

### 5. Verify Redpanda Topics
```bash
# List topics
kubectl exec -it redpanda-0 -- rpk topic list

# Consume from topic
kubectl exec -it redpanda-0 -- rpk topic consume task-events.task_created
```

## Troubleshooting

### Events Not Being Published

**Check Dapr sidecar is running**:
```bash
kubectl get pods -l app=backend
# Should show 2/2 (backend + daprd)
```

**Check Dapr component is loaded**:
```bash
kubectl logs <backend-pod> -c daprd | grep "component loaded"
```

**Test Dapr API directly**:
```bash
kubectl exec <backend-pod> -c backend -- curl http://localhost:3500/v1.0/publish/kafka-pubsub/task-events.test -X POST -d '{"test":"data"}'
```

### Events Not Being Consumed

**Check subscription endpoint**:
```bash
kubectl exec <notification-pod> -c notification-service -- \
  curl http://localhost:8001/dapr/subscribe
```

**Check Dapr registered subscriptions**:
```bash
kubectl logs <notification-pod> -c daprd | grep "subscription"
```

**Check consumer group offset**:
```bash
kubectl exec -it redpanda-0 -- rpk group describe notification-service
```

### Dapr Sidecar Not Injected

**Verify deployment annotations**:
```bash
kubectl get deployment backend -o yaml | grep dapr.io

# Should have:
# dapr.io/enabled: "true"
# dapr.io/app-id: "todo-backend"
# dapr.io/app-port: "8000"
```

## Event Flow Architecture

```
┌─────────────────┐
│  POST /tasks    │  User creates task
│  (Backend API)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to DB     │  1. Persist to PostgreSQL
│  (PostgreSQL)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Dapr Publish   │─────►│  Dapr Sidecar   │  2. Publish event
│  (localhost:    │      │  (daprd)        │
│   3500)         │      └────────┬────────┘
└─────────────────┘               │
                                  ▼
                         ┌─────────────────┐
                         │ Kafka/Redpanda  │  3. Event streaming
                         │  (task-events)  │
                         └────────┬────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │ Notification │ │  Recurring   │ │  Analytics   │  4. Subscribers
         │   Service    │ │    Task      │ │   Service    │     handle events
         │              │ │   Service    │ │              │
         └──────────────┘ └──────────────┘ └──────────────┘
```

## Example Usage

**Scenario**: Set up event publishing when tasks are created

**Steps**:
1. Define `TaskCreatedEvent` schema in `backend/app/schemas/events.py`
2. Create Dapr client wrapper in `backend/app/utils/dapr_client.py`
3. Update `create_task` endpoint to call `publish_event("task_created", data)`
4. Create `kafka-pubsub.yaml` component configuration
5. Apply component: `kubectl apply -f infrastructure/dapr/components/kafka-pubsub.yaml`
6. Restart backend pod to load Dapr component
7. Test: Create task via API, check Dapr logs for "Published event"
8. Create notification service to subscribe to `task-events.task_created`
9. Deploy notification service with Dapr annotations
10. Verify: Create task, check notification service logs for event receipt

## Quality Checklist
Before finalizing:
- [ ] Event schemas defined with Pydantic models
- [ ] Dapr client wrapper handles errors gracefully
- [ ] Event publishing is async and doesn't block API response
- [ ] CloudEvents format used for subscribers
- [ ] Dapr component YAMLs configured for local and production
- [ ] Kubernetes secrets created for Redpanda Cloud credentials
- [ ] Dapr sidecar annotations present on all deployments
- [ ] Subscription endpoint returns correct topic list
- [ ] Event handlers return {"status": "SUCCESS"}
- [ ] Logging includes event type and key data for debugging
- [ ] Testing verified end-to-end event flow
- [ ] Monitoring set up for event delivery metrics
