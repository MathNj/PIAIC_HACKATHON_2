# The Evolution of TODO: Project Constitution
<!--
SYNC IMPACT REPORT:
Version: 3.0.0 → 3.1.0
Change Type: MINOR - Phase IV/V infrastructure skills added, transition readiness documented
Modified Principles:
  - Phase III section → Added Skills Infrastructure Readiness subsection
  - Phase IV section → Added Infrastructure Skills subsection
  - Phase V section → Added Infrastructure Skills subsection
Added Sections:
  - Phase III Skills Infrastructure Readiness
  - Phase IV Infrastructure Skills (docker-ai-pilot, kubectl-ai-pilot, kagent-debugger)
  - Phase V Infrastructure Skills (dapr-scheduler, kafka-infra-provisioner, blueprint-architect)
  - Phase Transition Readiness Checklist
Removed Sections: None
Skills Created:
  ✅ Phase III: mcp-tool-maker, chatkit-integrator, openai-agents-sdk, agent-orchestrator
  ✅ Phase IV: docker-ai-pilot, kubectl-ai-pilot, kagent-debugger
  ✅ Phase V: dapr-scheduler, kafka-infra-provisioner, blueprint-architect
Templates Status:
  ✅ plan-template.md - Constitution Check section aligns with Phase III-V constraints
  ✅ spec-template.md - Requirements structure compatible with multi-phase architecture
  ✅ tasks-template.md - Task categorization supports infrastructure provisioning
Follow-up TODOs:
  - Complete Phase III MCP tool implementations
  - Test Phase IV Kubernetes deployment with created skills
  - Validate Phase V event-driven architecture with Kafka and Dapr skills
  - Document phase transition ADRs for Phase III → IV → V
-->

## Project Vision

**Project Name**: The Evolution of TODO

**Philosophy**: This application MUST evolve through distinct architectural phases, starting simple (CLI) and progressing to cloud-native AI-powered systems. Each phase builds upon the previous, demonstrating architectural evolution from monolithic scripts to event-driven microservices.

**Role Definition**: You are the Chief System Architect and Lead Engineer responsible for guiding this evolution while maintaining system integrity and spec-driven discipline at every stage.

## Core Principles (Across All Phases)

### I. Spec-First Development (NON-NEGOTIABLE)

Every feature MUST begin with a written specification before any code is written. The specification defines the business requirements, user stories, acceptance criteria, and success metrics in technology-agnostic terms.

**Rules:**
- NO code written until spec.md exists and is approved
- Specifications capture "what" and "why", never "how"
- All requirements MUST have testable acceptance criteria
- Unclear requirements marked with NEEDS CLARIFICATION
- Specs are versioned and maintained as living documents
- This principle applies to ALL phases without exception

**Rationale:** Prevents scope creep, misaligned implementations, and wasted development effort. Ensures all stakeholders agree on requirements before technical decisions are made. Critical for managing complexity as system evolves across phases.

### II. Evolutionary Architecture

The application MUST transition gracefully through defined architectural phases. Each phase introduces new capabilities while maintaining backward compatibility where feasible.

**Architecture Evolution Path:**
1. **Phase I**: Monolithic Script (single file CLI) ✅ COMPLETED
2. **Phase II**: Modular Monolith (web app with clear module boundaries) ✅ COMPLETED
3. **Phase III**: Agent-Augmented System (AI agents + MCP integration) 🚧 CURRENT
4. **Phase IV**: Microservices (containerized, orchestrated services)
5. **Phase V**: Event-Driven Architecture (Kafka + Dapr + cloud-native)

**Rules:**
- Each phase MUST complete fully before starting next phase
- Phase transitions require ADR (Architectural Decision Record) documenting rationale
- Migration path from previous phase MUST be documented in spec
- Breaking changes require major version bump and explicit justification
- No skipping phases (evolutionary, not revolutionary)

**Rationale:** Controlled evolution prevents "big bang" rewrites and allows learning from each architectural pattern. Demonstrates real-world progression from simple to complex systems.

### III. Technology Stack Governance

