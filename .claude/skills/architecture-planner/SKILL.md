---
name: "architecture-planner"
description: "Creates comprehensive implementation plans with component architecture, data models, API design, task breakdown, dependencies, and testing strategy. Use when planning feature implementations, designing system architecture, or breaking down complex features into actionable tasks across all development phases."
version: "1.0.0"
---

# Architecture Planner Skill

## When to Use
- User asks to "plan the implementation" or "design the architecture" for a feature
- User says "Break this down into tasks" or "Create an implementation plan"
- Starting a new feature (after spec is written)
- Need to decompose complex work into discrete tasks
- Planning phase transitions (I→II, II→III, etc.)
- Evaluating architectural tradeoffs
- Designing integration between multiple components

## Context
This skill creates implementation plans that bridge specifications and code:
- **Input**: Feature specification (`@specs/features/[feature].md`)
- **Output**: Implementation plan with architecture, tasks, dependencies
- **Purpose**: Translate "what" (spec) into "how" (implementation)
- **Phases**: Works across all phases (I, II, III, IV, V) with phase-specific patterns
- **Constitutional Alignment**: Follows project phase constraints and technology stacks

## Workflow

### 1. Read Specification
- Read feature spec: `@specs/features/[feature-name].md`
- Extract acceptance criteria, data models, API contracts, UI requirements
- Identify dependencies on existing features
- Note NFRs (non-functional requirements)

### 2. Analyze Current Architecture
- Review existing codebase structure
- Identify reusable patterns and components
- Check for architectural constraints
- Determine current phase (I, II, III, IV, or V)

### 3. Design Component Architecture
**For each layer, define:**
- Component responsibilities
- Module boundaries
- Interface contracts
- Data flow

**Phase-Specific Patterns:**
- **Phase I**: Single-file functions grouped by domain
- **Phase II**: Layered (models → routers → services)
- **Phase III**: Phase II + Agent layer + MCP tools
- **Phase IV**: Microservices with clear service boundaries
- **Phase V**: Event-driven with pub/sub patterns

### 4. Design Data Model
- Define database tables/models
- Plan relationships and foreign keys
- Identify required indexes
- Plan migrations (if changing existing schema)

### 5. Design API Contracts
- Define REST endpoints (method, path, auth)
- Specify request/response schemas
- Document error responses
- Plan versioning strategy (if needed)

### 6. Break Down into Tasks
**For each task:**
- Clear acceptance criteria
- Estimated complexity (Simple/Moderate/Complex)
- Dependencies (what must be done first)
- Testing requirements

### 7. Define Testing Strategy
- Unit tests (what to test)
- Integration tests (component interactions)
- E2E tests (user workflows)
- Performance tests (if applicable)

### 8. Identify Risks
- Technical risks (unknowns, complexity)
- Dependency risks (external services, other teams)
- Performance risks (scalability concerns)
- Mitigation strategies for each

## Output Format

### Implementation Plan Template

```markdown
# Implementation Plan: [Feature Name]

**Spec**: @specs/features/[feature-name].md
**Phase**: [I/II/III/IV/V]
**Estimated Complexity**: [Simple/Moderate/Complex/Very Complex]
**Timeline**: [X days/weeks]

---

## Overview

[2-3 sentence summary of what will be implemented and how it fits into the system]

**Success Criteria**:
- [ ] Criterion 1 from spec
- [ ] Criterion 2 from spec
- [ ] Criterion 3 from spec

---

## Architecture

### Component Diagram

```
┌─────────────────┐
│   Frontend      │
│  (Next.js)      │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│   Database      │
│  (PostgreSQL)   │
└─────────────────┘
```

### Component Responsibilities

**1. Frontend**:
- Location: `frontend/app/[feature]/`
- Responsibility: [What it does]
- Dependencies: [Backend API endpoints]
- Key Files:
  - `page.tsx` - Main page component
  - `components/[Component].tsx` - Reusable components
  - `lib/[feature]-api.ts` - API client

**2. Backend API**:
- Location: `backend/app/routers/[feature].py`
- Responsibility: [What it does]
- Dependencies: [Database models, auth, external services]
- Key Files:
  - `models/[feature].py` - SQLModel ORM
  - `schemas/[feature].py` - Pydantic DTOs
  - `routers/[feature].py` - FastAPI routes

**3. Database**:
- Location: `backend/app/models/[feature].py`
- Responsibility: Data persistence
- Dependencies: [Other tables via foreign keys]

---

## Data Model

### Tables

#### [TableName] (`table_name`)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| user_id | UUID | FK→users.id, NOT NULL, Indexed | User who owns this |
| [field] | [Type] | [Constraints] | [Description] |
| created_at | DateTime | NOT NULL, Default=now() | Creation timestamp |
| updated_at | DateTime | NOT NULL, Default=now() | Last update timestamp |

**Indexes**:
- Primary: `id`
- Foreign: `user_id` (for user isolation)
- Composite: `(user_id, created_at)` (for sorted user queries)

**Relationships**:
- Many-to-One: `[TableName]` → `User`
- One-to-Many: `[TableName]` → `[RelatedTable]`

---

## API Design

### Endpoint 1: List [Resource]

```http
GET /api/{user_id}/[resource]
Authorization: Bearer <jwt_token>

