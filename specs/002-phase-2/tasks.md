# Implementation Tasks: Full-Stack Web TODO Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-06
**Spec**: [spec.md](./spec.md)

## Task Format

- `[ ]` = Pending
- `[x]` = Completed
- `[P]` = Can be done in parallel with adjacent [P] tasks
- `[US1-US7]` = User Story reference from spec.md
- **Time estimates**: 5-20 minutes per task

---

## Phase 0: Project Setup (Foundation)

### 0.1 Initialize Project Structure

- [ ] **T001** [P] Create monorepo directory structure: `/backend`, `/frontend`, `/database`
  - Spec: Out of Scope → Monorepo structure
  - Files: `backend/`, `frontend/`, `database/`
  - Acceptance: Directories exist with proper naming

- [ ] **T002** [P] Create root `.gitignore` with Python, Node.js, and environment-specific patterns
  - Spec: FR-050 (environment variables)
  - Files: `.gitignore`
  - Acceptance: Includes `__pycache__/`, `node_modules/`, `.env*`, `venv/`, `.next/`

- [ ] **T003** [P] Create root `README.md` with architecture overview and setup instructions
  - Spec: Dependencies section
  - Files: `README.md`
  - Acceptance: Documents backend, frontend, database setup steps

### 0.2 Environment Configuration

- [ ] **T004** Create `.env.example` template with all required environment variables
  - Spec: FR-050 (sensitive configuration)
  - Files: `.env.example`
  - Acceptance: Includes `DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `NEXTAUTH_SECRET`, `NEXT_PUBLIC_API_URL`

- [ ] **T005** Create `database/.env.example` for Neon PostgreSQL connection string
  - Spec: FR-023 (Neon PostgreSQL)
  - Files: `database/.env.example`
  - Acceptance: Template includes `DATABASE_URL=postgresql://user:pass@host/db`

---

## Phase 1: Database Foundation (Blocking Prerequisites)

### 1.1 Database Setup

- [ ] **T006** Create Neon PostgreSQL database instance via Neon console
  - Spec: FR-023 (Neon PostgreSQL persistence)
  - Manual: Create project at console.neon.tech
  - Acceptance: Database created, connection string obtained

- [ ] **T007** Document database connection string in `database/.env`
  - Spec: FR-050 (environment variables)
  - Files: `database/.env`
  - Acceptance: `DATABASE_URL` set with valid Neon connection string

### 1.2 SQLModel Models

- [ ] **T008** Create `backend/app/models/__init__.py` for model exports
  - Spec: FR-024 (SQLModel ORM)
  - Files: `backend/app/models/__init__.py`
  - Acceptance: Empty init file ready for model imports

- [ ] **T009** Create `backend/app/models/user.py` with User model
  - Spec: FR-001 (user accounts), Key Entities (User)
  - Files: `backend/app/models/user.py`
  - Fields: `id` (UUID, primary key), `email` (str, unique), `name` (str), `created_at` (datetime)
  - Acceptance: Model validates with SQLModel, inherits SQLModel and `table=True`

- [ ] **T010** Create `backend/app/models/task.py` with Task model
  - Spec: FR-011 (create tasks), Key Entities (Task)
  - Files: `backend/app/models/task.py`
  - Fields: `id` (int, primary key, autoincrement), `user_id` (str, FK to User), `title` (str, max 200), `description` (str, max 2000), `completed` (bool, default False), `created_at` (datetime), `updated_at` (datetime)
  - Acceptance: Model validates, includes foreign key relationship to User, indexes on user_id and completed

### 1.3 Database Migrations

- [ ] **T011** Install Alembic in backend: `pip install alembic`
  - Spec: FR-024 (database operations)
  - Files: `backend/requirements.txt`
  - Acceptance: Alembic added to requirements.txt

- [ ] **T012** Initialize Alembic: `alembic init alembic` in backend directory
  - Spec: FR-024 (SQLModel ORM)
  - Files: `backend/alembic/`, `backend/alembic.ini`
  - Acceptance: Alembic config created

- [ ] **T013** Configure Alembic `env.py` to use SQLModel metadata and Neon DATABASE_URL
  - Spec: FR-023 (Neon PostgreSQL)
  - Files: `backend/alembic/env.py`
  - Acceptance: `target_metadata` references SQLModel models, `sqlalchemy.url` reads from `.env`

- [ ] **T014** Create initial migration: `alembic revision --autogenerate -m "Initial schema with users and tasks"`
  - Spec: FR-025 (unique constraint), FR-026 (foreign key), FR-027/FR-028 (indexes)
  - Files: `backend/alembic/versions/001_initial_schema.py`
  - Acceptance: Migration includes users table, tasks table, indexes on tasks.user_id and tasks.completed

