---
id: 009
title: ADR Generator and Architecture Planner Skills Created
stage: general
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-phase-5
user: Najma-LP
command: direct
labels: ["skills", "adr", "architecture", "planning", "vertical-intelligence", "decision-records"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/adr-generator/SKILL.md
  - .claude/skills/architecture-planner/SKILL.md
  - .claude/agents/architect.md
tests:
  - None (skill documentation)
---

## Prompt

User: "make skill for adr generator architecture planner"

The user requested creation of two new skills:
1. **adr-generator**: For creating Architecture Decision Records
2. **architecture-planner**: For creating comprehensive implementation plans

## Response snapshot

**Two New Architecture Skills Created**

### 1. adr-generator Skill ✅

**Purpose**: Creates Architecture Decision Records (ADRs) for documenting significant architectural decisions

**File**: `.claude/skills/adr-generator/SKILL.md` (549 lines)

**When to Use**:
- Significant architectural decision made (passes 3-part test)
- User asks to "create an ADR" or "document this decision"
- Technology choices need formal documentation
- Team needs alignment on technical direction
- Planning phase transitions (I→II, II→III, etc.)

**3-Part Significance Test**:
1. **Impact**: Long-term architectural consequences?
2. **Alternatives**: Multiple viable options considered?
3. **Scope**: Cross-cutting or system-defining?

**What it Provides**:
1. **Complete ADR Template** with sections:
   - Context (problem statement, constraints, assumptions)
   - Decision (chosen option and rationale)
   - Options Considered (2-3 alternatives with pros/cons/complexity)
   - Consequences (positive, negative, neutral)
   - Implementation Notes (actions, migration path, testing, rollback, timeline)
   - References (related ADRs, specs, external docs)
   - Review History (status tracking)
2. **Sequential Numbering**: Auto-increment ADR numbers (001, 002, 003...)
3. **Status Lifecycle**: Proposed → Accepted/Rejected → Superseded
4. **Immutability**: ADRs never modified once accepted (new ADRs supersede)

**Common Decision Categories**:
- Technology Stack (FastAPI vs Flask)
- Architecture Patterns (Monolith vs Microservices)
- Data Storage (PostgreSQL vs MongoDB)
- Integration Patterns (REST vs GraphQL vs gRPC)
- Deployment Strategy (Docker Compose vs Kubernetes)

**Examples Included**:
1. **Technology Choice**: ADR-003: Use FastAPI for Backend API Framework
   - Context: Need Python REST API framework with performance and DX
   - Options: FastAPI (chosen), Flask, Django REST Framework
   - Rationale: Async support, auto docs, Pydantic integration
   - Consequences: Learning curve, smaller ecosystem, but better DX

2. **Architecture Pattern**: ADR-007: Event-Driven Architecture for Notifications (Phase V)
   - Context: Need notification system without tight coupling
   - Options: Event-Driven (Dapr+Kafka), Direct HTTP, Message Queue (RabbitMQ)
   - Rationale: Decoupling, async processing, multiple subscribers
   - Consequences: Eventual consistency, operational complexity, scalability

---

### 2. architecture-planner Skill ✅

**Purpose**: Creates comprehensive implementation plans bridging specifications and code

**File**: `.claude/skills/architecture-planner/SKILL.md` (742 lines)

**When to Use**:
- User asks to "plan the implementation" or "create an implementation plan"
- Need to break down complex features into actionable tasks
- Planning feature implementation across any phase (I-V)
- Designing component architecture and data models
- Need to identify dependencies and risks

**What it Provides**:
1. **Complete Implementation Plan** with sections:
   - Overview and success criteria
   - Architecture (component diagram, responsibilities, key files)
   - Data Model (tables with columns, constraints, indexes, relationships)
   - API Design (all CRUD endpoints with request/response specs)
   - Implementation Tasks (8-10 tasks with acceptance criteria, complexity, dependencies)
   - Testing Strategy (unit, integration, E2E)
   - Risks & Mitigations (probability, impact, mitigation)
   - Dependencies (external, internal, blocking)
   - Success Metrics (functional and non-functional)
   - Rollback Plan

2. **Phase-Specific Patterns**:
   - **Phase I**: Single-file CLI structure (constants, logic, I/O, CLI, main)
   - **Phase II**: Layered architecture (models → schemas → routers, frontend components)
   - **Phase III**: Agent-augmented (MCP tools, orchestrator, conversations, ChatKit)
   - **Phase IV**: Microservices (service boundaries, Dockerfile, Helm charts)
   - **Phase V**: Event-driven (event schemas, Dapr components, publishers, subscribers)

3. **Task Breakdown Template**:
   - Task number and title
   - Complexity (Simple/Moderate/Complex)
   - Dependencies (which tasks must complete first)
   - Acceptance criteria (testable checklist)
   - Files created/modified

**Workflow**:
1. Read Specification → Analyze Current Architecture
2. Design Component Architecture → Design Data Model → Design API Contracts
3. Break Down into Tasks → Define Testing Strategy → Identify Risks

**Examples Included**:
- **Phase II**: Task Priority Management (8 tasks from schema to UI)
- **Phase III**: AI Task Assistant (10 tasks from agent setup to ChatKit)

---

### Integration with architect Agent

**Updated**: `.claude/agents/architect.md`

**architect Agent Now Has 3 Skills**:
1. **architecture-planner** (NEW)
   - Invoked when planning implementations
   - Creates detailed implementation plans with tasks
   - Phase-specific architecture patterns

2. **adr-generator** (NEW)
   - Invoked for significant architectural decisions
   - Documents decisions with full context
   - 3-part significance test validation

3. **spec-architect** (EXISTING)
   - Invoked when designing features
   - Creates Spec-Kit Plus specifications
   - Technology-agnostic requirements

**Skill Usage Flow**:
```
User: "Add user profile feature"
    ↓
architect invokes spec-architect
    → Creates @specs/features/user-profile.md
    ↓
architect invokes architecture-planner
    → Creates implementation plan with 8 tasks, data model, API design
    ↓
architect evaluates technology decision (e.g., image storage strategy)
    ↓
architect invokes adr-generator
    → Creates ADR-015: Image Storage Strategy (S3 vs Local vs CDN)
```

---

### Skills Library Summary

**Total Skills**: 14 (12 existing + 2 new)

**By Category**:
- **Backend** (4): backend-scaffolder, mcp-tool-maker, agent-orchestrator, db-migration-wizard
- **Frontend** (3): frontend-component, api-schema-sync, cors-fixer
- **Infrastructure** (3): k8s-deployer, k8s-troubleshoot, dapr-event-flow
- **Architecture** (3): spec-architect, architecture-planner ✨, adr-generator ✨
- **Meta** (1): skill-creator

**By Phase**:
- **Phase I**: architecture-planner (CLI patterns)
- **Phase II**: backend-scaffolder, frontend-component, db-migration-wizard, architecture-planner (Modular patterns), spec-architect
- **Phase III**: mcp-tool-maker, agent-orchestrator, frontend-component (ChatKit), architecture-planner (Agent patterns)
- **Phase IV**: k8s-deployer, k8s-troubleshoot, architecture-planner (Microservices patterns)
- **Phase V**: dapr-event-flow, architecture-planner (Event-Driven patterns)
- **All Phases**: adr-generator, spec-architect, api-schema-sync, cors-fixer, skill-creator

---

### Key Features

**adr-generator**:
✅ 3-part significance test (ensures only important decisions documented)
✅ Complete ADR template (context, options, decision, consequences, implementation)
✅ Sequential numbering with immutability (001, 002, 003... never modified)
✅ Status lifecycle (Proposed → Accepted → Superseded)
✅ Common decision categories with examples
✅ Technology choice and architecture pattern ADRs included

**architecture-planner**:
✅ Comprehensive implementation plan template (architecture to tasks)
✅ Phase-specific patterns (I through V)
✅ Task breakdown with dependencies and complexity
✅ Data model design (tables, relationships, indexes)
✅ API design (complete CRUD endpoint specs)
✅ Testing strategy (unit, integration, E2E)
✅ Risk analysis with mitigations
✅ Success metrics and rollback plan

---

### Validation Results

**Skill Compliance**: 2/2 ✅
- adr-generator: 549 lines, proper frontmatter ✅
- architecture-planner: 742 lines, proper frontmatter ✅

**Frontmatter**:
```yaml
---
name: "skill-name"
description: "Comprehensive description with triggers"
version: "1.0.0"
---
```

**Structure** (follows skill-creator pattern):
- When to Use ✅
- Context ✅
- Workflow ✅
- Output Format ✅
- Examples ✅
- Quality Checklist ✅

**Line Count**: Under 800 lines each ✅ (within best practices)

**Total Skills**: 14 ✅

**architect Agent Updated**: 3 skills referenced ✅

---

### Usage Examples

**Example 1: Technology Decision**
```
User: "Should we use FastAPI or Flask?"

architect:
  ↓
adr-generator skill:
  → Creates ADR-003: Use FastAPI for Backend API Framework
  → Context: Need Python REST API with performance
  → Options: FastAPI (chosen), Flask, Django
  → Rationale: Async, auto-docs, Pydantic integration
  → Status: Proposed → [user approves] → Accepted
```

**Example 2: Feature Implementation Planning**
```
User: "Plan the implementation for user profiles"

architect:
  ↓
architecture-planner skill:
  → Reads @specs/features/user-profile.md
  → Creates implementation plan with:
     - Component architecture (backend API + frontend UI)
     - Data model (profiles table with avatar_url)
     - API design (CRUD endpoints with JWT auth)
     - 8 tasks:
       1. Database schema & migration (Simple)
       2. Pydantic schemas (Simple)
       3. CRUD endpoints (Moderate)
       4. Backend tests (Moderate)
       5. TypeScript types (Simple)
       6. API client (Moderate)
       7. UI components (Complex)
       8. Integration tests (Moderate)
     - Testing strategy
     - Risks (image upload size limits)
```

**Example 3: Architecture Pattern Decision**
```
User: "Should we use event-driven architecture for notifications?"

architect:
  ↓
adr-generator skill:
  → Creates ADR-007: Event-Driven Architecture for Notifications
  → Context: Need notification system without tight coupling
  → Options: Event-Driven (Dapr+Kafka), Direct HTTP, Message Queue
  → Rationale: Decoupling, async, multiple subscribers
  → Consequences: Eventual consistency, operational complexity
  → Implementation: Event schemas, Dapr config, publisher, subscriber
  → Status: Proposed
```

---

### Benefits

**For architect Agent**:
- ✅ Systematic implementation planning (no ad-hoc task lists)
- ✅ Formal decision documentation (ADRs capture "why")
- ✅ Phase-aware planning (correct patterns for each phase)
- ✅ Reusable templates (consistency across features)

**For Development**:
- ✅ Clear roadmap (tasks with dependencies)
- ✅ Architectural history (ADRs explain past decisions)
- ✅ Onboarding (new developers read ADRs to understand choices)
- ✅ Reduced rework (plan before coding)

**For Governance**:
- ✅ Decision traceability (why was X chosen over Y?)
- ✅ Team alignment (ADRs force consensus)
- ✅ Risk awareness (plans identify risks upfront)
- ✅ Quality gates (plans define success criteria)

## Outcome

- ✅ Impact: Two new architecture skills created (adr-generator, architecture-planner), architect agent now has 3 specialized skills
- 🧪 Tests: N/A (skill documentation)
- 📁 Files: Created 2 new skills, updated architect agent
- 🔁 Next prompts:
  - Use adr-generator to document significant architectural decisions
  - Use architecture-planner to create implementation plans for features
  - Test full workflow: spec-architect → architecture-planner → adr-generator
  - Create ADRs for existing architectural decisions (FastAPI choice, Phase patterns, etc.)
- 🧠 Reflection: The addition of **adr-generator** and **architecture-planner** completes the architect agent's toolkit. The architect can now handle the complete lifecycle: (1) **spec-architect** defines "what" to build, (2) **architecture-planner** defines "how" to build it (with tasks, risks, testing), and (3) **adr-generator** documents "why" key decisions were made. This creates a complete paper trail from requirements → plan → decisions, ensuring architectural integrity and knowledge preservation across all phases.

## Evaluation notes (flywheel)

- Failure modes observed: None - skills created successfully
- Graders run and results (PASS/FAIL):
  - Skill-creator compliance: PASS (both skills follow template)
  - Frontmatter validation: PASS (name, description, version present)
  - Line count: PASS (549 and 742 lines, under 800)
  - Examples quality: PASS (realistic ADRs and plans included)
  - architect agent integration: PASS (3 skills properly referenced)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try):
  - Create first real ADR using adr-generator (e.g., ADR-001: Project Architecture Evolution Strategy)
  - Use architecture-planner for next feature implementation
  - Measure time savings from using architecture-planner vs manual planning