Query Parameters:
  - status: string (optional) - Filter by status
  - sort: string (optional) - Sort field (created, updated)
  - limit: integer (optional) - Pagination limit (default: 50)
  - offset: integer (optional) - Pagination offset (default: 0)

Response 200:
{
  "items": [
    {
      "id": 1,
      "field": "value",
      "created_at": "2025-12-15T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}

Errors:
  - 401: Unauthorized (invalid JWT)
  - 403: Forbidden (user_id mismatch)
```

### Endpoint 2: Create [Resource]

```http
POST /api/{user_id}/[resource]
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request Body:
{
  "field": "value",
  "priority": "high"
}

Response 201:
{
  "id": 1,
  "field": "value",
  "user_id": "uuid",
  "created_at": "2025-12-15T10:00:00Z"
}

Errors:
  - 400: Validation error (invalid field)
  - 401: Unauthorized
  - 403: Forbidden
```

### Endpoint 3: Update [Resource]

```http
PUT /api/{user_id}/[resource]/{id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request Body:
{
  "field": "new_value"
}

Response 200:
{
  "id": 1,
  "field": "new_value",
  "updated_at": "2025-12-15T11:00:00Z"
}

Errors:
  - 400: Validation error
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Resource not found
```

### Endpoint 4: Delete [Resource]

```http
DELETE /api/{user_id}/[resource]/{id}
Authorization: Bearer <jwt_token>

Response 204: No Content

Errors:
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Resource not found
```

---

## Implementation Tasks

### Task 1: Database Schema & Migration
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] SQLModel class created in `backend/app/models/[feature].py`
- [ ] All fields, constraints, and relationships defined
- [ ] Indexes created for performance
- [ ] Alembic migration generated: `alembic revision --autogenerate`
- [ ] Migration applied: `alembic upgrade head`
- [ ] Migration tested (upgrade and downgrade)

**Files**:
- `backend/app/models/[feature].py`
- `backend/alembic/versions/XXX_add_[feature]_table.py`

---

### Task 2: Backend API - Pydantic Schemas
**Complexity**: Simple
**Dependencies**: Task 1 (needs models)

**Acceptance Criteria**:
- [ ] Request schemas created (Create, Update)
- [ ] Response schemas created (Single, List)
- [ ] Validation rules match spec requirements
- [ ] Type hints on all fields

**Files**:
- `backend/app/schemas/[feature].py`

---

### Task 3: Backend API - CRUD Endpoints
**Complexity**: Moderate
**Dependencies**: Task 1, Task 2

**Acceptance Criteria**:
- [ ] All 4 CRUD endpoints implemented (List, Create, Update, Delete)
- [ ] JWT authentication on all endpoints (`Depends(get_current_user)`)
- [ ] User_id validation (can only access own resources)
- [ ] Pagination on list endpoint
- [ ] Error handling with proper status codes
- [ ] OpenAPI docs auto-generated

**Files**:
- `backend/app/routers/[feature].py`
- `backend/app/main.py` (register router)

---

### Task 4: Backend API - Tests
**Complexity**: Moderate
**Dependencies**: Task 3

**Acceptance Criteria**:
- [ ] pytest test file created
- [ ] Tests for all CRUD operations (happy path)
- [ ] Tests for error cases (401, 403, 404, 400)
- [ ] Tests for user isolation (can't access other users' data)
- [ ] 80%+ code coverage
- [ ] All tests passing

**Files**:
- `backend/tests/test_[feature].py`

---

### Task 5: Frontend - TypeScript Types
**Complexity**: Simple
**Dependencies**: Task 2 (matches backend schemas)

**Acceptance Criteria**:
- [ ] TypeScript interfaces defined in `frontend/lib/types.ts`
- [ ] Matches backend Pydantic schemas exactly
- [ ] Request and Response types defined

**Files**:
- `frontend/lib/types.ts`

---

### Task 6: Frontend - API Client
**Complexity**: Moderate
**Dependencies**: Task 5

**Acceptance Criteria**:
- [ ] API client created in `frontend/lib/[feature]-api.ts`
- [ ] Methods for all CRUD operations
- [ ] JWT token injection in headers
- [ ] Error handling (try/catch)
- [ ] Type-safe (uses TypeScript types)

**Files**:
- `frontend/lib/[feature]-api.ts`

---

### Task 7: Frontend - UI Components
**Complexity**: Complex
**Dependencies**: Task 6

**Acceptance Criteria**:
- [ ] List page created: `frontend/app/[feature]/page.tsx`
- [ ] Create form component
- [ ] Edit form component
- [ ] Delete confirmation modal
- [ ] Loading states implemented
- [ ] Error states displayed
- [ ] Responsive Tailwind CSS styling
- [ ] Accessibility (ARIA labels, keyboard navigation)

**Files**:
- `frontend/app/[feature]/page.tsx`
- `frontend/components/[Feature]List.tsx`
- `frontend/components/[Feature]Form.tsx`

---

### Task 8: Integration Testing
**Complexity**: Moderate
**Dependencies**: All previous tasks

**Acceptance Criteria**:
- [ ] End-to-end user flow tested
- [ ] Frontend can create, read, update, delete via backend
- [ ] JWT authentication working
- [ ] CORS configured correctly
- [ ] Error messages user-friendly
- [ ] Performance acceptable (< 200ms API response)

---

## Testing Strategy

### Unit Tests
**Backend** (`backend/tests/test_[feature].py`):
- Test each CRUD endpoint independently
- Mock database for isolation
- Test validation logic
- Test error handling

**Frontend** (if applicable):
- Test component rendering
- Test form validation
- Test API client methods

### Integration Tests
**Backend**:
- Test full request/response cycle
- Test database transactions
- Test authentication flow

**Frontend**:
- Test component integration
- Test API calls with mock server

### End-to-End Tests
- Test complete user workflows
- Test authentication from login to resource access
- Test error scenarios (network failures, invalid data)

---

## Risks & Mitigations

### Risk 1: Schema Migration Conflicts
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Test migration on copy of production database first
- Have rollback plan ready
- Coordinate with other developers on schema changes

### Risk 2: Frontend-Backend Type Mismatch
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Use api-schema-sync skill to validate types
- Add integration tests that catch type errors
- Review Pydantic schemas and TypeScript interfaces together

### Risk 3: Performance Issues with Large Datasets
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Implement pagination from the start
- Add database indexes on query fields
- Test with realistic data volume (1000+ records)

---

## Dependencies

**External**:
- None (or list external services/APIs)

**Internal**:
- User authentication system (existing)
- Database connection (existing)
- JWT token validation (existing)

**Blocking**:
- None (or list blockers)

---

## Success Metrics

**Functional**:
- [ ] All acceptance criteria from spec met
- [ ] All tests passing (unit + integration + E2E)
- [ ] Code reviewed and approved

**Non-Functional**:
- [ ] API response time < 200ms (p95)
- [ ] Frontend page load < 1s
- [ ] No security vulnerabilities (JWT enforced)
- [ ] 80%+ code coverage

---

## Rollback Plan

If implementation fails or critical bugs found:
1. **Backend**: Revert migration: `alembic downgrade -1`
2. **Frontend**: Revert to previous deployment
3. **Database**: Restore from backup if data corrupted

**Safe Rollback Window**: 24 hours after deployment

---

## Post-Implementation

After completing all tasks:
1. **Deploy to Staging**: Test in staging environment
2. **User Acceptance Testing**: Get user feedback
3. **Performance Testing**: Load test with realistic traffic
4. **Documentation**: Update API docs, user guides
5. **Create PHR**: Document implementation process
6. **Retrospective**: What went well? What could improve?
```

---

## Phase-Specific Patterns

### Phase I: Monolithic CLI

**Structure**:
```python
# main.py (single file)

# Constants
DATA_FILE = Path.home() / ".todo" / "data.json"

# Core Logic
def list_items():
    """List all items."""
    pass

def add_item(title: str):
    """Add new item."""
    pass

# File I/O
def load_data():
    """Load from JSON."""
    pass

def save_data(data):
    """Save to JSON."""
    pass

# CLI
def main():
    """Parse args and dispatch."""
    parser = argparse.ArgumentParser()
    # ... commands
```

**Tasks**:
1. Implement core logic functions
2. Add file I/O
3. Create CLI parser
4. Test manually
5. Write pytest tests

---

### Phase II: Modular Monolith

**Structure**:
```
backend/
  app/
    models/[feature].py       # SQLModel
    schemas/[feature].py      # Pydantic
    routers/[feature].py      # FastAPI
  tests/test_[feature].py

frontend/
  app/[feature]/page.tsx
  components/[Feature].tsx
  lib/[feature]-api.ts
```

**Tasks**:
1. Database schema & migration
2. Pydantic schemas
3. FastAPI CRUD endpoints
4. Backend tests
5. TypeScript types
6. API client
7. UI components
8. Integration tests

---

### Phase III: Agent-Augmented

**Structure**:
```
backend/
  app/
    mcp/tools/[tool].py       # MCP tools
    agents/orchestrator.py    # Agent logic
    models/conversation.py    # Chat history

frontend/
  app/agent/page.tsx          # ChatKit UI
  lib/chatkit-config.ts       # MCP tool config
```

**Tasks**:
1. Define MCP tools
2. Create agent orchestrator
3. Add conversations/messages tables
4. Implement chat API endpoints
5. Integrate OpenAI ChatKit
6. Test agent workflows

---

### Phase IV: Microservices

**Structure**:
```
services/
  [service-name]/
    Dockerfile
    app/main.py
    kubernetes/deployment.yaml

infrastructure/
  helm/[service]/
    Chart.yaml
    values.yaml
    templates/
```

**Tasks**:
1. Design service boundaries
2. Implement service logic
3. Create Dockerfile
4. Generate Helm chart
5. Deploy to Minikube (test)
6. Deploy to DOKS (production)

---

### Phase V: Event-Driven

**Structure**:
```
backend/
  app/
    schemas/events.py         # Event definitions
    utils/dapr_client.py      # Publisher

services/
  notification-service/
    app/main.py               # Subscriber

infrastructure/
  dapr/components/
    kafka-pubsub.yaml
```

**Tasks**:
1. Define event schemas
2. Configure Dapr components
3. Implement event publisher
4. Create subscriber service
5. Test event flow
6. Deploy event infrastructure

---

## Examples

### Example 1: Phase II Task Management Feature

**Input**: Spec for "Task Priority Management"

**Output**: Implementation plan with:
- Data Model: Add `priority_id` FK to tasks table
- API: CRUD endpoints for priorities, update task endpoint
- Frontend: Priority selector dropdown, color-coded priority badges
- Tasks: 8 tasks from schema to UI, with dependencies
- Testing: Unit tests for API, E2E test for complete priority workflow

---

### Example 2: Phase III AI Chat Feature

**Input**: Spec for "AI Task Assistant"

**Output**: Implementation plan with:
- Architecture: Stateless agent pattern with database-backed conversations
- Data Model: `conversations` and `messages` tables
- MCP Tools: `list_tasks`, `create_task`, `suggest_prioritization`
- API: Chat endpoints for conversation CRUD and message handling
- Frontend: OpenAI ChatKit integration with history sidebar
- Tasks: 10 tasks from agent setup to chat UI
- Testing: Mock LLM responses, test conversation persistence

---

## Quality Checklist

Before finalizing plan:
- [ ] Spec has been read completely
- [ ] Architecture aligns with current phase (I, II, III, IV, V)
- [ ] Data model includes all fields, indexes, relationships
- [ ] API endpoints follow RESTful conventions
- [ ] All tasks have clear acceptance criteria
- [ ] Task dependencies identified (no circular dependencies)
- [ ] Testing strategy covers unit, integration, E2E
- [ ] Risks identified with mitigation strategies
- [ ] Success metrics are measurable
- [ ] Rollback plan defined

## Post-Planning

After creating plan:
1. **Review with User**: Present plan for approval
2. **Refine**: Incorporate user feedback
3. **Create PHR**: Document planning process
4. **Generate Tasks**: Convert plan tasks to `/sp.tasks` format (if using task management)
5. **Begin Implementation**: Start with Task 1

**Plan is a Living Document**: Update as implementation reveals new information or challenges.
