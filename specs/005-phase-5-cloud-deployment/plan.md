# Implementation Plan: Phase 5 Event-Driven Architecture with Cloud Deployment

**Branch**: `005-phase-5` | **Date**: 2025-12-11 | **Spec**: [specs/005-phase-5/spec.md](./spec.md)
**Input**: Phase 5 specification from `/specs/005-phase-5/spec.md` + Component 4 detailed spec from `/specs/011-cloud-doks-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase 5 transforms the Todo App from a monolithic Kubernetes deployment (Phase 4) into a cloud-native, event-driven microservices architecture. The implementation strategy focuses on deploying to DigitalOcean Kubernetes Service (DOKS) with managed cloud services (Redpanda Cloud for Kafka, DigitalOcean Managed Redis) while enabling Dapr-based service mesh for pub/sub, state management, and bindings.

**Primary Requirements**:
1. Connect microservices to Redpanda Cloud using SASL/SCRAM-SHA-256 + TLS/SSL
2. Initialize Dapr control plane on DOKS cluster
3. Update Helm charts with Dapr sidecar annotations (`dapr.io/enabled`, `app-id`, `app-port`)
4. Inject Redpanda/Redis credentials via Kubernetes Secrets with `secretKeyRef` in Dapr components

**Technical Approach** (from research):
- Use Dapr 1.13.0+ as service mesh (Phase 5 stack requirement)
- Deploy with Helm 3.x charts updated with Dapr pod annotations
- Store credentials in Kubernetes Secrets (base64-encoded, encrypted at rest)
- Configure Dapr components (kafka-pubsub, statestore) with `secretKeyRef` for runtime credential injection
- Enable automatic Dapr sidecar injection via Kubernetes admission webhooks

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ (FastAPI)
- Frontend: TypeScript 5.x + Next.js 16 (App Router)
- Infrastructure: Kubernetes 1.28+, Dapr 1.13.0+, Helm 3.14+

**Primary Dependencies**:
- **Backend**: FastAPI 0.115+, SQLModel 0.0.22+, httpx 0.27+ (Dapr client), psycopg2 3.2+ (PostgreSQL)
- **Dapr Components**: dapr.io/kafka (pub/sub), dapr.io/redis (state store), dapr.io/cron (bindings)
- **Cloud Services**: DigitalOcean Kubernetes Service (DOKS), Redpanda Cloud (Kafka-compatible), DigitalOcean Managed Redis
- **CLI Tools**: kubectl 1.28+, dapr CLI 1.13+, helm 3.14+, doctl (DigitalOcean CLI)

**Storage**:
- **Primary Database**: Neon Serverless PostgreSQL (already provisioned, Phase 2)
- **Event Streaming**: Redpanda Cloud (Kafka-compatible, SASL/SCRAM-SHA-256, TLS 1.2+)
- **State Store**: DigitalOcean Managed Redis (TLS-enabled, for conversation history and caching)
- **Secrets**: Kubernetes Secrets (etcd encryption at rest)

**Testing**:
- **Unit**: pytest 8.3+ (backend Python), Jest 29+ (frontend TypeScript)
- **Integration**: pytest with test containers, Kubernetes test pods
- **E2E**: Manual testing with Postman/curl for API endpoints, kubectl for Dapr component verification
- **Infrastructure**: `helm lint`, `helm template` for chart validation, `kubectl dry-run` for manifests

**Target Platform**:
- **Local Development**: Minikube 1.32+ on Windows/macOS/Linux (already operational from Phase 4)
- **Production**: DigitalOcean Kubernetes Service (DOKS) - managed Kubernetes 1.28+
- **Deployment Regions**: NYC3 or SFO3 (DigitalOcean data centers, low latency to Redpanda Cloud)

**Project Type**: Web application (multi-service) + Infrastructure as Code (Helm charts, Kubernetes manifests, Dapr components)

**Performance Goals**:
- Task API response time: <200ms p95 (unchanged from Phase 2-4)
- Event publish latency: <100ms from API call to Kafka
- Event consumption latency: <2 minutes from publish to notification delivery
- Dapr sidecar overhead: <10ms per operation, <5s pod startup time increase
- State store operations (Redis): <50ms p95 for get/set
- Horizontal scaling: Linear throughput 1→3 replicas (no bottlenecks)

**Constraints**:
- **Cost**: Minimize cloud costs - use Basic DOKS cluster (2 nodes, 2 vCPU, 4GB RAM per node)
- **Security**: No plaintext credentials in version control, all sensitive data in Kubernetes Secrets
- **Backward Compatibility**: Existing Phase 2-3 deployments on Vercel remain operational during Phase 5 rollout
- **Network**: DOKS → Redpanda Cloud cross-cloud latency <50ms (same geographic region)
- **Availability**: 99.9% uptime SLA for DOKS (DigitalOcean managed), graceful degradation if Kafka unavailable

**Scale/Scope**:
- **Users**: 1000+ concurrent users (Phase 5 success criterion)
- **Services**: 3 microservices (backend, notification-service, recurring-task-service) with Dapr sidecars
- **Events**: 1000+ events/minute during peak load
- **State Store**: 10k conversation histories in Redis (Phase 3 AI chat)
- **Deployment Footprint**: 6-8 pods total (3 app pods + 3 Dapr sidecars + Dapr control plane components)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Transition Discipline (Section IV)
**Requirement**: Phase transitions require explicit governance and updated constitution

✅ **PASS**:
- Phase 4 (Kubernetes/Minikube) is complete and operational (specs/007-minikube-deployment/)
- Phase 5 introduces Dapr + event-driven architecture (approved Phase V technologies)
- Constitution already updated to include Phase IV/V infrastructure standards (version 3.1.0)
- ADR will be created post-planning to document architectural decisions (Redpanda Cloud selection, Dapr adoption rationale)

### Technology Stack Governance (Section III)
**Requirement**: Use ONLY technologies approved for current phase (Phase V)

✅ **PASS**:
- Dapr: Approved for Phase V (service mesh, pub/sub, state store)
- Kafka/Redpanda: Approved for Phase V (event streaming)
- Kubernetes + Helm: Already approved in Phase IV, extended in Phase V
- Managed cloud services (DOKS, Redpanda Cloud, DO Managed Redis): Aligned with Phase V cloud-native focus
- No premature introduction of future technologies (no Istio, ArgoCD, or other advanced service mesh features)

### Infrastructure & DevOps Standards (Section IV, lines 8-13)
**Requirement**: Containerization, Kubernetes deployment, Helm Charts, Secrets management

✅ **PASS**:
- **Containerization**: Docker images already exist from Phase 4 (backend, frontend)
- **Orchestration**: Targeting Kubernetes (DOKS production, Minikube local)
- **Configuration**: Helm Charts will be updated with Dapr annotations (FR-017 to FR-022)
- **Secrets**: Kubernetes Secrets mandatory for Redpanda/Redis credentials (FR-003, FR-004, FR-023)
- **kubectl-ai/kagent compatibility**: Not required for Phase 5 (deferred to Phase 6)

### Spec-First Development (Section I)
**Requirement**: NO code written until spec.md exists and is approved

✅ **PASS**:
- Phase 5 spec created: `specs/005-phase-5/spec.md` (high-level overview)
- Component 4 spec created: `specs/011-cloud-doks-deployment/spec.md` (detailed cloud deployment strategy)
- Component 4 spec validated: `specs/011-cloud-doks-deployment/checklists/requirements.md` ✅ PASSED
- All requirements have testable acceptance criteria (28 functional requirements documented)
- No code has been written yet for cloud deployment (planning phase)

### Evolutionary Architecture (Section II)
**Requirement**: Each phase MUST complete fully before starting next phase

✅ **PASS**:
- Phase 1 (CLI): Complete ✅
- Phase 2 (Web App + Auth): Complete ✅
- Phase 3 (AI Agent + MCP): Complete ✅
- Phase 4 (Kubernetes/Minikube): Complete ✅
- Phase 5 (Event-Driven + Cloud): In Progress 🚧
  - Component 1 (Dapr Infrastructure): Implemented ✅
  - Component 2 (Advanced Features): Implemented ✅
  - Component 3 (Microservices): Specified, not yet implemented
  - Component 4 (Cloud Deployment): Specified, now planning

**No violations detected**. Proceeding to Phase 0 research.

---

## Project Structure

### Documentation (this feature)

```text
specs/005-phase-5/
├── spec.md                    # Phase 5 overview (this consolidates all components)
├── plan.md                    # This file (/sp.plan command output)
├── research.md                # Phase 0 output (NEXT: to be generated)
├── data-model.md              # Phase 1 output (NEXT: to be generated)
├── quickstart.md              # Phase 1 output (NEXT: to be generated)
├── contracts/                 # Phase 1 output (NEXT: deployment manifests, Dapr components)
│   ├── redpanda-secret.yaml  # Kubernetes Secret manifest for Redpanda credentials
│   ├── redis-secret.yaml     # Kubernetes Secret manifest for Redis credentials
│   ├── kafka-pubsub-prod.yaml # Dapr kafka-pubsub component (production, with secretKeyRef)
│   ├── statestore-prod.yaml  # Dapr Redis state store component (production, with secretKeyRef)
│   └── helm-values-prod.yaml # Helm values override for production DOKS deployment
└── components/                # References to detailed component specs
    ├── README.md              # Component organization guide
    ├── dapr-infrastructure.md → specs/008-event-driven-dapr/spec.md
    ├── advanced-features.md → specs/009-advanced-task-features/spec.md
    ├── microservices.md → specs/010-microservices/spec.md
    └── cloud-deployment.md → specs/011-cloud-doks-deployment/spec.md

