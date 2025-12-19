---
id: 003
title: Phase IV Implementation Plan
stage: plan
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 007-minikube-deployment
branch: 007-minikube-deployment
user: MathNj
command: /sp.plan
labels: ["phase-iv", "kubernetes", "docker", "helm", "minikube", "infrastructure", "planning"]
links:
  spec: specs/007-minikube-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-minikube-deployment/plan.md
  - specs/007-minikube-deployment/research.md
  - specs/007-minikube-deployment/data-model.md
  - specs/007-minikube-deployment/quickstart.md
  - specs/007-minikube-deployment/contracts/dockerfile-backend.md
  - specs/007-minikube-deployment/contracts/dockerfile-frontend.md
  - specs/007-minikube-deployment/contracts/helm-chart-structure.md
tests:
  - Constitution Check validation (all gates passed)
  - Technical Context completeness verification
---

## Prompt

```text
@specs/infrastructure/phase4-k8s.md "Analyze the infrastructure spec and create a detailed step-by-step plan to implement Phase IV. ensure the plan prioritizes: 1. Creating optimized Dockerfiles first. 2. Generating the Helm Chart structure. 3. Providing the commands to build images inside Minikube."
```

## Response snapshot

Created comprehensive implementation plan for Phase IV Local Kubernetes Infrastructure.

**Planning Approach**:
- User requested analysis of `@specs/infrastructure/phase4-k8s.md` (file doesn't exist)
- Used existing `specs/007-minikube-deployment/spec.md` which contains all Phase IV requirements
- Prioritized: Dockerfiles → Helm Charts → Minikube build commands (as requested)

**Plan Structure**:

**Technical Context** (Complete):
- Languages: Python 3.13+ (backend), Node.js 20 LTS (frontend)
- Dependencies: FastAPI, Next.js, Docker, Helm 3.x, Kubernetes
- Storage: External Neon PostgreSQL
- Performance: <3min backend build, <4min frontend build, <2min pod startup
- Constraints: Backend <200MB, Frontend <150MB, 6GB RAM minimum
- Scale: 2 backend replicas, 1 frontend replica

**Constitution Check** (✅ ALL GATES PASSED):
- ✅ Spec-First Development: spec.md approved with 22 FRs, 14 success criteria
- ✅ Evolutionary Architecture: Phase III → Phase IV transition (ADR required)
- ✅ Technology Stack Governance: Phase IV approved stack (Docker, K8s, Helm)
- ✅ Infrastructure & DevOps Standards: All 5 rules compliant
  - Multi-stage Docker builds ✓
  - Kubernetes (Minikube/DOKS) ✓
  - Helm Charts mandatory ✓
  - kubectl-ai/kagent compatibility ✓
  - Kubernetes Secrets ✓

**Phase 0 - Research** (10 key decisions):
1. Multi-stage Docker strategy (3-stage frontend, 2-stage backend)
2. Helm architecture (single chart + environment values files)
3. Secrets management (manual kubectl for local, External Secrets for production future)
4. Minikube image building (build inside Docker daemon with `eval $(minikube docker-env)`)
5. Backend replica management (2 stateless replicas with health probes)
6. Frontend standalone output (Next.js optimization ~70% size reduction)
7. Service mesh deferred (NodePort for local, LoadBalancer for production)
8. AI ops compatibility (standardized labels and annotations)
9. Docker build optimization (layer caching, .dockerignore)
10. Resource limits (conservative for local, tunable via Helm)

**Phase 1 - Design Artifacts**:
- **data-model.md**: Infrastructure entities (Docker images, Helm chart, K8s resources, health checks)
- **quickstart.md**: Step-by-step deployment guide (10-15 min setup)
- **contracts/dockerfile-backend.md**: Multi-stage Python build with uv
- **contracts/dockerfile-frontend.md**: 3-stage Next.js with standalone output
- **contracts/helm-chart-structure.md**: Complete Helm chart specification

**Key Technical Decisions**:

1. **Docker Strategy**:
   - Backend: 2-stage (builder with uv + slim runtime)
   - Frontend: 3-stage (dependencies + builder + runner with standalone output)
   - Target sizes: Backend ~150MB, Frontend ~120MB

2. **Helm Architecture**:
   - Single chart: `todo-stack`
   - 3 values files: values.yaml (defaults), values-local.yaml, values-production.yaml
   - Templates: 2 Deployments, 2 Services, 1 Secret ref, 1 ConfigMap, 1 Ingress (optional)

3. **Minikube Workflow**:
   ```bash
   # Step 1: Start Minikube
   minikube start --cpus=4 --memory=6144

   # Step 2: Connect Docker to Minikube
   eval $(minikube docker-env)

   # Step 3: Build images inside Minikube
   docker build -t todo-backend:local ./backend
   docker build -t todo-frontend:local ./frontend

   # Step 4: Create secrets
   kubectl create secret generic todo-secrets \
     --from-literal=DATABASE_URL=... \
     --from-literal=OPENAI_API_KEY=... \
     --from-literal=BETTER_AUTH_SECRET=...

   # Step 5: Deploy with Helm
   helm install todo-stack ./infrastructure/helm/todo-stack -f values-local.yaml
   ```

4. **Scalability Pattern**:
   - Backend: 2 replicas, stateless, JWT auth, load balanced via ClusterIP
   - Frontend: 1 replica, NodePort 30080 for local access
   - Health probes: Readiness (database check) + Liveness (process check)

5. **Security**:
   - Non-root users in containers (appuser:1000, nextjs:1001)
   - Kubernetes Secrets for all sensitive data
   - No hardcoded credentials in images or Helm values

**Action Items Identified**:
1. Create ADR for Phase III → Phase IV transition (containerization strategy)
2. Verify Phase III Todo Chatbot completion status
3. Consider constitution update (Phase IV officially beginning - 3.1.0 → 4.0.0)

**Project Structure** (Phase IV additions):
- `backend/Dockerfile` (NEW)
- `backend/.dockerignore` (NEW)
- `frontend/Dockerfile` (NEW)
- `frontend/.dockerignore` (NEW)
- `infrastructure/helm/todo-stack/` (NEW - complete chart)
- `infrastructure/minikube/setup-minikube.sh` (NEW)
- `infrastructure/docs/deployment-guide.md` (NEW)

## Outcome

- ✅ Impact: Complete Phase IV implementation plan created with prioritized execution strategy (Dockerfiles → Helm → Minikube commands)
- 🧪 Tests: Constitution Check passed all gates, technical context validated
- 📁 Files: 7 files created (plan.md, research.md, data-model.md, quickstart.md, 3 contracts)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task breakdown, then `/sp.implement` to execute
- 🧠 Reflection: Plan follows user's priority order: optimized Dockerfiles specified first (contracts), Helm chart structure detailed, Minikube build workflow documented in quickstart. All decisions align with Constitution Section IV (Infrastructure & DevOps Standards) and support 14 success criteria from spec.

## Evaluation notes (flywheel)

- Failure modes observed: User referenced non-existent file `@specs/infrastructure/phase4-k8s.md` - gracefully handled by using existing spec.md
- Graders run and results (PASS/FAIL): PASS - All constitution gates passed, no NEEDS CLARIFICATION in Technical Context, comprehensive design artifacts generated
- Prompt variant (if applicable): User requested prioritized approach (Dockerfiles → Helm → Minikube) - plan structure reflects this priority
- Next experiment (smallest change to try): Validate Dockerfile contracts by creating actual Dockerfile files in backend/ and frontend/ directories to test build process
