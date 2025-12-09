---
id: 003
title: Phase II Implementation Plan
stage: plan
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase2-web
branch: 002-fullstack-web-app
user: Najma-LP
command: /sp.plan
labels: ["phase2", "plan", "fullstack", "batching", "backend-first", "architecture"]
links:
  spec: specs/phases/phase2-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phases/phase2-web/plan.md
tests:
  - null
---

## Prompt

/sp.plan "phase: phase2-web
spec_path: specs/phases/phase2-web.md
tasks_path: specs/phases/phase2-web.tasks.json
sprint_length: "5–7 days"
max_batch_size: S
strategy: "backend-first then frontend, strict dependency order"

goals:
  - Organize Phase 2 tasks into clear implementation batches.
  - Follow backend → auth → API → frontend → integration → testing sequence.
  - Ensure each batch is small, atomic, and testable.
  - Respect all dependencies from the /sp.tasks output.
  - Avoid Phase 3 (AI), Phase 4 (Docker), or Phase 5 (Cloud Native) work.

constraints:
  - No batch contains tasks from unrelated subsystems.
  - Every batch can be completed within ~30–60 minutes of coding.
  - Each batch must end in a testable, stable state.
  - Backend must be 100% functional before frontend begins.
  - JWT auth must be working before protected API calls are implemented.

plan_structure:
  batches:
    - batch_id
    - title
    - description
    - tasks
    - depends_on
    - expected_output
    - test_strategy

batches (user-provided structure as guidance)"

## Response snapshot

Successfully created comprehensive implementation plan with complete batching strategy and constitution compliance verification:

**Plan Created:**
- Location: specs/phases/phase2-web/plan.md
- Branch: 002-fullstack-web-app
- Strategy: Backend-first with strict dependency ordering
- Total batches: 23 (organized into 7 groups)
- Estimated time: 12-16 hours

**Constitution Check Results:**
✅ Phase Verification: Phase II (Modular Monolith) authorized, Phase I complete
✅ Technology Stack Compliance: Only Phase II approved tech (FastAPI, Next.js, Neon, Better Auth)
✅ Architecture Constraints: Modular monolith pattern, no premature microservices
✅ Migration Path: Clear transition from Phase I CLI to Phase II web app documented
✅ Spec-First Development: Complete spec with no NEEDS CLARIFICATION markers
✅ Workflow Compliance: Following spec → plan → tasks → implement sequence
✅ **OVERALL GATE STATUS: PASS** - Proceed to implementation

**Project Structure Defined:**
- **Backend**: FastAPI application with clear modules (models/, routers/, auth/, schemas/)
- **Frontend**: Next.js 16+ App Router with components/, app/, lib/ structure
- **Database**: Neon PostgreSQL with SQLModel ORM and Alembic migrations
- **Documentation**: specs/phases/phase2-web/ with spec.md, plan.md, tasks.md, checklists/

**Implementation Batching Strategy:**

**Group 1: Database Foundation (2 batches, ~60 min)**
- batch-db-001: Neon PostgreSQL init, SQLModel base, FastAPI setup, database connection
- batch-db-002: Task model creation, Alembic migrations, table creation with indexes

**Group 2: Authentication (4 batches, ~195 min)**
- batch-auth-001: Backend JWT middleware, password hashing, token verification
- batch-auth-002: Signup/login endpoints, auth router, Pydantic schemas
- batch-auth-003: Frontend Better Auth setup, Next.js initialization, Shadcn/UI
- batch-auth-004: Login/signup pages, AuthProvider, logout functionality

**Group 3: Backend Task API (4 batches, ~100 min)**
- batch-api-001: GET /api/{user_id}/tasks (list tasks with user isolation)
- batch-api-002: POST /api/{user_id}/tasks (create task with validation)
- batch-api-003: PATCH /api/{user_id}/tasks/{id}/complete (toggle completion)
- batch-api-004: PUT/GET/DELETE endpoints (update, retrieve single, delete)

**Group 4: Frontend Task UI (5 batches, ~200 min)**
- batch-fe-api-001: API client with JWT interceptor, task API functions
- batch-fe-ui-001: Task list view with dashboard layout (US2 - P1)
- batch-fe-ui-002: Create task dialog and form (US3 - P2)
- batch-fe-ui-003: Toggle complete checkbox (US4 - P2)
- batch-fe-ui-004: Edit/delete task UI (US5, US6 - P3)
- batch-fe-ui-005: Filter and sort controls (US7 - P4)