specs/011-cloud-doks-deployment/  # Component 4 detailed spec
├── spec.md                    # Detailed cloud deployment requirements (28 FRs)
└── checklists/
    └── requirements.md        # Spec validation (✅ PASSED)

specs/008-event-driven-dapr/   # Component 1 (already implemented)
specs/009-advanced-task-features/ # Component 2 (already implemented)
specs/010-microservices/       # Component 3 (specified, awaiting implementation)
```

### Source Code (repository root)

**Structure Decision**: Web application with microservices architecture. Phase 5 extends Phase 4 Kubernetes deployment with Dapr-enabled services and cloud-specific configurations.

```text
backend/                       # FastAPI backend (existing from Phase 2-4)
├── app/
│   ├── dapr/                 # Dapr client wrapper (Component 1, already implemented)
│   │   ├── __init__.py
│   │   └── client.py         # DaprClient class (httpx → localhost:3500)
│   ├── models/               # SQLModel entities (extended in Component 2)
│   │   ├── priority.py       # Priority model (Component 2, implemented)
│   │   ├── tag.py            # Tag model (Component 2, implemented)
│   │   └── recurring_task.py # RecurringTask model (Component 2, implemented)
│   └── routers/
│       └── tasks.py          # Task endpoints with event publishing (Component 1, implemented)
├── requirements.txt          # Python dependencies (httpx>=0.27 for Dapr)
└── Dockerfile                # Multi-stage Docker build (Phase 4, existing)

