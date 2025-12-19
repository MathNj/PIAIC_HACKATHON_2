# Feature Specification: Event-Driven Architecture with Dapr

**Feature Branch**: `008-event-driven-dapr`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "Create a new spec file @specs/architecture/event-driven-dapr.md. This spec must define: 1. Pub/Sub: Define the kafka-pubsub component. Topics: task-events, reminders, task-updates. 2. State Store: Define statestore using Redis (local) or Neon (cloud) for conversation state. 3. Bindings: Define reminder-cron for triggering the reminder service every 5 minutes. 4. Service Invocation: Define how the Frontend calls the Backend via Dapr Sidecar. 5. Event Schemas: Define the JSON structure for TaskEvent and ReminderEvent. Explicitly state that we will use httpx in Python to communicate with the Dapr sidecar (localhost:3500) rather than using native Kafka libraries."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event-Driven Task Notifications (Priority: P1)

When a user creates, updates, or completes a task, the system asynchronously publishes events to notify other services (notification service, analytics) without blocking the user's request.

**Why this priority**: Core decoupling mechanism - enables microservices architecture and prevents cascading failures. Task operations remain fast even when notification services are down.

**Independent Test**: Can be fully tested by creating a task and verifying that: (1) task is saved immediately (synchronous), (2) event is published to Kafka topic, (3) downstream services receive event asynchronously. Delivers immediate user feedback without waiting for notifications.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they create a new task, **Then** the task is saved to database AND a `task.created` event is published to `task-events` topic within 100ms
2. **Given** a task exists, **When** user updates the task status to "completed", **Then** the task is updated in database AND a `task.completed` event is published to `task-events` topic
3. **Given** the notification service is down, **When** a user creates a task, **Then** task creation succeeds immediately without errors

---

### User Story 2 - Distributed Conversation State Management (Priority: P1)

When a user interacts with the AI chat agent across multiple requests, the conversation history and context is stored in a distributed state store (Redis) accessible to all backend instances, enabling stateless backend pods and horizontal scaling.

**Why this priority**: Essential for Kubernetes deployment with multiple replicas. Without distributed state, users get inconsistent experiences when load balancer routes requests to different pods.

**Independent Test**: Can be tested by: (1) starting conversation in one backend pod, (2) forcing next request to different pod, (3) verifying conversation context is preserved. Delivers seamless user experience during scaling events.

**Acceptance Scenarios**:

1. **Given** a user starts a chat conversation, **When** the conversation state is saved, **Then** it is persisted to Redis via Dapr state store API (localhost:3500/v1.0/state/statestore)
2. **Given** conversation state exists in Redis, **When** the same user sends another message but routed to a different backend pod, **Then** the full conversation history is retrieved and context is preserved
3. **Given** Redis is temporarily unavailable, **When** user sends a message, **Then** the system gracefully degrades (uses in-memory fallback or returns error) without crashing

---

### User Story 3 - Scheduled Recurring Task Generation (Priority: P2)

Every 5 minutes, the system automatically triggers the Recurring Task Service via a cron binding to check for recurring task templates and generate new task instances based on recurrence patterns (daily, weekly, monthly).

**Why this priority**: Automates task creation for users with recurring responsibilities (daily standups, weekly reports). Less critical than core CRUD operations but key value-add feature.

**Independent Test**: Can be tested by: (1) creating recurring task template with "daily" pattern, (2) waiting for cron trigger (or manually invoking binding endpoint), (3) verifying new task instance is created. Delivers automation value independently.

**Acceptance Scenarios**:

1. **Given** a recurring task template exists with cron expression `*/5 * * * *`, **When** the cron binding triggers, **Then** the Recurring Task Service receives HTTP POST to `/dapr/cron/reminder-cron`
2. **Given** a recurring task is due, **When** the service processes it, **Then** a new task instance is created in the database AND the `next_occurrence` timestamp is updated
3. **Given** multiple recurring tasks are due, **When** cron triggers, **Then** all eligible tasks are processed in a single batch without duplicate instances

---

### User Story 4 - Dapr Service-to-Service Invocation (Priority: P2)