- [ ] **T015** Apply migration: `alembic upgrade head`
  - Spec: FR-023 (persist data)
  - Manual: Run migration command
  - Acceptance: Tables created in Neon database, verified via Neon console

---

## Phase 2: Backend API Foundation (Blocking Prerequisites)

### 2.1 FastAPI Setup

- [ ] **T016** Create `backend/requirements.txt` with core dependencies
  - Spec: Backend Dependencies
  - Files: `backend/requirements.txt`
  - Acceptance: Includes `fastapi`, `uvicorn[standard]`, `sqlmodel`, `pydantic>=2.0`, `python-dotenv`, `psycopg2-binary`, `python-jose[cryptography]`, `passlib[bcrypt]`

- [ ] **T017** [P] Create `backend/app/__init__.py` for app package
  - Files: `backend/app/__init__.py`
  - Acceptance: Empty init file

- [ ] **T018** [P] Create `backend/app/config.py` to load environment variables
  - Spec: FR-050 (environment variables)
  - Files: `backend/app/config.py`
  - Acceptance: Loads `DATABASE_URL`, `BETTER_AUTH_SECRET`, exports as `Settings` class using pydantic.BaseSettings

- [ ] **T019** Create `backend/app/database.py` with SQLModel engine and session factory
  - Spec: FR-024 (SQLModel ORM)
  - Files: `backend/app/database.py`
  - Acceptance: Creates engine from DATABASE_URL, provides `get_session()` dependency for FastAPI

- [ ] **T020** Create `backend/app/main.py` with FastAPI app initialization
  - Spec: FR-029 (Next.js frontend), FR-047 (CORS)
  - Files: `backend/app/main.py`
  - Acceptance: FastAPI app created, CORS middleware configured to allow frontend origin, health check endpoint GET /health returns {"status": "ok"}

### 2.2 Authentication Middleware

- [ ] **T021** Create `backend/app/auth/__init__.py` for auth module
  - Files: `backend/app/auth/__init__.py`
  - Acceptance: Empty init file

- [ ] **T022** Create `backend/app/auth/utils.py` with JWT verification function
  - Spec: FR-006 (validate JWT with BETTER_AUTH_SECRET)
  - Files: `backend/app/auth/utils.py`
  - Acceptance: Function `verify_jwt_token(token: str) -> dict` decodes JWT, validates signature, returns payload with user_id

- [ ] **T023** Create `backend/app/auth/dependencies.py` with `get_current_user` dependency
  - Spec: FR-005 (require JWT for all endpoints), FR-007 (extract user_id)
  - Files: `backend/app/auth/dependencies.py`
  - Acceptance: FastAPI dependency extracts Bearer token from Authorization header, verifies JWT, returns user_id, raises HTTPException 401 if invalid

- [ ] **T024** Create `backend/app/auth/password.py` with password hashing utilities
  - Spec: FR-046 (hash passwords with bcrypt)
  - Files: `backend/app/auth/password.py`
  - Acceptance: Functions `hash_password(plain: str) -> str` and `verify_password(plain: str, hashed: str) -> bool` using passlib.context.CryptContext with bcrypt

### 2.3 Pydantic Schemas

- [ ] **T025** Create `backend/app/schemas/__init__.py` for schema exports
  - Files: `backend/app/schemas/__init__.py`
  - Acceptance: Empty init file

- [ ] **T026** [P] Create `backend/app/schemas/task.py` with TaskCreate, TaskUpdate, TaskResponse schemas
  - Spec: FR-011 (create task), FR-019 (update task), FR-045 (JSON responses)
  - Files: `backend/app/schemas/task.py`
  - Acceptance: `TaskCreate` has title (str, max 200), description (str | None, max 2000). `TaskUpdate` same fields optional. `TaskResponse` has all task fields including id, user_id, completed, timestamps

- [ ] **T027** [P] Create `backend/app/schemas/user.py` with UserCreate, UserResponse schemas
  - Spec: FR-001 (create account), FR-002 (email validation)
  - Files: `backend/app/schemas/user.py`
  - Acceptance: `UserCreate` has email (EmailStr), name (str), password (str, min 8 chars). `UserResponse` has id, email, name, created_at (no password)

---

## Phase 3: User Story 1 - Authentication (Priority P1)

### 3.1 User Registration Endpoint

- [ ] **T028** Create `backend/app/routers/__init__.py` for router module
  - Files: `backend/app/routers/__init__.py`
  - Acceptance: Empty init file

- [ ] **T029** Create `backend/app/routers/auth.py` with POST /signup endpoint
  - Spec: FR-001 (create account), US1 Scenario 1
  - Files: `backend/app/routers/auth.py`
  - Endpoint: POST /api/signup
  - Input: UserCreate schema (email, name, password)
  - Logic: Validate email format (FR-002), validate password requirements (FR-003), hash password (FR-046), create User record in DB, return UserResponse (HTTP 201)
  - Acceptance: Returns user object without password, returns 400 if email exists (FR-025), returns 400 if password validation fails

