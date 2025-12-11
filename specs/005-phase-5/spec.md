# Phase 5: Event-Driven Architecture with Dapr, Kafka, and Cloud Deployment

**Feature Branch**: `005-phase-5`
**Created**: 2025-12-11
**Status**: In Progress
**Parent Phases**: Phase 4 (Minikube/K8s) ✅ Complete

## Overview

Phase 5 transforms the Todo App from a monolithic Kubernetes deployment into a cloud-native, event-driven microservices architecture using Dapr, Kafka/Redpanda, and DigitalOcean Kubernetes Service (DOKS).

This phase encompasses four major components:
1. **Event-Driven Infrastructure** (Dapr + Kafka/Redpanda)
2. **Advanced Task Features** (Priorities, Tags, Recurring Tasks)
3. **Microservices** (Notification Service + Recurring Task Service)
4. **Cloud Deployment** (DOKS + Redpanda Cloud)

## Phase Structure

Phase 5 is organized into sub-components with dedicated specifications:

```
specs/005-phase-5/
├── spec.md (this file - Phase 5 overview)
├── components/
│   ├── dapr-infrastructure.md → specs/008-event-driven-dapr/spec.md
│   ├── advanced-features.md → specs/009-advanced-task-features/spec.md
│   ├── microservices.md → specs/010-microservices/spec.md
│   └── cloud-deployment.md → specs/011-cloud-doks-deployment/spec.md
└── checklists/
    └── requirements.md (quality validation)
```

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event-Driven Task Operations (Priority: P1)

As a user, when I create or update tasks, I want the system to respond immediately while notifying other services asynchronously, so that my experience is fast and reliable even when notification services are unavailable.

**Why this priority**: Core architectural shift that enables microservices decoupling. Without event-driven patterns, the system cannot scale horizontally or tolerate partial failures.

**Independent Test**: Create a task → verify immediate response → confirm event published to Kafka → verify notification service receives event asynchronously. Delivers value by preventing cascading failures.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** task is saved to database, **Then** task creation API returns success in <200ms AND task.created event is published to Kafka within 100ms
2. **Given** notification service is down, **When** user creates a task, **Then** task creation succeeds without errors and event is queued for later processing
3. **Given** multiple backend replicas are running, **When** events are published, **Then** only one notification service instance processes each event (consumer group guarantees)
4. **Given** user completes a task, **When** completion is saved, **Then** task.completed event triggers notification to user within 2 minutes

---

### User Story 2 - Distributed Conversation State (Priority: P1)

As a user chatting with the AI assistant, I want my conversation history preserved across multiple requests, even when load balancing routes me to different backend pods, so that the AI maintains context throughout our conversation.

**Why this priority**: Essential for stateless backend architecture in Kubernetes. Without distributed state store, horizontal scaling breaks conversation continuity.

**Independent Test**: Start conversation on Pod A → simulate pod restart → continue conversation routed to Pod B → verify full history retrieved from Redis. Delivers seamless UX during scaling.

**Acceptance Scenarios**:

1. **Given** user starts a chat conversation, **When** messages are exchanged, **Then** conversation state is persisted to Redis via Dapr state store API (localhost:3500)
2. **Given** backend pod restarts mid-conversation, **When** user sends next message, **Then** new pod retrieves full conversation history from Redis without data loss
3. **Given** Redis is temporarily unavailable, **When** state operation is attempted, **Then** system gracefully degrades with error message rather than crashing
4. **Given** conversation has 100+ messages, **When** history is retrieved, **Then** retrieval completes in <50ms from Redis cache

---

### User Story 3 - Recurring Task Automation (Priority: P2)

As a user with recurring responsibilities, I want to define task templates (e.g., "Daily standup at 9 AM") and have the system automatically create task instances based on my schedule, so I don't have to manually recreate the same tasks repeatedly.

**Why this priority**: Valuable automation feature but not critical for core functionality. Can be implemented after event infrastructure is stable.

**Independent Test**: Create recurring task template → wait for cron trigger (5 minutes) → verify new task instance created with correct due date. Delivers automation value independently.

**Acceptance Scenarios**:

1. **Given** user creates a recurring task template with "daily" pattern, **When** cron binding triggers recurring-task-service every 5 minutes, **Then** service generates new task instance for current day if not already created
2. **Given** recurring task template has "weekly" pattern on Mondays, **When** it's Monday and cron triggers, **Then** new task instance is created with due date set to current Monday
3. **Given** recurring-task-service is down for 2 hours, **When** service restarts, **Then** all missed task instances are generated in batch (catch-up logic)
4. **Given** user disables a recurring task template, **When** cron triggers, **Then** no new instances are generated until template is re-enabled

