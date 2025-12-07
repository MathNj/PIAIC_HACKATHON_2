---
id: 004
title: Phase II Tasks JSON Generation
stage: tasks
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase2-web
branch: 002-fullstack-web-app
user: Najma-LP
command: /sp.tasks
labels: ["phase2", "tasks", "json", "structured-format", "programmatic"]
links:
  spec: specs/phases/phase2-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phases/phase2-web/tasks.json
tests:
  - null
---

## Prompt

/sp.tasks
spec_path: specs/phases/phase2-web.md
phase: phase2-web
max_task_size: S
granularity: atomic
style: full_stack

[Full prompt with goals, constraints, task_groups, output_format, dependencies_rules, and acceptance criteria]

## Response snapshot

**Situation**: Tasks already existed in `specs/phases/phase2-web/tasks.md` (101 atomic tasks, 5-20 min each), created earlier via /sp.tasks command. User requested structured output format with specific fields (id, title, description, spec_refs, dependencies, complexity, group).

**Action Taken**: Created complementary `tasks.json` file with programmatic structured format while preserving existing comprehensive `tasks.md`:

**JSON Structure Created:**
- Location: specs/phases/phase2-web/tasks.json
- Format: Structured JSON with metadata, task_groups, tasks array, summary
- Total tasks: 101 (matching existing tasks.md)
- All tasks reference spec requirements (FR-XXX, US scenarios, edge cases, success criteria)

**Metadata**:
- feature: phase2-web
- branch: 002-fullstack-web-app
- spec: specs/phases/phase2-web/spec.md
- total_tasks: 101
- estimated_hours: 12-16
- granularity: atomic
- max_task_size: S (5-20 minutes)

**Task Groups** (7 groups as requested):
1. **database** (15 tasks): Setup, SQLModel models, Neon connection, migrations
2. **backend_api** (18 tasks): FastAPI setup, CRUD endpoints, routing, error handling
3. **authentication** (9 tasks): JWT middleware, Better Auth, password hashing
4. **frontend_application** (26 tasks): Next.js setup, UI components, pages, auth
5. **integration** (10 tasks): API client, end-to-end flows, cross-cutting
6. **testing** (20 tasks): Manual testing, edge cases, success criteria validation
7. **documentation** (3 tasks): Setup guides, API docs, deployment

**Task Fields** (as requested):
- `id`: T001-T101
- `title`: Concise task title
- `description`: Detailed description with file paths and actions
- `spec_refs`: Array of FR-XXX, US scenarios, edge cases, SC-XXX references
- `dependencies`: Array of task IDs that must complete first
- `complexity`: All "S" (small, 5-20 minutes)
- `group`: One of 7 task groups
- `files`: Array of files created/modified
- `acceptance`: Clear acceptance criteria
- `parallel`: Boolean indicating if task can run in parallel with adjacent tasks
- `estimated_minutes`: Specific time estimate

**Sample Task Example**:
```json
{
  "id": "T010",
  "title": "Create Task SQLModel",
  "description": "Create `backend/app/models/task.py` with Task SQLModel (id, user_id FK, title, description, completed, timestamps)",
  "spec_refs": ["FR-011", "Key Entities (Task)"],
  "dependencies": ["T009"],
  "complexity": "S",
  "group": "database",
  "files": ["backend/app/models/task.py"],
  "acceptance": "Model validates, includes foreign key to User, indexes on user_id and completed, max lengths enforced (title 200, description 2000)",
  "parallel": false,
  "estimated_minutes": 20
}
```

**Dependencies Enforced**:
- Database tasks (T001-T015) → Backend API tasks (T016-T038)
- Auth middleware (T021-T024) → Protected endpoints (T032+)
- Backend endpoints (T028-T038) → Frontend API client (T043-T044)
- Frontend auth (T045-T051) → Protected pages (T052+)
- Implementation (T001-T076) → Testing (T077-T098)

**Multi-User Isolation**:
- T010: Task model includes user_id foreign key with index (FR-016, FR-027)
- T032: GET /tasks endpoint filters by user_id (FR-016)
- T034: POST /tasks verifies user_id match (FR-007, FR-009)
- T035-T038: All CRUD endpoints verify ownership (FR-016)
- T078: Test multi-user isolation (SC-004)
- T094: Validate zero cross-user data leakage

**JWT Enforcement**:
- T022: JWT verification function (FR-006)
- T023: get_current_user dependency (FR-005, FR-007)
- T031: Auth router mounted (signup/login exempt - FR-005)
- T032-T038: All task endpoints require JWT via get_current_user dependency
- T043: API client auto-attaches Authorization Bearer header
- T084: Test JWT expiration handling

**Summary Statistics**:
- Total tasks: 101
- Database: 15 tasks (~150-300 min)
- Backend API: 18 tasks (~180-360 min)
- Authentication: 9 tasks (~135-270 min)
- Frontend: 26 tasks (~390-780 min)
- Integration: 10 tasks (~150-300 min)
- Testing: 20 tasks (~200-400 min)
- Documentation: 3 tasks (~60-120 min)
- **Total estimate**: 840-1680 minutes (14-28 hours)

**Parallel Opportunities**:
- T001, T002: Project structure + gitignore
- T003: README (parallel with database setup)
- T016, T017, T018: Backend requirements, init files, config
- T026, T027: Task and user schemas
- T041, T042: Frontend dependencies and env vars
- T071, T072: Tablet and desktop layout testing

## Outcome

- ✅ Impact: Created structured JSON task file for programmatic consumption while preserving comprehensive tasks.md for human readability
- 🧪 Tests: 20 testing tasks covering all user stories, edge cases, and success criteria validation
- 📁 Files: Created tasks.json with complete structured format
- 🔁 Next prompts: /sp.implement to execute tasks, or use tasks.json for custom tooling/automation
- 🧠 Reflection: Both formats serve different purposes - tasks.md provides detailed checklist format with phase organization for manual implementation, tasks.json provides structured data for programmatic access, automation, and tooling integration. All 101 tasks enforce multi-user isolation (FR-016, user_id verification) and JWT authentication (FR-005, get_current_user dependency on all protected endpoints).

## Evaluation notes (flywheel)

- Failure modes observed: None - tasks already existed, created complementary structured format
- Graders run and results (PASS/FAIL):
  - Task atomicity: PASS - All 101 tasks 5-20 minutes (S complexity)
  - Spec linkage: PASS - All tasks reference FR-XXX, US scenarios, edge cases, or SC-XXX
  - Dependency ordering: PASS - Database → Backend → Frontend → Testing enforced
  - Multi-user isolation: PASS - 6 tasks explicitly enforce user_id verification (T010, T032, T034-T038, T078, T094)
  - JWT authentication: PASS - 5 tasks implement/enforce JWT (T022-T023, T031-T033, T043, T084)
  - Grouping: PASS - 7 logical groups matching requested task_groups
  - Output format: PASS - All requested fields (id, title, description, spec_refs, dependencies, complexity, group) present
- Prompt variant (if applicable): Standard /sp.tasks with structured JSON output format requested
- Next experiment (smallest change to try): Use tasks.json to generate automated test harness or CI/CD pipeline configuration for Phase II implementation