Each phase has a defined technology stack that MUST be respected. No premature introduction of future-phase technologies.

**Phase-Specific Stacks:**
- **Phase I**: Python 3.13+ CLI (standard library only) ✅ COMPLETED
- **Phase II**: Next.js frontend + FastAPI backend + Neon (PostgreSQL) ✅ COMPLETED
- **Phase III**: Phase II stack + OpenAI Agents SDK + MCP Python SDK + OpenAI ChatKit 🚧 CURRENT
- **Phase IV**: Phase III stack + Kubernetes + Helm charts
- **Phase V**: Phase IV stack + Kafka + Dapr + cloud services

**Rules:**
- Use ONLY technologies approved for current phase
- External dependencies require explicit constitution approval
- Technology choices documented in ADRs with rationale
- New technologies introduced only during phase transitions
- Backward compatibility maintained during stack evolution

**Rationale:** Enforces architectural discipline and prevents technology sprawl. Ensures each phase demonstrates specific architectural patterns without conflation.

### IV. Phase Transition Discipline

Transitioning between phases requires explicit governance and cannot occur mid-feature.

**Rules:**
- Phase transitions require updated constitution (MAJOR version bump)
- All Phase N features MUST be complete before Phase N+1 begins
- Migration strategy from Phase N to Phase N+1 documented in ADR
- No mixing of phase technologies (clean boundaries)
- User-facing features remain functional during transitions

**Rationale:** Prevents architectural chaos and ensures each phase is fully validated before evolution. Maintains system stability during transitions.

## Phase I: Monolithic Script ✅ COMPLETED

### Storage Constraints
In-memory data structures (lists, dictionaries) for all data storage. NO persistent storage mechanisms permitted in Phase I.

**Phase Transition:** Phase II introduced Neon (PostgreSQL) for persistence.

### Dependency Constraints
Python standard library only. NO external dependencies or third-party packages permitted in Phase I.

**Phase Transition:** Phase II introduced FastAPI, Next.js, and Neon client libraries.

### Interface Constraints
Continuous interactive loop with menu-driven interface for all operations.

**Phase Transition:** Phase II replaced CLI with Next.js web UI + FastAPI REST endpoints.

## Phase II: Modular Monolith ✅ COMPLETED

### Storage Implementation
Neon PostgreSQL with SQLModel ORM for data persistence. Multi-user isolation with user_id foreign keys.

**Achievements:**
- Task CRUD operations with priority and due dates
- User authentication with JWT tokens
- Database migrations with proper indexing
- Multi-user data isolation

### Technology Stack Implemented
- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI 0.95.2 with SQLModel 0.0.14
- **Database**: Neon PostgreSQL (SQLite for local development)
- **Authentication**: JWT with Better Auth pattern
- **Testing**: pytest with 37 tests passing
- **Deployment**: Vercel (both frontend and backend)

### Interface Implementation
Web UI with REST API following OpenAPI specification.

**Phase Transition:** Phase III builds upon this stack by adding AI agents and MCP integration.

## Phase III: Agent-Augmented System 🚧 CURRENT PHASE

### Architecture Pattern

The application MUST implement a stateless AI Agent using the Model Context Protocol (MCP). The agent serves as an intelligent assistant that manages the user's TODO list through natural language interaction.

**Core Pattern:**
- **Agent Type**: Stateless AI assistant (no in-memory conversation state)
- **Communication Protocol**: Model Context Protocol (MCP)
- **Frameworks**: OpenAI Agents SDK + Official MCP Python SDK + OpenAI ChatKit (Frontend)
- **Integration**: Agent layer sits above Phase II backend, consuming existing Task API

**Rules:**
- Agent MUST be stateless (NO in-memory state retention)
- All conversation history fetched from database on every request
- Agent communicates with backend exclusively through MCP tools
- Agent cannot directly access database (must use MCP tools)
- Agent identity: Helpful assistant managing user's specific TODO list

**Rationale:** Stateless design ensures scalability, fault tolerance, and consistent behavior. MCP provides standardized protocol for AI-application integration. Separates AI layer from business logic, maintaining Phase II architecture integrity.

