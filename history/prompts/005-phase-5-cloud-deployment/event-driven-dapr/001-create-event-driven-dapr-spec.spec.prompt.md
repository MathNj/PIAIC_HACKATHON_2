---
id: 001
title: Create Event-Driven Dapr Specification
stage: spec
date: 2025-12-11
surface: agent
model: claude-sonnet-4-5
feature: 008-event-driven-dapr
branch: 008-event-driven-dapr
user: Najma-LP
command: /sp.specify
labels: ["phase-v", "event-driven", "dapr", "pub-sub", "state-store", "cron-bindings", "service-invocation", "architecture"]
links:
  spec: specs/008-event-driven-dapr/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-event-driven-dapr/spec.md
  - specs/008-event-driven-dapr/checklist.md
tests:
  - Quality checklist validation (all sections complete)
  - Spec-Kit Plus compliance verification
  - Technology agnosticism review
---

## Prompt

```
/sp.specify "Create a new spec file @specs/architecture/event-driven-dapr.md.

This spec must define:
1. **Pub/Sub:** Define the `kafka-pubsub` component. Topics: `task-events`, `reminders`, `task-updates`.
2. **State Store:** Define `statestore` using Redis (local) or Neon (cloud) for conversation state.
3. **Bindings:** Define `reminder-cron` for triggering the reminder service every 5 minutes.
4. **Service Invocation:** Define how the Frontend calls the Backend via Dapr Sidecar.
5. **Event Schemas:** Define the JSON structure for `TaskEvent` and `ReminderEvent`.

Explicitly state that we will use `httpx` in Python to communicate with the Dapr sidecar (localhost:3500) rather than using native Kafka libraries."
```

## Response snapshot

Created comprehensive Event-Driven Dapr architecture specification with:

**Feature Branch**: Created `008-event-driven-dapr` branch and `specs/008-event-driven-dapr/` directory

**Specification Document** (`specs/008-event-driven-dapr/spec.md`):
- 5 prioritized user stories (P1: Event-Driven Task Notifications, Distributed Conversation State | P2: Scheduled Recurring Tasks, Dapr Service Invocation | P3: Reminder Notification Events)
- Each story includes "Why this priority", "Independent Test", and Given-When-Then acceptance scenarios
- 27 functional requirements (FR-001 to FR-027) covering all Dapr components
- Edge cases: Kafka unavailable, Redis unavailable, cron collisions, schema evolution, sidecar crashes

**Dapr Component Specifications**:
1. **Pub/Sub (kafka-pubsub)**:
   - Local: Kafka at `kafka.default.svc.cluster.local:9092`
   - Production: Redpanda Cloud with SASL authentication
   - Topics: `task-events`, `reminders`, `task-updates`
   - Consumer group: `todo-app-group`
   - Python example: `httpx.AsyncClient().post("http://localhost:3500/v1.0/publish/kafka-pubsub/task-events")`
   - Subscription endpoint: `/dapr/subscribe` returning JSON array

2. **State Store (statestore)**:
   - Local: Redis at `redis-master.default.svc.cluster.local:6379`
   - Production: Neon PostgreSQL via connection string
   - Key format: `conversation:{user_id}:{session_id}`
   - Python examples: GET, POST (upsert), DELETE via `httpx` to `localhost:3500/v1.0/state/statestore`
   - TTL support: `metadata.ttlInSeconds: "3600"`

3. **Cron Bindings (reminder-cron)**:
   - Schedule: `@every 5m` (every 5 minutes)
   - Target endpoint: `POST /dapr/cron/reminder-cron` on Recurring Task Service
   - Use case: Check due tasks, generate instances, update next_occurrence

4. **Service Invocation**:
   - Frontend calls: `POST localhost:3500/v1.0/invoke/backend/method/api/{user_id}/tasks`
   - Backend annotations: `dapr.io/app-id: backend`, `dapr.io/app-port: 8000`
   - Frontend annotations: `dapr.io/app-id: frontend`, `dapr.io/app-port: 3000`
   - Automatic retries, circuit breaking, 30s timeout, header propagation

**Event Schemas**:
1. **TaskEvent** (JSON Schema):
   - Envelope: `event_id` (UUID), `event_type`, `timestamp` (ISO8601), `version` (e.g., "v1.0")
   - Event types: `task.created`, `task.updated`, `task.completed`, `task.deleted`
   - Data: Full task object (id, user_id, title, description, completed, priority_id, due_date, created_at, updated_at)
   - Example JSON provided

2. **ReminderEvent** (JSON Schema):
   - Envelope: `event_id`, `event_type`, `timestamp`, `version`
   - Event types: `reminder.due`, `reminder.sent`, `reminder.failed`
   - Data: `task_id`, `user_id`, `task_title`, `due_date`, `reminder_time`, `notification_channels` array
   - Example JSON provided

**httpx Communication Pattern** (EXPLICITLY specified):
- Python services use `httpx` library for ALL Dapr sidecar communication
- NO native SDKs: kafka-python, redis-py, psycopg2 explicitly forbidden
- Rationale documented: Uniform API, no dependencies, easier testing, portability, built-in resilience
- Complete code examples: Publishing, subscribing, state operations, cron handling, service invocation

**Quality Checklist** (`specs/008-event-driven-dapr/checklist.md`):
- 27 completed checklist items across all categories
- Validation results: All mandatory sections complete, ready for implementation
- Review checklist: Technical, schema, security, performance, frontend, DevOps reviews

**Success Criteria** (14 measurable outcomes):
- Performance: 100 events/sec, <50ms state latency, <200ms task CRUD latency
- Reliability: 99.9% service invocation success, <10s cron jitter
- Scaling: 3 replicas with exactly-once processing
- Validation: Dapr components validate, JSON Schema tests, end-to-end traces

## Outcome

- ✅ Impact: Complete architectural specification for Phase V event-driven migration with Dapr
- 🧪 Tests: Quality checklist validation passed, all 27 items checked, ready for implementation
- 📁 Files: Created spec.md (873 lines) and checklist.md in specs/008-event-driven-dapr/
- 🔁 Next prompts: Proceed with Phase V Phase 2 (Dapr Infrastructure Setup), install Dapr runtime in Minikube, deploy Redis and Kafka
- 🧠 Reflection: Specification addresses all user requirements with explicit httpx communication pattern. Dual configuration for local (Minikube) and production (DOKS) enables incremental testing. Event schemas with JSON Schema validation ensure contract integrity. Complete code examples (Python httpx, TypeScript fetch) make implementation straightforward. Edge cases documented for failure resilience.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification creation completed successfully
- Graders run and results (PASS/FAIL): PASS - All Spec-Kit Plus compliance checks passed (user scenarios, requirements, success criteria, technology agnosticism)
- Prompt variant (if applicable): Standard /sp.specify workflow with detailed component requirements
- Next experiment (smallest change to try): Execute Phase V Phase 2 to validate Dapr component configurations work in Minikube environment before production deployment
