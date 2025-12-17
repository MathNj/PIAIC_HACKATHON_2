---
id: 010
title: Utility Skills Expansion - CRUD Builder, Doc Generator, and More
stage: general
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-phase-5
user: Najma-LP
command: direct
labels: ["skills", "crud", "documentation", "testing", "monorepo", "deployment", "backend", "infrastructure"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/crud-builder/SKILL.md
  - .claude/skills/doc-generator/SKILL.md
  - .claude/skills/fastapi-endpoint-generator/SKILL.md
  - .claude/skills/integration-tester/SKILL.md
  - .claude/skills/monorepo-setup/SKILL.md
  - .claude/skills/deployment-validator/SKILL.md
  - .claude/agents/backend-specialist.md
  - .claude/agents/deployment-engineer.md
  - .claude/agents/architect.md
tests:
  - None (skill documentation)
---

## Prompt

User: "crud builder
doc generator
fastapi endpoint generator
integration tester
monorepo setup
deployment validator add these aswell"

The user requested creation of six new utility skills to expand the skills library with practical development tools.

## Response snapshot

**Six New Utility Skills Created**

### 1. crud-builder Skill ✅

**Purpose**: Generates complete CRUD operations for data models

**File**: `.claude/skills/crud-builder/SKILL.md` (800+ lines)

**When to Use**:
- User says "Create CRUD for..." or "Generate CRUD operations for [Model]"
- Need to scaffold a new data resource with full Create, Read, Update, Delete operations
- Adding standard database operations for a new entity

**What it Provides**:
1. **SQLModel Database Model** with:
   - Proper table name and primary key
   - Foreign keys and relationships
   - Field constraints (max_length, nullable, index, unique)
   - Timestamps (created_at, updated_at)

2. **Pydantic Schemas**:
   - Create schema (excludes user_id, extracted from JWT)
   - Update schema (all fields optional for partial updates)
   - Response schema (with from_attributes = True)
   - List response schema (with pagination)

3. **FastAPI Router** with 5 CRUD endpoints:
   - POST / - Create new entity
   - GET / - List entities (paginated, user-scoped)
   - GET /{id} - Get single entity
   - PATCH /{id} - Update entity
   - DELETE /{id} - Delete entity

4. **Security**:
   - JWT authentication on all endpoints
   - User isolation (user_id scoping)
   - Input validation

5. **Pytest Tests**:
   - Test for each CRUD operation
   - User isolation test
   - Error scenario tests

6. **Post-Creation**:
   - Database migration commands
   - Router registration
   - Frontend type generation guidance

**Examples**:
- Comment model with task_id, content, user_id
- Profile model with avatar_url, bio, display_name

---

### 2. doc-generator Skill ✅

**Purpose**: Generates comprehensive documentation for APIs, components, architecture, and deployment

**File**: `.claude/skills/doc-generator/SKILL.md` (700+ lines)

**When to Use**:
- User says "Generate documentation for..." or "Create README for..."
- API endpoints lack documentation
- New feature needs user-facing documentation
- Architecture changes require updated diagrams
- Deployment process needs step-by-step guide

**What it Provides**:
1. **README.md Template**:
   - Project overview with features list
   - Tech stack breakdown (backend, frontend, infrastructure)
   - Architecture diagram (ASCII)
   - Prerequisites and installation
   - Usage instructions with API endpoints
   - Environment variables documentation
   - Development guide (tests, code quality, migrations)
   - Deployment instructions
   - Project structure overview
   - Contributing guidelines

2. **API Documentation Template**:
   - Base URLs (development, production)
   - Authentication flow
   - Endpoint reference with request/response examples
   - Error responses with status codes
   - Rate limiting info
   - Pagination documentation
   - API versioning

3. **Architecture Documentation Template**:
   - System overview with diagrams
   - Component responsibilities
   - Data flow diagrams
   - Security architecture
   - Deployment architecture
   - Scalability considerations

4. **Other Documentation Types**:
   - Component documentation (props, usage)
   - Changelog format
   - Deployment guides (step-by-step)

**Quality Checklist**:
- All code examples tested
- Commands work on both Windows and Unix
- Environment variables documented
- Links verified

---

### 3. fastapi-endpoint-generator Skill ✅

**Purpose**: Generates custom FastAPI endpoints for non-CRUD operations

**File**: `.claude/skills/fastapi-endpoint-generator/SKILL.md` (600+ lines)

**When to Use**:
- User says "Create endpoint for..." or "Add API endpoint that..."
- Need custom business logic endpoint (not standard CRUD)
- Complex query operations (aggregations, joins, filters)
- Batch operations (bulk create, update, delete)
- Analytics endpoints (statistics, reports, dashboards)
- Action endpoints (send email, generate PDF, trigger workflow)

**What it Provides**:
1. **Custom Endpoint Template** with:
   - Proper HTTP method selection
   - Path/query/body parameters
   - JWT authentication
   - Request/response validation
   - Error handling
   - OpenAPI documentation

2. **Five Example Patterns**:
   - **Statistics Endpoint**: Task stats with aggregations (func.count)
   - **Bulk Operations**: Mark multiple tasks as completed
   - **Search Endpoint**: Complex query with filters and pagination
   - **Action Endpoint**: Send task reminder notification
   - **Analytics Endpoint**: Weekly task completion report

3. **Common Patterns**:
   - Pagination helper
   - Error handling decorator
   - Background tasks

**Quality Checklist**:
- HTTP method matches operation
- Path follows RESTful conventions
- Request schema validates all inputs
- Proper status codes (200, 201, 204, 400, 404)
- Authentication required
- User_id used for data scoping
- Tests cover success and error cases

---

### 4. integration-tester Skill ✅

**Purpose**: Creates comprehensive integration tests for component interactions

**File**: `.claude/skills/integration-tester/SKILL.md` (750+ lines)

**When to Use**:
- User says "Create integration tests for..." or "Test the integration between..."
- New feature needs integration testing
- API endpoints need end-to-end validation
- Database operations need testing
- After CRUD or endpoint creation

**What it Provides**:
1. **Backend API Integration Tests (pytest)**:
   - Test database setup with fixtures
   - TestClient for FastAPI
   - Authentication token fixtures
   - Complete flow tests (create → read → update → delete)
   - Pagination tests
   - User isolation tests
   - Cascade delete tests

2. **Frontend Integration Tests (Jest + React Testing Library)**:
   - MSW (Mock Service Worker) for API mocking
   - Component rendering with API calls
   - User interaction testing
   - Error handling tests

3. **E2E Tests (Playwright)**:
   - Complete user workflows
   - Authentication flows
   - Task filtering and search
   - Pagination

4. **Test Fixtures**:
   - Database session fixture with transaction rollback
   - Authentication fixtures
   - Test user creation
   - Test data factories

**Examples**:
- Complete authentication flow (register → login → authenticated request)
- Database transaction rollback on error
- API client helper classes

---

### 5. monorepo-setup Skill ✅

**Purpose**: Sets up and configures monorepo structure with workspace management

**File**: `.claude/skills/monorepo-setup/SKILL.md` (650+ lines)

**When to Use**:
- User says "Set up monorepo" or "Configure workspace"
- Need to organize multiple projects in single repository
- Want shared dependencies and tooling across packages
- Migrating from polyrepo to monorepo architecture
- Setting up new full-stack project

**What it Provides**:
1. **Workspace Configuration**:
   - pnpm-workspace.yaml for package definition
   - Root package.json with workspace scripts
   - Turborepo configuration (turbo.json) for build orchestration

2. **Package Structure**:
   ```
   apps/
     ├── frontend/    # Next.js app
     └── backend/     # FastAPI app
   packages/
     ├── types/       # Shared TypeScript types
     ├── shared/      # Shared utilities
     └── config/      # Shared configs
   ```

3. **Shared Packages**:
   - **types**: Shared TypeScript interfaces (Task, User, ApiResponse)
   - **shared**: Utility functions (formatDate, truncate, validateEmail, debounce)
   - **config**: ESLint, Prettier, tsconfig base

4. **Turborepo Pipeline**:
   - Build orchestration with dependency graph
   - Caching for faster builds
   - Parallel execution
   - Dev mode with persistent tasks

5. **CI/CD Workflow**:
   - GitHub Actions for monorepo
   - pnpm installation
   - Parallel lint, typecheck, build, test

6. **Common Commands**:
   ```bash
   pnpm dev                        # Start all apps
   pnpm --filter frontend dev      # Start frontend only
   pnpm build                      # Build all packages
   pnpm test                       # Run all tests
   pnpm add <pkg> --filter frontend # Add to frontend
   ```

**Migration Guide**: Step-by-step from polyrepo to monorepo

---

### 6. deployment-validator Skill ✅

**Purpose**: Validates deployment configurations and production readiness

**File**: `.claude/skills/deployment-validator/SKILL.md` (700+ lines)

**When to Use**:
- User says "Validate deployment" or "Check if deployment is working"
- After deploying to Kubernetes or cloud platform
- Before production deployment to catch issues early
- Troubleshooting deployment failures

**What it Provides**:
1. **Kubernetes Deployment Validation Script** (`validate-deployment.sh`):
   - Check namespace exists
   - Verify deployments (ready replicas)
   - Check pod status (Running and Ready)
   - Validate services (ClusterIP, type)
   - Check ingress configuration
   - Verify ConfigMaps and Secrets
   - Check PersistentVolumeClaims (Bound status)
   - Validate resource limits
   - Check logs for errors

2. **Health Check Validator** (`health-check.sh`):
   - Backend health endpoint
   - Backend API endpoint
   - Frontend health check

3. **Environment Variable Validator** (`validate-env.py`):
   - Required variables check
   - Recommended variables check
   - Sensitive value masking

4. **Docker Container Validator** (`validate-docker.sh`):
   - Container running status
   - Health check status
   - Resource usage (CPU, memory)
   - Logs error scanning
   - Exposed ports

5. **Pre-Deployment Checklist**:
   - Configuration validation
   - Security checks
   - Networking setup
   - Data preparation

6. **Post-Deployment Checklist**:
   - Pods status
   - Services endpoints
   - Logs verification
   - Endpoints testing
   - Monitoring setup

7. **Common Issues & Fixes**:
   - ImagePullBackOff
   - CrashLoopBackOff
   - Service not reachable
   - High resource usage

---

### Agent Integration

**Updated 3 Agents:**

1. **backend-specialist.md** - Added 3 skills:
   - `crud-builder` - For scaffolding CRUD operations
   - `fastapi-endpoint-generator` - For custom endpoints
   - `integration-tester` - For API integration tests

2. **deployment-engineer.md** - Added 1 skill:
   - `deployment-validator` - For deployment validation

3. **architect.md** - Added 2 skills:
   - `doc-generator` - For documentation generation
   - `monorepo-setup` - For workspace configuration

---

### Skills Library Summary

**Total Skills**: 20 (14 existing + 6 new)

**By Category**:
- **Backend** (7): backend-scaffolder, crud-builder, fastapi-endpoint-generator, mcp-tool-maker, agent-orchestrator, db-migration-wizard, integration-tester
- **Frontend** (3): frontend-component, api-schema-sync, cors-fixer
- **Infrastructure** (5): k8s-deployer, k8s-troubleshoot, dapr-event-flow, deployment-validator, monorepo-setup
- **Architecture** (3): spec-architect, architecture-planner, adr-generator
- **Documentation** (1): doc-generator
- **Meta** (1): skill-creator

**By Phase**:
- **Phase I**: architecture-planner (CLI patterns)
- **Phase II**: backend-scaffolder, crud-builder, fastapi-endpoint-generator, frontend-component, db-migration-wizard, integration-tester, architecture-planner, spec-architect
- **Phase III**: mcp-tool-maker, agent-orchestrator, frontend-component (ChatKit), architecture-planner
- **Phase IV**: k8s-deployer, k8s-troubleshoot, deployment-validator, architecture-planner
- **Phase V**: dapr-event-flow, architecture-planner
- **All Phases**: adr-generator, spec-architect, api-schema-sync, cors-fixer, doc-generator, monorepo-setup, skill-creator

---

### Key Features

**crud-builder**:
✅ Complete CRUD scaffolding (Model + Schema + Router + Tests)
✅ JWT authentication and user isolation
✅ Pagination built-in
✅ Database migration guidance

**doc-generator**:
✅ README.md with complete setup guide
✅ API documentation with endpoint examples
✅ Architecture diagrams and system overview
✅ Deployment guides

**fastapi-endpoint-generator**:
✅ Custom business logic endpoints
✅ 5 example patterns (stats, bulk, search, action, analytics)
✅ Request/response validation
✅ OpenAPI documentation

**integration-tester**:
✅ Backend API integration tests (pytest + TestClient)
✅ Frontend integration tests (Jest + RTL + MSW)
✅ E2E tests (Playwright)
✅ Database fixtures with transaction rollback

**monorepo-setup**:
✅ pnpm workspaces configuration
✅ Turborepo build orchestration
✅ Shared packages (types, utilities, config)
✅ CI/CD workflow for monorepo

**deployment-validator**:
✅ Kubernetes validation scripts (10-step check)
✅ Health check validators
✅ Environment variable validation
✅ Docker container validators
✅ Pre and post-deployment checklists

---

### Validation Results

**Skill Compliance**: 6/6 ✅
- All skills have proper frontmatter (name, description, version)
- All follow skill-creator pattern
- Line counts range from 600-800 lines

**Agent Integration**: 3/3 ✅
- backend-specialist: 3 new skills added
- deployment-engineer: 1 new skill added
- architect: 2 new skills added

**Total Skills**: 20 ✅
**Total Agents**: 11 ✅

---

### Usage Examples

**Example 1: CRUD Scaffolding**
```
User: "Create CRUD for Comment model with task_id, content, and user_id"

backend-specialist:
  ↓
crud-builder skill:
  → Creates Comment SQLModel with relationships
  → Generates Pydantic schemas (Create, Update, Response, List)
  → Builds FastAPI router with 5 endpoints
  → Generates pytest tests with user isolation
  → Provides migration commands
```

**Example 2: Custom Endpoint**
```
User: "Create endpoint to get task statistics"

backend-specialist:
  ↓
fastapi-endpoint-generator skill:
  → Creates TaskStatsResponse schema
  → Generates GET /tasks/stats endpoint
  → Implements aggregation queries
  → Adds JWT authentication
  → Generates pytest tests
```

**Example 3: Monorepo Setup**
```
User: "Set up monorepo for the project"

architect:
  ↓
monorepo-setup skill:
  → Creates pnpm-workspace.yaml
  → Configures Turborepo (turbo.json)
  → Sets up apps/ and packages/ structure
  → Creates shared packages (types, shared, config)
  → Updates CI/CD workflow
```

**Example 4: Deployment Validation**
```
User: "Validate deployment to Kubernetes"

deployment-engineer:
  ↓
deployment-validator skill:
  → Runs 10-step validation script
  → Checks pod status (Running and Ready)
  → Validates services and ingress
  → Verifies resource limits
  → Checks logs for errors
  → Provides health check results
```

**Example 5: Generate Documentation**
```
User: "Generate README for the project"

architect:
  ↓
doc-generator skill:
  → Creates README.md with:
     - Project overview
     - Tech stack
     - Installation guide
     - Usage examples
     - API endpoints
     - Development guide
     - Deployment instructions
```

---

### Benefits

**For Backend Development**:
- ✅ Rapid CRUD scaffolding with crud-builder
- ✅ Custom endpoint generation with fastapi-endpoint-generator
- ✅ Comprehensive integration testing with integration-tester
- ✅ Consistent patterns across all endpoints

**For Infrastructure**:
- ✅ Deployment validation before and after releases
- ✅ Monorepo configuration for large projects
- ✅ Automated health checks

**For Documentation**:
- ✅ Auto-generated README with all necessary sections
- ✅ API documentation with examples
- ✅ Architecture diagrams
- ✅ Onboarding guides

**For Quality Assurance**:
- ✅ Integration tests for all components
- ✅ Deployment validation scripts
- ✅ Environment variable validation
- ✅ Pre and post-deployment checklists

## Outcome

- ✅ Impact: Six new utility skills created, expanding skills library from 14 to 20 total skills
- 🧪 Tests: N/A (skill documentation)
- 📁 Files: Created 6 new skills, updated 3 agents
- 🔁 Next prompts:
  - Use crud-builder to scaffold Comment model CRUD
  - Use fastapi-endpoint-generator for task statistics endpoint
  - Use integration-tester for API integration tests
  - Use deployment-validator after next Kubernetes deployment
  - Use doc-generator to create comprehensive README
  - Use monorepo-setup if migrating to monorepo architecture
- 🧠 Reflection: The addition of these 6 utility skills addresses practical development needs across the entire stack. **crud-builder** and **fastapi-endpoint-generator** dramatically accelerate backend development by automating repetitive scaffolding. **integration-tester** ensures quality by providing comprehensive test templates. **deployment-validator** prevents production issues by validating configurations before and after deployment. **doc-generator** maintains up-to-date documentation without manual effort. **monorepo-setup** enables scaling to multi-package architectures. Together with the existing 14 skills, the library now covers the complete development lifecycle: architecture → planning → implementation → testing → deployment → validation → documentation. This creates a self-reinforcing ecosystem where each skill builds upon others, reducing development time and improving code quality.

## Evaluation notes (flywheel)

- Failure modes observed: None - all skills created successfully
- Graders run and results (PASS/FAIL):
  - Skill-creator compliance: PASS (all 6 skills follow template)
  - Frontmatter validation: PASS (name, description, version present)
  - Line count: PASS (600-800 lines each, comprehensive but focused)
  - Examples quality: PASS (realistic examples with code)
  - Agent integration: PASS (3 agents updated with appropriate skills)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try):
  - Test crud-builder by scaffolding a real model
  - Use fastapi-endpoint-generator for analytics endpoint
  - Run integration-tester after next feature implementation
  - Use deployment-validator in next Kubernetes deployment
  - Generate project README with doc-generator
  - Measure time savings from using these skills vs manual implementation