### State Management (CRITICAL CONSTRAINT)

The AI Agent MUST be completely stateless. ALL conversation history MUST be persisted in the database and fetched on every request.

**Rules:**
- NO in-memory conversation state in agent runtime
- ALL messages stored in `conversations` and `messages` tables
- Conversation history fetched from database at request start
- Conversation state saved to database before request completion
- Agent runtime can be restarted without losing conversation context
- Multiple agent instances can serve same user (load balancing compatible)

**Database Schema Requirements:**
- `conversations` table: id, user_id, title, created_at, updated_at
- `messages` table: id, conversation_id, role (user|assistant), content, created_at

**Rationale:** Stateless architecture enables horizontal scaling, fault tolerance, and session persistence. Supports multi-instance deployment without sticky sessions. Conversation history becomes valuable data asset for analytics and improvement.

### MCP Compliance (NON-NEGOTIABLE)

ALL Task operations MUST be implemented as strict MCP Tools. The agent CANNOT access the backend directly.

**Required MCP Tools:**
- `list_tasks`: Retrieve all tasks for authenticated user
- `create_task`: Create new task from natural language description
- `update_task`: Modify existing task properties
- `delete_task`: Remove task by ID
- `toggle_task_completion`: Mark task as complete/incomplete
- `get_task_summary`: Get analytics and task statistics
- `suggest_task_prioritization`: AI-powered task ordering recommendations

**MCP Tool Requirements:**
- Each tool MUST accept user authentication token (JWT)
- Each tool MUST return structured JSON or string interpretable by LLM
- Each tool MUST handle errors gracefully with user-friendly messages
- Each tool MUST validate user_id from token matches target user_id
- Each tool MUST include comprehensive docstrings (LLM reads these)

**File Structure:**
- `backend/mcp/`: MCP tool definitions
- `backend/mcp/server.py`: MCP server initialization and tool registration
- `backend/agents/`: Agent runner logic and orchestration
- `backend/models.py`: Updated with Conversation and Message models

**Rationale:** MCP standardizes AI-application communication. Tool-based architecture provides clear boundaries, testability, and auditability. Agent cannot bypass business logic or security constraints.

### Security Constraints (CRITICAL)

The Agent MUST strictly respect user_id boundaries. It CANNOT access data belonging to other users.

**Rules:**
- Agent MUST extract user_id from JWT token in every request
- All MCP tools MUST validate token-derived user_id matches path user_id
- Agent CANNOT list, view, modify, or delete tasks for other users
- Failed user_id validation MUST return 403 Forbidden
- Agent conversations scoped to single user (no cross-user data leakage)
- All agent requests require valid JWT authentication

**Rationale:** Multi-tenancy security is non-negotiable. Agent acts on behalf of authenticated user only. Prevents data leakage and unauthorized access through AI interface.

### Natural Language Processing

The Agent MUST parse natural language task descriptions to extract structured data.

**Extraction Requirements:**
- **Title**: Concise task name (first 100 chars or semantic extraction)
- **Priority**: Infer from urgency keywords ("urgent", "asap", "critical" → high)
- **Due Date**: Parse temporal expressions ("tomorrow", "next week", ISO dates)
- **Description**: Full context preserved in description field

**Examples:**
- Input: "Buy groceries tomorrow"
  - Title: "Buy groceries"
  - Due Date: tomorrow's date
  - Priority: normal

- Input: "URGENT: Fix production bug"
  - Title: "Fix production bug"
  - Priority: high
  - Due Date: null

- Input: "Schedule dentist appointment next Monday at 2pm"
  - Title: "Schedule dentist appointment"
  - Due Date: next Monday 14:00
  - Priority: normal

**Rationale:** Natural language input removes friction from task creation. LLM excels at semantic parsing. Structured extraction enables proper database storage and querying.

### Frontend Integration

OpenAI ChatKit MUST be integrated into the Next.js frontend for agent interaction.

