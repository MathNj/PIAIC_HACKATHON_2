# The Evolution of TODO: Project Constitution
<!--
SYNC IMPACT REPORT:
Version: 1.0.0 → 2.0.0
Change Type: MAJOR - Evolutionary architecture model added, Phase I principles now scoped to current phase
Modified Principles:
  - Principle I: Spec-First Development (unchanged - still NON-NEGOTIABLE)
  - Principle II: In-Memory Storage Only → Phase I Storage (scoped to Phase I only)
  - Principle III: Standard Library Only → Phase I Dependencies (scoped to Phase I only)
  - Principle IV: Continuous Loop Interface → Phase I Interface (scoped to Phase I only)
Added Sections:
  - Project Vision & Role Definition
  - Evolutionary Architecture Roadmap (5 phases)
  - Phase Transition Rules
  - Technology Stack Evolution
Removed Sections: None
Templates Status:
  ✅ plan-template.md - Constitution Check section still aligns (Phase I constraints preserved)
  ✅ spec-template.md - Requirements structure compatible
  ✅ tasks-template.md - Task categorization aligned
  ⚠ Future phases will require template updates for new tech stacks
Follow-up TODOs:
  - Create phase-specific spec templates when transitioning to Phase II
  - Document migration strategy from Phase I to Phase II in ADR
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
1. **Phase I**: Monolithic Script (single file CLI)
2. **Phase II**: Modular Monolith (web app with clear module boundaries)
3. **Phase III**: Agent-Augmented System (AI agents + MCP integration)
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
- **Phase I**: Python 3.13+ CLI (standard library only)
- **Phase II**: Next.js frontend + FastAPI backend + Neon (PostgreSQL)
- **Phase III**: Phase II stack + AI Agents + MCP (Model Context Protocol)
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

## Phase I: Monolithic Script (Current Phase)

### Storage Constraints

For Phase I ONLY, the application MUST use in-memory data structures (lists, dictionaries) for all data storage. NO persistent storage mechanisms are permitted in Phase I.

**Rules (Phase I Only):**
- NO SQL databases (PostgreSQL, MySQL, SQLite, etc.)
- NO NoSQL databases (MongoDB, Redis, etc.)
- NO file-based persistence (JSON, CSV, pickle, etc.)
- Data stored ONLY in Python lists, dictionaries, or similar in-memory structures
- Data loss on application restart is EXPECTED and ACCEPTABLE for Phase I

**Phase Transition:** Phase II will introduce Neon (PostgreSQL) for persistence. Migration ADR required.

**Rationale:** Phase I focuses on core business logic and user experience without persistence complexity. Simplifies initial implementation and testing. Validates core CRUD operations before adding persistence.

### Dependency Constraints

All Phase I implementation MUST use only Python's standard library. NO external dependencies or third-party packages are permitted in Phase I.

**Rules (Phase I Only):**
- NO pip packages or external libraries
- Use built-in modules only (typing, datetime, sys, dataclasses, etc.)
- NO framework dependencies (Flask, FastAPI, Click, etc.)
- Database drivers explicitly forbidden (psycopg2, pymongo, etc.)

**Phase Transition:** Phase II will introduce FastAPI, Next.js, and Neon client libraries.

**Rationale:** Eliminates dependency management complexity in initial phase. Forces clear understanding of core Python capabilities. Demonstrates that complex frameworks aren't needed for simple CLIs.

### Interface Constraints

Phase I application MUST run in a continuous interactive loop until the user explicitly chooses to exit. The application provides a menu-driven interface for all operations.

**Rules (Phase I Only):**
- Application runs in infinite `while True` loop
- User presented with menu of options after each operation
- Only "Exit" or equivalent option terminates the application
- Invalid input handled gracefully with error messages and re-prompt
- Each operation returns control to main menu

**Phase Transition:** Phase II will replace CLI with Next.js web UI + FastAPI REST endpoints.

**Rationale:** Standard pattern for CLI tools. Provides intuitive user experience for console applications. Allows multiple operations without restarting.

### Code Quality Standards (Phase I)