### 3.2 User Login Endpoint

- [ ] **T030** Create POST /login endpoint in `backend/app/routers/auth.py`
  - Spec: FR-004 (authenticate via Better Auth), US1 Scenario 2
  - Files: `backend/app/routers/auth.py`
  - Endpoint: POST /api/login
  - Input: email (str), password (str)
  - Logic: Query user by email, verify password hash, generate JWT token with user_id using BETTER_AUTH_SECRET, return token + user info
  - Acceptance: Returns {"access_token": "...", "token_type": "bearer", "user": {...}}, returns 401 if credentials invalid (US1 Scenario 4)

### 3.3 Mount Auth Router

- [ ] **T031** Register auth router in `backend/app/main.py`
  - Spec: FR-005 (auth endpoints exempt from JWT)
  - Files: `backend/app/main.py`
  - Acceptance: `app.include_router(auth.router, prefix="/api", tags=["auth"])`, signup and login endpoints accessible without JWT

---

## Phase 4: User Story 2 - View Task List (Priority P1)

### 4.1 List Tasks Endpoint

- [ ] **T032** Create `backend/app/routers/tasks.py` with GET /api/{user_id}/tasks endpoint
  - Spec: FR-038 (list all tasks), FR-015 (sorted by created_at newest first), US2 Scenario 1
  - Files: `backend/app/routers/tasks.py`
  - Dependencies: `current_user = Depends(get_current_user)`
  - Logic: Verify current_user matches path user_id (FR-007/FR-009), query tasks filtered by user_id (FR-016), sort by created_at DESC, return list of TaskResponse
  - Acceptance: Returns tasks for authenticated user only, returns 401 if no JWT, returns 403 if JWT user_id ≠ path user_id, returns [] if no tasks (US2 Scenario 3)

### 4.2 Mount Tasks Router

- [ ] **T033** Register tasks router in `backend/app/main.py`
  - Spec: FR-005 (require JWT for all task endpoints)
  - Files: `backend/app/main.py`
  - Acceptance: `app.include_router(tasks.router, prefix="/api", tags=["tasks"])`

---

## Phase 5: User Story 3 - Create Tasks (Priority P2)

### 5.1 Create Task Endpoint

- [ ] **T034** Create POST /api/{user_id}/tasks endpoint in `backend/app/routers/tasks.py`
  - Spec: FR-039 (create task), FR-012 (auto-generate ID), FR-013 (associate user_id), FR-014 (defaults), US3 Scenario 1, US3 Scenario 2
  - Files: `backend/app/routers/tasks.py`
  - Input: TaskCreate schema
  - Dependencies: `current_user = Depends(get_current_user)`
  - Logic: Verify current_user matches path user_id, validate title non-empty (FR-021), validate char limits (FR-022), create Task with user_id=current_user, completed=false, auto-populate created_at and updated_at, return TaskResponse (HTTP 201)
  - Acceptance: Returns new task with generated ID, returns 400 if title empty (US3 Scenario 3), returns 403 if user_id mismatch

---

## Phase 6: User Story 4 - Mark Tasks Complete (Priority P2)

### 6.1 Toggle Completion Endpoint

- [ ] **T035** Create PATCH /api/{user_id}/tasks/{id}/complete endpoint in `backend/app/routers/tasks.py`
  - Spec: FR-043 (toggle completion), FR-017 (toggle status), FR-018 (update timestamp), US4 Scenario 1, US4 Scenario 2
  - Files: `backend/app/routers/tasks.py`
  - Dependencies: `current_user = Depends(get_current_user)`
  - Logic: Verify current_user matches path user_id, fetch task by ID, verify task.user_id matches current_user (FR-016), toggle completed boolean, update updated_at timestamp, save to DB, return TaskResponse
  - Acceptance: Toggles task.completed (true ↔ false), returns updated task, returns 404 if task not found, returns 403 if task belongs to different user

---

## Phase 7: User Story 5 - Update Tasks (Priority P3)

### 7.1 Update Task Endpoint

- [ ] **T036** Create PUT /api/{user_id}/tasks/{id} endpoint in `backend/app/routers/tasks.py`
  - Spec: FR-041 (update task), FR-019 (update title/description), US5 Scenario 1, US5 Scenario 2
  - Files: `backend/app/routers/tasks.py`
  - Input: TaskUpdate schema (title, description both optional)
  - Dependencies: `current_user = Depends(get_current_user)`
  - Logic: Verify current_user matches path user_id, fetch task, verify ownership, validate title if provided (FR-021, FR-022), update only provided fields, update updated_at, return TaskResponse
  - Acceptance: Updates only provided fields, returns 400 if title empty (US5 Scenario 3), returns 404 if task not found, returns 403 if ownership mismatch