**Requirements:**
- ChatKit component in dashboard or dedicated `/agent` route
- MCP tool discovery endpoint (`GET /api/mcp/tools`)
- MCP tool execution endpoint (`POST /api/mcp/execute`)
- Chat interface styled consistently with Phase II design
- JWT token automatically included in all MCP requests
- Conversation history persisted across page refreshes

**File Structure:**
- `frontend/lib/chatkit-config.ts`: ChatKit configuration and MCP tool definitions
- `frontend/app/agent/page.tsx`: Agent chat interface component
- `frontend/components/ChatInterface.tsx`: Reusable chat UI component

**Rationale:** ChatKit provides production-ready chat UI. MCP endpoints enable standardized tool calling. Consistent authentication flow maintains Phase II security model.

### Code Quality Standards (Phase III)

**Language & Version:**
- Python 3.13+ (backend), TypeScript 5.x (frontend)
- Type hints REQUIRED for all MCP tools and agent functions
- Pydantic models for MCP tool input/output validation
- TypeScript strict mode enabled

**Project Structure:**
- `backend/mcp/`: MCP tool implementations
- `backend/agents/`: Agent orchestration logic
- `backend/app/models/`: Updated with Conversation and Message models
- `frontend/lib/`: ChatKit configuration and MCP client
- `frontend/app/agent/`: Agent UI components

**Error Handling:**
- MCP tools MUST catch all exceptions and return structured errors
- Agent MUST handle tool failures gracefully (retry, fallback, user notification)
- Conversation save failures MUST not crash agent runtime
- Frontend MUST display user-friendly error messages for agent failures

**Testing:**
- Unit tests for each MCP tool
- Integration tests for agent conversation flow
- End-to-end tests for ChatKit UI interaction
- Mock LLM responses for deterministic testing

**Documentation:**
- Each MCP tool MUST have comprehensive docstring (LLM-readable)
- Agent behavior documented in ADR
- MCP integration guide in `docs/mcp-integration.md`

### Skills Infrastructure Readiness

Phase III has established comprehensive skill infrastructure to support AI-augmented development and prepare for future phase transitions.

**Phase III Skills (AI Agent Infrastructure):**
- ✅ **mcp-tool-maker**: Create MCP tools to expose backend functionality to AI agents
- ✅ **chatkit-integrator**: Integrate OpenAI ChatKit with database-backed conversation persistence
- ✅ **openai-agents-sdk**: Build stateless AI agents with tool use and streaming responses
- ✅ **agent-orchestrator**: Orchestrate agent initialization with database context and JWT auth

**Phase IV Skills (Containerization & Orchestration) - CREATED IN ADVANCE:**
- ✅ **docker-ai-pilot**: AI-assisted Docker container management and optimization
- ✅ **kubectl-ai-pilot**: AI-assisted Kubernetes cluster operations and debugging
- ✅ **kagent-debugger**: Kubernetes agent debugging with pod inspection and log analysis

**Phase V Skills (Event-Driven Architecture) - CREATED IN ADVANCE:**
- ✅ **dapr-scheduler**: Dapr Jobs API for exact-time task reminder scheduling
- ✅ **kafka-infra-provisioner**: Kafka cluster provisioning (Strimzi/Redpanda) on Kubernetes
- ✅ **blueprint-architect**: Extract and productize cloud-native architectural patterns

**Skill Creation Philosophy:**
Creating infrastructure skills in advance of their deployment phase enables:
1. **Preparedness**: Skills are ready when phase transition occurs
2. **Validation**: Skills can be tested and refined before production use
3. **Learning**: Team familiarizes with upcoming technologies ahead of time
4. **Confidence**: Reduces risk during actual phase transitions

**Important:** Skills are created proactively but MUST NOT be deployed until their respective phase begins. Phase III implementations MUST NOT use Phase IV/V technologies prematurely.

## Evolutionary Architecture Roadmap

### Phase I: Monolithic Script ✅ COMPLETED
**Goal**: Validate core CRUD functionality with minimal complexity
**Duration**: Single feature implementation
**Architecture**: Single Python file with layered structure (Model/Logic/Presentation)
**Technology**: Python 3.13+ standard library only
**Storage**: In-memory (dict/list)
**Interface**: CLI menu-driven loop
**Deployment**: Local execution (`python src/main.py`)
**Success Criteria**: All CRUD operations working with error handling
**Status**: ✅ Completed - Phase I spec fully implemented