When the frontend needs to call backend APIs, it routes requests through the Dapr sidecar using service invocation, enabling built-in retries, timeouts, distributed tracing, and mTLS without application code changes.

**Why this priority**: Improves reliability and observability but not strictly required for MVP. Direct HTTP calls work but lack resilience patterns.

**Independent Test**: Can be tested by: (1) frontend making HTTP POST to `localhost:3500/v1.0/invoke/backend/method/api/tasks`, (2) verifying request is routed to backend pod, (3) checking distributed trace IDs in logs. Delivers improved reliability independently.

**Acceptance Scenarios**:

1. **Given** frontend needs to create a task, **When** it calls `POST localhost:3500/v1.0/invoke/backend/method/api/{user_id}/tasks`, **Then** Dapr routes request to any available backend pod with automatic retries
2. **Given** backend pod crashes mid-request, **When** frontend invokes via Dapr, **Then** Dapr automatically retries on another pod without frontend code changes
3. **Given** backend is slow to respond, **When** request exceeds 30s timeout, **Then** Dapr returns timeout error to frontend instead of hanging indefinitely

---

### User Story 5 - Reminder Notification Events (Priority: P3)

When a task's due date approaches (e.g., 1 hour before), the Recurring Task Service publishes a `reminder.due` event to the `reminders` topic, which the Notification Service consumes to send email/push notifications to the user.

**Why this priority**: Nice-to-have feature that enhances user experience but not critical for core functionality. Depends on Notification Service being implemented.

**Independent Test**: Can be tested by: (1) creating task with due date 1 hour from now, (2) waiting for recurring service to detect due task, (3) verifying `reminder.due` event is published, (4) notification service logs receipt. Delivers reminder value independently.

**Acceptance Scenarios**:

1. **Given** a task has `due_date` set to 1 hour from now, **When** the Recurring Task Service checks due tasks, **Then** a `reminder.due` event is published to `reminders` topic with task details
2. **Given** a reminder event is published, **When** Notification Service subscribes to `reminders` topic, **Then** it receives the event and sends email notification to task owner
3. **Given** a task is already completed, **When** reminder check runs, **Then** no reminder event is published for completed tasks

---

### Edge Cases

- **What happens when Kafka is unavailable?** Backend should continue accepting task CRUD operations but log warnings about event publishing failures. Use Dapr's outbox pattern for guaranteed delivery when Kafka recovers.
- **What happens when Redis is unavailable?** Conversation state API calls return 500 errors. Backend should have fallback to ephemeral in-memory storage or return user-friendly errors.
- **What happens when multiple instances process the same cron trigger?** Only one instance should process each recurring task. Use distributed locks via Redis or rely on database constraints (unique indexes on `task_id + occurrence_date`).
- **What happens when event schema changes?** Use versioned event schemas (e.g., `v1.task.created`) and maintain backward compatibility for 2 versions. Old services can ignore new fields.
- **What happens when Dapr sidecar crashes?** The application container loses access to Dapr APIs. Kubernetes should restart the sidecar automatically. Application should implement circuit breaker patterns for Dapr calls.

## Requirements *(mandatory)*

### Functional Requirements

#### Pub/Sub Component (Kafka)

- **FR-001**: System MUST provide a Dapr Pub/Sub component named `kafka-pubsub` using `pubsub.kafka` type
- **FR-002**: System MUST support three message topics: `task-events`, `reminders`, `task-updates`
- **FR-003**: System MUST connect to Kafka brokers at `kafka.default.svc.cluster.local:9092` (local Minikube) or `redpanda-cloud-endpoint:9092` (production)
- **FR-004**: System MUST use consumer group `todo-app-group` for all subscribers to enable horizontal scaling
- **FR-005**: Python services MUST publish events via HTTP POST to `localhost:3500/v1.0/publish/kafka-pubsub/{topic}` using `httpx` library (NOT native Kafka SDK)
- **FR-006**: Python services MUST subscribe to events via Dapr subscription endpoint `/dapr/subscribe` returning JSON array of subscriptions

#### State Store Component (Redis/Neon)