---

### User Story 4 - Cloud Production Deployment (Priority: P2)

As a DevOps engineer, I want to deploy the Todo App to DigitalOcean Kubernetes with managed Redpanda Cloud (Kafka) and managed Redis, so that the production environment is scalable, secure, and operates with minimal infrastructure maintenance.

**Why this priority**: Required for production readiness but can be tested locally first. Cloud deployment follows after local Minikube validation.

**Independent Test**: Deploy Helm charts to DOKS → configure Redpanda Cloud with SASL/SSL → verify all services connect with 0 authentication errors. Delivers production-grade infrastructure.

**Acceptance Scenarios**:

1. **Given** DOKS cluster is provisioned, **When** DevOps runs `dapr init --kubernetes`, **Then** Dapr control plane is installed and all system pods are Running
2. **Given** Redpanda Cloud cluster is provisioned with SASL/SCRAM-SHA-256, **When** Kubernetes Secret is created with credentials, **Then** Dapr kafka-pubsub component connects successfully with TLS encryption
3. **Given** Helm charts include Dapr annotations (dapr.io/enabled: "true"), **When** services are deployed, **Then** Dapr sidecars are automatically injected (2/2 containers per pod)
4. **Given** production deployment is complete, **When** DevOps rotates Redpanda credentials, **Then** Kubernetes Secret is updated and pods restart with new credentials without manual YAML changes

---

## Requirements *(mandatory)*

### Phase 5 Components

Phase 5 is divided into four interconnected components. Each component has its own detailed specification:

#### Component 1: Dapr Infrastructure (`specs/008-event-driven-dapr/`)

**Purpose**: Establish event-driven foundation with Dapr, Kafka/Redpanda, and Redis state store.

**Key Requirements**:
- Install Dapr control plane on Minikube and DOKS
- Configure kafka-pubsub component (local Kafka for Minikube, Redpanda Cloud for production)
- Configure Redis state store (local Redis for Minikube, DO Managed Redis for production)
- Configure cron binding for recurring task triggers (every 5 minutes)
- Define event schemas: TaskEvent, ReminderEvent, NotificationEvent
- Use httpx in Python to communicate with Dapr sidecar (localhost:3500)

**Detailed Spec**: `specs/008-event-driven-dapr/spec.md`

---

#### Component 2: Advanced Task Features (`specs/009-advanced-task-features/`)

**Purpose**: Extend database schema to support priorities, tags, and recurring task templates.

**Key Requirements**:
- Create `priorities` table with seed data (Low, Medium, High, Critical)
- Create `tags` table with user-scoped custom labels
- Create `task_tags` junction table (many-to-many relationship)
- Create `recurring_tasks` table with cron expression support
- Add `priority_id` and `recurring_task_id` foreign keys to `tasks` table
- Update SQLModel models for all new entities
- Create REST API endpoints for priorities, tags, and recurring task CRUD
- Update frontend UI to support priority selection and tag management

**Detailed Spec**: `specs/009-advanced-task-features/spec.md`

---

#### Component 3: Microservices (`specs/010-microservices/`)

**Purpose**: Build two new event-driven microservices: Notification Service and Recurring Task Service.

**Key Requirements**:

**Notification Service**:
- Subscribe to `task-events` Kafka topic via Dapr
- Handle task.created, task.completed, task.due events
- Send email notifications via SendGrid
- Send push notifications via Firebase Cloud Messaging (optional)
- Track notification delivery status in Redis state store
- Retry failed deliveries with exponential backoff

**Recurring Task Service**:
- Receive cron trigger every 5 minutes via Dapr binding
- Query `recurring_tasks` table for templates where `next_occurrence <= now()`
- Generate new task instances from templates
- Calculate next occurrence based on recurrence pattern (daily, weekly, monthly, custom cron)
- Publish task.created events for generated instances
- Update template's `next_occurrence` timestamp

**Detailed Spec**: `specs/010-microservices/spec.md`

---

#### Component 4: Cloud Deployment (`specs/011-cloud-doks-deployment/`)

**Purpose**: Deploy Phase 5 architecture to DigitalOcean Kubernetes with managed cloud services.

**Key Requirements**:
- Provision DigitalOcean Kubernetes Service (DOKS) cluster
- Provision Redpanda Cloud cluster with SASL/SCRAM-SHA-256 authentication
- Provision DigitalOcean Managed Redis
- Configure Kubernetes Secrets for Redpanda and Redis credentials
- Update Dapr components to use `secretKeyRef` for production credentials
- Update Helm charts with Dapr annotations: `dapr.io/enabled`, `dapr.io/app-id`, `dapr.io/app-port`
- Deploy all services with Dapr sidecars (backend, notification-service, recurring-task-service)
- Configure TLS/SSL for all external connections (Redpanda, Redis)
- Verify 0 authentication errors and 99.9% event delivery reliability