### Phase II: Modular Monolith ✅ COMPLETED
**Goal**: Add persistence, web UI, and API layer while maintaining modularity
**Architecture**: Separate frontend/backend with clear module boundaries
**Technology**: Next.js (frontend) + FastAPI (backend) + Neon PostgreSQL (database)
**Storage**: Neon (PostgreSQL) with migrations
**Interface**: Web UI (Next.js React components) + REST API (FastAPI endpoints)
**Deployment**: Vercel (frontend + backend) + Neon (database)
**Success Criteria**: Web CRUD with persistence, authentication, multi-user support, priority levels, due dates
**Status**: ✅ Completed - Full-stack web app deployed with 37 tests passing

### Phase III: Agent-Augmented System 🚧 CURRENT
**Goal**: Integrate AI agents for intelligent task management and natural language interaction
**Architecture**: Phase II stack + AI agent layer + MCP integration + conversation persistence
**Technology**: Phase II stack + OpenAI Agents SDK + MCP Python SDK + OpenAI ChatKit
**Storage**: Phase II storage + conversations table + messages table
**Interface**: Phase II UI + ChatKit agent interface + MCP tool endpoints
**Deployment**: Phase II deployment + agent orchestration layer
**Success Criteria**:
- AI agent can create/update/prioritize tasks via natural language
- MCP tools implemented for all task operations
- Stateless agent with database-backed conversation history
- ChatKit UI integrated in frontend
- Multi-user security maintained through agent layer
**Migration Path**:
1. Add Conversation and Message models to database
2. Implement MCP tools in `backend/mcp/`
3. Create agent orchestration in `backend/agents/`
4. Add MCP endpoints to FastAPI
5. Integrate ChatKit in Next.js frontend
6. Deploy agent layer alongside Phase II backend

### Phase IV: Microservices
**Goal**: Decompose monolith into independently deployable services
**Architecture**: Task Service, User Service, Agent Service, Notification Service (independent microservices)
**Technology**: Phase III stack + Kubernetes + Helm charts + Service mesh
**Storage**: Database per service pattern (separate schemas/databases)
**Interface**: API Gateway + Phase III UI (consuming multiple services)
**Deployment**: Kubernetes cluster with Helm charts, auto-scaling, health checks
**Success Criteria**: Services independently deployable, fault-tolerant, scalable
**Migration Path**: Extract bounded contexts → separate services, deploy to K8s, implement service discovery

**Infrastructure Skills (Pre-Created):**
- **docker-ai-pilot**: AI-assisted Docker container management
  - Optimize Dockerfiles with multi-stage builds
  - Security hardening (non-root users, vulnerability scanning)
  - BuildKit features (cache mounts, secrets)
  - Production-ready templates for FastAPI/Next.js
  - Health checks and metadata labels

- **kubectl-ai-pilot**: AI-assisted Kubernetes operations
  - Cluster management and resource inspection
  - Deployment troubleshooting (pod failures, CrashLoopBackOff)
  - Service connectivity debugging
  - Log aggregation and analysis
  - Resource quota and limit management

- **kagent-debugger**: Kubernetes agent debugging
  - Pod inspection and container status analysis
  - Log analysis with error pattern detection
  - Resource usage monitoring
  - Network connectivity testing
  - Dapr sidecar troubleshooting

**Skills Deployment Trigger:** Phase IV begins when microservices decomposition starts and Kubernetes deployment is approved.

### Phase V: Event-Driven Architecture
**Goal**: Achieve cloud-native architecture with event streaming and eventual consistency
**Architecture**: Event-driven microservices with Kafka backbone + Dapr runtime
**Technology**: Phase IV stack + Kafka (event streaming) + Dapr (service mesh) + Cloud-native services
**Storage**: Event store (Kafka) + CQRS pattern (read/write separation)
**Interface**: Phase IV UI + real-time event-driven updates
**Deployment**: Multi-cloud Kubernetes + Kafka cluster + Dapr sidecars
**Success Criteria**: Event sourcing, CQRS, real-time collaboration, multi-cloud deployment
**Migration Path**: Implement event sourcing, add Kafka backbone, refactor to CQRS, deploy Dapr sidecars

