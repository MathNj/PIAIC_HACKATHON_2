# Todo App Overview

## Purpose
A todo application that evolves from console app to cloud-native microservices through five phases.

## Current Phase
Phase 5: Event-Driven Architecture with Dapr, Kafka, and Cloud Deployment 🚧 **In Progress**

## Phase Progress
- **Phase 1**: Console CRUD Application ✅ **Completed**
- **Phase 2**: Full-Stack Web Application ✅ **Completed** (Deployed to Vercel)
- **Phase 3**: AI Chat Agent with OpenAI Agents SDK ✅ **Completed** (Deployed to Vercel)
- **Phase 4**: Kubernetes & Minikube Deployment ✅ **Completed**
- **Phase 5**: Event-Driven Architecture (Dapr/Kafka/DigitalOcean) 🚧 **In Progress**

## Tech Stack

### Core Application
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python 3.13+, FastAPI, SQLModel
- **Database**: Neon Serverless PostgreSQL (SQLite for local)
- **Auth**: Better Auth with JWT tokens

### AI & Integration (Phase 3)
- **AI**: OpenAI Agents SDK + Gemini 2.5 Flash
- **MCP**: Model Context Protocol for tool integration

### Cloud-Native (Phase 4-5)
- **Kubernetes**: Minikube (local), DigitalOcean Kubernetes Service (production)
- **Service Mesh**: Dapr (pub/sub, state store, bindings)
- **Event Streaming**: Kafka/Redpanda (local), Redpanda Cloud (production)
- **State Store**: Redis (local), DigitalOcean Managed Redis (production)
- **Containerization**: Docker, Helm charts

### Deployment
- **Phase 1-3**: Vercel (Backend + Frontend)
- **Phase 4-5**: Kubernetes (Minikube → DOKS)

## Features Status

### ✅ Phase 1 - Console App (Completed)
**Spec**: `specs/001-phase-1/spec.md`

- [x] Console CRUD operations
- [x] Task management (add, view, update, delete, mark complete)
- [x] Input validation and error handling

---

### ✅ Phase 2 - Backend API (Completed & Deployed to Vercel)
**Spec**: `specs/002-phase-2/spec.md`

- [x] Backend API infrastructure (FastAPI)
- [x] User authentication (signup/login with JWT)
- [x] JWT token generation and verification
- [x] Database models (User, Task, Conversation, Message)
- [x] Password hashing with bcrypt
- [x] CORS configuration (all Vercel domains)
- [x] Task CRUD API endpoints (create, read, update, delete)
- [x] Task completion toggle endpoint
- [x] **Deployed to Vercel**: https://backend-pl7shcy6m-mathnjs-projects.vercel.app

---

### ✅ Phase 3 - AI Chat Agent (Completed & Deployed to Vercel)
**Spec**: `specs/003-phase-3-ai-agent/spec.md`

- [x] OpenAI Agents SDK integration with Gemini 2.5 Flash
- [x] Agent/Runner pattern implementation
- [x] MCP tools for task operations (list, create, update, delete, toggle)
- [x] Conversation persistence (database-backed chat history)
- [x] Chat API endpoint (POST /api/{user_id}/chat)
- [x] JWT authentication for chat endpoint
- [x] Tool call logging and execution
- [x] Frontend chat UI (basic React interface)
- [x] **Deployed to Vercel**: Backend with AI agent live

---

### ✅ Phase 4 - Kubernetes & Minikube (Completed)
**Specs**: `specs/004-k8s-blueprint/`, `specs/005-docker-containers/`, `specs/006-helm-chart/`, `specs/007-minikube-deployment/`

- [x] Docker containerization (backend + frontend)
- [x] Kubernetes manifests (Deployment, Service, ConfigMap, Secret)
- [x] Helm charts for package management
- [x] Minikube local cluster deployment
- [x] Database migration strategy
- [x] Port-forwarding for local access
- [x] Resource limits and health checks

---

### 🚧 Phase 5 - Event-Driven Architecture (In Progress)
**Spec**: `specs/005-phase-5/spec.md` ⭐ **Consolidated Phase 5 Spec**

**Components** (see `specs/005-phase-5/components/README.md`):

#### Component 1: Dapr Infrastructure ✅ Implemented
**Spec**: `specs/008-event-driven-dapr/spec.md`

- [x] Dapr control plane installation (Minikube)
- [x] kafka-pubsub component configuration
- [x] Redis state store component configuration
- [x] Cron binding for recurring task triggers
- [x] Event schema definitions
- [x] Backend Dapr client wrapper (httpx → localhost:3500)
- [x] Event publishing in task endpoints

#### Component 2: Advanced Task Features ✅ Implemented
**Spec**: `specs/009-advanced-task-features/spec.md`

- [x] Database schema: priorities, tags, task_tags, recurring_tasks tables
- [x] SQLModel models for new entities
- [x] REST API endpoints (priorities, tags, recurring tasks CRUD)
- [x] Alembic migrations