### 7.2 Get Single Task Endpoint

- [ ] **T037** Create GET /api/{user_id}/tasks/{id} endpoint in `backend/app/routers/tasks.py`
  - Spec: FR-040 (retrieve single task)
  - Files: `backend/app/routers/tasks.py`
  - Dependencies: `current_user = Depends(get_current_user)`
  - Logic: Verify current_user matches path user_id, fetch task by ID, verify ownership, return TaskResponse
  - Acceptance: Returns single task if owned by user, returns 404 if not found, returns 403 if ownership mismatch

---

## Phase 8: User Story 6 - Delete Tasks (Priority P3)

### 8.1 Delete Task Endpoint

- [ ] **T038** Create DELETE /api/{user_id}/tasks/{id} endpoint in `backend/app/routers/tasks.py`
  - Spec: FR-042 (delete task), FR-020 (permanent delete), US6 Scenario 1, US6 Scenario 3
  - Files: `backend/app/routers/tasks.py`
  - Dependencies: `current_user = Depends(get_current_user)`
  - Logic: Verify current_user matches path user_id, fetch task, verify ownership, delete from DB, return 204 No Content
  - Acceptance: Permanently removes task from database, returns 204 on success, returns 404 if not found, returns 403 if ownership mismatch

---

## Phase 9: Frontend Foundation (Blocking Prerequisites)

### 9.1 Next.js Project Setup

- [ ] **T039** Initialize Next.js 16+ project: `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`
  - Spec: FR-029 (Next.js 16+ App Router), Frontend Dependencies
  - Files: `frontend/` (entire Next.js project)
  - Acceptance: Next.js project created with TypeScript, Tailwind CSS, App Router, no src directory

- [ ] **T040** Install Shadcn/UI: `npx shadcn-ui@latest init` in frontend directory
  - Spec: FR-030 (Shadcn/UI components)
  - Files: `frontend/components/ui/` (Shadcn components)
  - Acceptance: Shadcn configured, components.json created

- [ ] **T041** [P] Install additional dependencies: `npm install @tanstack/react-query axios better-auth`
  - Spec: Frontend Dependencies (Better Auth)
  - Files: `frontend/package.json`
  - Acceptance: Dependencies added to package.json

- [ ] **T042** [P] Create `frontend/.env.local` with NEXT_PUBLIC_API_URL pointing to backend
  - Spec: FR-050 (environment variables)
  - Files: `frontend/.env.local`
  - Acceptance: `NEXT_PUBLIC_API_URL=http://localhost:8000` (adjust for backend port)

### 9.2 API Client Setup

- [ ] **T043** Create `frontend/lib/api-client.ts` with Axios instance configured with base URL and JWT interceptor
  - Spec: FR-005 (include JWT automatically), FR-036 (error handling)
  - Files: `frontend/lib/api-client.ts`
  - Acceptance: Axios instance uses NEXT_PUBLIC_API_URL, request interceptor adds Authorization Bearer token from Better Auth session, response interceptor handles 401 errors by redirecting to login

- [ ] **T044** Create `frontend/lib/api/tasks.ts` with task API functions
  - Spec: FR-038 to FR-043 (API endpoints)
  - Files: `frontend/lib/api/tasks.ts`
  - Acceptance: Functions `getTasks(userId)`, `createTask(userId, data)`, `updateTask(userId, taskId, data)`, `deleteTask(userId, taskId)`, `toggleComplete(userId, taskId)` using api-client

### 9.3 Better Auth Integration

- [ ] **T045** Configure Better Auth in `frontend/lib/auth.ts`
  - Spec: FR-004 (Better Auth JWT), FR-010 (persist sessions)
  - Files: `frontend/lib/auth.ts`
  - Acceptance: Better Auth configured with backend URL, JWT token storage in cookies/localStorage, session management functions exported

- [ ] **T046** Create `frontend/app/api/auth/[...all]/route.ts` for Better Auth API routes
  - Spec: FR-004 (authentication)
  - Files: `frontend/app/api/auth/[...all]/route.ts`
  - Acceptance: Handles Better Auth callbacks, integrates with backend /signup and /login endpoints

---

## Phase 10: User Story 1 - Frontend Authentication (Priority P1)

### 10.1 Login Page

- [ ] **T047** Create `frontend/app/login/page.tsx` with login form
  - Spec: US1 Scenario 2, FR-033 (form validation), FR-034 (loading states)
  - Files: `frontend/app/login/page.tsx`
  - Components: Email input, password input, submit button, error message display
  - Logic: Call Better Auth login, store JWT token, redirect to /dashboard on success, display error on failure (US1 Scenario 4)
  - Acceptance: Form validates inputs, shows loading spinner during submission, redirects authenticated users to dashboard