**Language & Version:**
- Python 3.13+
- Type hints REQUIRED for all function signatures and class attributes
- Docstrings REQUIRED for all public functions and classes (Google style)

**Project Structure:**
- Single file implementation in `src/main.py`
- Entry point: `if __name__ == "__main__":` block required
- Modularity: Functions and classes for organization even within single file

**Error Handling:**
- Try-except blocks for user input and validation
- Input validation before processing (type checks, range checks, null checks)
- Graceful error messages (no stack traces shown to users)

**Naming Conventions:**
- snake_case for functions/variables
- PascalCase for classes
- UPPER_CASE for constants

**Comments:**
- Inline comments for complex logic only
- Prefer self-documenting code (clear names, simple logic)
- Docstrings explain "why", not "what"

## Evolutionary Architecture Roadmap

### Phase I: Monolithic Script ✅ CURRENT
**Goal**: Validate core CRUD functionality with minimal complexity
**Duration**: Single feature implementation
**Architecture**: Single Python file with layered structure (Model/Logic/Presentation)
**Technology**: Python 3.13+ standard library only
**Storage**: In-memory (dict/list)
**Interface**: CLI menu-driven loop
**Deployment**: Local execution (`python src/main.py`)
**Success Criteria**: All CRUD operations working with error handling

### Phase II: Modular Monolith
**Goal**: Add persistence, web UI, and API layer while maintaining modularity
**Architecture**: Separate frontend/backend with clear module boundaries
**Technology**: Next.js (frontend) + FastAPI (backend) + Neon PostgreSQL (database)
**Storage**: Neon (PostgreSQL) with migrations
**Interface**: Web UI (Next.js React components) + REST API (FastAPI endpoints)
**Deployment**: Vercel (frontend) + Cloud provider (backend) + Neon (database)
**Success Criteria**: Web CRUD with persistence, authentication, multi-user support
**Migration Path**: Extract TaskManager logic → FastAPI endpoints, build Next.js UI consuming API

### Phase III: Agent-Augmented System
**Goal**: Integrate AI agents for intelligent task management and assistance
**Architecture**: Phase II stack + AI agent layer + MCP integration
**Technology**: Phase II stack + AI Agents (Claude, GPT) + MCP (Model Context Protocol)
**Storage**: Phase II storage + agent conversation history
**Interface**: Phase II UI + agent chat interface + MCP tools
**Deployment**: Phase II deployment + agent orchestration layer
**Success Criteria**: AI agents can create/update/prioritize tasks, natural language input, MCP tool integration
**Migration Path**: Add agent endpoints to FastAPI, integrate MCP, build agent UI components

### Phase IV: Microservices
**Goal**: Decompose monolith into independently deployable services
**Architecture**: Task Service, User Service, Agent Service, Notification Service (independent microservices)
**Technology**: Phase III stack + Kubernetes + Helm charts + Service mesh
**Storage**: Database per service pattern (separate schemas/databases)
**Interface**: API Gateway + Phase III UI (consuming multiple services)
**Deployment**: Kubernetes cluster with Helm charts, auto-scaling, health checks
**Success Criteria**: Services independently deployable, fault-tolerant, scalable
**Migration Path**: Extract bounded contexts → separate services, deploy to K8s, implement service discovery

### Phase V: Event-Driven Architecture
**Goal**: Achieve cloud-native architecture with event streaming and eventual consistency
**Architecture**: Event-driven microservices with Kafka backbone + Dapr runtime
**Technology**: Phase IV stack + Kafka (event streaming) + Dapr (service mesh) + Cloud-native services
**Storage**: Event store (Kafka) + CQRS pattern (read/write separation)
**Interface**: Phase IV UI + real-time event-driven updates
**Deployment**: Multi-cloud Kubernetes + Kafka cluster + Dapr sidecars
**Success Criteria**: Event sourcing, CQRS, real-time collaboration, multi-cloud deployment
**Migration Path**: Implement event sourcing, add Kafka backbone, refactor to CQRS, deploy Dapr sidecars

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
4. Design interfaces (CLI for Phase I, API for Phase II+)
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

**Version**: 2.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-05