**Infrastructure Skills (Pre-Created):**
- **dapr-scheduler**: Dapr Jobs API for exact-time scheduling
  - Schedule jobs via POST /v1.0/jobs endpoint
  - One-time and recurring job support
  - Callback endpoint handling (/api/jobs/trigger)
  - Job payload with task_id, user_id, scheduled_at
  - State persistence via Redis
  - Retry policies and idempotency
  - FastAPI integration with job management endpoints
  - Replaces older Cron bindings with modern Jobs API

- **kafka-infra-provisioner**: Kafka cluster provisioning
  - Dual provider support (Strimzi/Redpanda)
  - Automated deployment scripts (deploy_kafka.sh)
  - Single-node ephemeral for Minikube (1GB RAM)
  - 3-node persistent for production (2GB RAM per broker)
  - Required topics: task-events, reminders, task-updates
  - Comprehensive health checks (pods, services, topics)
  - Bootstrap server configuration for Dapr pub/sub
  - Kubernetes manifests and Helm charts

- **blueprint-architect**: Cloud-native pattern extraction
  - Analyze project structure (FastAPI + Next.js + Dapr + Kafka)
  - Extract reusable architectural patterns
  - Package Helm charts and K8s manifests
  - Generate Spec-Kit templates
  - Create BLUEPRINT.md with deployment guide
  - Metadata extraction (blueprint.json)
  - Productize architecture for reuse
  - Supports bonus points for cloud-native blueprints

**Skills Deployment Trigger:** Phase V begins when event-driven architecture is approved, Kafka infrastructure is required, and Dapr runtime is deployed.

## Development Workflow

### Specification (All Phases)
1. Write feature specification in `specs/<feature>/spec.md`
2. Define user stories with priorities (P1, P2, P3)
3. List functional requirements (FR-001, FR-002, etc.)
4. Define success criteria (SC-001, SC-002, etc.)
5. Get stakeholder approval before proceeding

### Planning (All Phases)
1. Run `/sp.plan` to generate implementation plan
2. Verify Constitution Check passes (phase-specific constraints)
3. Define data structures (appropriate for current phase storage)
4. Design interfaces (CLI for Phase I, API for Phase II+, MCP tools for Phase III+)
5. Identify edge cases and error scenarios
6. Document phase-appropriate architecture decisions in ADRs

### Task Generation (All Phases)
1. Run `/sp.tasks` to generate actionable task list
2. Tasks organized by user story priority
3. Each task includes exact file path and acceptance criteria
4. Foundational tasks (setup, infrastructure) before user stories
5. User stories can be implemented independently

### Implementation (All Phases)
1. Run `/sp.implement` to execute tasks
2. Implement in priority order (P1 → P2 → P3)
3. Test each user story independently before proceeding
4. Commit after completing each user story
5. Validate against spec acceptance criteria

### Validation (All Phases)
1. Testing appropriate to phase (manual for Phase I, automated for Phase II+)
2. Edge case validation
3. Error handling verification
4. Performance check (phase-appropriate benchmarks)
5. Update documentation (specs, ADRs, README)

## Phase Transition Readiness

### Infrastructure Skills Completion Status

**Phase III (AI Agent Infrastructure):**
- ✅ mcp-tool-maker skill created and packaged
- ✅ chatkit-integrator skill created and packaged
- ✅ openai-agents-sdk skill created and packaged
- ✅ agent-orchestrator skill created and packaged
- ⏳ MCP tools implementation pending
- ⏳ ChatKit UI integration pending
- ⏳ Conversation/message database models pending
- ⏳ Agent orchestration layer deployment pending

**Phase IV (Microservices Infrastructure):**
- ✅ docker-ai-pilot skill created and packaged
- ✅ kubectl-ai-pilot skill created and packaged
- ✅ kagent-debugger skill created and packaged
- ⏳ Microservices decomposition pending
- ⏳ Kubernetes cluster setup pending
- ⏳ Helm charts pending
- ⏳ Service mesh configuration pending