### 10.2 Signup Page

- [ ] **T048** Create `frontend/app/signup/page.tsx` with registration form
  - Spec: US1 Scenario 1, FR-002 (email validation), FR-003 (password requirements)
  - Files: `frontend/app/signup/page.tsx`
  - Components: Email, name, password inputs, submit button
  - Logic: Validate email format, enforce password rules (8+ chars, uppercase, lowercase, number), call Better Auth signup, redirect to /login on success
  - Acceptance: Shows validation errors inline, enforces password requirements, handles duplicate email error

### 10.3 Authentication Context

- [ ] **T049** Create `frontend/components/providers/auth-provider.tsx` with AuthContext
  - Spec: FR-010 (persist sessions across refreshes), US1 Scenario 3
  - Files: `frontend/components/providers/auth-provider.tsx`
  - Acceptance: Provides `user` and `logout` to child components, checks Better Auth session on mount, redirects to /login if unauthenticated

- [ ] **T050** Wrap `frontend/app/layout.tsx` with AuthProvider
  - Spec: FR-010 (session persistence)
  - Files: `frontend/app/layout.tsx`
  - Acceptance: All pages have access to auth context

### 10.4 Logout Functionality

- [ ] **T051** Create logout button component in `frontend/components/logout-button.tsx`
  - Spec: US1 Scenario 5
  - Files: `frontend/components/logout-button.tsx`
  - Logic: Call Better Auth logout, clear session, redirect to /login
  - Acceptance: Clicking logout clears session and redirects to login page

---

## Phase 11: User Story 2 - Frontend Task List View (Priority P1)

### 11.1 Dashboard Layout

- [ ] **T052** Create `frontend/app/dashboard/layout.tsx` with navigation header
  - Spec: FR-037 (responsive design)
  - Files: `frontend/app/dashboard/layout.tsx`
  - Components: Header with app name, user name display, logout button
  - Acceptance: Header responsive on mobile (375px), tablet (768px), desktop (1920px)

### 11.2 Task List Page

- [ ] **T053** Create `frontend/app/dashboard/page.tsx` with task list fetch using React Query
  - Spec: US2 Scenario 1, FR-015 (sorted by created_at), FR-034 (loading states)
  - Files: `frontend/app/dashboard/page.tsx`
  - Logic: Fetch tasks via `getTasks(userId)` from api/tasks.ts, display loading skeleton while fetching, render TaskList component when loaded
  - Acceptance: Shows loading skeleton, fetches tasks on mount, passes tasks to TaskList component

### 11.3 Task List Component

- [ ] **T054** Create `frontend/components/tasks/task-list.tsx` displaying tasks
  - Spec: US2 Scenario 2 (visual distinction), FR-031 (list format), FR-032 (completed styling)
  - Files: `frontend/components/tasks/task-list.tsx`
  - Components: Map over tasks, render TaskItem for each
  - Acceptance: Displays all tasks, shows empty state if no tasks (US2 Scenario 3), completed tasks have strikethrough and gray color

### 11.4 Task Item Component

- [ ] **T055** Create `frontend/components/tasks/task-item.tsx` with checkbox, title, description, action buttons
  - Spec: FR-031 (task display format), FR-032 (visual distinction)
  - Files: `frontend/components/tasks/task-item.tsx`
  - Components: Checkbox (controlled by completed prop), title (strikethrough if completed), truncated description, edit/delete icons
  - Acceptance: Checkbox reflects completed status, completed tasks styled differently, description truncated if > 100 chars

---

## Phase 12: User Story 3 - Frontend Create Tasks (Priority P2)

### 12.1 Create Task Form

- [ ] **T056** Install Shadcn/UI components: `npx shadcn-ui@latest add button input textarea dialog`
  - Spec: FR-030 (Shadcn/UI)
  - Files: `frontend/components/ui/` (button, input, textarea, dialog components)
  - Acceptance: Components installed in components/ui/

- [ ] **T057** Create `frontend/components/tasks/create-task-dialog.tsx` with form
  - Spec: US3 Scenario 1, US3 Scenario 2, FR-033 (validation)
  - Files: `frontend/components/tasks/create-task-dialog.tsx`
  - Components: Dialog with title input, description textarea, submit button
  - Logic: Validate title required (US3 Scenario 3), call `createTask(userId, data)`, optimistic update to task list (FR-035), close dialog on success
  - Acceptance: Shows validation error if title empty, adds task to list immediately, shows loading state during submission

### 12.2 Add Task Button

- [ ] **T058** Add "Add Task" button to `frontend/app/dashboard/page.tsx` triggering CreateTaskDialog
  - Spec: US3 Scenario 1
  - Files: `frontend/app/dashboard/page.tsx`
  - Acceptance: Button opens CreateTaskDialog, new tasks appear in list after creation (US3 Scenario 4, US3 Scenario 5)

