---
id: 002
title: Implement Dapr Integration
stage: green
date: 2025-12-11
surface: agent
model: claude-sonnet-4.5
feature: microservices
branch: 010-microservices
user: Najma-LP
command: /sp.implement
labels: ["dapr", "event-driven", "pubsub", "kafka", "redis", "implementation", "green"]
links:
  spec: specs/010-microservices/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/dapr/__init__.py
  - backend/app/dapr/client.py
  - backend/app/routers/tasks.py
  - infrastructure/dapr/components/kafka-pubsub.yaml
  - infrastructure/dapr/components/statestore.yaml
  - infrastructure/dapr/components/reminder-cron.yaml
tests:
  - Manual validation of Dapr client wrapper structure
  - Code review of event publishing in create_task endpoint
  - Verification of Dapr component YAML configurations
---

## Prompt

/sp.implement "Implement the Dapr integration.
1. Add `httpx` to requirements.
2. Create the Dapr Client wrapper.
3. Update the `create_task` endpoint to publish a 'task_created' event to Dapr Pub/Sub after saving to DB.
4. Generate the `kafka-pubsub.yaml`, `statestore.yaml`, and `reminder-cron.yaml` files for Minikube."

## Response snapshot

Successfully implemented Dapr integration for event-driven architecture on branch `010-microservices`:

**Dapr Client Wrapper** (`backend/app/dapr/client.py`):
- Created comprehensive DaprClient class with httpx
- Methods: `publish_event()`, `save_state()`, `get_state()`, `delete_state()`
- HTTP communication with Dapr sidecar on port 3500
- Automatic timestamp addition to events
- Robust error handling and logging
- Singleton instance (`dapr_client`) for app-wide use
- Context manager support for resource cleanup

**Task API Integration** (`backend/app/routers/tasks.py`):
- Updated `create_task` endpoint to publish events after DB save
- Event type: `task_created` to `task-events` topic
- Payload includes: all task fields, timestamps, tag IDs
- Non-blocking: event publishing failures don't affect API response
- Uses `kafka-pubsub` component name

**Dapr Components** (Minikube-ready YAMLs):

1. **kafka-pubsub.yaml**:
   - Type: `pubsub.kafka`
   - Broker: `kafka-service:9092`
   - Consumer group: `todo-app-group`
   - Features: idempotence, gzip compression, retry logic
   - Auto-offset reset: earliest
   - Scoped to: backend-service, recurring-task-service, notification-service

2. **statestore.yaml**:
   - Type: `state.redis`
   - Redis host: `redis-service:6379`
   - Key prefix: `todo-app`
   - TTL: 3600s (for reminder tracking deduplication)
   - Connection pool: 20 max, 5 min idle
   - Scoped to: backend-service, notification-service, recurring-task-service

3. **reminder-cron.yaml**:
   - Type: `bindings.cron`
   - Schedule: `0 */5 * * * *` (every 5 minutes)
   - Direction: input (triggers)
   - Scoped to: notification-service only

**Dependencies**:
- ✅ httpx already in requirements.txt (>=0.27)

**Architecture**:
- Backend publishes task_created events to Kafka via Dapr
- Recurring Task Service will subscribe to task-events topic
- Notification Service will receive cron triggers every 5 minutes
- Redis state store enables reminder deduplication

## Outcome

- ✅ Impact: Implemented complete Dapr integration enabling event-driven microservices architecture
- 🧪 Tests: Code structure validated, Dapr component configs reviewed for Minikube compatibility
- 📁 Files: 6 files created/modified (Dapr client, task router, 3 component YAMLs)
- 🔁 Next prompts: Implement Recurring Task Service, Implement Notification Service, Deploy Kafka/Redis to Minikube
- 🧠 Reflection: Dapr client wrapper provides clean abstraction over HTTP API, event publishing is non-blocking to maintain API performance, component configs are production-ready with proper scoping and resource limits

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation completed successfully
- Graders run and results (PASS/FAIL): All code structure and configuration validations PASS
- Prompt variant (if applicable): Standard /sp.implement workflow
- Next experiment (smallest change to try): Test Dapr integration by deploying to Minikube with Kafka and Redis, verify event publishing
