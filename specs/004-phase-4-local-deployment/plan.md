# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Branch**: `main` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Phase IV specification with AI-assisted DevOps tooling (Gordon, kubectl-ai, kagent)

## Summary

Deploy the Phase III Todo Chatbot application to a local Kubernetes cluster (Minikube) using AI-assisted DevOps tools for containerization, deployment, and cluster management. This phase introduces Docker AI (Gordon) for container optimization, kubectl-ai for natural language Kubernetes operations, and kagent for AI-powered SRE operations.

**Primary Goal**: Establish production-grade local deployment pipeline with AI-assisted tooling to reduce manual DevOps overhead and improve deployment reliability.

**Technical Approach**: Multi-stage Docker builds → Gordon optimization → kubectl-ai deployments → kagent health monitoring

## Technical Context

**Language/Version**: Python 3.13+ (Backend), Node.js 20+ (Frontend)
**Primary Dependencies**: Docker Desktop 4.x, Minikube 1.32+, Helm 3.x, kubectl 1.28+
**AI DevOps Tools**: Docker AI (Gordon), kubectl-ai, kagent
**Container Runtime**: Docker (containerd backend)
**Orchestration**: Kubernetes 1.28+ (via Minikube)
**Package Manager**: Helm 3.x
**Storage**: PostgreSQL (Neon for production, containerized for local)
**Testing**: Docker health checks, K8s readiness/liveness probes, integration tests
**Target Platform**: Local development (Minikube on Windows/macOS/Linux)
**Project Type**: Web application (FastAPI backend + Next.js frontend)
**Performance Goals**: <100MB backend image, <200MB frontend image, <30s deployment time
**Constraints**: Local resource limits (4GB RAM allocated to Minikube), ephemeral storage
**Scale/Scope**: 2 services (backend, frontend), 2-3 replicas each, <10 pods total

## Constitution Check

*GATE: Must pass before implementation. AI-assisted tools must be available.*

✅ **Simplicity**: Multi-stage Docker builds minimize complexity
✅ **Local-First**: Minikube provides local Kubernetes environment
✅ **AI-Assisted**: Gordon, kubectl-ai, and kagent reduce manual DevOps overhead
✅ **Production-Ready**: Helm charts enable cloud migration (Phase V)
✅ **Security**: Non-root users, secret management, security scanning with Gordon
⚠️ **Complexity Justified**: Kubernetes adds complexity but prepares for cloud deployment

## Project Structure

### Documentation (this feature)

```text
specs/004-phase-4-local-deployment/
├── spec.md              # Feature specification with AI DevOps requirements
├── plan.md              # This file - implementation plan
├── tasks.md             # Task breakdown (to be created)
├── data-model.md        # Deployment architecture and data flow
├── quickstart.md        # Quick start guide for local deployment
├── research.md          # Research on AI DevOps tools
├── contracts/           # API contracts (unchanged from Phase III)
├── docker-containers/   # Dockerfile templates and configs
├── helm-chart/          # Helm chart templates
└── k8s-blueprint/       # Raw Kubernetes manifests
```

### Source Code (repository root)

```text
backend/
├── Dockerfile           # Multi-stage build for FastAPI backend
├── .dockerignore        # Exclude unnecessary files
├── app/                 # Application code (existing)
└── requirements.txt     # Python dependencies (existing)

frontend/
├── Dockerfile           # Multi-stage build for Next.js frontend
├── .dockerignore        # Exclude node_modules, .next
├── app/                 # Next.js app (existing)
└── package.json         # Node dependencies (existing)

k8s/
├── backend/
│   ├── deployment.yaml  # Backend Deployment
│   ├── service.yaml     # Backend Service
│   └── configmap.yaml   # Backend ConfigMap
├── frontend/
│   ├── deployment.yaml  # Frontend Deployment
│   ├── service.yaml     # Frontend Service (NodePort)
│   └── configmap.yaml   # Frontend ConfigMap
├── database/
│   ├── deployment.yaml  # PostgreSQL Deployment (optional for local)
│   ├── service.yaml     # PostgreSQL Service
│   └── pvc.yaml         # Persistent Volume Claim
└── secrets/
    └── app-secrets.yaml # Secrets template (not committed)

helm/
└── todo-app/
    ├── Chart.yaml       # Helm chart metadata
    ├── values.yaml      # Default values
    └── templates/
        ├── backend/     # Backend templates
        ├── frontend/    # Frontend templates
        └── _helpers.tpl # Helper templates

.github/
└── workflows/
    └── phase-4-deployment.yml  # CI/CD for Phase IV (optional)
```

