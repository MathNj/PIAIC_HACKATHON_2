# Todo App Skills Library

Specialized, reusable skills for the Todo App project. Each skill automates a specific development task with intelligent workflows and best practices.

## Overview

Skills are invoked using the `Skill` tool with the skill name. Each skill provides:
- **When to Use**: Trigger conditions
- **Context**: Tech stack and patterns
- **Workflow**: Step-by-step execution
- **Output Formats**: Code templates and configurations
- **Examples**: Real-world usage scenarios
- **Quality Checklist**: Validation criteria

## Skills Catalog

### Development Skills

#### 1. **spec-architect** - Feature Specification
**Description**: Generates Spec-Kit Plus compliant feature specifications
**Use When**: Designing features or creating specs following spec-driven development workflow
**Output**: `specs/features/[feature].md` with requirements, data model, API contracts
**Version**: 2.0.0

#### 2. **backend-scaffolder** - Backend CRUD Scaffolding
**Description**: Scaffolds complete FastAPI vertical slices (Model, Schema, Router) with SQLModel, JWT auth, and pytest tests
**Use When**: User asks to "implement the backend" or "Generate CRUD endpoints"
**Output**:
- `backend/app/models/[feature].py` - SQLModel ORM
- `backend/app/schemas/[feature].py` - Pydantic DTOs
- `backend/app/routers/[feature].py` - FastAPI routes
- `backend/tests/test_[feature].py` - Pytest tests
**Version**: 2.0.0

#### 3. **frontend-component** - Next.js Component Builder
**Description**: Builds Next.js 16+ App Router components with TypeScript, Tailwind CSS, and API integration
**Use When**: UI implementation tasks in Phase II/III
**Output**:
- `frontend/app/[feature]/page.tsx` - Next.js pages
- `frontend/components/[Feature].tsx` - React components
- API integration with typed hooks
**Version**: 2.0.0

#### 4. **mcp-tool-maker** - MCP Tool Generator
**Description**: Creates MCP (Model Context Protocol) tools to expose backend functionality to AI agents
**Use When**: Phase III OpenAI ChatKit integration and AI-driven task management
**Output**: `backend/app/mcp/tools/[tool].py` - MCP tool definitions
**Version**: 2.0.0

### Deployment Skills

#### 5. **k8s-deployer** - Deployment Configuration Generator
**Description**: Generates deployment configurations: Docker containers, Kubernetes manifests, Dapr components
**Use When**: User asks to "deploy to Vercel", "containerize this", or "Create K8s manifests"
**Output**:
- `frontend/Dockerfile` and `backend/Dockerfile`
- `infrastructure/kubernetes/[service]-deployment.yaml`
- `infrastructure/dapr/components/*.yaml`
- `vercel.json` configurations
**Version**: 2.0.0

#### 6. **db-migration-wizard** - Database Migration Automation
**Description**: Automates Alembic migrations: generates scripts, handles schema changes, converts data types
**Use When**:
- "Add a new database column"
- "Change column type"
- "Fix schema mismatch"
- Errors show "column does not exist"
**Output**:
- Updated SQLModel models
- Alembic migration scripts
- Data conversion SQL
**Version**: 1.0.0

#### 7. **k8s-troubleshoot** - Kubernetes Troubleshooting
**Description**: Diagnoses and fixes Kubernetes issues: pod failures, ImagePullBackOff, CrashLoopBackOff, service connectivity
**Use When**:
- "Pod not starting"
- ImagePullBackOff, CrashLoopBackOff errors
- Services not accessible
- Dapr sidecar not injecting
**Output**: Diagnostic commands, root cause analysis, targeted fixes
**Version**: 1.0.0

### Integration Skills

#### 8. **dapr-event-flow** - Event-Driven Architecture Setup
**Description**: Automates Dapr pub/sub: configures components, implements publishers/subscribers, tests event flow
**Use When**:
- "Publish events" or "Subscribe to events"
- "Set up Dapr pub/sub"
- Building microservices that communicate
- Phase V event-driven workflows
**Output**:
- `backend/app/schemas/events.py` - Event schemas
- `backend/app/utils/dapr_client.py` - Publisher
- `notification-service/app/main.py` - Subscriber
- `infrastructure/dapr/components/*.yaml` - Dapr configs
**Version**: 1.0.0

#### 9. **api-schema-sync** - Frontend-Backend Schema Synchronization
**Description**: Synchronizes API contracts between FastAPI (Pydantic) and Next.js (TypeScript)
**Use When**:
- "Type mismatch" or "validation error"
- Backend schema changed
- Errors show "unable to parse string as integer"
- Adding new endpoints
**Output**:
- Updated TypeScript interfaces in `frontend/lib/types.ts`
- Type conversion helpers
- Typed API client methods
**Version**: 1.0.0

#### 10. **cors-fixer** - CORS Configuration Troubleshooter
**Description**: Diagnoses and fixes CORS errors: credentials mode conflicts, wildcard origins, JWT auth issues
**Use When**:
- "Blocked by CORS policy" error
- Frontend cannot connect to backend
- Preflight OPTIONS requests failing
**Output**:
- Updated FastAPI CORSMiddleware config
- Fixed frontend fetch requests
- Environment-specific CORS policies
**Version**: 1.0.0