- **FR-007**: System MUST provide a Dapr State Store component named `statestore`
- **FR-008**: Local Minikube deployments MUST use `state.redis` type pointing to `redis-master.default.svc.cluster.local:6379`
- **FR-009**: Production DOKS deployments MUST use `state.postgresql` type pointing to Neon database connection string
- **FR-010**: System MUST store conversation state with keys in format `conversation:{user_id}:{session_id}`
- **FR-011**: Conversation state MUST include: `messages` (array), `context` (object), `created_at`, `updated_at` timestamps
- **FR-012**: Python services MUST access state via HTTP requests to `localhost:3500/v1.0/state/statestore` using `httpx` library (NOT native Redis/PostgreSQL SDK)
- **FR-013**: State operations MUST support GET, POST (upsert), DELETE methods

#### Cron Bindings Component

- **FR-014**: System MUST provide a Dapr Cron Binding named `reminder-cron`
- **FR-015**: Cron binding MUST trigger every 5 minutes using schedule `@every 5m` or cron expression `*/5 * * * *`
- **FR-016**: Cron binding MUST send HTTP POST to `/dapr/cron/reminder-cron` endpoint on Recurring Task Service
- **FR-017**: Recurring Task Service MUST process all due tasks and update `next_occurrence` timestamps in a single execution

#### Service Invocation

- **FR-018**: Frontend MUST invoke backend APIs via Dapr service invocation: `POST localhost:3500/v1.0/invoke/backend/method/{api-path}`
- **FR-019**: Backend Dapr app MUST have `dapr.io/app-id: backend` and `dapr.io/app-port: 8000` annotations
- **FR-020**: Frontend Dapr app MUST have `dapr.io/app-id: frontend` and `dapr.io/app-port: 3000` annotations
- **FR-021**: Service invocation MUST include automatic retries (3 attempts), circuit breaking (5 consecutive failures = open), and 30-second timeouts
- **FR-022**: Service invocation MUST propagate HTTP headers (Authorization, Content-Type, X-Request-ID) between services

#### Event Schemas

- **FR-023**: All events MUST include standard envelope fields: `event_id` (UUID), `event_type` (string), `timestamp` (ISO8601), `version` (semantic version string)
- **FR-024**: System MUST support `TaskEvent` schema with event types: `task.created`, `task.updated`, `task.completed`, `task.deleted`
- **FR-025**: System MUST support `ReminderEvent` schema with event types: `reminder.due`, `reminder.sent`, `reminder.failed`
- **FR-026**: Events MUST be published as JSON with `Content-Type: application/json` header
- **FR-027**: Event payloads MUST include full entity data (not just IDs) to reduce downstream service dependencies

### Key Entities

- **TaskEvent**: Represents state changes to tasks. Attributes: `event_id`, `event_type`, `timestamp`, `version`, `data` (contains full Task object: `id`, `user_id`, `title`, `description`, `completed`, `priority_id`, `due_date`, `created_at`, `updated_at`)

- **ReminderEvent**: Represents reminder notifications. Attributes: `event_id`, `event_type`, `timestamp`, `version`, `data` (contains: `task_id`, `user_id`, `task_title`, `due_date`, `reminder_time`, `notification_channels` array)

- **ConversationState**: Represents AI chat conversation context. Attributes: `user_id`, `session_id`, `messages` (array of `{role, content, timestamp}`), `context` (object with task_ids, preferences), `created_at`, `updated_at`

- **Dapr Component**: Infrastructure configuration for Dapr building blocks. Attributes: `apiVersion`, `kind`, `metadata.name`, `spec.type`, `spec.version`, `spec.metadata` (key-value pairs)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend can publish 100 events per second to Kafka via Dapr Pub/Sub API without errors or latency spikes
- **SC-002**: Conversation state read/write operations via Dapr State Store complete in under 50ms (p95 latency)
- **SC-003**: Cron binding successfully triggers Recurring Task Service every 5 minutes with <10 seconds jitter
- **SC-004**: Frontend-to-backend service invocation via Dapr has 99.9% success rate with automatic retries on transient failures
- **SC-005**: All events published include complete event envelope (event_id, event_type, timestamp, version) validated via schema tests
- **SC-006**: Backend services can horizontally scale to 3 replicas with consumer group ensuring exactly-once event processing
- **SC-007**: System maintains <200ms p95 latency for task CRUD operations even with event publishing enabled (async pattern)
- **SC-008**: Distributed traces show end-to-end request flow from frontend → Dapr → backend → Kafka with correlation IDs

