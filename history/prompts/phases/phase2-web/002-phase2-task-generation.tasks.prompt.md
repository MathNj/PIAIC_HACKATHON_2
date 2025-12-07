---
id: 002
title: Phase II Task Generation
stage: tasks
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase2-web
branch: 002-fullstack-web-app
user: Najma-LP
command: /sp.tasks
labels: ["phase2", "tasks", "fullstack", "web-app", "atomic-tasks"]
links:
  spec: specs/phases/phase2-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phases/phase2-web/tasks.md
tests:
  - null
---

## Prompt

/sp.tasks "Generate atomic implementation tasks (5-20 min each) for Phase II full-stack web TODO application.

Backend: FastAPI + SQLModel + Neon PostgreSQL
Frontend: Next.js 16+ + TypeScript + Tailwind CSS + Shadcn/UI
Auth: Better Auth with JWT tokens

Tasks must:
- Be organized by phase (setup, foundation, user stories P1-P4, integration, docs)
- Reference spec.md functional requirements
- Enforce multi-user data isolation (FR-016)
- Enforce JWT authentication on all task endpoints (FR-005)
- Include acceptance criteria
- Be small and independently testable

Generate tasks for all 7 user stories:
- US1 (P1): User Registration and Authentication
- US2 (P1): View Personal Task List
- US3 (P2): Create New Tasks
- US4 (P2): Mark Tasks Complete
- US5 (P3): Update Task Details
- US6 (P3): Delete Tasks
- US7 (P4): Filter and Sort Tasks

Include setup tasks for database (Neon, SQLModel models, migrations), backend (FastAPI, auth middleware), and frontend (Next.js, Better Auth, API client).

Also include integration testing tasks and documentation tasks."

## Response snapshot

Successfully generated comprehensive task breakdown with 101 atomic tasks organized across 19 phases:

**Tasks Created:**
- Location: specs/phases/phase2-web/tasks.md
- Total tasks: 101
- Estimated time: 8-33 hours (5-20 min per task)
- All tasks reference spec.md requirements

**Phase Organization:**

1. **Phase 0: Project Setup (5 tasks)** - Monorepo structure, gitignore, README, environment templates
2. **Phase 1: Database Foundation (10 tasks)** - Neon setup, SQLModel models (User, Task), Alembic migrations with indexes
3. **Phase 2: Backend API Foundation (9 tasks)** - FastAPI setup, JWT middleware, password hashing, Pydantic schemas
4. **Phase 3: User Story 1 - Authentication (4 tasks)** - Signup/login endpoints, JWT token generation
5. **Phase 4: User Story 2 - View Task List (2 tasks)** - GET /api/{user_id}/tasks with user_id isolation
6. **Phase 5: User Story 3 - Create Tasks (1 task)** - POST /api/{user_id}/tasks with validation
7. **Phase 6: User Story 4 - Mark Complete (1 task)** - PATCH /api/{user_id}/tasks/{id}/complete toggle
8. **Phase 7: User Story 5 - Update Tasks (2 tasks)** - PUT and GET single task endpoints
9. **Phase 8: User Story 6 - Delete Tasks (1 task)** - DELETE /api/{user_id}/tasks/{id}
10. **Phase 9: Frontend Foundation (8 tasks)** - Next.js setup, Shadcn/UI, API client, Better Auth integration
11. **Phase 10: US1 Frontend Auth (5 tasks)** - Login/signup pages, AuthContext, logout
12. **Phase 11: US2 Frontend View (4 tasks)** - Dashboard layout, task list with loading states
13. **Phase 12: US3 Frontend Create (2 tasks)** - Create task dialog with validation
14. **Phase 13: US4 Frontend Toggle (1 task)** - Checkbox interaction with optimistic updates
15. **Phase 14: US5 Frontend Update (2 tasks)** - Edit task dialog with pre-filled data
16. **Phase 15: US6 Frontend Delete (2 tasks)** - Delete confirmation with AlertDialog
17. **Phase 16: US7 Frontend Filter/Sort (3 tasks)** - Filter controls, sort dropdown, dynamic filtering
18. **Phase 17: Cross-Cutting Concerns (10 tasks)** - Error handling, loading states, responsive design (375px/768px/1920px), security, performance
19. **Phase 18: Integration Testing (22 tasks)** - End-to-end user flows for all 7 stories, edge case testing (JWT expiration, SQL injection, slow network), success criteria validation (SC-001 to SC-010)
20. **Phase 19: Documentation (3 tasks)** - API docs, setup guide, deployment guide

