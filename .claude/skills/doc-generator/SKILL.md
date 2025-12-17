---
name: "doc-generator"
description: "Generates comprehensive documentation for APIs, components, architecture, and deployment. Creates README files, API documentation, architecture diagrams, and deployment guides. Use when documentation is missing, outdated, or needs to be created from code."
version: "1.0.0"
---

# Doc Generator Skill

## When to Use
- User says "Generate documentation for..." or "Create README for..."
- API endpoints lack documentation
- New feature needs user-facing documentation
- Architecture changes require updated diagrams
- Deployment process needs step-by-step guide
- Onboarding documentation for new developers

## Context
This skill creates documentation for the Todo App across multiple formats:
- **README.md**: Project overview, setup, usage
- **API Documentation**: OpenAPI/Swagger specs, endpoint guides
- **Architecture Docs**: System diagrams, component relationships
- **Deployment Guides**: Step-by-step deployment instructions
- **Contributing Guides**: Development workflow, coding standards
- **Changelog**: Version history and release notes

## Workflow

### 1. Identify Documentation Type
Determine what type of documentation is needed:
- **Project README** - Overview and getting started
- **API Documentation** - Endpoint reference
- **Architecture Docs** - System design
- **Deployment Guide** - Production deployment
- **Contributing Guide** - Development workflow
- **Component Docs** - Frontend component library

### 2. Gather Information
- Read existing code and specs
- Extract API endpoints from routers
- Identify dependencies from package files
- Review architecture from codebase structure
- Check deployment configs (Docker, Kubernetes, etc.)

### 3. Generate Documentation
Use appropriate template for the documentation type.

### 4. Validate Documentation
- Check all code examples are correct
- Verify links work
- Ensure commands are accurate
- Test setup instructions

## Output Format

### README.md Template

```markdown
# [Project Name]

[One-line project description]

## Overview

[2-3 paragraph description of what the project does, its purpose, and key features]

## Features

- ✅ [Feature 1]
- ✅ [Feature 2]
- ✅ [Feature 3]
- 🚧 [In Progress Feature]
- 📋 [Planned Feature]

## Tech Stack

### Backend
- **Framework**: FastAPI 0.100+
- **Database**: PostgreSQL (Neon production, SQLite local)
- **ORM**: SQLModel 0.0.8
- **Authentication**: JWT with Better Auth
- **Testing**: pytest

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3
- **UI Components**: shadcn/ui
- **State Management**: React Context / Zustand

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube local, DOKS production)
- **Service Mesh**: Dapr
- **Event Streaming**: Kafka/Redpanda

## Architecture

```
┌─────────────┐
│   Frontend  │  Next.js 16 (Port 3000)
│   (React)   │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│   Backend   │  FastAPI (Port 8000)
│   (Python)  │
└──────┬──────┘
       │ SQLModel
       ▼
┌─────────────┐
│  Database   │  PostgreSQL/SQLite
│   (Neon)    │
└─────────────┘
```

## Prerequisites

- Node.js 18+ and npm/pnpm
- Python 3.13+
- PostgreSQL (or use SQLite for local)
- Docker (optional, for containerization)

## Installation

### 1. Clone Repository
\`\`\`bash
git clone https://github.com/[username]/[repo-name].git
cd [repo-name]
\`\`\`

### 2. Backend Setup
\`\`\`bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and secrets

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
\`\`\`

Backend runs on http://localhost:8000

### 3. Frontend Setup
\`\`\`bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your API URL

# Start dev server
npm run dev
\`\`\`

Frontend runs on http://localhost:3000

## Usage

### API Endpoints

**Authentication**:
- POST /auth/register - Register new user
- POST /auth/login - Login user
- GET /auth/me - Get current user

**Tasks**:
- GET /tasks/ - List tasks (paginated)
- POST /tasks/ - Create task
- GET /tasks/{id} - Get task by ID
- PATCH /tasks/{id} - Update task
- DELETE /tasks/{id} - Delete task

See full API documentation at http://localhost:8000/docs

### Environment Variables

**Backend** (`.env`):
\`\`\`env
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
\`\`\`

**Frontend** (`.env.local`):
\`\`\`env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
\`\`\`

## Development

### Running Tests

**Backend**:
\`\`\`bash
cd backend
pytest tests/ -v --cov=app
\`\`\`

**Frontend**:
\`\`\`bash
cd frontend
npm run test
\`\`\`

### Code Quality

**Backend**:
\`\`\`bash
# Format
black app/ tests/

# Lint
ruff app/ tests/

# Type check
mypy app/
\`\`\`

**Frontend**:
\`\`\`bash
# Format
npm run format

# Lint
npm run lint

# Type check
npm run type-check
\`\`\`

### Database Migrations

\`\`\`bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
\`\`\`

## Deployment

### Docker Compose (Development)

\`\`\`bash
docker-compose up -d
\`\`\`

### Kubernetes (Production)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

\`\`\`bash
# Build images
docker build -t [registry]/[app]-backend:latest ./backend
docker build -t [registry]/[app]-frontend:latest ./frontend

# Push images
docker push [registry]/[app]-backend:latest
docker push [registry]/[app]-frontend:latest

# Deploy with Helm
helm install [app] ./infrastructure/helm/[app]
\`\`\`

## Project Structure

\`\`\`
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # SQLModel database models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── routers/      # API endpoint routers
│   │   ├── auth.py       # JWT authentication
│   │   ├── database.py   # Database connection
│   │   └── main.py       # FastAPI app entry point
│   ├── tests/            # Pytest tests
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   ├── types/            # TypeScript type definitions
│   └── package.json      # Node dependencies
├── infrastructure/       # Deployment configs
│   ├── docker/           # Dockerfiles
│   ├── kubernetes/       # K8s manifests
│   └── helm/             # Helm charts
├── specs/                # Feature specifications
│   ├── overview.md
│   ├── features/
│   ├── api/
│   └── database/
└── history/              # Prompt History Records
    ├── prompts/
    └── adr/
\`\`\`

## Contributing

1. Read [CLAUDE.md](./CLAUDE.md) for project constitution and principles
2. Check [specs/](./specs/) for feature specifications
3. Follow the spec-first development workflow
4. Write tests for all new features
5. Create PHR (Prompt History Record) for completed work
6. Submit PR following the template

## License

[License Type]

## Support

- Issues: [GitHub Issues](https://github.com/[username]/[repo]/issues)
- Docs: [Documentation](https://[docs-url])
- Chat: [Discord/Slack]
\`\`\`

---

### API Documentation Template

```markdown
# API Documentation