---

## Phase 13: User Story 4 - Frontend Toggle Completion (Priority P2)

### 13.1 Checkbox Interaction

- [ ] **T059** Implement checkbox onClick handler in `frontend/components/tasks/task-item.tsx`
  - Spec: US4 Scenario 1, US4 Scenario 2, FR-035 (optimistic updates)
  - Files: `frontend/components/tasks/task-item.tsx`
  - Logic: Call `toggleComplete(userId, taskId)`, optimistically update checkbox state immediately, revert if API call fails, show loading indicator (US4 Scenario 5)
  - Acceptance: Checkbox toggles immediately on click, persists after page refresh (US4 Scenario 3), visual feedback shows completed status (US4 Scenario 4)

---

## Phase 14: User Story 5 - Frontend Update Tasks (Priority P3)

### 14.1 Edit Task Dialog

- [ ] **T060** Create `frontend/components/tasks/edit-task-dialog.tsx` with pre-filled form
  - Spec: US5 Scenario 1, US5 Scenario 2, FR-033 (validation)
  - Files: `frontend/components/tasks/edit-task-dialog.tsx`
  - Components: Dialog with title input (pre-filled), description textarea (pre-filled), save/cancel buttons
  - Logic: Pre-populate form with existing task data, validate title non-empty (US5 Scenario 3), call `updateTask(userId, taskId, data)`, update task list on success
  - Acceptance: Form shows current task data, saves changes, handles cancel (US5 Scenario 4), persists updates (US5 Scenario 5)

### 14.2 Edit Button in Task Item

- [ ] **T061** Add edit icon button to `frontend/components/tasks/task-item.tsx` triggering EditTaskDialog
  - Spec: US5 Scenario 1
  - Files: `frontend/components/tasks/task-item.tsx`
  - Acceptance: Clicking edit icon opens EditTaskDialog with pre-filled data

---

## Phase 15: User Story 6 - Frontend Delete Tasks (Priority P3)

### 15.1 Delete Confirmation

- [ ] **T062** Install Shadcn/UI alert-dialog: `npx shadcn-ui@latest add alert-dialog`
  - Spec: FR-030 (Shadcn/UI)
  - Files: `frontend/components/ui/alert-dialog.tsx`
  - Acceptance: Component installed

- [ ] **T063** Create delete confirmation in `frontend/components/tasks/task-item.tsx`
  - Spec: US6 Scenario 1, US6 Scenario 2
  - Files: `frontend/components/tasks/task-item.tsx`
  - Components: AlertDialog with "Are you sure?" message, confirm/cancel buttons
  - Logic: Show confirmation on delete icon click, call `deleteTask(userId, taskId)` on confirm, remove task from list (US6 Scenario 5), cancel closes dialog (US6 Scenario 2)
  - Acceptance: Confirmation required before delete, task removed from list immediately, persists after refresh (US6 Scenario 3), handles empty state (US6 Scenario 4)

---

## Phase 16: User Story 7 - Frontend Filter/Sort (Priority P4)

### 16.1 Filter Controls

- [ ] **T064** Create `frontend/components/tasks/task-filters.tsx` with filter buttons
  - Spec: US7 Scenario 1, US7 Scenario 2
  - Files: `frontend/components/tasks/task-filters.tsx`
  - Components: Radio group or tabs for "All", "Incomplete only", "Complete only"
  - Logic: Update state on selection, filter task list client-side
  - Acceptance: Filters work correctly (US7 Scenario 1, US7 Scenario 2), filter state persists in URL params (US7 Scenario 5)

### 16.2 Sort Controls

- [ ] **T065** Add sort dropdown to `frontend/components/tasks/task-filters.tsx`
  - Spec: US7 Scenario 3
  - Files: `frontend/components/tasks/task-filters.tsx`
  - Components: Select with "Newest first" (default), "Oldest first"
  - Logic: Sort task array by created_at ascending or descending
  - Acceptance: Sort order changes task display (US7 Scenario 3), persists in URL params (US7 Scenario 5)

### 16.3 Dynamic Filtering

- [ ] **T066** Implement real-time filter updates in `frontend/app/dashboard/page.tsx`
  - Spec: US7 Scenario 4
  - Files: `frontend/app/dashboard/page.tsx`
  - Logic: When user toggles task completion, immediately update filtered view if filter applied
  - Acceptance: Task disappears from "Complete only" filter when marked incomplete (US7 Scenario 4)

---

## Phase 17: Cross-Cutting Concerns

### 17.1 Error Handling

- [ ] **T067** Create `frontend/components/error-boundary.tsx` for React error boundary
  - Spec: FR-036 (graceful error handling)
  - Files: `frontend/components/error-boundary.tsx`
  - Acceptance: Catches React errors, displays user-friendly message