frontend/                      # Next.js frontend (existing from Phase 2-4)
├── app/
│   ├── dashboard/
│   └── chat/
├── Dockerfile                # Multi-stage Docker build (Phase 4, existing)
└── package.json

notification-service/          # NEW: Component 3 microservice (TO BE CREATED)
├── app/
│   ├── main.py               # FastAPI with Dapr subscription endpoint
│   ├── handlers/             # Event handlers (task.created, task.completed, task.due)
│   │   ├── task_events.py
│   │   └── notification_providers.py
│   └── config.py
├── requirements.txt          # FastAPI, httpx, sendgrid, firebase-admin
├── Dockerfile                # Multi-stage Docker build
└── README.md

recurring-task-service/        # NEW: Component 3 microservice (TO BE CREATED)
├── app/
│   ├── main.py               # FastAPI with cron binding endpoint
│   ├── services/
│   │   ├── task_generator.py
│   │   └── schedule_calculator.py
│   └── config.py
├── requirements.txt          # FastAPI, SQLModel, croniter, httpx
├── Dockerfile                # Multi-stage Docker build
└── README.md

infrastructure/                # Kubernetes manifests and Dapr components
├── dapr/
│   └── components/           # Dapr component YAMLs
│       ├── kafka-pubsub.yaml         # Local Minikube (Component 1, implemented)
│       ├── kafka-pubsub-prod.yaml    # DOKS production with secretKeyRef (TO BE CREATED)
│       ├── statestore.yaml           # Local Minikube (Component 1, implemented)
│       ├── statestore-prod.yaml      # DOKS production with secretKeyRef (TO BE CREATED)
│       └── reminder-cron.yaml        # Cron binding (Component 1, implemented)
├── helm/
│   └── todo-chart/           # Helm chart for all services
│       ├── Chart.yaml
│       ├── values.yaml               # Default values (Minikube)
│       ├── values-prod.yaml          # Production values for DOKS (TO BE CREATED)
│       └── templates/
│           ├── backend-deployment.yaml       # Updated with Dapr annotations (TO BE UPDATED)
│           ├── frontend-deployment.yaml      # Updated with Dapr annotations (TO BE UPDATED)
│           ├── notification-deployment.yaml  # NEW (TO BE CREATED)
│           ├── recurring-task-deployment.yaml # NEW (TO BE CREATED)
│           ├── redpanda-secret.yaml          # NEW (TO BE CREATED)
│           └── redis-secret.yaml             # NEW (TO BE CREATED)
└── digitalocean/              # DOKS-specific deployment artifacts (TO BE CREATED)
    ├── cluster-config.yaml   # DOKS cluster configuration (doctl reference)
    ├── deploy-doks.sh        # Deployment script for DOKS
    └── README.md             # DOKS deployment runbook