**Structure Decision**: Web application structure (Option 2) with added Kubernetes and Helm directories. Dockerfiles colocated with source code. Kubernetes manifests organized by service in `k8s/` directory. Helm chart provides reusable packaging for Phase V migration.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Namespace: default                  │  │
│  │                                                         │  │
│  │  ┌──────────────────┐       ┌──────────────────┐      │  │
│  │  │  Frontend Pod    │       │  Backend Pod     │      │  │
│  │  │  ┌────────────┐  │       │  ┌────────────┐  │      │  │
│  │  │  │ Next.js    │  │       │  │  FastAPI   │  │      │  │
│  │  │  │ (port 3000)│  │       │  │ (port 8000)│  │      │  │
│  │  │  └────────────┘  │       │  └────────────┘  │      │  │
│  │  │  Replicas: 2     │       │  Replicas: 2     │      │  │
│  │  └──────────────────┘       └──────────────────┘      │  │
│  │           ▲                           ▲                │  │
│  │           │                           │                │  │
│  │  ┌────────┴────────┐       ┌─────────┴────────┐       │  │
│  │  │  Frontend Svc   │       │   Backend Svc    │       │  │
│  │  │  (NodePort)     │       │   (ClusterIP)    │       │  │
│  │  │  30080:3000     │       │   8000:8000      │       │  │
│  │  └─────────────────┘       └──────────────────┘       │  │
│  │                                     │                  │  │
│  │                           ┌─────────┴────────┐         │  │
│  │                           │   PostgreSQL     │         │  │
│  │                           │   (External)     │         │  │
│  │                           │   Neon Cloud     │         │  │
│  │                           └──────────────────┘         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                     │                    │
         ▼                     ▼                    ▼
    [Gordon]             [kubectl-ai]          [kagent]
  Optimize Images     Deploy/Scale/Debug    Monitor Health
