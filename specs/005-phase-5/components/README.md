# Phase 5 Components

This directory organizes Phase 5 work into four interconnected components. Each component has its own detailed specification in the main `specs/` directory.

## Component Structure

### 1. Dapr Infrastructure (`008-event-driven-dapr`)

**Location**: `specs/008-event-driven-dapr/spec.md`

**Purpose**: Establish event-driven foundation with Dapr, Kafka/Redpanda, and Redis state store.

**Key Deliverables**:
- Dapr control plane installation (Minikube + DOKS)
- kafka-pubsub component configuration
- Redis state store component configuration
- Cron binding for recurring task triggers
- Event schema definitions (TaskEvent, ReminderEvent)
- Backend integration with Dapr HTTP API (httpx to localhost:3500)

**Status**: ✅ Implemented (Dapr client wrapper, event publishing, component YAMLs)

---

### 2. Advanced Task Features (`009-advanced-task-features`)

**Location**: `specs/009-advanced-task-features/spec.md`

**Purpose**: Extend database schema to support priorities, tags, and recurring task templates.

**Key Deliverables**:
- Database tables: priorities, tags, task_tags, recurring_tasks
- Alembic migration scripts
- SQLModel models for new entities
- REST API endpoints (priorities, tags, recurring tasks CRUD)
- Frontend UI updates (priority selector, tag manager)

**Status**: ✅ Implemented (schema complete, API endpoints created)

---

### 3. Microservices (`010-microservices`)

**Location**: `specs/010-microservices/spec.md`

**Purpose**: Build two new event-driven microservices: Notification Service and Recurring Task Service.

**Key Deliverables**:

**Notification Service**:
- Dapr pub/sub subscription to task-events topic
- Event handlers for task.created, task.completed, task.due
- Email notifications via SendGrid
- Push notifications via Firebase Cloud Messaging
- Delivery tracking in Redis state store

**Recurring Task Service**:
- Cron trigger handler (every 5 minutes)
- Recurring task template processing logic
- Task instance generation from templates
- Next occurrence calculation (daily, weekly, monthly, custom cron)
- Event publishing for generated task instances

**Status**: 📋 Specified (awaiting implementation)

---

### 4. Cloud Deployment (`011-cloud-doks-deployment`)

**Location**: `specs/011-cloud-doks-deployment/spec.md`

**Purpose**: Deploy Phase 5 architecture to DigitalOcean Kubernetes with managed cloud services.

**Key Deliverables**:
- DOKS cluster provisioning instructions
- Redpanda Cloud configuration with SASL/SCRAM-SHA-256
- DigitalOcean Managed Redis setup
- Kubernetes Secrets for production credentials
- Updated Dapr components with secretKeyRef
- Helm chart updates with Dapr annotations
- Deployment runbooks and troubleshooting guides

**Status**: 📋 Specified (awaiting cloud infrastructure)

---

## Implementation Order

Follow this sequence for Phase 5 migration:

1. **Component 2 (Advanced Features)** - Database foundation
2. **Component 1 (Dapr Infrastructure)** - Event-driven foundation (✅ Complete)
3. **Component 3 (Microservices)** - Build notification and recurring task services
4. **Component 4 (Cloud Deployment)** - Production deployment to DOKS

---

## Reference Links

- **Phase 5 Overview**: `../spec.md`
- **Migration Plan**: `specs/007-minikube-deployment/phase-v-migration-plan.md`
- **Dapr Infrastructure**: `../../008-event-driven-dapr/spec.md`
- **Advanced Features**: `../../009-advanced-task-features/spec.md`
- **Microservices**: `../../010-microservices/spec.md`
- **Cloud Deployment**: `../../011-cloud-doks-deployment/spec.md`

---

**Last Updated**: 2025-12-11
**Branch**: `005-phase-5`