**Group 5: Cross-Cutting Concerns (3 batches, ~105 min)**
- batch-polish-001: Error handling, toast notifications, loading states
- batch-polish-002: Responsive design testing (375px, 768px, 1920px)
- batch-polish-003: Security (XSS prevention, CSRF), performance (caching, debouncing)

**Group 6: Integration Testing (4 batches, ~210 min)**
- batch-test-001: Backend pytest suite (deferred - manual testing sufficient)
- batch-test-002: End-to-end user flows for all 7 user stories
- batch-test-003: Edge case validation (JWT expiration, SQL injection, etc.)
- batch-test-004: Success criteria validation (SC-001 to SC-010)

**Group 7: Documentation (1 batch, ~30 min)**
- batch-docs-001: SETUP.md, DEPLOYMENT.md, update root README

**Batch Dependency Graph:**
- Critical path: DB Init → Migrations → JWT Middleware → Auth Endpoints → Auth Pages → API Endpoints → API Client → Task UI → Polish → Testing → Docs
- Parallelization opportunities identified after batch-auth-002 (frontend and backend can proceed in parallel)

**Multi-User Isolation Strategy:**
- **Database Layer**: Foreign key constraints, user_id index, filtered queries
- **API Layer**: JWT user_id extraction, path parameter verification, 403 on mismatch (FR-007, FR-009)
- **Frontend Layer**: Auth context manages user ID, API client auto-injects JWT
- **Testing**: Create User A and User B, verify cross-user access returns 403

**JWT Authentication Flow Documented:**
1. Signup → hashed password stored
2. Login → password verification → JWT issued with user_id claim
3. JWT stored in Better Auth session
4. API requests include Authorization Bearer header
5. Backend validates signature, extracts user_id, compares with URL parameter
6. 403 if mismatch, 401 if expired

**Performance Targets:**
- API response time: <500ms p95 (SC-010)
- Task list load: <2 seconds for 100 tasks (SC-003)
- Task creation: <3 seconds end-to-end (SC-002)
- Form validation: <500ms (SC-009)

**Security Measures:**
- Bcrypt password hashing (FR-046)
- JWT signed with BETTER_AUTH_SECRET (FR-006)
- User ID verification on all task operations (FR-007, FR-009)
- Input validation via Pydantic schemas (FR-022, FR-002, FR-003)
- XSS prevention via input sanitization (FR-048)
- SQL injection prevention via SQLModel parameterized queries (FR-049)
- CORS whitelist for frontend origin only (FR-047)

**Technical Context:**
- Backend: Python 3.13+, FastAPI 0.104+, SQLModel 0.0.14+, Neon PostgreSQL
- Frontend: TypeScript 5+, Next.js 16+, React 18+, Tailwind CSS, Shadcn/UI, React Query
- Auth: Better Auth with JWT tokens, shared secret validation
- Testing: pytest (backend), manual E2E (frontend)
- Deployment: Vercel (frontend), Render/Railway (backend), Neon (database)

## Outcome

- ✅ Impact: Complete implementation plan with 23 batches, constitution compliance verified, backend-first strategy documented
- 🧪 Tests: Testing strategy defined across 4 batches (manual E2E + edge cases + success criteria validation)
- 📁 Files: Created plan.md with comprehensive batching strategy, dependency graph, security measures
- 🔁 Next prompts: /sp.implement to execute batches sequentially, or manually implement batch-db-001 to start
- 🧠 Reflection: Plan successfully integrates user's batch structure with existing 101 tasks, enforces strict backend-first dependency ordering, and validates all Phase II constitution constraints. Batch sizes optimized for 30-60 minute work sessions with clear test strategies. Multi-user isolation and JWT security enforced at all layers (database, API, frontend).

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL):
  - Constitution compliance: PASS - All 6 gates passed (phase transition, tech stack, architecture, migration, spec-first, workflow)
  - Backend-first strategy: PASS - Database → Auth → API → Frontend → Testing sequence enforced
  - Batch atomicity: PASS - All batches 30-60 minutes with testable outputs
  - Dependency ordering: PASS - Mermaid graph shows critical path, parallelization opportunities identified
  - Multi-user isolation: PASS - Strategy documented at all 3 layers (DB, API, frontend)
  - JWT security: PASS - Complete flow documented with 7-step process
  - Performance targets: PASS - All metrics specified with SC references
- Prompt variant (if applicable): Standard /sp.plan workflow enhanced with user's batch structure guidance
- Next experiment (smallest change to try): Execute batch-db-001 (Neon PostgreSQL initialization) to validate database connection and SQLModel setup before proceeding with remaining batches