**Detailed Spec**: `specs/011-cloud-doks-deployment/spec.md`

---

### Functional Requirements Summary

**High-Level Phase 5 Requirements**:

- **FR-P5-001**: System MUST use Dapr as the service mesh for all microservice communication patterns (pub/sub, state, bindings)
- **FR-P5-002**: Backend MUST publish events to Kafka for all task operations (create, update, delete, complete) via Dapr HTTP API
- **FR-P5-003**: Notification Service MUST subscribe to task-events topic and process events asynchronously
- **FR-P5-004**: Recurring Task Service MUST run on a 5-minute cron schedule to generate task instances from templates
- **FR-P5-005**: All services MUST use Redis via Dapr state store API for distributed session and cache management
- **FR-P5-006**: Event publishing MUST NOT block API responses - events published asynchronously with non-failing semantics
- **FR-P5-007**: Database schema MUST include priorities, tags, task_tags, and recurring_tasks tables with proper foreign keys
- **FR-P5-008**: Production deployment MUST use Redpanda Cloud with SASL/SSL authentication and TLS encryption
- **FR-P5-009**: Kubernetes Secrets MUST store all production credentials (Redpanda, Redis) with secretKeyRef in Dapr components
- **FR-P5-010**: Helm charts MUST include Dapr sidecar annotations for automatic injection in all service deployments
- **FR-P5-011**: System MUST gracefully degrade when Kafka or Redis are temporarily unavailable (no cascading failures)
- **FR-P5-012**: All microservices MUST be independently deployable without requiring coordinated releases

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Phase 5 Complete When**:

- **SC-P5-001**: Task creation API responds in <200ms, event published to Kafka in <100ms additional latency
- **SC-P5-002**: Notification Service processes 99.9% of events successfully with <2 minute end-to-end latency (publish → consume → deliver)
- **SC-P5-003**: Recurring Task Service generates task instances within 5 minutes of scheduled time with 100% accuracy
- **SC-P5-004**: All backend pods achieve statelessness - any pod can handle any request with full conversation context from Redis
- **SC-P5-005**: System remains operational during Kafka downtime - task operations succeed, events queued for later
- **SC-P5-006**: Production deployment on DOKS with Redpanda Cloud achieves 0 authentication errors and 99.9% uptime
- **SC-P5-007**: Dapr sidecars add <5 seconds to pod startup time and <10ms latency per operation
- **SC-P5-008**: All services horizontally scalable - increasing replicas from 1 to 3 shows linear throughput improvement
- **SC-P5-009**: Event-driven architecture supports 1000+ concurrent users with <1% error rate
- **SC-P5-010**: DevOps can deploy full Phase 5 stack to fresh DOKS cluster in <30 minutes following documentation

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Phase 5: Event-Driven Architecture                  │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js       │         │   FastAPI        │         │   Neon          │
│   Frontend      │ ◄────►  │   Backend        │ ◄────►  │   PostgreSQL    │
│   (Vercel)      │  JWT    │   + Dapr Sidecar │  SQL    │   (Tasks, Users)│
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │ Pub/Sub (HTTP)
                                     ▼
                            ┌──────────────────┐
                            │   Dapr Sidecar   │
                            │   (Port 3500)    │
                            └──────────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                ▼                    ▼                    ▼
       ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
       │  Kafka/Redpanda │  │  Redis State    │  │  Cron Binding   │
       │  (task-events)  │  │  Store (Cache)  │  │  (@every 5m)    │
       └─────────────────┘  └─────────────────┘  └─────────────────┘
                │                    │                    │
       ┌────────┴────────┐           │           ┌────────┴────────┐
       │                 │           │           │                 │
       ▼                 ▼           ▼           ▼                 ▼
┌─────────────┐   ┌─────────────┐   │   ┌─────────────┐   ┌─────────────┐
│ Notification│   │  Analytics  │   │   │  Recurring  │   │   Future    │
│  Service    │   │  Service    │   │   │Task Service │   │  Services   │
│ + Daprd     │   │ + Daprd     │   │   │  + Daprd    │   │  + Daprd    │
└─────────────┘   └─────────────┘   │   └─────────────┘   └─────────────┘
       │                             │           │
       ▼                             ▼           ▼