### Implementation Validation

- **SC-009**: All Python services use `httpx` library (NOT kafka-python or redis-py) for Dapr sidecar communication
- **SC-010**: Dapr component YAML files pass `dapr components validate` command without errors
- **SC-011**: All Kubernetes deployments include Dapr sidecar annotations (`dapr.io/enabled: true`, `dapr.io/app-id`, `dapr.io/app-port`)
- **SC-012**: Event schemas are documented in JSON Schema format and validated in automated tests
- **SC-013**: Local Minikube deployment successfully runs Redis, Kafka, Dapr runtime, and all application services
- **SC-014**: Production DOKS deployment successfully uses managed services (Neon for state, Redpanda Cloud for messaging)

## Event Schema Definitions

### TaskEvent Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "TaskEvent",
  "description": "Event published when task state changes",
  "required": ["event_id", "event_type", "timestamp", "version", "data"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this event instance"
    },
    "event_type": {
      "type": "string",
      "enum": ["task.created", "task.updated", "task.completed", "task.deleted"],
      "description": "Type of task event"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO8601 timestamp when event occurred"
    },
    "version": {
      "type": "string",
      "pattern": "^v[0-9]+\\.[0-9]+$",
      "description": "Event schema version (e.g., v1.0)"
    },
    "data": {
      "type": "object",
      "description": "Full task object at time of event",
      "required": ["id", "user_id", "title", "completed"],
      "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "completed": { "type": "boolean" },
        "priority_id": { "type": "integer", "nullable": true },
        "due_date": { "type": "string", "format": "date-time", "nullable": true },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

**Example TaskEvent JSON:**

```json
{
  "event_id": "a3c7f8e9-1234-5678-9abc-def012345678",
  "event_type": "task.created",
  "timestamp": "2025-12-11T10:30:00Z",
  "version": "v1.0",
  "data": {
    "id": 42,
    "user_id": "usr_abc123",
    "title": "Complete Phase V migration",
    "description": "Implement event-driven architecture with Dapr and Kafka",
    "completed": false,
    "priority_id": 1,
    "due_date": "2025-12-20T23:59:59Z",
    "created_at": "2025-12-11T10:30:00Z",
    "updated_at": "2025-12-11T10:30:00Z"
  }
}
```

### ReminderEvent Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ReminderEvent",
  "description": "Event published when task reminder is due",
  "required": ["event_id", "event_type", "timestamp", "version", "data"],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this event instance"
    },
    "event_type": {
      "type": "string",
      "enum": ["reminder.due", "reminder.sent", "reminder.failed"],
      "description": "Type of reminder event"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO8601 timestamp when event occurred"
    },
    "version": {
      "type": "string",
      "pattern": "^v[0-9]+\\.[0-9]+$",
      "description": "Event schema version (e.g., v1.0)"
    },
    "data": {
      "type": "object",
      "description": "Reminder details",
      "required": ["task_id", "user_id", "task_title", "due_date", "reminder_time"],
      "properties": {
        "task_id": { "type": "integer" },
        "user_id": { "type": "string" },
        "task_title": { "type": "string" },
        "due_date": { "type": "string", "format": "date-time" },
        "reminder_time": { "type": "string", "format": "date-time" },
        "notification_channels": {
          "type": "array",
          "items": { "type": "string", "enum": ["email", "push", "sms"] }
        }
      }
    }
  }
}
```

**Example ReminderEvent JSON:**

```json
{
  "event_id": "b4d8g9f0-2345-6789-0bcd-ef1234567890",
  "event_type": "reminder.due",
  "timestamp": "2025-12-20T22:59:59Z",
  "version": "v1.0",
  "data": {
    "task_id": 42,
    "user_id": "usr_abc123",
    "task_title": "Complete Phase V migration",
    "due_date": "2025-12-20T23:59:59Z",
    "reminder_time": "2025-12-20T22:59:59Z",
    "notification_channels": ["email", "push"]
  }
}
```

## Dapr Component Specifications

### 1. Pub/Sub Component (kafka-pubsub)

**Local Minikube Configuration:**

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka.default.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-app-group"
  - name: clientId
    value: "todo-backend"
  - name: authType
    value: "none"  # No auth for local development
  - name: maxMessageBytes
    value: "1024000"  # 1MB max message size
```