.github/                       # CI/CD (optional, deferred to Phase 6)
└── workflows/
    └── deploy-doks.yml       # GitHub Actions for DOKS deployment (optional)

docs/                          # Deployment documentation
├── DEPLOYMENT_GUIDE.md       # General deployment guide (existing from Phase 4)
├── MINIKUBE_DEPLOYMENT_GUIDE.md # Minikube-specific guide (existing from Phase 4)
└── DOKS_DEPLOYMENT_GUIDE.md  # NEW: DigitalOcean Kubernetes deployment guide (TO BE CREATED)

tests/                         # Test suite
├── integration/
│   ├── test_dapr_pubsub.py   # Test Dapr pub/sub with Kafka
│   └── test_dapr_statestore.py # Test Dapr state store with Redis
└── e2e/
    └── test_cloud_deployment.py # E2E tests for DOKS deployment
```

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected**. All Phase 5 work aligns with constitutional requirements:
- Phase 4 complete before starting Phase 5 ✅
- Technologies approved for Phase V (Dapr, Kafka/Redpanda, cloud services) ✅
- Spec-first development followed (specs exist and validated) ✅
- Infrastructure standards met (Kubernetes, Helm, Secrets) ✅

---

## Phase 0: Research & Technology Decisions

**Goal**: Resolve all unknowns and make informed technology decisions for cloud deployment.

### Research Tasks

1. **Redpanda Cloud Setup & Authentication**
   - **Question**: How to provision Redpanda Cloud cluster and obtain SASL/SCRAM-SHA-256 credentials?
   - **Research**: Redpanda Cloud onboarding docs, credential generation flow, broker URL format
   - **Deliverable**: Step-by-step guide in research.md with screenshots/examples

2. **DigitalOcean Kubernetes Service (DOKS) Provisioning**
   - **Question**: How to provision DOKS cluster via doctl CLI or web console? What node size/count for Phase 5 workload?
   - **Research**: DOKS pricing tiers, node configurations, cluster creation via doctl
   - **Deliverable**: DOKS provisioning commands and cost estimates

3. **Dapr on DOKS Installation**
   - **Question**: How to install Dapr control plane on DOKS? Any DOKS-specific considerations?
   - **Research**: `dapr init --kubernetes` on DOKS, namespace configuration, admission webhooks
   - **Deliverable**: Dapr installation commands and verification steps

4. **Kubernetes Secrets with secretKeyRef in Dapr Components**
   - **Question**: How to reference Kubernetes Secrets in Dapr component metadata using `secretKeyRef`?
   - **Research**: Dapr documentation for secret references, Kubernetes Secret best practices
   - **Deliverable**: Example Dapr component YAML with `secretKeyRef` syntax

5. **Helm Chart Dapr Annotations**
   - **Question**: What Dapr annotations are required in Helm chart pod templates? How to make them configurable via values.yaml?
   - **Research**: Dapr Kubernetes integration docs, annotation reference
   - **Deliverable**: Helm template snippet with conditional Dapr annotations

6. **DigitalOcean Managed Redis Configuration**
   - **Question**: How to provision DO Managed Redis and connect from DOKS with TLS?
   - **Research**: DO Redis pricing, connection strings, TLS certificate handling
   - **Deliverable**: Redis provisioning guide and Dapr statestore component config

7. **Cross-Cloud Networking (DOKS ↔ Redpanda Cloud)**
   - **Question**: What are latency considerations for DOKS (NYC3) connecting to Redpanda Cloud (AWS us-east-1)?
   - **Research**: Network latency benchmarks, Redpanda Cloud region options, VPC peering feasibility
   - **Deliverable**: Network architecture diagram and latency expectations

8. **Credential Rotation Strategy**
   - **Question**: How to rotate Redpanda/Redis credentials in production without downtime?
   - **Research**: Kubernetes Secret updates, pod restart strategies, Dapr credential refresh behavior
   - **Deliverable**: Credential rotation runbook with step-by-step commands

**Output**: `specs/005-phase-5/research.md` (to be generated in next step)

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### 1.1 Data Model

**Entities** (no new database entities in Component 4):
- Phase 5 Component 2 (Advanced Features) already added: priorities, tags, task_tags, recurring_tasks tables
- Component 4 (Cloud Deployment) focuses on infrastructure configuration, not data model changes
- Existing entities: User, Task, Conversation, Message, Priority, Tag, TaskTag, RecurringTask

**Data Model Output**: `specs/005-phase-5/data-model.md` will reference Component 2 schema extensions and confirm no new entities for cloud deployment.

### 1.2 API Contracts

**Infrastructure Contracts** (Component 4 focuses on deployment configuration, not API changes):

1. **Kubernetes Secret Manifests**:
   - `contracts/redpanda-secret.yaml`: Kubernetes Secret for Redpanda Cloud credentials
   - `contracts/redis-secret.yaml`: Kubernetes Secret for DigitalOcean Managed Redis credentials

2. **Dapr Component Configurations** (Production):
   - `contracts/kafka-pubsub-prod.yaml`: Dapr pub/sub component with SASL/SSL and secretKeyRef
   - `contracts/statestore-prod.yaml`: Dapr Redis state store with TLS and secretKeyRef

3. **Helm Chart Values Override**:
   - `contracts/helm-values-prod.yaml`: Production-specific Helm values for DOKS deployment

**API Endpoints** (no changes in Component 4):
- All REST API endpoints defined in Phase 2 remain unchanged
- Event publishing added in Component 1 (already implemented) - no new HTTP endpoints

### 1.3 Quickstart Guide

**Output**: `specs/005-phase-5/quickstart.md` - Developer onboarding guide covering:
- Local Minikube setup with Dapr (Component 1 recap)
- DOKS cluster provisioning steps
- Redpanda Cloud + DO Managed Redis setup
- Helm chart deployment to DOKS
- Verification steps (Dapr status, event flow, pod health)

### 1.4 Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to update `.claude/` context files with Phase 5 technologies:
- Add: Dapr 1.13.0, Redpanda Cloud, DigitalOcean Kubernetes Service, Helm 3.14+
- Add: Kubernetes Secrets with secretKeyRef pattern
- Add: Dapr annotations for sidecar injection

---

## Phase 2: Task Breakdown

**NOT INCLUDED IN `/sp.plan`**. Run `/sp.tasks` separately after planning is complete.

Expected task categories:
- **Infrastructure Provisioning**: DOKS cluster, Redpanda Cloud, DO Managed Redis
- **Dapr Setup**: Install control plane on DOKS, verify sidecar injection
- **Configuration**: Create Kubernetes Secrets, update Dapr components with secretKeyRef
- **Helm Charts**: Add Dapr annotations to all service deployments
- **Deployment**: Deploy services to DOKS, verify event flow
- **Testing**: E2E tests for cloud deployment, credential rotation tests
- **Documentation**: DOKS deployment runbook, troubleshooting guide

---

## Next Steps

1. **Generate Phase 0 Research**: Create `research.md` with answers to all 8 research questions
2. **Generate Phase 1 Design**: Create `data-model.md`, `contracts/`, and `quickstart.md`
3. **Update Agent Context**: Run update-agent-context.ps1 to add Phase 5 technologies
4. **Run `/sp.tasks`**: Generate actionable task list with test cases
5. **Implement Components 3-4**: Build microservices and deploy to DOKS

**Branch**: `005-phase-5` (already checked out)
**Spec Status**: ✅ Validated (specs/011-cloud-doks-deployment/checklists/requirements.md)
**Planning Status**: ✅ Complete (this file)
**Ready for**: Research phase (Phase 0) → Design phase (Phase 1) → Task generation (`/sp.tasks`)

---

**Created**: 2025-12-11
**Author**: Claude Sonnet 4.5 via `/sp.plan` command
**Phase**: Phase 5 - Event-Driven Architecture with Cloud Deployment
**Component Focus**: Component 4 (Cloud Deployment to DOKS with Redpanda Cloud)