- [ ] **T068** Add global error toast system using Shadcn/UI toast: `npx shadcn-ui@latest add toast`
  - Spec: FR-036 (user-friendly error messages)
  - Files: `frontend/components/ui/toast.tsx`, `frontend/components/providers/toast-provider.tsx`
  - Acceptance: API errors display as toast notifications with actionable messages

### 17.2 Loading States

- [ ] **T069** Create `frontend/components/ui/skeleton-card.tsx` for task list loading skeleton
  - Spec: FR-034 (skeleton screens)
  - Files: `frontend/components/ui/skeleton-card.tsx`
  - Acceptance: Displays placeholder UI while tasks load (US2 initial load)

### 17.3 Responsive Design

- [ ] **T070** Test and fix mobile layout (375px viewport) for all pages
  - Spec: FR-037 (responsive across viewports), SC-007
  - Files: All frontend components
  - Acceptance: All pages functional and readable on 375px width (iPhone SE), touch targets minimum 44x44px

- [ ] **T071** [P] Test and fix tablet layout (768px viewport)
  - Spec: FR-037 (responsive design)
  - Acceptance: Layouts adapt correctly at tablet breakpoint

- [ ] **T072** [P] Test and fix desktop layout (1920px viewport)
  - Spec: FR-037 (responsive design)
  - Acceptance: Layouts use available space effectively on large screens

### 17.4 Security

- [ ] **T073** Implement input sanitization in all form components
  - Spec: FR-048 (prevent XSS)
  - Files: `frontend/components/tasks/create-task-dialog.tsx`, `edit-task-dialog.tsx`
  - Acceptance: User inputs sanitized before rendering, no script execution from task titles/descriptions

- [ ] **T074** Add CSRF protection via Better Auth configuration
  - Spec: FR-048 (security)
  - Files: `frontend/lib/auth.ts`
  - Acceptance: Better Auth CSRF tokens included in requests

### 17.5 Performance

- [ ] **T075** Implement React Query caching for task list with 5-minute stale time
  - Spec: SC-003 (2-second load time for 100 tasks)
  - Files: `frontend/app/dashboard/page.tsx`
  - Acceptance: Subsequent task list loads use cache, manual refetch available

- [ ] **T076** Add request debouncing to create/update task forms (500ms)
  - Spec: SC-009 (validation feedback within 500ms)
  - Files: Form validation in create/edit dialogs
  - Acceptance: Validation runs after 500ms of input inactivity

---

## Phase 18: Integration Testing & Validation

### 18.1 End-to-End User Flows

- [ ] **T077** Manually test User Story 1 (Auth) full flow: signup → login → logout → login
  - Spec: US1 all scenarios
  - Acceptance: All US1 acceptance scenarios pass, session persists (US1 Scenario 3)

- [ ] **T078** Manually test User Story 2 (View) with multiple users
  - Spec: US2 all scenarios, SC-004 (data isolation)
  - Acceptance: User A sees only their tasks, User B sees only their tasks (US2 Scenario 4)

- [ ] **T079** Manually test User Story 3 (Create) scenarios
  - Spec: US3 all scenarios, SC-002 (create in <3 seconds)
  - Acceptance: Task creation works, persists (US3 Scenario 4, 5), validation enforced (US3 Scenario 3)

- [ ] **T080** Manually test User Story 4 (Complete) toggle behavior
  - Spec: US4 all scenarios
  - Acceptance: Toggle works both ways (US4 Scenario 1, 2), persists (US4 Scenario 3), visual feedback (US4 Scenario 4)

- [ ] **T081** Manually test User Story 5 (Update) edit functionality
  - Spec: US5 all scenarios
  - Acceptance: Edit saves correctly (US5 Scenario 1, 2, 5), validation works (US5 Scenario 3), cancel works (US5 Scenario 4)

- [ ] **T082** Manually test User Story 6 (Delete) with confirmation
  - Spec: US6 all scenarios
  - Acceptance: Confirmation required (US6 Scenario 1, 2), delete persists (US6 Scenario 3), empty state shown (US6 Scenario 4)

- [ ] **T083** Manually test User Story 7 (Filter/Sort) all combinations
  - Spec: US7 all scenarios
  - Acceptance: All filters work (US7 Scenarios 1-4), preferences persist (US7 Scenario 5)

### 18.2 Edge Case Testing

- [ ] **T084** Test JWT expiration handling: wait for token to expire, attempt API call
  - Spec: Edge Case #1
  - Acceptance: Expired token detected, user redirected to login with clear message

- [ ] **T085** Test duplicate email registration
  - Spec: Edge Case #2
  - Acceptance: Second signup with same email displays "Email already registered" error

- [ ] **T086** Test slow network simulation (Chrome DevTools throttling)
  - Spec: Edge Case #3, SC-002/SC-010 (performance)
  - Acceptance: Optimistic updates work, loading indicators shown, retry logic functions