```

### AI DevOps Tooling Integration

1. **Gordon (Docker AI Agent)**
   - **Purpose**: Optimize Dockerfiles, scan for vulnerabilities
   - **Usage**: `docker ai "optimize backend/Dockerfile for minimal size"`
   - **Integration Point**: Before building production images
   - **Fallback**: Manual Dockerfile optimization

2. **kubectl-ai**
   - **Purpose**: Natural language Kubernetes operations
   - **Usage**: `kubectl-ai "deploy todo frontend with 2 replicas"`
   - **Integration Point**: Deployment, scaling, troubleshooting
   - **Fallback**: Standard kubectl commands

3. **kagent**
   - **Purpose**: AI-powered cluster health and SRE operations
   - **Usage**: `kagent "analyze cluster health and suggest optimizations"`
   - **Integration Point**: Post-deployment monitoring and optimization
   - **Fallback**: Manual kubectl commands and monitoring

## Implementation Phases

### Phase 0: Prerequisites and Tool Installation

**Objective**: Install and verify all required tools

**Tasks**:
1. Install Docker Desktop (if not installed)
2. Enable Kubernetes in Docker Desktop OR install Minikube
3. Install Helm CLI
4. Install Docker AI (Gordon) - verify with `docker ai --version`
5. Install kubectl-ai - verify with `kubectl-ai --version`
6. Install kagent - verify with `kagent --version`
7. Start Minikube (if using Minikube): `minikube start --memory=4096 --cpus=2`
8. Verify cluster: `kubectl cluster-info`

**Success Criteria**:
- All tools installed and accessible via CLI
- Minikube cluster running with adequate resources
- AI tools respond to version/help commands

**Estimated Effort**: 30-60 minutes (depending on downloads)

---

### Phase 1: Containerization with Gordon

**Objective**: Create optimized Docker images for backend and frontend

**Tasks**:

1. **Create Backend Dockerfile**
   - Multi-stage build (builder + runtime)
   - Non-root user (uid 1000)
   - Health check endpoint
   - Image size target: <100MB

2. **Gordon Optimization - Backend**
   - Run: `docker ai "review backend/Dockerfile and suggest optimizations"`
   - Apply suggestions for size and security
   - Run: `docker ai "scan backend image for vulnerabilities"`
   - Fix critical/high vulnerabilities

3. **Create Frontend Dockerfile**
   - Multi-stage build (dependencies → builder → runtime)
   - Standalone Next.js build
   - Non-root user
   - Image size target: <200MB

4. **Gordon Optimization - Frontend**
   - Run: `docker ai "optimize frontend/Dockerfile for production"`
   - Apply suggestions
   - Run: `docker ai "review frontend image security"`
   - Address security findings

5. **Build and Test Images Locally**
   - Build: `docker build -t todo-backend:latest ./backend`
   - Build: `docker build -t todo-frontend:latest ./frontend`
   - Test: `docker run -p 8000:8000 todo-backend:latest`
   - Test: `docker run -p 3000:3000 todo-frontend:latest`
   - Verify health checks and functionality

6. **Create .dockerignore Files**
   - Backend: Exclude `__pycache__`, `.pytest_cache`, `.env`, etc.
   - Frontend: Exclude `node_modules`, `.next`, `.git`, etc.

**Success Criteria**:
- ✅ Dockerfiles create functional images
- ✅ Images pass Gordon security scans
- ✅ Backend image <100MB, Frontend <200MB
- ✅ Containers run successfully with health checks
- ✅ Non-root users configured

**Estimated Effort**: 2-3 hours

---

### Phase 2: Kubernetes Manifests with kubectl-ai

**Objective**: Deploy services to Minikube using natural language commands

**Tasks**:

1. **Create Backend Deployment**
   - Use kubectl-ai: `kubectl-ai "create a deployment for todo backend with 2 replicas, image todo-backend:latest, port 8000"`
   - Review generated manifest
   - Add resource limits (CPU: 500m, Memory: 512Mi)
   - Add liveness/readiness probes
   - Save to `k8s/backend/deployment.yaml`

2. **Create Backend Service**
   - Use kubectl-ai: `kubectl-ai "create a ClusterIP service for todo backend on port 8000"`
   - Review and save to `k8s/backend/service.yaml`

3. **Create Frontend Deployment**
   - Use kubectl-ai: `kubectl-ai "deploy todo frontend with 2 replicas, expose port 3000"`
   - Review generated manifest
   - Add resource limits (CPU: 500m, Memory: 512Mi)
   - Add probes
   - Save to `k8s/frontend/deployment.yaml`

4. **Create Frontend Service (NodePort)**
   - Use kubectl-ai: `kubectl-ai "create a NodePort service for todo frontend on port 3000"`
   - Set NodePort to 30080 for consistency
   - Save to `k8s/frontend/service.yaml`

5. **Create ConfigMaps**
   - Backend: Environment variables (API URLs, feature flags)
   - Frontend: Runtime config (backend URL, public keys)
   - Use kubectl-ai or manual creation

6. **Create Secrets**
   - Template file: `k8s/secrets/app-secrets.yaml.template`
   - Actual secrets: Created manually (not committed to git)
   - Include: JWT secret, database URL, API keys

7. **Apply Manifests**
   - Use kubectl-ai: `kubectl-ai "apply all manifests in k8s/ directory"`
   - Or manual: `kubectl apply -f k8s/backend/ -f k8s/frontend/`
   - Verify: `kubectl get pods,svc`

**Success Criteria**:
- ✅ kubectl-ai generates valid Kubernetes manifests
- ✅ Deployments create pods successfully
- ✅ Services route traffic correctly
- ✅ Frontend accessible via NodePort (http://localhost:30080)
- ✅ Backend accessible from frontend pod
- ✅ ConfigMaps and Secrets mounted correctly

**Estimated Effort**: 2-3 hours

---

### Phase 3: Helm Chart Creation

**Objective**: Package application as reusable Helm chart for Phase V migration

**Tasks**:

1. **Generate Helm Chart Scaffold**
   - Use kubectl-ai: `kubectl-ai "create a helm chart for todo app"`
   - Or manual: `helm create helm/todo-app`
   - Clean up unnecessary templates

2. **Template Backend Resources**
   - Convert `k8s/backend/*.yaml` to Helm templates
   - Parameterize: image tag, replicas, resources, environment vars
   - Use `values.yaml` for configuration

3. **Template Frontend Resources**
   - Convert `k8s/frontend/*.yaml` to Helm templates
   - Parameterize: image tag, replicas, NodePort

4. **Configure values.yaml**
   - Default values for local deployment
   - Override sections for production (Phase V)
   - Document all values with comments

5. **Create _helpers.tpl**
   - Common labels
   - Name generators
   - Selector templates

6. **Test Helm Installation**
   - Lint: `helm lint helm/todo-app`
   - Dry run: `helm install todo-app helm/todo-app --dry-run --debug`
   - Install: `helm install todo-app helm/todo-app`
   - Verify: `kubectl get all -l app.kubernetes.io/instance=todo-app`

7. **Document Helm Usage**
   - Installation instructions
   - Value overrides
   - Upgrade/rollback procedures

**Success Criteria**:
- ✅ Helm chart passes linting
- ✅ Chart installs successfully
- ✅ All resources created with proper labels
- ✅ Values can be overridden
- ✅ Chart can be uninstalled cleanly

**Estimated Effort**: 2-3 hours

---

### Phase 4: Cluster Health Monitoring with kagent

**Objective**: Use kagent to monitor cluster health and optimize resource allocation

**Tasks**:

1. **Initial Cluster Health Analysis**
   - Run: `kagent "analyze the cluster health and identify any issues"`
   - Review report for warnings or errors
   - Document baseline metrics

2. **Resource Optimization**
   - Run: `kagent "analyze resource allocation and suggest optimizations"`
   - Review CPU/memory utilization
   - Adjust resource limits if needed
   - Re-apply manifests or upgrade Helm chart

3. **Performance Analysis**
   - Run: `kagent "check for performance bottlenecks in the todo app"`
   - Review pod performance metrics
   - Identify slow endpoints or resource-intensive operations

4. **Capacity Planning**
   - Run: `kagent "estimate capacity for 100 concurrent users"`
   - Review scaling recommendations
   - Document findings for Phase V

5. **Troubleshooting Scenarios**
   - Test: `kagent "why is the backend pod restarting?"`
   - Test: `kagent "diagnose connection issues between frontend and backend"`
   - Verify kagent provides actionable insights

6. **Create Health Monitoring Runbook**
   - Document common kagent commands
   - Create troubleshooting playbook
   - Add to quickstart.md

**Success Criteria**:
- ✅ kagent provides comprehensive health reports
- ✅ Resource optimization suggestions applied
- ✅ Performance bottlenecks identified and addressed
- ✅ Troubleshooting runbook created
- ✅ Cluster runs stably with <80% resource utilization

**Estimated Effort**: 1-2 hours

---

## Integration Workflow (Complete DevOps Cycle)

### Day 1: Containerization
1. Write Dockerfiles
2. Gordon: Optimize and scan
3. Build and test locally
4. Tag images for deployment

### Day 2: Deployment
1. Generate K8s manifests with kubectl-ai
2. Apply to cluster
3. Verify pods and services
4. Test application functionality

### Day 3: Packaging
1. Create Helm chart
2. Test installation/upgrade
3. Document values and usage

### Day 4: Monitoring
1. Run kagent health analysis
2. Optimize resources
3. Create runbook
4. Document findings

**Total Timeline**: 4 days (with AI tools) vs. 7-10 days (manual)

## Key Decisions and Rationale

### 1. Minikube vs. Docker Desktop Kubernetes

**Decision**: Support both, default to Minikube
**Rationale**:
- Minikube provides consistent environment across OS
- Docker Desktop K8s simpler for Mac/Windows users
- Instructions cover both approaches

**Trade-offs**:
- Minikube: Additional installation step, resource overhead
- Docker Desktop: Less portable, Mac/Windows only

### 2. Multi-Stage Docker Builds

**Decision**: Use multi-stage builds for both services
**Rationale**:
- Reduces final image size (50-70% reduction typical)
- Separates build dependencies from runtime
- Industry best practice

**Trade-offs**:
- More complex Dockerfiles
- Longer initial build time (cached after first build)

### 3. External PostgreSQL (Neon) vs. Containerized

**Decision**: Use existing Neon database, optionally containerize for offline development
**Rationale**:
- Avoids data migration
- Production-like environment
- Neon already configured in Phase III

**Trade-offs**:
- Requires internet connection
- Optional local PostgreSQL adds complexity

### 4. NodePort vs. Ingress for Frontend

**Decision**: NodePort for Phase IV, Ingress for Phase V
**Rationale**:
- NodePort simpler for local development
- No Ingress controller needed in Minikube
- Phase V will add Ingress for production

**Trade-offs**:
- NodePort not production-ready
- Non-standard port (30080)

### 5. Helm Chart Necessity

**Decision**: Create Helm chart in Phase IV
**Rationale**:
- Prepares for Phase V cloud deployment
- Reusable packaging
- Easier environment configuration

**Trade-offs**:
- Additional complexity for local deployment
- Learning curve for Helm

### 6. AI Tool Fallbacks

**Decision**: Provide standard kubectl alternatives for all AI commands
**Rationale**:
- AI tools may not be available in all environments
- Educational value in understanding raw commands
- Reliability when AI tools fail

**Trade-offs**:
- Dual documentation burden
- Potential for drift between AI and manual approaches

## Dependencies

### External Dependencies
- Docker Desktop 4.x or Docker Engine 20.x+
- Minikube 1.32+ (if not using Docker Desktop K8s)
- kubectl 1.28+
- Helm 3.x
- Docker AI (Gordon) - optional but recommended
- kubectl-ai - optional but recommended
- kagent - optional but recommended

### Internal Dependencies
- Phase III Todo Chatbot implementation (must be complete)
- Backend API at `/health` endpoint
- Frontend environment variable support
- Neon PostgreSQL database (or local PostgreSQL)

### Prerequisites
- Git repository with Phase III code
- Environment variables documented
- API contracts defined (from Phase III)

## Risk Mitigation

### Risk 1: Image Build Failures
**Mitigation**:
- Test Dockerfiles incrementally (one stage at a time)
- Use Gordon to identify issues early
- Maintain `.dockerignore` to exclude large files
- Document known build issues and solutions

### Risk 2: Minikube Resource Constraints
**Mitigation**:
- Allocate minimum 4GB RAM, 2 CPU cores
- Set resource limits on all pods
- Use kagent to monitor resource usage
- Document resource requirements in quickstart.md

### Risk 3: AI Tool Unavailability
**Mitigation**:
- Provide standard kubectl alternatives
- Document manual workflows
- Test both AI and manual approaches
- Make AI tools optional, not required

### Risk 4: Service Discovery Issues
**Mitigation**:
- Use Kubernetes DNS (service-name.namespace.svc.cluster.local)
- Test service connectivity with kubectl exec
- Document networking troubleshooting steps
- Use kubectl-ai to debug connectivity issues

### Risk 5: Secret Management
**Mitigation**:
- Never commit secrets to git
- Use `.gitignore` for `app-secrets.yaml`
- Provide template file with placeholders
- Document secret creation process clearly

### Risk 6: Database Connection Issues
**Mitigation**:
- Verify Neon connectivity from Minikube network
- Test database URL from pod (kubectl exec)
- Document connection string format
- Consider local PostgreSQL for offline development

## Success Metrics

### Quantitative Metrics
- ✅ Backend image size: <100MB (target: 80MB)
- ✅ Frontend image size: <200MB (target: 150MB)
- ✅ Deployment time: <30 seconds (from helm install)
- ✅ Pod startup time: <10 seconds (frontend), <5 seconds (backend)
- ✅ Health check response: <100ms
- ✅ Resource utilization: <80% CPU and Memory

### Qualitative Metrics
- ✅ Gordon provides actionable optimization suggestions
- ✅ kubectl-ai generates valid manifests
- ✅ kagent identifies real issues and optimizations
- ✅ Documentation is clear and complete
- ✅ Deployment is reproducible across environments

### Acceptance Criteria (from spec.md)
- ✅ SC-001: Application accessible via Minikube IP
- ✅ SC-002: Backend responds to health checks
- ✅ SC-003: Helm chart installs successfully
- ✅ SC-015: Gordon provides optimization suggestions
- ✅ SC-016: Gordon scans for security vulnerabilities
- ✅ SC-017: kubectl-ai deploys services successfully
- ✅ SC-021: kagent provides cluster health reports
- ✅ SC-022: kagent suggests resource optimizations

## Testing Strategy

### Container Testing
1. Build images: `docker build -t <service>:test .`
2. Run containers: `docker run -p <port>:<port> <service>:test`
3. Health checks: `curl http://localhost:<port>/health`
4. Gordon scans: `docker ai "scan <service>:test for vulnerabilities"`

### Kubernetes Testing
1. Manifest validation: `kubectl apply --dry-run=client -f k8s/`
2. Deployment rollout: `kubectl rollout status deployment/<name>`
3. Service connectivity: `kubectl exec -it <pod> -- curl http://<service>:<port>`
4. Logs inspection: `kubectl logs -f deployment/<name>`

### Helm Testing
1. Lint chart: `helm lint helm/todo-app`
2. Dry run: `helm install todo-app helm/todo-app --dry-run`
3. Install: `helm install todo-app helm/todo-app`
4. Upgrade: `helm upgrade todo-app helm/todo-app`
5. Rollback: `helm rollback todo-app`

### End-to-End Testing
1. Access frontend: `http://localhost:30080`
2. Login with test credentials
3. Create task via chatbot
4. Verify task appears in dashboard
5. Test voice interaction (if Phase III complete)

### AI Tool Testing
1. Gordon: Verify optimization suggestions are actionable
2. kubectl-ai: Verify generated manifests are valid
3. kagent: Verify health reports identify real issues

## Rollback Plan

### Container Issues
1. Revert to previous Dockerfile
2. Rebuild image
3. Update Kubernetes deployment with new image tag

### Deployment Issues
1. Delete resources: `kubectl delete -f k8s/`
2. Fix manifests
3. Reapply: `kubectl apply -f k8s/`

### Helm Issues
1. Rollback: `helm rollback todo-app <revision>`
2. Or uninstall: `helm uninstall todo-app`
3. Fix chart and reinstall

## Next Steps (Post Phase IV)

1. **Phase V Migration Planning**
   - Evaluate cloud providers (DigitalOcean Kubernetes, GKE, EKS)
   - Plan Ingress configuration
   - Design CI/CD pipeline
   - Plan monitoring and logging (Prometheus, Grafana)

2. **Performance Optimization**
   - Implement horizontal pod autoscaling
   - Add caching layer (Redis)
   - Optimize database queries
   - CDN for frontend assets

3. **Security Hardening**
   - Implement network policies
   - Add Pod Security Policies/Pod Security Standards
   - Scan images in CI/CD
   - Implement secrets rotation

4. **Observability**
   - Add distributed tracing (Jaeger)
   - Implement structured logging
   - Set up dashboards (Grafana)
   - Configure alerting (Prometheus Alertmanager)

## Appendix

### Useful Commands

**Minikube**:
```bash
minikube start --memory=4096 --cpus=2
minikube status
minikube dashboard
minikube service frontend --url
minikube stop
minikube delete
```

**Docker**:
```bash
docker build -t todo-backend:latest ./backend
docker run -p 8000:8000 todo-backend:latest
docker images
docker ps
docker logs <container-id>
```

**kubectl**:
```bash
kubectl get pods,svc,deployments
kubectl describe pod <pod-name>
kubectl logs -f <pod-name>
kubectl exec -it <pod-name> -- /bin/sh
kubectl delete pod <pod-name>
kubectl apply -f k8s/
kubectl port-forward service/backend 8000:8000
```

**Helm**:
```bash
helm install todo-app helm/todo-app
helm upgrade todo-app helm/todo-app
helm rollback todo-app
helm uninstall todo-app
helm list
helm get values todo-app
```

**Gordon**:
```bash
docker ai "optimize backend/Dockerfile"
docker ai "scan todo-backend:latest for vulnerabilities"
docker ai "why is my container crashing?"
```

**kubectl-ai**:
```bash
kubectl-ai "deploy todo backend with 2 replicas"
kubectl-ai "scale frontend to 3 replicas"
kubectl-ai "check why pods are failing"
kubectl-ai "create a service for backend on port 8000"
```

**kagent**:
```bash
kagent "analyze cluster health"
kagent "optimize resource allocation"
kagent "investigate performance issues"
kagent "estimate capacity for 100 users"
```

### References
- Kubernetes Documentation: https://kubernetes.io/docs/
- Helm Documentation: https://helm.sh/docs/
- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Gordon Documentation: (Docker AI - check Docker Desktop)
- kubectl-ai: (check installation docs)
- kagent: (check installation docs)