**Key Features:**

- **Vertical Slice Approach**: Each user story has backend endpoint → frontend component → integration test
- **Parallel Work**: Tasks marked [P] can be done simultaneously (e.g., T001-T003 project setup)
- **Multi-User Isolation**: All task endpoints verify JWT user_id matches URL user_id (FR-007, FR-009, FR-016)
- **JWT Enforcement**: Auth middleware applied to all endpoints except /signup and /login (FR-005)
- **Acceptance Criteria**: Every task includes specific acceptance criteria referencing spec requirements
- **Database Indexes**: Tasks include creating indexes on tasks.user_id and tasks.completed (FR-027, FR-028)
- **Responsive Design**: Explicit tasks for testing 375px (mobile), 768px (tablet), 1920px (desktop) viewports (FR-037, SC-007)
- **Edge Cases**: 7 edge case tests including JWT expiration, duplicate email, SQL injection (Edge Cases section)
- **Success Criteria Validation**: 8 tasks validating measurable outcomes (SC-001, SC-002, SC-003, SC-004, SC-007, SC-008, SC-009, SC-010)

**Blocking Prerequisites Identified:**

- Database setup (Phase 1) must complete before backend endpoints (Phases 3-8)
- Backend auth middleware (Phase 2) must complete before any protected endpoints
- Frontend foundation (Phase 9) must complete before UI components (Phases 10-16)

**Priority Task Distribution:**

- P1 (Auth + View): 26 tasks (foundational MVP)
- P2 (Create + Complete): 6 tasks (core value)
- P3 (Update + Delete): 8 tasks (quality of life)
- P4 (Filter/Sort): 3 tasks (enhancement)

## Outcome

- ✅ Impact: Complete implementation roadmap for Phase II full-stack transformation with 101 atomic, testable tasks
- 🧪 Tests: 22 integration and edge case testing tasks covering all user stories and success criteria
- 📁 Files: Created tasks.md with 19-phase breakdown
- 🔁 Next prompts: /sp.implement to execute tasks in batches, or manually select priority tasks to implement first
- 🧠 Reflection: Task breakdown balances granularity (5-20 min per task) with clear dependencies and blocking relationships. Vertical slice approach ensures each user story is fully functional (backend + frontend + tests) before moving to next priority level. Extensive integration testing phase (22 tasks) validates all acceptance scenarios and edge cases from spec.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL):
  - Task atomicity: PASS - All tasks 5-20 minutes, independently executable
  - Spec traceability: PASS - All tasks reference FR-XXX or US scenarios
  - Multi-user isolation: PASS - All task endpoints verify user_id from JWT matches URL (FR-007, FR-009, FR-016)
  - JWT enforcement: PASS - Auth middleware required on all endpoints except /signup, /login (FR-005)
  - Testing coverage: PASS - 22 integration tasks cover all 7 user stories + edge cases + success criteria
  - Dependencies clear: PASS - Blocking prerequisites identified (database → backend → frontend)
- Prompt variant (if applicable): Standard /sp.tasks workflow with emphasis on atomic task size and multi-user security
- Next experiment (smallest change to try): Begin implementation with Phase 0-1 (setup + database foundation) to validate Neon PostgreSQL connection and SQLModel schema before proceeding to backend API