**Phase V (Event-Driven Architecture):**
- ✅ dapr-scheduler skill created and packaged
- ✅ kafka-infra-provisioner skill created and packaged
- ✅ blueprint-architect skill created and packaged
- ⏳ Kafka cluster deployment pending
- ⏳ Dapr runtime installation pending
- ⏳ Event sourcing implementation pending
- ⏳ CQRS pattern implementation pending

### Transition Readiness Checklist

**Phase III → Phase IV Readiness:**
- [ ] All Phase III MCP tools implemented and tested
- [ ] ChatKit UI integrated and functional
- [ ] Conversation persistence validated
- [ ] Agent can manage tasks via natural language
- [ ] Multi-user security verified through agent layer
- [ ] Performance benchmarks meet requirements
- [ ] Documentation complete (MCP integration guide, agent ADR)
- [ ] Phase IV ADR drafted with migration strategy

**Phase IV → Phase V Readiness:**
- [ ] All microservices extracted and deployed
- [ ] Services independently scalable
- [ ] Inter-service communication working
- [ ] Kubernetes cluster stable
- [ ] Monitoring and logging operational
- [ ] Service mesh configured
- [ ] Documentation complete (service boundaries, API contracts)
- [ ] Phase V ADR drafted with event sourcing strategy

**Current Status:** Phase III implementation in progress. Skills for Phases IV and V created proactively.

## Phase Transition Rules

### Transition Trigger Conditions
A phase transition can ONLY occur when:
1. All planned features for current phase are complete
2. All acceptance criteria validated
3. Technical debt addressed or documented
4. Migration strategy documented in ADR
5. Updated constitution ratified (new MAJOR version)

### Transition Process
1. **Assessment**: Review current phase completeness
2. **Planning**: Draft migration ADR with strategy and risks
3. **Constitution Update**: Amend constitution for next phase (MAJOR version bump)
4. **Specification**: Write migration spec detailing transition steps
5. **Implementation**: Execute migration tasks (data, code, infrastructure)
6. **Validation**: Verify all Phase N features still work in Phase N+1
7. **Commit**: Tag release marking phase transition

### Backward Compatibility
- User-facing features MUST remain functional during transitions
- Data migration MUST preserve all existing data
- Breaking API changes require versioning (v1 → v2)
- Deprecation warnings for removed features (at least one phase notice)

## Governance

### Amendment Process
1. Proposed changes documented in constitution update commit
2. Version number incremented following semantic versioning:
   - **MAJOR**: Phase transition, backward-incompatible governance changes, principle removal/redefinition
   - **MINOR**: New principles added, materially expanded guidance (within same phase)
   - **PATCH**: Clarifications, wording improvements, typo fixes, non-semantic refinements
3. All dependent templates reviewed and updated
4. Team approval required before merge
5. Changes tracked in Sync Impact Report

### Compliance Verification
- All code reviews MUST verify constitution compliance
- Phase-appropriate constraints MUST be enforced during planning
- Constitution violations require explicit justification in Complexity Tracking section of plan.md
- Unjustified violations result in change request
- No premature introduction of future-phase technologies

### Constitution Supersedes Defaults
- When constitution conflicts with standard practices, constitution wins
- Agents MUST follow constitution rules exactly as written
- Constitution takes precedence over internal knowledge or assumptions
- Phase constraints are non-negotiable (cannot skip or merge phases)

### Living Document
- Constitution evolves with project phases
- Changes tracked in version history and Sync Impact Report
- Each phase transition updates constitution (MAJOR version)
- Principles remain consistent; constraints evolve per phase

### Architecture Decision Records (ADRs)
- Significant technical decisions MUST be documented in ADRs
- Phase transitions require migration ADR
- Technology stack changes require justification ADR
- ADRs stored in `history/adr/` directory
- ADR format: Context, Decision, Consequences, Alternatives Considered

**Version**: 3.1.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-22