## Base URL
- **Development**: http://localhost:8000
- **Production**: https://api.[domain].com

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

\`\`\`
Authorization: Bearer <token>
\`\`\`

### Get Token

**POST /auth/login**

Request:
\`\`\`json
{
  "email": "user@example.com",
  "password": "secure-password"
}
\`\`\`

Response:
\`\`\`json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
\`\`\`

## Endpoints

### Tasks

#### List Tasks
**GET /tasks/**

Query Parameters:
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20, max: 100) - Items per page
- `status` (string, optional) - Filter by status: "pending", "in_progress", "completed"
- `priority` (string, optional) - Filter by priority: "low", "normal", "high"

Response:
\`\`\`json
{
  "items": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "priority": "high",
      "due_date": "2025-12-20T00:00:00",
      "created_at": "2025-12-17T10:00:00",
      "updated_at": "2025-12-17T10:00:00",
      "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
\`\`\`

#### Create Task
**POST /tasks/**

Request:
\`\`\`json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "due_date": "2025-12-20T00:00:00"
}
\`\`\`

Response (201 Created):
\`\`\`json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "priority": "high",
  "due_date": "2025-12-20T00:00:00",
  "created_at": "2025-12-17T10:00:00",
  "updated_at": "2025-12-17T10:00:00",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
\`\`\`

#### Get Task
**GET /tasks/{id}**

Response:
\`\`\`json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "priority": "high",
  "due_date": "2025-12-20T00:00:00",
  "created_at": "2025-12-17T10:00:00",
  "updated_at": "2025-12-17T10:00:00",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
\`\`\`

#### Update Task
**PATCH /tasks/{id}**

Request (all fields optional):
\`\`\`json
{
  "title": "Buy groceries and cook dinner",
  "status": "in_progress"
}
\`\`\`

Response:
\`\`\`json
{
  "id": 1,
  "title": "Buy groceries and cook dinner",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-12-20T00:00:00",
  "created_at": "2025-12-17T10:00:00",
  "updated_at": "2025-12-17T15:30:00",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
\`\`\`

#### Delete Task
**DELETE /tasks/{id}**

Response: 204 No Content

## Error Responses

### 400 Bad Request
\`\`\`json
{
  "detail": "Validation error message"
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "detail": "Invalid or missing authentication token"
}
\`\`\`

### 404 Not Found
\`\`\`json
{
  "detail": "Task not found"
}
\`\`\`

### 422 Unprocessable Entity
\`\`\`json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
\`\`\`

## Rate Limiting

- **Unauthenticated**: 100 requests/hour
- **Authenticated**: 1000 requests/hour

## Pagination

All list endpoints support pagination:
- Default page size: 20
- Max page size: 100
- Use `page` and `page_size` query parameters

Response includes:
- `items`: Array of results
- `total`: Total count
- `page`: Current page
- `page_size`: Items per page

## Versioning

API version is included in the URL path:
- Current: `/v1/...`
- Legacy: `/v0/...` (deprecated)
```

---

### Architecture Documentation Template

```markdown
# Architecture Documentation

## System Overview

[High-level description of the system architecture]

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                       Client Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  Web App    │  │  Mobile App │  │  CLI Tool   │      │
│  │  (Next.js)  │  │  (React N.) │  │  (Python)   │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
└─────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                      API Gateway                          │
│                    (FastAPI / Nginx)                      │
└─────────────────────┬────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Task Service    │    │  User Service    │
│  (FastAPI)       │    │  (FastAPI)       │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌──────────────────────┐
         │  Database (Postgres) │
         └──────────────────────┘
```