**Production DOKS Configuration (Redpanda Cloud):**

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "seed-a1b2c3d4.redpanda.cloud:9092"
  - name: consumerGroup
    value: "todo-app-group"
  - name: clientId
    value: "todo-backend"
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: kafka-secrets
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password
  - name: maxMessageBytes
    value: "1024000"
```

**Python Publishing Example (using httpx, NOT kafka-python):**

```python
import httpx
import uuid
from datetime import datetime, timezone

async def publish_task_event(event_type: str, task_data: dict):
    """
    Publish task event via Dapr Pub/Sub API.
    Uses httpx to communicate with Dapr sidecar at localhost:3500.
    """
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "v1.0",
        "data": task_data
    }

    dapr_url = "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            dapr_url,
            json=event,
            headers={"Content-Type": "application/json"},
            timeout=5.0
        )
        response.raise_for_status()

    print(f"Published event {event['event_id']} to task-events topic")
```

**Python Subscription Example:**

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr calls this endpoint to discover subscriptions.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """
    Handle incoming task events from Dapr Pub/Sub.
    Dapr sends CloudEvent format.
    """
    cloud_event = await request.json()
    event_data = cloud_event["data"]

    print(f"Received task event: {event_data['event_type']}")
    # Process event (send notification, update analytics, etc.)

    return {"status": "SUCCESS"}
```

### 2. State Store Component (statestore)

**Local Minikube Configuration (Redis):**

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master.default.svc.cluster.local:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
  - name: actorStateStore
    value: "true"
```

**Production DOKS Configuration (Neon PostgreSQL):**

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: neon-secrets
      key: state-connection-string
  - name: tableName
    value: "dapr_state"
  - name: metadataTableName
    value: "dapr_state_metadata"
```

**Python State Store Example (using httpx, NOT redis-py or psycopg2):**

```python
import httpx
from typing import Optional

DAPR_STATE_URL = "http://localhost:3500/v1.0/state/statestore"

async def save_conversation_state(user_id: str, session_id: str, state_data: dict):
    """
    Save conversation state via Dapr State Store API.
    Uses httpx to communicate with Dapr sidecar at localhost:3500.
    """
    key = f"conversation:{user_id}:{session_id}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            DAPR_STATE_URL,
            json=[
                {
                    "key": key,
                    "value": state_data,
                    "metadata": {
                        "ttlInSeconds": "3600"  # 1 hour expiration
                    }
                }
            ],
            timeout=5.0
        )
        response.raise_for_status()

async def get_conversation_state(user_id: str, session_id: str) -> Optional[dict]:
    """
    Retrieve conversation state via Dapr State Store API.
    """
    key = f"conversation:{user_id}:{session_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DAPR_STATE_URL}/{key}",
            timeout=5.0
        )

        if response.status_code == 204:  # No content = key not found
            return None

        response.raise_for_status()
        return response.json()

async def delete_conversation_state(user_id: str, session_id: str):
    """
    Delete conversation state via Dapr State Store API.
    """
    key = f"conversation:{user_id}:{session_id}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{DAPR_STATE_URL}/{key}",
            timeout=5.0
        )
        response.raise_for_status()
```

### 3. Cron Binding Component (reminder-cron)

**Configuration:**

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 5m"  # Trigger every 5 minutes
  - name: direction
    value: "input"  # Input binding (receives triggers)