- [ ] **T087** Test empty task list state
  - Spec: Edge Case #4
  - Acceptance: "Create your first task" message displayed, filter controls hidden

- [ ] **T088** Test max length validation (title 200 chars, description 2000 chars)
  - Spec: Edge Case #5, FR-022
  - Acceptance: Character counter shown, validation prevents exceeding limits

- [ ] **T089** Test backend unavailability
  - Spec: Edge Case #6
  - Acceptance: User-friendly error message displayed, retry mechanism available

- [ ] **T090** Test SQL injection attempt in task title
  - Spec: Edge Case #8, FR-049
  - Acceptance: Input sanitized, no SQL injection possible (SQLModel parameterized queries)

### 18.3 Success Criteria Validation

- [ ] **T091** Validate SC-001: Time user registration flow (target <1 minute)
  - Spec: SC-001
  - Acceptance: Registration flow completes in under 60 seconds

- [ ] **T092** Validate SC-002: Measure task creation latency (target <3 seconds)
  - Spec: SC-002
  - Acceptance: Task appears in list within 3 seconds of submission

- [ ] **T093** Validate SC-003: Load 100 tasks, measure render time (target <2 seconds)
  - Spec: SC-003
  - Acceptance: Task list with 100 items loads in under 2 seconds

- [ ] **T094** Validate SC-004: Verify multi-user data isolation with 2+ test users
  - Spec: SC-004
  - Acceptance: Zero instances of users seeing other users' tasks

- [ ] **T095** Validate SC-007: Test on mobile device (375px width)
  - Spec: SC-007
  - Acceptance: All features functional on iPhone SE or equivalent

- [ ] **T096** Validate SC-008: Refresh page during authenticated session
  - Spec: SC-008
  - Acceptance: User remains logged in, no data loss

- [ ] **T097** Validate SC-009: Test form validation response time (target <500ms)
  - Spec: SC-009
  - Acceptance: Validation feedback appears within 500ms of invalid input

- [ ] **T098** Validate SC-010: Measure API response times under normal load (target <500ms)
  - Spec: SC-010
  - Acceptance: All authenticated endpoints respond in under 500ms

---

## Phase 19: Documentation

### 19.1 API Documentation

- [ ] **T099** Document all API endpoints in `backend/README.md`
  - Spec: FR-038 to FR-045 (API endpoints)
  - Files: `backend/README.md`
  - Content: Endpoint paths, HTTP methods, request/response schemas, auth requirements, example curl commands
  - Acceptance: All 8 endpoints documented with examples

### 19.2 Setup Documentation

- [ ] **T100** Create `docs/SETUP.md` with environment setup steps
  - Spec: Dependencies section, Assumptions #10-12
  - Files: `docs/SETUP.md`
  - Content: Prerequisites (Python 3.13+, Node.js 18+), Neon database setup, environment variable configuration, migration commands, run instructions
  - Acceptance: Developer can follow docs to set up project from scratch

### 19.3 Deployment Guide

- [ ] **T101** Create `docs/DEPLOYMENT.md` with production deployment steps
  - Spec: Out of Scope → Production deployment (documenting approach for future)
  - Files: `docs/DEPLOYMENT.md`
  - Content: Environment variable checklist, database migration workflow, CORS configuration for production, hosting recommendations (Vercel for frontend, Render/Railway for backend)
  - Acceptance: Deployment process documented for future use

---

## Summary Statistics

- **Total Tasks**: 101
- **Estimated Time**: 8-33 hours (101 tasks × 5-20 min each)
- **Phases**: 19
- **Priority Breakdown**:
  - P0 (Setup): 5 tasks
  - P1 (Auth + View): 26 tasks
  - P2 (Create + Complete): 6 tasks
  - P3 (Update + Delete): 8 tasks
  - P4 (Filter/Sort): 3 tasks
  - Foundation: 21 tasks
  - Integration/Testing: 23 tasks
  - Documentation: 3 tasks
  - Cross-cutting: 6 tasks

## Task Execution Strategy

1. **Blocking Prerequisites First** (Phases 0-2): Setup project structure, database, backend foundation before any features
2. **Vertical Slice Per User Story** (Phases 3-16): Implement backend + frontend for each user story in priority order (P1 → P4)
3. **Parallel Work Opportunities**: Tasks marked [P] can be done simultaneously if multiple developers available
4. **Integration Last** (Phases 17-19): Cross-cutting concerns, testing, and documentation after core features complete

## Next Steps

1. Run `/sp.implement` to execute tasks in batches
2. Use Claude Code to work through tasks sequentially or in parallel groups
3. Mark tasks complete with `[x]` as they finish
4. Create PHR after major milestones (each phase completion)