## Components

### Frontend (Next.js 16)
**Responsibility**: User interface and client-side logic

**Technologies**:
- React 19
- TypeScript 5
- Tailwind CSS 3
- shadcn/ui components

**Key Files**:
- `app/` - App Router pages
- `components/` - Reusable components
- `lib/api.ts` - API client

### Backend (FastAPI)
**Responsibility**: Business logic and data access

**Technologies**:
- FastAPI 0.100+
- SQLModel 0.0.8
- Pydantic v2
- Alembic (migrations)

**Key Files**:
- `app/main.py` - Application entry point
- `app/routers/` - API endpoints
- `app/models/` - Database models
- `app/schemas/` - Request/response schemas

### Database (PostgreSQL)
**Responsibility**: Data persistence

**Technologies**:
- PostgreSQL 15+
- Neon (production)
- SQLite (local development)

**Schema**:
- `users` - User accounts
- `tasks` - Todo tasks
- `comments` - Task comments

## Data Flow

### Create Task Flow

1. User submits form in Next.js app
2. Frontend sends POST /tasks/ with JWT token
3. FastAPI validates JWT, extracts user_id
4. SQLModel creates Task with user_id
5. Database persists task
6. Response returns task with ID
7. Frontend updates UI

### Authentication Flow

1. User submits login form
2. Backend validates credentials
3. JWT token generated and returned
4. Frontend stores token in httpOnly cookie
5. All subsequent requests include token in Authorization header
6. Backend validates token on each request

## Security Architecture

### Authentication
- JWT tokens with HS256 signing
- Token expiry: 7 days
- Refresh tokens: Not implemented yet

### Authorization
- Row-level security via user_id checks
- All data operations scoped to authenticated user
- Admin role for elevated permissions

### Data Protection
- HTTPS enforced in production
- Passwords hashed with bcrypt
- Environment variables for secrets
- CORS configured for allowed origins

## Deployment Architecture

### Development
- Docker Compose
- Local database (SQLite)
- Hot reload enabled

### Staging
- Kubernetes (Minikube)
- Neon PostgreSQL
- SSL certificates

### Production
- Kubernetes (DOKS)
- Neon PostgreSQL (production branch)
- Let's Encrypt SSL
- Horizontal pod autoscaling

## Scalability Considerations

### Current Limits
- Single backend instance
- Single database instance
- Synchronous request handling

### Scaling Strategy (Phase IV/V)
- Horizontal scaling with Kubernetes
- Event-driven architecture with Dapr + Kafka
- Microservices decomposition
- Caching layer (Redis)
```

## Quality Checklist

Before finalizing documentation:
- [ ] All code examples are tested and correct
- [ ] Commands work on both Windows and Unix
- [ ] Environment variables documented
- [ ] Prerequisites clearly listed
- [ ] Installation steps are sequential and complete
- [ ] API endpoints include request/response examples
- [ ] Error responses documented
- [ ] Architecture diagrams are accurate
- [ ] Links to external resources work
- [ ] Project structure reflects actual codebase
- [ ] Contributing guidelines included
- [ ] License information present

## Common Documentation Types

### 1. Component Documentation (Frontend)
```markdown
# Button Component

## Usage
\`\`\`tsx
import { Button } from '@/components/ui/button'

<Button variant="primary" onClick={handleClick}>
  Click Me
</Button>
\`\`\`

## Props
- `variant`: "primary" | "secondary" | "danger"
- `size`: "sm" | "md" | "lg"
- `disabled`: boolean
```

### 2. Changelog
```markdown
# Changelog

## [1.2.0] - 2025-12-17

### Added
- Task priority levels (low, normal, high)
- Due date reminders

### Changed
- Improved task list performance

### Fixed
- Auth token expiration handling

## [1.1.0] - 2025-12-10
...
```

### 3. Deployment Guide
```markdown
# Deployment Guide

## Prerequisites
- Docker Hub account
- Kubernetes cluster
- Domain with DNS access

## Steps

### 1. Build Images
\`\`\`bash
docker build -t username/app-backend:v1.0.0 ./backend
docker build -t username/app-frontend:v1.0.0 ./frontend
\`\`\`

### 2. Push to Registry
\`\`\`bash
docker push username/app-backend:v1.0.0
docker push username/app-frontend:v1.0.0
\`\`\`

### 3. Deploy to Kubernetes
\`\`\`bash
kubectl apply -f infrastructure/kubernetes/
\`\`\`
```

## Post-Generation

After creating documentation:
1. **Review for Accuracy**: Test all commands and examples
2. **Check Links**: Verify all URLs work
3. **Add to Project**: Place in appropriate location
4. **Update README**: Link to new documentation
5. **Create PHR**: Document the documentation work
6. **Announce**: Share with team/users