## Usage Examples

### Example 1: Backend Development
```
User: "Create CRUD endpoints for the Comment feature"
Assistant: [Invokes backend-scaffolder skill]
Output:
  ✓ backend/app/models/comment.py
  ✓ backend/app/schemas/comment.py
  ✓ backend/app/routers/comment.py
  ✓ backend/tests/test_comment.py
```

### Example 2: Database Schema Change
```
User: "Add priority_id column to tasks table"
Assistant: [Invokes db-migration-wizard skill]
Output:
  ✓ Updated Task model with priority_id field
  ✓ Alembic migration: add_priority_id_to_tasks.py
  ✓ Applied migration to database
  ✓ Verified data integrity
```

### Example 3: CORS Error
```
User: "Frontend shows 'blocked by CORS policy' error"
Assistant: [Invokes cors-fixer skill]
Diagnosis: credentials mode conflict
Fix:
  ✓ Removed credentials: "include" from api.ts
  ✓ Rebuilt frontend Docker image
  ✓ Verified CORS resolved
```

### Example 4: Kubernetes Deployment Failure
```
User: "Backend pod stuck in CrashLoopBackOff"
Assistant: [Invokes k8s-troubleshoot skill]
Diagnosis: Missing DATABASE_URL environment variable
Fix:
  ✓ Created Kubernetes secret with DATABASE_URL
  ✓ Restarted deployment
  ✓ Verified pod running (2/2 READY)
```

### Example 5: Event-Driven Architecture
```
User: "Set up event publishing when tasks are created"
Assistant: [Invokes dapr-event-flow skill]
Output:
  ✓ TaskCreatedEvent schema defined
  ✓ Dapr client wrapper created
  ✓ Event publishing added to create_task endpoint
  ✓ kafka-pubsub.yaml component configured
  ✓ Notification service subscribes to task_created
```

## Skill Categories

### By Development Phase

**Phase I (Console App)**:
- spec-architect

**Phase II (Backend API)**:
- backend-scaffolder
- db-migration-wizard
- api-schema-sync
- cors-fixer

**Phase III (AI Agent)**:
- mcp-tool-maker
- frontend-component

**Phase IV (Local Kubernetes)**:
- k8s-deployer
- k8s-troubleshoot

**Phase V (Cloud Event-Driven)**:
- dapr-event-flow
- k8s-deployer
- k8s-troubleshoot

### By Domain

**Backend**:
- backend-scaffolder
- db-migration-wizard
- mcp-tool-maker

**Frontend**:
- frontend-component
- api-schema-sync
- cors-fixer

**Infrastructure**:
- k8s-deployer
- k8s-troubleshoot
- dapr-event-flow

**Specification**:
- spec-architect

## Skill Invocation

Skills are invoked using the `Skill` tool:

```typescript
Skill({
  skill: "backend-scaffolder"  // Skill name
})
```

**Note**: Skills are automatically invoked when relevant trigger conditions are detected. You can also explicitly request a skill.

## Quality Standards

All skills follow these quality standards:

### Output Quality
- ✅ Code follows project conventions (see `CLAUDE.md`)
- ✅ Type safety enforced (TypeScript, Pydantic)
- ✅ Security best practices (JWT auth, input validation)
- ✅ Error handling implemented
- ✅ Tests included where applicable

### Documentation
- ✅ Clear "When to Use" conditions
- ✅ Context explains tech stack and patterns
- ✅ Workflow provides step-by-step guidance
- ✅ Examples demonstrate real-world usage
- ✅ Quality checklist for validation

### Reusability
- ✅ Environment-agnostic (local, staging, production)
- ✅ Technology-specific but pattern-agnostic
- ✅ Configurable via environment variables
- ✅ Tested across multiple use cases

## Contributing New Skills

To create a new skill:

1. **Create skill directory**: `.claude/skills/[skill-name]/`
2. **Write SKILL.md** with sections:
   - YAML frontmatter (name, description, version)
   - When to Use
   - Context
   - Workflow
   - Output Formats
   - Example
   - Quality Checklist
3. **Test skill**: Verify on real project scenarios
4. **Update README**: Add skill to catalog and examples

## Skill Maintenance

Skills are versioned using semantic versioning:
- **Major (X.0.0)**: Breaking changes to workflow or output
- **Minor (1.X.0)**: New features or enhancements
- **Patch (1.0.X)**: Bug fixes and clarifications

## Related Documentation

- **Project Constitution**: `.specify/memory/constitution.md`
- **Backend Guide**: `backend/CLAUDE.md`
- **Frontend Guide**: `frontend/CLAUDE.md`
- **Deployment Guides**:
  - `MINIKUBE_DEPLOYMENT_GUIDE.md`
  - `DEPLOYMENT_GUIDE.md`
- **Spec Overview**: `specs/overview.md`

---

**Total Skills**: 10 (5 existing + 5 new)
**Coverage**: Full development lifecycle (specification → implementation → deployment → troubleshooting)
**Maintained By**: Todo App Development Team
**Last Updated**: 2025-12-12