#### Component 3: Microservices 📋 Specified
**Spec**: `specs/010-microservices/spec.md`

- [ ] Notification Service (email, push notifications)
- [ ] Recurring Task Service (cron-based task generation)
- [ ] Dapr pub/sub subscriptions
- [ ] Event handlers (task.created, task.completed, task.due)

#### Component 4: Cloud Deployment 📋 Specified
**Spec**: `specs/011-cloud-doks-deployment/spec.md`

- [ ] DigitalOcean Kubernetes Service (DOKS) provisioning
- [ ] Redpanda Cloud configuration (SASL/SSL)
- [ ] DigitalOcean Managed Redis setup
- [ ] Kubernetes Secrets for production credentials
- [ ] Helm chart updates with Dapr annotations
- [ ] Production deployment runbooks

## Architecture

### Phase 1-3: Monolithic Deployment (Vercel)
```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js       │         │   FastAPI        │         │   Neon          │
│   Frontend      │ ◄────►  │   Backend        │ ◄────►  │   PostgreSQL    │
│   (Vercel)      │  JWT    │   (Vercel)       │  SQL    │   (Cloud)       │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │   Gemini 2.5     │
                           │   + MCP Tools    │
                           └──────────────────┘
```

### Phase 4-5: Event-Driven Microservices (Kubernetes)
```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js       │         │   FastAPI        │         │   Neon          │
│   Frontend      │ ◄────►  │   Backend        │ ◄────►  │   PostgreSQL    │
│   (Vercel)      │  JWT    │   + Dapr Sidecar │  SQL    │   (Tasks)       │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │ Pub/Sub
                                     ▼
                            ┌──────────────────┐
                            │ Kafka/Redpanda   │
                            │  (task-events)   │
                            └──────────────────┘
                ┌──────────────────┼──────────────────┐
                │                  │                  │
                ▼                  ▼                  ▼
       ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
       │  Notification   │ │  Recurring Task │ │  Redis State    │
       │  Service        │ │  Service        │ │  Store (Cache)  │
       │  + Dapr Sidecar │ │  + Dapr Sidecar │ └─────────────────┘
       └─────────────────┘ └─────────────────┘
```

## Current Status (Phase 5 - In Progress)

### Completed
- **Phase 1-3**: ✅ Fully deployed to Vercel
- **Phase 4**: ✅ Kubernetes/Minikube deployment operational
- **Phase 5 Component 1**: ✅ Dapr infrastructure setup (Dapr client, event publishing, component YAMLs)
- **Phase 5 Component 2**: ✅ Advanced task features (priorities, tags, recurring tasks schema)

### In Progress
- **Phase 5 Component 3**: 📋 Microservices (Notification + Recurring Task services)
- **Phase 5 Component 4**: 📋 Cloud deployment to DOKS with Redpanda Cloud

### Infrastructure Status
- **Backend API**: ✅ Deployed to Vercel + Running on Minikube with Dapr
- **Frontend**: ✅ Deployed to Vercel + Running on Minikube
- **Database**: ✅ Neon PostgreSQL (production) + SQLite (local)
- **Kubernetes**: ✅ Minikube cluster operational with Dapr control plane
- **Event Streaming**: ✅ Local Kafka configured, Redpanda Cloud pending
- **State Store**: ✅ Local Redis configured, DO Managed Redis pending

---

## Phase 5 Accomplishments So Far
1. ✅ Created consolidated Phase 5 specification (`specs/005-phase-5/spec.md`)
2. ✅ Installed Dapr control plane on Minikube
3. ✅ Implemented Dapr client wrapper (httpx → localhost:3500)
4. ✅ Updated backend to publish events (task.created, task.updated, task.completed)
5. ✅ Created Dapr component YAMLs (kafka-pubsub, statestore, reminder-cron)
6. ✅ Extended database schema with priorities, tags, recurring_tasks tables
7. ✅ Created REST API endpoints for new entities

---

## Next Steps (Phase 5 Continuation)
1. **Implement Notification Service**: Build FastAPI microservice with Dapr pub/sub subscription
2. **Implement Recurring Task Service**: Build cron-triggered service for task generation
3. **Test Microservices Locally**: Verify end-to-end event flow on Minikube
4. **Provision Cloud Infrastructure**: DOKS, Redpanda Cloud, DO Managed Redis
5. **Deploy to Production**: Migrate from Minikube to DOKS with updated Dapr components
6. **Monitoring & Observability**: Set up Grafana dashboards and alerting

---

## Spec Organization

All project specifications are in `specs/` directory:
- **Overview**: `specs/overview.md` (this file)
- **Phase 1**: `specs/001-phase-1/spec.md`
- **Phase 2**: `specs/002-phase-2/spec.md`
- **Phase 3**: `specs/003-phase-3-ai-agent/spec.md`
- **Phase 4**: `specs/004-k8s-blueprint/` through `specs/007-minikube-deployment/`
- **Phase 5**: `specs/005-phase-5/spec.md` ⭐ (consolidates components 008-011)
