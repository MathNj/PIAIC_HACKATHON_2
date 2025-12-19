# Phase V Migration Plan: Event-Driven Architecture with Dapr

**Branch**: phase-v-event-driven (to be created)
**Created**: 2025-12-11
**Status**: Planning

## Executive Summary

This document outlines the step-by-step migration from Phase IV (Kubernetes deployment) to Phase V (Event-Driven Architecture with Dapr, Kafka, and cloud-native patterns). The migration follows a deliberate sequence to minimize risk and maintain system availability.

## Migration Sequence Overview

1. **Database Schema Evolution** (Advanced Features)
2. **Local Dapr Infrastructure** (Minikube)
3. **Backend Dapr Integration** (Sidecar Pattern)
4. **New Microservices** (Notification + Recurring Task)
5. **Cloud Deployment** (DOKS + Redpanda Cloud)

---

## Phase 0: Prerequisites & Research

### Research Tasks

1. **Dapr Component Configuration Research**
   - Decision: Which Dapr components to use
   - Scope: Pub/Sub (Kafka), State Store (Redis), Bindings (Cron)
   - Deliverable: Component spec templates

2. **Event Schema Design Research**
   - Decision: Event payload structures
   - Scope: task.created, task.updated, task.completed, task.due, notification.send
   - Deliverable: Event schema definitions (JSON Schema or Avro)

3. **Kafka/Redpanda Topic Strategy**
   - Decision: Topic naming, partitioning, retention policies
   - Scope: Local development vs. cloud production
   - Deliverable: Topic configuration manifest

4. **State Store Strategy Research**
   - Decision: What data to store in Redis vs. PostgreSQL
   - Scope: Caching, session data, temporary workflow state
   - Deliverable: State management guidelines

5. **Dapr Sidecar Communication Patterns**
   - Decision: HTTP vs. gRPC for service-to-Dapr communication
   - Scope: Performance, debugging, tooling support
   - Deliverable: Communication pattern standards

### Prerequisites Checklist

- [ ] Phase IV Kubernetes deployment fully operational
- [ ] Minikube cluster running with sufficient resources (8GB RAM, 4 CPU)
- [ ] Docker Desktop installed and configured
- [ ] Helm 3.x installed
- [ ] kubectl configured for Minikube context
- [ ] Dapr CLI installed (`dapr version` works)
- [ ] PostgreSQL database accessible (Neon)

---

## Phase 1: Database Schema Migration (Advanced Features)

### Goal
Extend the existing database schema to support Phase V features: priorities, tags, and recurring tasks.

### New Tables

#### 1.1 Priorities Table

**Purpose**: Define task priority levels with UI metadata

```sql
CREATE TABLE priorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,  -- Low, Medium, High, Critical
    level INT NOT NULL UNIQUE,         -- 1 (lowest) to 5 (highest)
    color VARCHAR(7) NOT NULL,         -- Hex color (#FF5733)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed data
INSERT INTO priorities (name, level, color) VALUES
('Low', 1, '#6B7280'),
('Medium', 2, '#3B82F6'),
('High', 3, '#F59E0B'),
('Critical', 4, '#EF4444');
```

#### 1.2 Tags Table

**Purpose**: User-defined labels for task categorization

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)  -- Prevent duplicate tag names per user
);