┌─────────────┐            ┌─────────────┐   ┌─────────────┐
│  SendGrid   │            │Conversation │   │  Generate   │
│  (Email)    │            │   History   │   │ Task        │
└─────────────┘            │  (Chats)    │   │ Instances   │
                           └─────────────┘   └─────────────┘

Environment: Minikube (local) → DOKS + Redpanda Cloud (production)
```

---

## Migration Path

Phase 5 follows a deliberate sequence to minimize risk:

1. **Database Schema Evolution** (009-advanced-task-features)
   - Extend schema with priorities, tags, recurring_tasks tables
   - Run Alembic migrations on local SQLite and production Neon
   - Update SQLModel models and REST API endpoints
   - Update frontend UI for new features

2. **Local Dapr Infrastructure** (008-event-driven-dapr)
   - Install Dapr on Minikube: `dapr init --kubernetes`
   - Deploy local Kafka (or Redpanda) via Helm
   - Deploy local Redis via Helm
   - Create Dapr components: kafka-pubsub, statestore, reminder-cron

3. **Backend Dapr Integration** (008-event-driven-dapr)
   - Add Dapr sidecar to backend Helm chart (annotations)
   - Implement event publisher using httpx to localhost:3500
   - Update task endpoints to publish events (non-blocking)
   - Verify events appear in Kafka logs

4. **Microservices Implementation** (010-microservices)
   - Build Notification Service (FastAPI + Dapr subscription)
   - Build Recurring Task Service (FastAPI + cron handler)
   - Deploy both services to Minikube with Dapr sidecars
   - Verify end-to-end event flow: create task → event → notification sent

5. **Cloud Deployment** (011-cloud-doks-deployment)
   - Provision DOKS cluster, Redpanda Cloud, DO Managed Redis
   - Update Dapr components with production credentials (secretKeyRef)
   - Deploy Helm charts with Dapr annotations
   - Verify 0 auth errors, 99.9% event delivery

---

## Assumptions

- Phase 4 (Minikube deployment) is fully operational
- Minikube cluster has sufficient resources (8GB RAM, 4 CPU)
- Dapr CLI is installed (`dapr version` works)
- Helm 3.x is installed and configured
- DigitalOcean account with DOKS access (for Phase 5.5)
- Redpanda Cloud account or alternative managed Kafka (for Phase 5.5)
- Frontend remains deployed on Vercel (frontend changes minimal in Phase 5)
- PostgreSQL database (Neon) is accessible from both local and DOKS
- DevOps has cluster-admin permissions for Dapr installation
- Budget approved for cloud services (DOKS, Redpanda Cloud, DO Managed Redis)

---

## Out of Scope

**Not included in Phase 5**:

- Service mesh beyond Dapr (Istio, Linkerd)
- Advanced observability (distributed tracing with Jaeger/Zipkin)
- GitOps deployment automation (ArgoCD, Flux)
- Multi-region deployment or global load balancing
- Advanced Kafka features (Schema Registry, Kafka Streams)
- Dapr actors or workflows
- Frontend architectural changes (remains on Vercel)
- Mobile app development
- Advanced analytics or business intelligence
- Disaster recovery and backup automation
- Cost optimization and FinOps
- Security hardening beyond TLS/SSL (network policies, pod security policies)
- Performance testing and load testing
- End-to-end integration tests (manual testing sufficient for Phase 5)

---

## Dependencies

**Phase 5 depends on**:
- Phase 4 (Kubernetes/Minikube deployment) ✅ Complete
- Phase 3 (AI Chat Agent) ✅ Complete
- Phase 2 (Backend API + Auth) ✅ Complete

**Phase 5 enables**:
- Phase 6 (Future): Advanced observability, multi-region, GitOps

---

## Component Specifications

For detailed requirements, acceptance criteria, and implementation plans, see:

- **Dapr Infrastructure**: `specs/008-event-driven-dapr/spec.md`
- **Advanced Task Features**: `specs/009-advanced-task-features/spec.md`
- **Microservices**: `specs/010-microservices/spec.md`
- **Cloud Deployment**: `specs/011-cloud-doks-deployment/spec.md`

---

## Next Steps

1. **Complete Component 1**: Dapr infrastructure setup on Minikube
2. **Complete Component 2**: Database schema migration (advanced features)
3. **Complete Component 3**: Microservices implementation (Notification + Recurring Task)
4. **Complete Component 4**: Cloud deployment to DOKS with Redpanda Cloud

**Recommended Command**: `/sp.plan` to create detailed implementation plan for Phase 5 migration.

---

**Created**: 2025-12-11
**Status**: Draft
**Branch**: `005-phase-5`
**Owner**: System Architect