```

**Python Cron Handler Example:**

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/dapr/cron/reminder-cron")
async def handle_reminder_cron(request: Request):
    """
    Handle cron trigger from Dapr Cron Binding.
    This endpoint is called every 5 minutes by Dapr.
    """
    print("Reminder cron triggered - checking for due tasks...")

    # Query database for tasks with due_date within next hour
    # Generate reminder events for each due task
    # Publish reminder.due events to reminders topic

    due_tasks = await get_due_tasks()

    for task in due_tasks:
        await publish_reminder_event(task)

    print(f"Processed {len(due_tasks)} reminder events")

    return {"status": "SUCCESS", "processed": len(due_tasks)}
```

### 4. Service Invocation Configuration

**Backend Kubernetes Deployment (with Dapr Sidecar):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: registry.digitalocean.com/todo-chatbot-reg/backend:latest
        ports:
        - containerPort: 8000
```

**Frontend JavaScript/TypeScript Invocation Example:**

```typescript
// frontend/lib/dapr-api.ts

/**
 * Call backend API via Dapr service invocation.
 * Uses Dapr sidecar at localhost:3500 to route requests to backend.
 *
 * Benefits:
 * - Automatic retries on transient failures
 * - Circuit breaking on persistent failures
 * - Distributed tracing with correlation IDs
 * - mTLS encryption between services
 */
export async function invokeDaprBackend(
  method: string,
  path: string,
  body?: any
): Promise<any> {
  const daprUrl = `http://localhost:3500/v1.0/invoke/backend/method${path}`;

  const response = await fetch(daprUrl, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getJwtToken()}`
    },
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    throw new Error(`Dapr invocation failed: ${response.statusText}`);
  }

  return response.json();
}

// Usage example
async function createTask(userId: string, taskData: any) {
  return invokeDaprBackend(
    'POST',
    `/api/${userId}/tasks`,
    taskData
  );
}
```

## Technology Stack (Implementation Notes)

**IMPORTANT**: This specification is technology-agnostic and describes WHAT the system must do. The following implementation notes describe HOW we will build it:

- **Dapr Runtime**: v1.14+ (installed as Kubernetes DaemonSet or via `dapr init` for local development)
- **Message Broker**: Kafka (Minikube local) or Redpanda Cloud (DOKS production)
- **State Store**: Redis (Minikube local) or Neon PostgreSQL (DOKS production)
- **Communication Library**: Python `httpx` for all Dapr sidecar communication (NOT kafka-python, redis-py, or psycopg2)
- **Backend Framework**: FastAPI with async/await support
- **Container Orchestration**: Kubernetes with Dapr sidecar injection via annotations

**Rationale for httpx over native SDKs:**

1. **Uniform API**: Single HTTP client for all Dapr interactions (pub/sub, state, bindings, invocation)
2. **No SDK Dependencies**: Reduces dependency conflicts and container image size
3. **Easier Testing**: Can mock HTTP endpoints instead of complex SDK clients
4. **Dapr Portability**: Switching state stores (Redis → PostgreSQL) requires zero code changes, only Dapr component config updates
5. **Built-in Resilience**: Dapr sidecar handles retries, circuit breaking, and timeouts - no need to configure in application code

## Next Steps

1. **Phase 0: Research & Prerequisites** - Review Dapr documentation, set up local Kafka and Redis in Minikube
2. **Phase 1: Database Schema** - Add priorities, tags, task_tags, recurring_tasks tables via Alembic migration
3. **Phase 2: Dapr Infrastructure** - Install Dapr runtime, deploy Redis and Kafka, create Dapr component YAMLs
4. **Phase 3: Backend Dapr Integration** - Add httpx dependency, implement EventPublisher service, add Dapr annotations to deployment
5. **Phase 4: New Microservices** - Build Notification Service and Recurring Task Service as separate FastAPI apps with Dapr sidecars
6. **Phase 5: Cloud Deployment** - Provision Neon state store, Redpanda Cloud messaging, deploy to DOKS with production Dapr components

## References

- [Dapr Pub/Sub Specification](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-kafka/)
- [Dapr State Store Specification](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
- [Dapr Cron Binding Specification](https://docs.dapr.io/reference/components-reference/supported-bindings/cron/)
- [Dapr Service Invocation](https://docs.dapr.io/developing-applications/building-blocks/service-invocation/)
- Phase V Migration Plan: `specs/007-minikube-deployment/phase-v-migration-plan.md`