CREATE INDEX idx_tags_user_id ON tags(user_id);
```

#### 1.3 Task-Tags Junction Table

**Purpose**: Many-to-many relationship between tasks and tags

```sql
CREATE TABLE task_tags (
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

#### 1.4 Recurring Tasks Table

**Purpose**: Templates for automatically generating recurring task instances

```sql
CREATE TABLE recurring_tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_title VARCHAR(200) NOT NULL,
    template_description TEXT,
    recurrence_pattern VARCHAR(50) NOT NULL,  -- daily, weekly, monthly, custom
    cron_expression VARCHAR(100),              -- For custom patterns (e.g., "0 9 * * MON")
    next_occurrence TIMESTAMP NOT NULL,
    priority_id INT REFERENCES priorities(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recurring_tasks_user_id ON recurring_tasks(user_id);
CREATE INDEX idx_recurring_tasks_next_occurrence ON recurring_tasks(next_occurrence) WHERE is_active = true;
```

#### 1.5 Update Tasks Table

**Purpose**: Add foreign keys for priorities and recurring task linkage

```sql
ALTER TABLE tasks
ADD COLUMN priority_id INT REFERENCES priorities(id) DEFAULT 2,  -- Default to Medium
ADD COLUMN recurring_task_id INT REFERENCES recurring_tasks(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_priority_id ON tasks(priority_id);
CREATE INDEX idx_tasks_recurring_task_id ON tasks(recurring_task_id) WHERE recurring_task_id IS NOT NULL;
```

### Migration Tasks

**Task 1.1: Create Alembic Migration**
- **File**: `backend/alembic/versions/005_phase_v_schema.py`
- **Actions**:
  1. Create priorities table with seed data
  2. Create tags table
  3. Create task_tags junction table
  4. Create recurring_tasks table
  5. Add priority_id and recurring_task_id columns to tasks table
- **Acceptance**: Migration runs successfully on local SQLite and production Neon

**Task 1.2: Update SQLModel Models**
- **Files**: `backend/app/models/priority.py`, `backend/app/models/tag.py`, `backend/app/models/recurring_task.py`
- **Actions**:
  1. Create Priority model
  2. Create Tag model with user_id relationship
  3. Create TaskTag junction model
  4. Create RecurringTask model with cron expression validation
  5. Update Task model with priority and recurring_task relationships
- **Acceptance**: Models import without errors, relationships are properly defined

**Task 1.3: Create API Endpoints (REST)**
- **Files**: `backend/app/routers/priorities.py`, `backend/app/routers/tags.py`, `backend/app/routers/recurring_tasks.py`
- **Actions**:
  1. GET /api/priorities - List all priorities
  2. GET /api/{user_id}/tags - List user's tags
  3. POST /api/{user_id}/tags - Create new tag
  4. PUT /api/{user_id}/tags/{tag_id} - Update tag
  5. DELETE /api/{user_id}/tags/{tag_id} - Delete tag
  6. GET /api/{user_id}/recurring-tasks - List user's recurring tasks
  7. POST /api/{user_id}/recurring-tasks - Create recurring task template
  8. PUT /api/{user_id}/recurring-tasks/{id} - Update template
  9. DELETE /api/{user_id}/recurring-tasks/{id} - Delete template
  10. Update POST /api/{user_id}/tasks to accept priority_id and tag_ids
- **Acceptance**: All endpoints tested with Postman, proper JWT validation, user_id isolation

**Task 1.4: Update Frontend UI**
- **Files**: `frontend/app/dashboard/page.tsx`, `frontend/components/TaskForm.tsx`, `frontend/components/TagManager.tsx`
- **Actions**:
  1. Add priority dropdown to task form
  2. Add tag selector (multi-select) to task form
  3. Create tag management UI (/tags page)
  4. Create recurring task setup UI (/recurring page)
  5. Display priority badges on task cards
  6. Display tags on task cards with colors
- **Acceptance**: UI functional, tags and priorities saved correctly

---

## Phase 2: Dapr Infrastructure Setup (Local Minikube)

### Goal
Install Dapr on Minikube and configure components for local development.

### Dapr Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐
│   FastAPI       │         │   Dapr Sidecar  │
│   Backend       │ ◄─────► │   (HTTP/gRPC)   │
│   (Port 8000)   │         │   (Port 3500)   │
└─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Dapr Components │
                            │  - Pub/Sub      │
                            │  - State Store  │
                            │  - Bindings     │
                            └─────────────────┘
```

### Dapr Installation

**Task 2.1: Install Dapr on Minikube**
- **Command**: `dapr init -k --wait --timeout 600`
- **Actions**:
  1. Install Dapr control plane (operator, placement, sentry, sidecar-injector)
  2. Verify Dapr system pods running in `dapr-system` namespace
  3. Check Dapr version: `dapr version`
- **Acceptance**: All Dapr system pods in Running state

**Task 2.2: Deploy Redis (State Store)**
- **File**: `infrastructure/helm/redis-values.yaml`
- **Actions**:
  1. Add Redis Helm chart: `helm repo add bitnami https://charts.bitnami.com/bitnami`
  2. Create values file for local Redis (no persistence for development)
  3. Deploy: `helm install redis bitnami/redis -f infrastructure/helm/redis-values.yaml`
  4. Get Redis password: `kubectl get secret redis -o jsonpath="{.data.redis-password}" | base64 --decode`
- **Acceptance**: Redis pod running, accessible at `redis-master.default.svc.cluster.local:6379`

**Task 2.3: Deploy Kafka/Redpanda (Local)**
- **File**: `infrastructure/helm/redpanda-values.yaml`
- **Actions**:
  1. Add Redpanda Helm chart: `helm repo add redpanda https://charts.redpanda.com/`
  2. Create values file for single-node Redpanda (development mode)
  3. Deploy: `helm install redpanda redpanda/redpanda -f infrastructure/helm/redpanda-values.yaml`
  4. Create topics: task-events, notification-events
- **Acceptance**: Redpanda pod running, topics created

### Dapr Component Configuration

**Task 2.4: Create Pub/Sub Component (Kafka)**
- **File**: `infrastructure/dapr/components/pubsub-kafka.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda.default.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-app-group"
  - name: clientId
    value: "todo-backend"
  - name: authType
    value: "none"  # No auth for local development
  - name: maxMessageBytes
    value: "1048576"  # 1MB
scopes:
- backend
- notification-service
- recurring-task-service
```
- **Acceptance**: Component applied to Kubernetes, no errors in Dapr logs

**Task 2.5: Create State Store Component (Redis)**
- **File**: `infrastructure/dapr/components/statestore-redis.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master.default.svc.cluster.local:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis
      key: redis-password
  - name: actorStateStore
    value: "true"
scopes:
- notification-service
- recurring-task-service
```
- **Acceptance**: Component applied, services can read/write state

**Task 2.6: Create Cron Binding Component**
- **File**: `infrastructure/dapr/components/binding-cron.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: recurring-task-cron
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 1m"  # Run every minute
  - name: direction
    value: "input"
scopes:
- recurring-task-service
```
- **Acceptance**: Cron trigger fires every minute (verified in logs)

---

## Phase 3: Backend Dapr Integration (Sidecar Pattern)

### Goal
Refactor the existing FastAPI backend to publish events via Dapr instead of direct database writes for some operations.

### Event-Driven Patterns

**Events to Publish:**
1. `task.created` - When a new task is created
2. `task.updated` - When a task is modified
3. `task.completed` - When a task is marked as done
4. `task.deleted` - When a task is removed
5. `task.due.approaching` - When a task's due date is within 24 hours

### Backend Refactoring

**Task 3.1: Add Dapr SDK to Backend**
- **File**: `backend/requirements.txt`
- **Actions**:
  1. Add `dapr==1.12.0` to requirements
  2. Add `dapr-ext-grpc==1.12.0` (optional, for gRPC)
  3. Run `pip install -r requirements.txt`
- **Acceptance**: Dapr SDK imported without errors

**Task 3.2: Create Event Publisher Service**
- **File**: `backend/app/services/event_publisher.py`
```python
from dapr.clients import DaprClient
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, pubsub_name: str = "task-pubsub"):
        self.pubsub_name = pubsub_name

    async def publish_event(self, topic: str, event_data: Dict[str, Any]):
        """Publish an event to Dapr Pub/Sub"""
        try:
            with DaprClient() as client:
                client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=topic,
                    data=json.dumps(event_data),
                    data_content_type="application/json"
                )
            logger.info(f"Published event to {topic}: {event_data.get('event_type')}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            # Don't fail the main operation if event publishing fails

    async def publish_task_created(self, task_id: int, user_id: str, task_data: Dict[str, Any]):
        await self.publish_event("task-events", {
            "event_type": "task.created",
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": task_data
        })

    async def publish_task_completed(self, task_id: int, user_id: str):
        await self.publish_event("task-events", {
            "event_type": "task.completed",
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
```
- **Acceptance**: Event publisher tested, events appear in Kafka logs

**Task 3.3: Integrate Event Publisher into Task Endpoints**
- **File**: `backend/app/routers/tasks.py`
- **Actions**:
  1. Inject EventPublisher into task creation endpoint
  2. Publish `task.created` event after successful DB insert
  3. Publish `task.updated` event after task modification
  4. Publish `task.completed` event when toggling completion status
  5. Publish `task.deleted` event before DB deletion
- **Acceptance**: Events published for all task operations, endpoints still return correct HTTP responses

**Task 3.4: Add Dapr Sidecar to Backend Deployment**
- **File**: `infrastructure/helm/todo-chart/templates/backend-deployment.yaml`
- **Actions**:
  1. Add Dapr annotations to backend pod spec:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
```
  2. Update Helm chart
  3. Redeploy backend
- **Acceptance**: Backend pod shows 2/2 containers (app + daprd sidecar), Dapr logs show successful initialization

**Task 3.5: Create State Management Service (Optional Caching)**
- **File**: `backend/app/services/state_manager.py`
```python
from dapr.clients import DaprClient

class StateManager:
    def __init__(self, store_name: str = "todo-statestore"):
        self.store_name = store_name

    async def save_state(self, key: str, value: dict):
        with DaprClient() as client:
            client.save_state(self.store_name, key, value)

    async def get_state(self, key: str):
        with DaprClient() as client:
            return client.get_state(self.store_name, key).data

    async def delete_state(self, key: str):
        with DaprClient() as client:
            client.delete_state(self.store_name, key)
```
- **Use Cases**: Cache frequently accessed task lists, store temporary workflow state
- **Acceptance**: State operations tested, data persists in Redis

---

## Phase 4: New Microservices Implementation

### Goal
Build two new microservices: Notification Service and Recurring Task Service.

### 4.1 Notification Service

**Purpose**: Subscribe to task events and send notifications (email, push, webhook).

**Architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Kafka Topic   │      │  Notification   │      │   External      │
│  task-events    │ ───► │   Service       │ ───► │   Providers     │
└─────────────────┘      │  (Subscriber)   │      │  (SendGrid,     │
                         └─────────────────┘      │   FCM, etc.)    │
                                                   └─────────────────┘
```

**Task 4.1.1: Scaffold Notification Service**
- **Directory**: `notification-service/`
- **Actions**:
  1. Create FastAPI application (`notification-service/app/main.py`)
  2. Add Dockerfile (multi-stage build)
  3. Add requirements.txt (dapr, fastapi, httpx, sendgrid)
  4. Create Kubernetes deployment manifest with Dapr sidecar
  5. Create Helm chart values for notification-service
- **Acceptance**: Service starts successfully, health endpoint responds

**Task 4.1.2: Implement Dapr Pub/Sub Subscription**
- **File**: `notification-service/app/main.py`
```python
from fastapi import FastAPI, Request
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/task-events")  # Dapr will POST events here
async def handle_task_event(request: Request):
    event_data = await request.json()
    event_type = event_data.get("event_type")

    if event_type == "task.completed":
        await send_completion_notification(event_data)
    elif event_type == "task.due.approaching":
        await send_due_reminder(event_data)

    return {"status": "processed"}

@app.get("/dapr/subscribe")  # Dapr subscription endpoint
def subscribe():
    return [
        {
            "pubsubname": "task-pubsub",
            "topic": "task-events",
            "route": "/task-events"
        }
    ]
```
- **Acceptance**: Service receives events from Kafka, logs show event processing

**Task 4.1.3: Implement Notification Providers**
- **Files**: `notification-service/app/providers/email.py`, `notification-service/app/providers/push.py`
- **Actions**:
  1. Implement SendGrid email provider (task completion, due reminders)
  2. Implement Firebase Cloud Messaging (push notifications)
  3. Add notification delivery tracking (save to state store)
  4. Add retry logic for failed deliveries
- **Acceptance**: Email and push notifications sent successfully for test events

**Task 4.1.4: Deploy Notification Service to Kubernetes**
- **File**: `infrastructure/helm/todo-chart/templates/notification-deployment.yaml`
- **Actions**:
  1. Create deployment manifest with Dapr annotations
  2. Add to Helm chart as optional component (enabled: true)
  3. Deploy to Minikube
  4. Verify Dapr subscription established
- **Acceptance**: Service pod running (2/2 containers), subscribes to task-events topic

### 4.2 Recurring Task Service

**Purpose**: Generate task instances from recurring task templates based on cron schedules.

**Architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Dapr Cron      │      │  Recurring Task │      │   PostgreSQL    │
│  Binding        │ ───► │   Service       │ ───► │   (Templates)   │
│  (@every 1m)    │      │  (Cron Handler) │      └─────────────────┘
└─────────────────┘      └─────────────────┘               │
                                  │                          │
                                  ▼                          ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │   Kafka Topic   │      │   Tasks Table   │
                         │  task-events    │      │  (Instances)    │
                         └─────────────────┘      └─────────────────┘
```

**Task 4.2.1: Scaffold Recurring Task Service**
- **Directory**: `recurring-task-service/`
- **Actions**:
  1. Create FastAPI application
  2. Add Dockerfile
  3. Add requirements.txt (dapr, fastapi, sqlmodel, psycopg2, croniter)
  4. Create Kubernetes deployment manifest with Dapr sidecar and cron binding
- **Acceptance**: Service starts, cron binding triggers every minute

**Task 4.2.2: Implement Cron Trigger Handler**
- **File**: `recurring-task-service/app/main.py`
```python
from fastapi import FastAPI, Request
from datetime import datetime, timedelta
from croniter import croniter
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/recurring-task-cron")  # Dapr cron binding calls this
async def process_recurring_tasks(request: Request):
    logger.info("Cron trigger received, processing recurring tasks...")

    # Fetch active recurring tasks with next_occurrence <= now
    templates = await fetch_due_templates()

    for template in templates:
        await generate_task_instance(template)
        await update_next_occurrence(template)

    return {"status": "processed", "count": len(templates)}
```
- **Acceptance**: Cron handler executes every minute, processes templates

**Task 4.2.3: Implement Task Instance Generation**
- **File**: `recurring-task-service/app/services/task_generator.py`
```python
async def generate_task_instance(template: RecurringTask):
    """Create a new task instance from template"""
    task_data = {
        "user_id": template.user_id,
        "title": template.template_title,
        "description": template.template_description,
        "priority_id": template.priority_id,
        "recurring_task_id": template.id,
        "due_date": template.next_occurrence
    }

    # Insert task into database
    task_id = await create_task_in_db(task_data)

    # Publish task.created event via Dapr
    await publish_event("task-events", {
        "event_type": "task.created",
        "task_id": task_id,
        "user_id": template.user_id,
        "source": "recurring-task-service",
        "timestamp": datetime.utcnow().isoformat()
    })

    logger.info(f"Generated task instance {task_id} from template {template.id}")
```
- **Acceptance**: Task instances created correctly, visible in database and frontend

**Task 4.2.4: Implement Next Occurrence Calculation**
- **File**: `recurring-task-service/app/services/schedule_calculator.py`
```python
from croniter import croniter
from datetime import datetime

def calculate_next_occurrence(pattern: str, cron_expression: str, base_time: datetime) -> datetime:
    """Calculate next occurrence based on recurrence pattern"""
    if pattern == "daily":
        return base_time + timedelta(days=1)
    elif pattern == "weekly":
        return base_time + timedelta(weeks=1)
    elif pattern == "monthly":
        return base_time + timedelta(days=30)  # Simplified
    elif pattern == "custom" and cron_expression:
        cron = croniter(cron_expression, base_time)
        return cron.get_next(datetime)
    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")
```
- **Acceptance**: Next occurrence calculated correctly for all patterns

**Task 4.2.5: Deploy Recurring Task Service**
- **File**: `infrastructure/helm/todo-chart/templates/recurring-task-deployment.yaml`
- **Actions**:
  1. Create deployment with Dapr annotations and cron binding
  2. Add to Helm chart
  3. Deploy to Minikube
  4. Verify cron triggers fire every minute
- **Acceptance**: Service running, generates task instances on schedule

---

## Phase 5: Cloud Deployment (DOKS + Redpanda Cloud)

### Goal
Deploy the full Phase V architecture to DigitalOcean Kubernetes Service with managed Kafka (Redpanda Cloud).

### Cloud Infrastructure

**Task 5.1: Provision DigitalOcean Managed Redis**
- **Actions**:
  1. Create Redis cluster via DigitalOcean console (or doctl CLI)
  2. Note connection string (rediss://...)
  3. Update Dapr state store component with production Redis URL
  4. Create Kubernetes secret for Redis password
- **Acceptance**: Redis accessible from DOKS cluster, state operations work

**Task 5.2: Provision Redpanda Cloud (Managed Kafka)**
- **Actions**:
  1. Sign up for Redpanda Cloud (or use Confluent Cloud / AWS MSK)
  2. Create cluster (single-zone for cost optimization)
  3. Create topics: task-events, notification-events
  4. Generate SASL/SCRAM credentials
  5. Update Dapr pub/sub component with production Kafka brokers and auth
  6. Create Kubernetes secret for Kafka credentials
- **Acceptance**: Kafka cluster accessible, topics created, authentication working

**Task 5.3: Update Dapr Components for Production**
- **Files**: `infrastructure/dapr/components/pubsub-kafka-prod.yaml`, `infrastructure/dapr/components/statestore-redis-prod.yaml`
- **Actions**:
  1. Update Kafka component with TLS and SASL authentication
  2. Update Redis component with TLS connection string
  3. Apply components to DOKS cluster
- **Acceptance**: Components configured correctly, no authentication errors

**Task 5.4: Deploy Full Stack to DOKS**
- **Actions**:
  1. Update Helm values for production (LoadBalancer services, resource limits)
  2. Deploy backend: `helm upgrade todo-app ./infrastructure/helm/todo-chart --set environment=production`
  3. Deploy notification-service (enabled: true)
  4. Deploy recurring-task-service (enabled: true)
  5. Verify all pods running with Dapr sidecars (3/3 containers)
  6. Check Dapr dashboard for component health
- **Acceptance**: All services running, events flowing through Kafka, tasks generated on schedule

**Task 5.5: Configure External Access**
- **Actions**:
  1. Verify LoadBalancer external IPs assigned
  2. Configure DNS (todo-app.yourdomain.com → LoadBalancer IP)
  3. Update frontend API URL to point to production backend
  4. Test end-to-end: create task → notification sent → recurring tasks generated
- **Acceptance**: Application accessible via public URL, all features working

**Task 5.6: Monitoring & Observability**
- **Actions**:
  1. Enable Dapr telemetry (Prometheus metrics)
  2. Deploy Grafana dashboard for Dapr metrics
  3. Configure log aggregation (Loki or ELK stack)
  4. Set up alerts for service failures
  5. Document runbook for common issues
- **Acceptance**: Metrics visible in Grafana, logs searchable, alerts firing correctly

---

## Success Criteria

### Phase V Complete When:
- [ ] All new database tables created and seeded
- [ ] Dapr installed on Minikube and DOKS
- [ ] Backend publishes events via Dapr for all task operations
- [ ] Notification Service deployed and sending notifications
- [ ] Recurring Task Service deployed and generating task instances
- [ ] Kafka/Redpanda cluster operational (local and cloud)
- [ ] Redis state store operational (local and cloud)
- [ ] All services running with Dapr sidecars (2/2 or 3/3 containers)
- [ ] Event flow validated end-to-end
- [ ] Production deployment on DOKS with external access
- [ ] Monitoring and alerting configured

### Performance Targets:
- Event latency (publish to consume): < 500ms
- Task instance generation: Within 1 minute of schedule
- Notification delivery: Within 2 minutes of trigger event
- State store operations: < 50ms latency
- All services: < 2 second startup time

### Quality Gates:
- Zero data loss during migration
- All existing features remain functional
- New events backward compatible (consumers ignore unknown fields)
- Graceful degradation if Kafka unavailable (operations continue, events buffered)
- All microservices independently deployable

---

## Rollback Plan

### Phase 1 Rollback (Schema):
- Run Alembic downgrade migration
- Remove foreign key constraints
- Drop new tables

### Phase 2-3 Rollback (Dapr):
- Remove Dapr sidecars from deployments
- Restore direct database calls in backend
- Uninstall Dapr from cluster

### Phase 4 Rollback (Microservices):
- Scale down notification-service to 0 replicas
- Scale down recurring-task-service to 0 replicas
- System continues with core functionality

### Phase 5 Rollback (Cloud):
- Switch DNS back to Phase IV deployment
- Shut down Redpanda Cloud cluster
- Delete DO Managed Redis

---

## Timeline Estimate

| Phase | Description | Estimated Duration |
|-------|-------------|-------------------|
| Phase 0 | Research & Prerequisites | 2-3 days |
| Phase 1 | Database Schema Migration | 3-4 days |
| Phase 2 | Dapr Infrastructure Setup | 2-3 days |
| Phase 3 | Backend Dapr Integration | 4-5 days |
| Phase 4 | New Microservices | 6-8 days |
| Phase 5 | Cloud Deployment | 3-4 days |
| **Total** | **Complete Phase V Migration** | **20-27 days** |

---

## Next Steps

1. **Create Phase V Feature Branch**: `git checkout -b phase-v-event-driven`
2. **Run `/sp.specify`**: Create formal Phase V specification
3. **Execute Phase 0**: Complete research tasks
4. **Execute Phase 1**: Database schema migration
5. **Continue sequentially through Phase 5**

---

**Document Status**: Draft
**Last Updated**: 2025-12-11
**Owner**: System Architect
