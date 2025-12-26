# Tasks: Phase IV - Local Kubernetes Deployment

**Branch**: `main` | **Date**: 2025-12-27
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Task Overview

This document breaks down Phase IV implementation into atomic, testable work units. Each task references the specification and plan, includes acceptance criteria, and provides test cases.

**Total Tasks**: 24
**Estimated Total Effort**: 8-10 hours (with AI tools), 15-20 hours (manual)

---

## Phase 0: Prerequisites and Tool Installation

### T-001: Verify Docker Desktop Installation

**Description**: Verify Docker Desktop is installed and running with Kubernetes enabled

**Preconditions**:
- Windows, macOS, or Linux environment
- Admin/sudo privileges

**Steps**:
1. Check Docker Desktop installation: `docker --version`
2. Verify Docker daemon running: `docker ps`
3. Check if Kubernetes is enabled in Docker Desktop settings (optional)

**Expected Outputs**:
- Docker version 4.x or higher
- Docker daemon responds to `docker ps`
- Decision: Use Docker Desktop K8s OR Minikube

**Test Cases**:
```bash
# TC-001-1: Docker version check
docker --version
# Expected: Docker version 4.x.x or higher

# TC-001-2: Docker daemon running
docker ps
# Expected: No errors (empty list OK)

# TC-001-3: Docker info
docker info
# Expected: Server info displayed
```

**Acceptance Criteria**:
- ✅ Docker CLI responds to commands
- ✅ Docker daemon is running
- ✅ Decision made: Docker Desktop K8s OR Minikube

**References**: [Plan § Phase 0](./plan.md#phase-0-prerequisites-and-tool-installation), [Spec § FR-001](./spec.md#functional-requirements)

---

### T-002: Install and Start Minikube

**Description**: Install Minikube (if not using Docker Desktop K8s) and start local cluster

**Preconditions**:
- Docker Desktop installed (from T-001)
- Decision to use Minikube (from T-001)
- Minimum 4GB RAM available for allocation

**Steps**:
1. Install Minikube (if not installed): Follow https://minikube.sigs.k8s.io/docs/start/
2. Start Minikube: `minikube start --memory=4096 --cpus=2`
3. Verify cluster: `kubectl cluster-info`
4. Check nodes: `kubectl get nodes`

**Expected Outputs**:
- Minikube started successfully
- Kubernetes cluster accessible via kubectl
- Single node in "Ready" state

**Test Cases**:
```bash
# TC-002-1: Minikube version
minikube version
# Expected: minikube version: v1.32.x or higher

# TC-002-2: Start Minikube
minikube start --memory=4096 --cpus=2
# Expected: "Done! kubectl is now configured..."

# TC-002-3: Cluster info
kubectl cluster-info
# Expected: Kubernetes control plane running at https://...

# TC-002-4: Node status
kubectl get nodes
# Expected: 1 node with STATUS "Ready"
```

**Acceptance Criteria**:
- ✅ Minikube installed and running
- ✅ kubectl configured to use Minikube context
- ✅ Cluster has 1 ready node
- ✅ Minimum 4GB RAM allocated

**References**: [Plan § Phase 0 Task 7-8](./plan.md#phase-0-prerequisites-and-tool-installation), [Spec § FR-002](./spec.md#functional-requirements)

**Skip If**: Using Docker Desktop Kubernetes instead of Minikube

---

### T-003: Install Helm CLI

**Description**: Install Helm package manager for Kubernetes

**Preconditions**:
- Kubernetes cluster running (from T-001 or T-002)

**Steps**:
1. Install Helm: Follow https://helm.sh/docs/intro/install/
2. Verify installation: `helm version`
3. Add stable repository (optional): `helm repo add stable https://charts.helm.sh/stable`

**Expected Outputs**:
- Helm CLI installed (version 3.x+)
- Helm can communicate with cluster

**Test Cases**:
```bash
# TC-003-1: Helm version
helm version
# Expected: version.BuildInfo{Version:"v3.x.x", ...}

# TC-003-2: Helm list (empty OK)
helm list
# Expected: No errors (empty list OK)
```

**Acceptance Criteria**:
- ✅ Helm 3.x or higher installed
- ✅ Helm can communicate with Kubernetes cluster
- ✅ No Helm 2.x (Tiller) components present

**References**: [Plan § Phase 0 Task 3](./plan.md#phase-0-prerequisites-and-tool-installation), [Spec § FR-004](./spec.md#functional-requirements)

---

### T-004: Install Docker AI (Gordon)

**Description**: Install and verify Docker AI agent (Gordon) for container optimization

**Preconditions**:
- Docker Desktop 4.x installed (from T-001)

**Steps**:
1. Check if Docker AI available: `docker ai --version` OR `docker ai --help`
2. If not available, check Docker Desktop settings for AI features
3. Enable Docker AI in Docker Desktop (if available)
4. Test Gordon: `docker ai "hello, can you help me?"`

**Expected Outputs**:
- Docker AI responds to commands
- Gordon provides helpful responses

**Test Cases**:
```bash
# TC-004-1: Docker AI version/help
docker ai --version
# OR
docker ai --help
# Expected: Command recognized, help text or version displayed

# TC-004-2: Gordon response test
docker ai "what is a Dockerfile?"
# Expected: Gordon provides explanation (not an error)
```

**Acceptance Criteria**:
- ✅ Docker AI (Gordon) available via CLI
- ✅ Gordon responds to simple queries
- ✅ AI suggestions can be reviewed

**References**: [Plan § Phase 0 Task 4](./plan.md#phase-0-prerequisites-and-tool-installation), [Spec § FR-023, US5](./spec.md#functional-requirements)

**Fallback**: If Docker AI unavailable, proceed without it (manual optimization required)

---

### T-005: Install kubectl-ai

**Description**: Install kubectl-ai for natural language Kubernetes operations

**Preconditions**:
- kubectl installed and configured (from T-001 or T-002)

**Steps**:
1. Install kubectl-ai: Follow installation docs (GitHub: sozercan/kubectl-ai)
2. Verify installation: `kubectl-ai --version` OR `kubectl-ai --help`
3. Test kubectl-ai: `kubectl-ai "what version is my cluster?"`

**Expected Outputs**:
- kubectl-ai installed and accessible
- kubectl-ai can communicate with cluster

**Test Cases**:
```bash
# TC-005-1: kubectl-ai version/help
kubectl-ai --version
# OR
kubectl-ai --help
# Expected: Command recognized

# TC-005-2: kubectl-ai cluster query
kubectl-ai "what is the cluster version?"
# Expected: kubectl-ai provides cluster version info

# TC-005-3: kubectl-ai dry run
kubectl-ai "create a pod named test-pod" --dry-run
# Expected: Manifest generated (not actually created)
```

**Acceptance Criteria**:
- ✅ kubectl-ai CLI installed
- ✅ kubectl-ai can query cluster info
- ✅ kubectl-ai provides confirmation prompts for destructive actions

**References**: [Plan § Phase 0 Task 5](./plan.md#phase-0-prerequisites-and-tool-installation), [Spec § FR-025-027, US6](./spec.md#functional-requirements)

**Fallback**: If kubectl-ai unavailable, use standard kubectl commands

---

### T-006: Install kagent

**Description**: Install kagent for AI-powered cluster health monitoring and SRE operations

**Preconditions**:
- kubectl installed and configured (from T-001 or T-002)

**Steps**:
1. Install kagent: Follow installation docs (GitHub: k8sgpt-ai/k8sgpt or similar)
2. Verify installation: `kagent --version` OR `kagent --help`
3. Test kagent: `kagent "check cluster health"`

**Expected Outputs**:
- kagent installed and accessible
- kagent can analyze cluster

**Test Cases**:
```bash
# TC-006-1: kagent version/help
kagent --version
# OR
kagent --help
# Expected: Command recognized

# TC-006-2: kagent cluster analysis
kagent "analyze the cluster"
# Expected: Health report generated
```

**Acceptance Criteria**:
- ✅ kagent CLI installed
- ✅ kagent can analyze cluster health
- ✅ kagent provides actionable recommendations

**References**: [Plan § Phase 0 Task 6](./plan.md#phase-0-prerequisites-and-tool-installation), [Spec § FR-028-030, US7](./spec.md#functional-requirements)

**Fallback**: If kagent unavailable, use manual kubectl commands and monitoring

---

## Phase 1: Containerization with Gordon

### T-007: Create Backend Dockerfile

**Description**: Create multi-stage Dockerfile for FastAPI backend with optimization targets

**Preconditions**:
- Backend code exists in `backend/` directory
- Python 3.13+ application (Phase III complete)

**Steps**:
1. Create `backend/Dockerfile`
2. Implement multi-stage build (builder + runtime)
3. Set non-root user (uid 1000)
4. Add HEALTHCHECK instruction
5. Target image size: <100MB

**Expected Outputs**:
- `backend/Dockerfile` created
- Multi-stage build: `builder` stage and `runtime` stage
- Non-root user configured
- Health check endpoint defined

**Dockerfile Structure**:
```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY ./app ./app
RUN useradd -u 1000 -m appuser && chown -R appuser:appuser /app
USER appuser
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl --fail http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Test Cases**:
```bash
# TC-007-1: Dockerfile syntax validation
docker build --no-cache -t backend-test:v1 ./backend
# Expected: Build succeeds

# TC-007-2: Image size check
docker images backend-test:v1 --format "{{.Size}}"
# Expected: Size shown (target: <100MB)

# TC-007-3: Non-root user verification
docker run --rm backend-test:v1 whoami
# Expected: "appuser" (not root)
```

**Acceptance Criteria**:
- ✅ Dockerfile builds successfully
- ✅ Multi-stage build implemented
- ✅ Non-root user (uid 1000) configured
- ✅ HEALTHCHECK instruction present
- ✅ Initial image size documented (optimization in T-008)

**References**: [Plan § Phase 1 Task 1](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-006](./spec.md#functional-requirements)

---

### T-008: Optimize Backend Dockerfile with Gordon

**Description**: Use Docker AI (Gordon) to optimize backend Dockerfile for size and security

**Preconditions**:
- Backend Dockerfile created (from T-007)
- Docker AI (Gordon) installed (from T-004)

**Steps**:
1. Run Gordon optimization: `docker ai "review backend/Dockerfile and suggest optimizations for minimal size and security"`
2. Review Gordon's suggestions
3. Apply actionable suggestions to Dockerfile
4. Rebuild image: `docker build -t todo-backend:optimized ./backend`
5. Compare image sizes (before vs after)

**Expected Outputs**:
- Gordon provides optimization suggestions
- Dockerfile updated based on suggestions
- Image size reduced (target: <100MB, ideal: <80MB)

**Test Cases**:
```bash
# TC-008-1: Gordon optimization suggestions
docker ai "review backend/Dockerfile and suggest optimizations"
# Expected: Gordon provides suggestions (e.g., use alpine, multi-stage, minimize layers)

# TC-008-2: Rebuild optimized image
docker build -t todo-backend:optimized ./backend
# Expected: Build succeeds

# TC-008-3: Size comparison
docker images todo-backend:optimized --format "{{.Size}}"
# Expected: Size <100MB (ideally <80MB)

# TC-008-4: Gordon security scan
docker ai "scan todo-backend:optimized for security vulnerabilities"
# Expected: Security report generated
```

**Acceptance Criteria**:
- ✅ Gordon provides actionable optimization suggestions
- ✅ Suggestions applied to Dockerfile
- ✅ Image size <100MB (ideally <80MB)
- ✅ Gordon security scan shows no critical vulnerabilities
- ✅ Image functionality verified (container runs successfully)

**References**: [Plan § Phase 1 Task 2](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-023-024, SC-015-016](./spec.md#functional-requirements)

**Fallback**: If Gordon unavailable, apply manual optimizations (alpine base, layer consolidation)

---

### T-009: Create Backend .dockerignore

**Description**: Create .dockerignore file to exclude unnecessary files from backend image

**Preconditions**:
- Backend directory structure known

**Steps**:
1. Create `backend/.dockerignore`
2. Exclude: `__pycache__`, `.pytest_cache`, `.env`, `.git`, `*.pyc`, `*.pyo`, `*.pyd`, `.venv`, `venv/`
3. Test build size impact

**Expected Outputs**:
- `backend/.dockerignore` created
- Build time reduced
- Image size may decrease slightly

**.dockerignore Content**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.env
.env.*
.git
.gitignore
venv/
.venv/
*.egg-info
dist/
build/
*.log
.DS_Store
Thumbs.db
README.md
tests/
```

**Test Cases**:
```bash
# TC-009-1: Build with .dockerignore
docker build -t backend-clean:v1 ./backend
# Expected: Build succeeds, excludes .git, __pycache__, etc.

# TC-009-2: Inspect image layers (no excluded files)
docker run --rm backend-clean:v1 ls -la /app/.git 2>&1 | grep "No such file"
# Expected: .git directory not present
```

**Acceptance Criteria**:
- ✅ .dockerignore created with comprehensive exclusions
- ✅ Build excludes __pycache__, .git, .env
- ✅ Image does not contain development files

**References**: [Plan § Phase 1 Task 6](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-007](./spec.md#functional-requirements)

---

### T-010: Create Frontend Dockerfile

**Description**: Create multi-stage Dockerfile for Next.js frontend with standalone build

**Preconditions**:
- Frontend code exists in `frontend/` directory
- Next.js 16+ application (Phase III complete)

**Steps**:
1. Create `frontend/Dockerfile`
2. Implement multi-stage build (deps → builder → runner)
3. Use standalone Next.js output
4. Set non-root user
5. Target image size: <200MB

**Expected Outputs**:
- `frontend/Dockerfile` created
- Multi-stage build with 3 stages
- Standalone build configured
- Non-root user configured

**Dockerfile Structure**:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

**Test Cases**:
```bash
# TC-010-1: Dockerfile build
docker build -t frontend-test:v1 ./frontend
# Expected: Build succeeds

# TC-010-2: Image size check
docker images frontend-test:v1 --format "{{.Size}}"
# Expected: Size documented (target: <200MB)

# TC-010-3: Non-root user verification
docker run --rm frontend-test:v1 whoami
# Expected: "nextjs" (not root)
```

**Acceptance Criteria**:
- ✅ Dockerfile builds successfully
- ✅ Multi-stage build (3 stages) implemented
- ✅ Standalone Next.js output configured
- ✅ Non-root user (nextjs:nodejs) configured
- ✅ Initial image size documented

**References**: [Plan § Phase 1 Task 3](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-006](./spec.md#functional-requirements)

**Note**: Requires `output: 'standalone'` in `next.config.js`

---

### T-011: Optimize Frontend Dockerfile with Gordon

**Description**: Use Docker AI (Gordon) to optimize frontend Dockerfile for size and security

**Preconditions**:
- Frontend Dockerfile created (from T-010)
- Docker AI (Gordon) installed (from T-004)

**Steps**:
1. Run Gordon optimization: `docker ai "optimize frontend/Dockerfile for production deployment"`
2. Review suggestions
3. Apply optimizations
4. Rebuild: `docker build -t todo-frontend:optimized ./frontend`
5. Compare sizes

**Expected Outputs**:
- Gordon provides frontend-specific optimizations
- Dockerfile updated
- Image size reduced (target: <200MB, ideal: <150MB)

**Test Cases**:
```bash
# TC-011-1: Gordon optimization
docker ai "optimize frontend/Dockerfile for minimal size"
# Expected: Suggestions provided

# TC-011-2: Rebuild optimized
docker build -t todo-frontend:optimized ./frontend
# Expected: Build succeeds

# TC-011-3: Size check
docker images todo-frontend:optimized --format "{{.Size}}"
# Expected: <200MB (ideally <150MB)

# TC-011-4: Security scan
docker ai "review todo-frontend:optimized for security issues"
# Expected: Security report
```

**Acceptance Criteria**:
- ✅ Gordon provides actionable suggestions
- ✅ Image size <200MB (ideally <150MB)
- ✅ No critical security vulnerabilities
- ✅ Standalone build works correctly

**References**: [Plan § Phase 1 Task 4](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-023-024, SC-015-016](./spec.md#functional-requirements)

---

### T-012: Create Frontend .dockerignore

**Description**: Create .dockerignore for frontend to exclude node_modules, .next, .git

**Preconditions**:
- Frontend directory structure known

**Steps**:
1. Create `frontend/.dockerignore`
2. Exclude: `node_modules`, `.next`, `.git`, `*.log`, `.env*`, etc.
3. Test build

**Expected Outputs**:
- `frontend/.dockerignore` created
- Build time reduced significantly

**.dockerignore Content**:
```
node_modules
.next
.git
.gitignore
*.log
.env*
.DS_Store
Thumbs.db
README.md
.vscode
.idea
coverage
.cache
dist
build
```

**Test Cases**:
```bash
# TC-012-1: Build with .dockerignore
docker build -t frontend-clean:v1 ./frontend
# Expected: Faster build, smaller context

# TC-012-2: Verify exclusions
docker run --rm frontend-clean:v1 ls /app/node_modules 2>&1 | grep "No such file"
# Expected: node_modules not in final image (only in deps stage)
```

**Acceptance Criteria**:
- ✅ .dockerignore created
- ✅ Build excludes node_modules, .next, .git
- ✅ Build context size reduced

**References**: [Plan § Phase 1 Task 6](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-007](./spec.md#functional-requirements)

---

### T-013: Build and Test Docker Images Locally

**Description**: Build final optimized images and test functionality locally

**Preconditions**:
- Optimized Dockerfiles created (from T-008, T-011)
- .dockerignore files created (from T-009, T-012)

**Steps**:
1. Build backend: `docker build -t todo-backend:latest ./backend`
2. Build frontend: `docker build -t todo-frontend:latest ./frontend`
3. Test backend: `docker run -p 8000:8000 -e DATABASE_URL="..." todo-backend:latest`
4. Test frontend: `docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL="http://localhost:8000" todo-frontend:latest`
5. Verify health checks
6. Verify frontend can reach backend

**Expected Outputs**:
- Both images build successfully
- Containers start without errors
- Health checks respond
- Application functionality verified

**Test Cases**:
```bash
# TC-013-1: Build backend
docker build -t todo-backend:latest ./backend
# Expected: Build succeeds

# TC-013-2: Build frontend
docker build -t todo-frontend:latest ./frontend
# Expected: Build succeeds

# TC-013-3: Run backend
docker run -d --name test-backend -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  todo-backend:latest
# Expected: Container starts

# TC-013-4: Backend health check
curl http://localhost:8000/health
# Expected: {"status": "ok"} or similar

# TC-013-5: Run frontend
docker run -d --name test-frontend -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  todo-frontend:latest
# Expected: Container starts

# TC-013-6: Frontend accessible
curl http://localhost:3000
# Expected: HTML response (Next.js app)

# TC-013-7: Cleanup
docker stop test-backend test-frontend
docker rm test-backend test-frontend
# Expected: Containers stopped and removed
```

**Acceptance Criteria**:
- ✅ Backend image builds and runs
- ✅ Frontend image builds and runs
- ✅ Backend health check responds
- ✅ Frontend serves pages
- ✅ Images meet size targets (<100MB backend, <200MB frontend)

**References**: [Plan § Phase 1 Task 5](./plan.md#phase-1-containerization-with-gordon), [Spec § FR-008, SC-004-007](./spec.md#functional-requirements)

---

## Phase 2: Kubernetes Manifests with kubectl-ai

### T-014: Create Backend Kubernetes Deployment

**Description**: Create Deployment manifest for backend service using kubectl-ai

**Preconditions**:
- kubectl-ai installed (from T-005)
- Kubernetes cluster running (from T-001 or T-002)
- Backend Docker image built (from T-013)

**Steps**:
1. Generate with kubectl-ai: `kubectl-ai "create a deployment for todo backend with 2 replicas, image todo-backend:latest, container port 8000"`
2. Review generated manifest
3. Enhance manifest:
   - Add resource limits (CPU: 500m, Memory: 512Mi)
   - Add liveness probe (HTTP GET /health)
   - Add readiness probe (HTTP GET /health)
   - Add environment variables (DATABASE_URL from secret)
4. Save to `k8s/backend/deployment.yaml`

**Expected Outputs**:
- `k8s/backend/deployment.yaml` created
- Deployment with 2 replicas
- Resource limits configured
- Health probes configured

**Manifest Structure** (after enhancements):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

**Test Cases**:
```bash
# TC-014-1: Validate manifest
kubectl apply --dry-run=client -f k8s/backend/deployment.yaml
# Expected: No errors, "deployment.apps/backend created (dry run)"

# TC-014-2: Apply deployment
kubectl apply -f k8s/backend/deployment.yaml
# Expected: deployment.apps/backend created

# TC-014-3: Check rollout status
kubectl rollout status deployment/backend
# Expected: "deployment "backend" successfully rolled out"

# TC-014-4: Verify replicas
kubectl get deployment backend -o jsonpath='{.spec.replicas}'
# Expected: 2

# TC-014-5: Check pod status
kubectl get pods -l app=todo-backend
# Expected: 2 pods in "Running" state
```

**Acceptance Criteria**:
- ✅ Deployment manifest created
- ✅ 2 replicas configured
- ✅ Resource limits set (CPU: 500m, Memory: 512Mi)
- ✅ Liveness and readiness probes configured
- ✅ Pods start successfully

**References**: [Plan § Phase 2 Task 1](./plan.md#phase-2-kubernetes-manifests-with-kubectl-ai), [Spec § FR-009-010](./spec.md#functional-requirements)

---

### T-015: Create Backend Kubernetes Service

**Description**: Create ClusterIP Service for backend internal communication

**Preconditions**:
- Backend Deployment created (from T-014)
- kubectl-ai installed (from T-005)

**Steps**:
1. Generate with kubectl-ai: `kubectl-ai "create a ClusterIP service for todo backend on port 8000"`
2. Review manifest
3. Save to `k8s/backend/service.yaml`
4. Apply: `kubectl apply -f k8s/backend/service.yaml`

**Expected Outputs**:
- `k8s/backend/service.yaml` created
- Service type: ClusterIP
- Port: 8000 → targetPort: 8000

**Manifest Structure**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  labels:
    app: todo-backend
spec:
  type: ClusterIP
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
```

**Test Cases**:
```bash
# TC-015-1: Validate service
kubectl apply --dry-run=client -f k8s/backend/service.yaml
# Expected: No errors

# TC-015-2: Apply service
kubectl apply -f k8s/backend/service.yaml
# Expected: service/backend created

# TC-015-3: Check service
kubectl get svc backend
# Expected: ClusterIP type, port 8000

# TC-015-4: Test service connectivity (from another pod)
kubectl run test-curl --image=curlimages/curl --rm -it --restart=Never \
  -- curl http://backend:8000/health
# Expected: {"status": "ok"} response
```

**Acceptance Criteria**:
- ✅ Service manifest created
- ✅ ClusterIP service type
- ✅ Service routes to backend pods
- ✅ Internal DNS works (backend:8000 resolves)

**References**: [Plan § Phase 2 Task 2](./plan.md#phase-2-kubernetes-manifests-with-kubectl-ai), [Spec § FR-011](./spec.md#functional-requirements)

---

### T-016: Create Frontend Kubernetes Deployment

**Description**: Create Deployment manifest for frontend service using kubectl-ai

**Preconditions**:
- kubectl-ai installed (from T-005)
- Frontend Docker image built (from T-013)
- Backend service running (from T-014, T-015)

**Steps**:
1. Generate with kubectl-ai: `kubectl-ai "create a deployment for todo frontend with 2 replicas, image todo-frontend:latest, container port 3000"`
2. Enhance manifest (resource limits, probes, env vars)
3. Save to `k8s/frontend/deployment.yaml`
4. Apply

**Expected Outputs**:
- `k8s/frontend/deployment.yaml` created
- 2 replicas, port 3000
- Resource limits and probes

**Test Cases**:
```bash
# TC-016-1: Apply deployment
kubectl apply -f k8s/frontend/deployment.yaml
# Expected: deployment.apps/frontend created

# TC-016-2: Rollout status
kubectl rollout status deployment/frontend
# Expected: Success

# TC-016-3: Verify pods
kubectl get pods -l app=todo-frontend
# Expected: 2 pods running
```

**Acceptance Criteria**:
- ✅ Frontend deployment created
- ✅ 2 replicas running
- ✅ Pods start successfully
- ✅ Environment variable NEXT_PUBLIC_API_URL configured

**References**: [Plan § Phase 2 Task 3](./plan.md#phase-2-kubernetes-manifests-with-kubectl-ai), [Spec § FR-009-010](./spec.md#functional-requirements)

---

### T-017: Create Frontend Kubernetes Service (NodePort)

**Description**: Create NodePort Service to expose frontend externally

**Preconditions**:
- Frontend Deployment created (from T-016)

**Steps**:
1. Generate with kubectl-ai: `kubectl-ai "create a NodePort service for todo frontend on port 3000, nodePort 30080"`
2. Save to `k8s/frontend/service.yaml`
3. Apply
4. Get Minikube IP: `minikube ip` (if using Minikube)
5. Test access: `http://<minikube-ip>:30080` or `http://localhost:30080`

**Expected Outputs**:
- `k8s/frontend/service.yaml` created
- NodePort: 30080
- Frontend accessible externally

**Manifest Structure**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  labels:
    app: todo-frontend
spec:
  type: NodePort
  selector:
    app: todo-frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
    nodePort: 30080
```

**Test Cases**:
```bash
# TC-017-1: Apply service
kubectl apply -f k8s/frontend/service.yaml
# Expected: service/frontend created

# TC-017-2: Get service details
kubectl get svc frontend
# Expected: NodePort type, nodePort 30080

# TC-017-3: Access frontend
curl http://localhost:30080
# OR (if Minikube)
curl http://$(minikube ip):30080
# Expected: HTML response

# TC-017-4: Minikube service URL (if Minikube)
minikube service frontend --url
# Expected: URL displayed (http://<ip>:30080)
```

**Acceptance Criteria**:
- ✅ NodePort service created
- ✅ Port 30080 accessible
- ✅ Frontend loads in browser
- ✅ Frontend can communicate with backend

**References**: [Plan § Phase 2 Task 4](./plan.md#phase-2-kubernetes-manifests-with-kubectl-ai), [Spec § FR-012, SC-001](./spec.md#functional-requirements)

---

### T-018: Create Kubernetes Secrets

**Description**: Create Kubernetes Secret for sensitive environment variables

**Preconditions**:
- Kubernetes cluster running
- Database URL and JWT secret available

**Steps**:
1. Create secret template: `k8s/secrets/app-secrets.yaml.template`
2. Document secret creation process
3. Create actual secret: `kubectl create secret generic app-secrets --from-literal=database-url="postgresql://..." --from-literal=jwt-secret="..."`
4. OR create from YAML (base64-encoded values)
5. Verify secret created

**Expected Outputs**:
- Secret template file created (not containing actual secrets)
- Actual secret created in cluster (not committed to git)
- Secret referenced in deployments

**Secret Template** (`app-secrets.yaml.template`):
```yaml
# DO NOT COMMIT THIS FILE WITH REAL VALUES
# Create secret with: kubectl create secret generic app-secrets --from-literal=database-url="..." --from-literal=jwt-secret="..."
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: <BASE64_ENCODED_DATABASE_URL>
  jwt-secret: <BASE64_ENCODED_JWT_SECRET>
```

**Test Cases**:
```bash
# TC-018-1: Create secret
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://user:pass@host/db" \
  --from-literal=jwt-secret="your-secret-key-here"
# Expected: secret/app-secrets created

# TC-018-2: Verify secret exists
kubectl get secret app-secrets
# Expected: Secret listed

# TC-018-3: Check secret keys
kubectl get secret app-secrets -o jsonpath='{.data}' | jq 'keys'
# Expected: ["database-url", "jwt-secret"]

# TC-018-4: Test secret mount in pod
kubectl get pod -l app=todo-backend -o jsonpath='{.items[0].spec.containers[0].env[?(@.name=="DATABASE_URL")].valueFrom.secretKeyRef.name}'
# Expected: app-secrets
```

**Acceptance Criteria**:
- ✅ Secret template created (with placeholders)
- ✅ Secret creation documented
- ✅ Actual secret created in cluster
- ✅ Deployments reference secret correctly
- ✅ No secrets committed to git

**References**: [Plan § Phase 2 Task 6](./plan.md#phase-2-kubernetes-manifests-with-kubectl-ai), [Spec § FR-019-020](./spec.md#functional-requirements)

**Security Note**: Add `app-secrets.yaml` to `.gitignore`

---

## Phase 3: Helm Chart Creation

### T-019: Generate Helm Chart Scaffold

**Description**: Create Helm chart structure for Todo App

**Preconditions**:
- Helm CLI installed (from T-003)
- Kubernetes manifests created (from T-014-T-018)

**Steps**:
1. Generate chart: `helm create helm/todo-app`
2. Clean up default templates (remove nginx examples)
3. Verify chart structure

**Expected Outputs**:
- `helm/todo-app/` directory created
- Chart.yaml, values.yaml, templates/ present
- Default templates removed

**Test Cases**:
```bash
# TC-019-1: Create chart
helm create helm/todo-app
# Expected: Creating helm/todo-app

# TC-019-2: Verify structure
ls helm/todo-app/
# Expected: Chart.yaml, values.yaml, templates/, charts/

# TC-019-3: Lint chart
helm lint helm/todo-app
# Expected: 0 chart(s) linted, 0 chart(s) failed
```

**Acceptance Criteria**:
- ✅ Helm chart directory created
- ✅ Chart.yaml configured
- ✅ values.yaml present
- ✅ templates/ directory ready

**References**: [Plan § Phase 3 Task 1](./plan.md#phase-3-helm-chart-creation), [Spec § FR-004](./spec.md#functional-requirements)

---

### T-020: Template Backend Resources in Helm

**Description**: Convert backend Kubernetes manifests to Helm templates

**Preconditions**:
- Helm chart scaffold created (from T-019)
- Backend manifests exist (from T-014, T-015)

**Steps**:
1. Copy `k8s/backend/deployment.yaml` to `helm/todo-app/templates/backend-deployment.yaml`
2. Parameterize values: image tag, replicas, resources
3. Use `{{ .Values.backend.image }}`, `{{ .Values.backend.replicas }}`, etc.
4. Copy `k8s/backend/service.yaml` to `helm/todo-app/templates/backend-service.yaml`
5. Update `values.yaml` with backend defaults

**Expected Outputs**:
- Backend deployment template created
- Backend service template created
- values.yaml contains backend configuration

**values.yaml (backend section)**:
```yaml
backend:
  image: todo-backend:latest
  replicas: 2
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  service:
    type: ClusterIP
    port: 8000
```

**Test Cases**:
```bash
# TC-020-1: Helm template rendering
helm template todo-app helm/todo-app
# Expected: Renders backend deployment and service

# TC-020-2: Dry run install
helm install todo-app helm/todo-app --dry-run --debug
# Expected: Manifests displayed, no errors

# TC-020-3: Verify parameterization
helm template todo-app helm/todo-app --set backend.replicas=3 | grep -A 2 "replicas:"
# Expected: replicas: 3
```

**Acceptance Criteria**:
- ✅ Backend templates created
- ✅ Values properly parameterized
- ✅ Chart renders valid manifests
- ✅ Values can be overridden

**References**: [Plan § Phase 3 Task 2](./plan.md#phase-3-helm-chart-creation), [Spec § FR-014](./spec.md#functional-requirements)

---

### T-021: Template Frontend Resources in Helm

**Description**: Convert frontend Kubernetes manifests to Helm templates

**Preconditions**:
- Helm chart scaffold created (from T-019)
- Frontend manifests exist (from T-016, T-017)

**Steps**:
1. Copy and parameterize frontend deployment
2. Copy and parameterize frontend service (NodePort)
3. Update values.yaml with frontend defaults

**Expected Outputs**:
- Frontend templates created
- values.yaml contains frontend configuration

**Test Cases**:
```bash
# TC-021-1: Template rendering
helm template todo-app helm/todo-app
# Expected: Frontend resources rendered

# TC-021-2: Override test
helm template todo-app helm/todo-app --set frontend.service.nodePort=30090
# Expected: nodePort: 30090 in output
```

**Acceptance Criteria**:
- ✅ Frontend templates created
- ✅ NodePort configurable via values
- ✅ Chart renders correctly

**References**: [Plan § Phase 3 Task 3](./plan.md#phase-3-helm-chart-creation), [Spec § FR-014](./spec.md#functional-requirements)

---

### T-022: Test Helm Chart Installation

**Description**: Install, upgrade, and uninstall Helm chart in Kubernetes cluster

**Preconditions**:
- Helm chart completed (from T-019-T-021)
- Kubernetes cluster running
- Docker images available

**Steps**:
1. Lint chart: `helm lint helm/todo-app`
2. Dry run: `helm install todo-app helm/todo-app --dry-run --debug`
3. Install: `helm install todo-app helm/todo-app`
4. Verify: `kubectl get all -l app.kubernetes.io/instance=todo-app`
5. Test upgrade: Modify values.yaml, run `helm upgrade todo-app helm/todo-app`
6. Test rollback: `helm rollback todo-app`
7. Uninstall: `helm uninstall todo-app`

**Expected Outputs**:
- Chart installs successfully
- All resources created with correct labels
- Upgrade and rollback work
- Uninstall removes all resources

**Test Cases**:
```bash
# TC-022-1: Lint chart
helm lint helm/todo-app
# Expected: 0 chart(s) failed

# TC-022-2: Install
helm install todo-app helm/todo-app
# Expected: NAME: todo-app, STATUS: deployed

# TC-022-3: Check resources
kubectl get all -l app.kubernetes.io/instance=todo-app
# Expected: Pods, services, deployments listed

# TC-022-4: Upgrade
helm upgrade todo-app helm/todo-app --set backend.replicas=3
# Expected: Release "todo-app" has been upgraded

# TC-022-5: Rollback
helm rollback todo-app 1
# Expected: Rollback was a success

# TC-022-6: Uninstall
helm uninstall todo-app
# Expected: release "todo-app" uninstalled

# TC-022-7: Verify cleanup
kubectl get all -l app.kubernetes.io/instance=todo-app
# Expected: No resources found
```

**Acceptance Criteria**:
- ✅ Helm chart passes linting
- ✅ Chart installs without errors
- ✅ All resources created correctly
- ✅ Upgrade process works
- ✅ Rollback process works
- ✅ Uninstall removes all resources

**References**: [Plan § Phase 3 Task 6](./plan.md#phase-3-helm-chart-creation), [Spec § FR-015, SC-003](./spec.md#functional-requirements)

---

## Phase 4: Cluster Health Monitoring with kagent

### T-023: Run Initial Cluster Health Analysis

**Description**: Use kagent to analyze cluster health and document baseline metrics

**Preconditions**:
- kagent installed (from T-006)
- Application deployed (from T-022)
- Cluster has been running for at least 5 minutes

**Steps**:
1. Run health analysis: `kagent "analyze the cluster health and identify any issues"`
2. Review report for warnings or errors
3. Document baseline metrics (CPU, memory, pod count, node health)
4. Create report file: `docs/cluster-health-baseline.md`

**Expected Outputs**:
- kagent health report generated
- Baseline metrics documented
- Any issues identified and noted

**Test Cases**:
```bash
# TC-023-1: Health analysis
kagent "analyze the cluster health"
# Expected: Health report with metrics and recommendations

# TC-023-2: Node health check
kagent "check if nodes are healthy"
# Expected: Node status report

# TC-023-3: Pod health check
kagent "identify any unhealthy pods"
# Expected: List of pod statuses
```

**Acceptance Criteria**:
- ✅ kagent provides comprehensive health report
- ✅ Baseline metrics documented
- ✅ No critical issues identified (or issues documented)
- ✅ Report saved for future comparison

**References**: [Plan § Phase 4 Task 1](./plan.md#phase-4-cluster-health-monitoring-with-kagent), [Spec § FR-029, SC-021](./spec.md#functional-requirements)

---

### T-024: Optimize Resource Allocation with kagent

**Description**: Use kagent to analyze resource utilization and apply optimizations

**Preconditions**:
- Initial health analysis complete (from T-023)
- Application running under load (optional: run load tests first)

**Steps**:
1. Run resource analysis: `kagent "analyze resource allocation and suggest optimizations"`
2. Review CPU and memory utilization
3. Identify over/under-provisioned pods
4. Adjust resource requests/limits in Helm values.yaml
5. Upgrade chart: `helm upgrade todo-app helm/todo-app`
6. Re-run analysis to verify improvements

**Expected Outputs**:
- Resource optimization report
- Updated resource limits in values.yaml
- Improved resource utilization (<80% CPU/memory)

**Test Cases**:
```bash
# TC-024-1: Resource analysis
kagent "suggest resource optimizations for the todo app"
# Expected: Recommendations for CPU/memory adjustments

# TC-024-2: Check current utilization
kubectl top pods
# Expected: Current CPU/memory usage displayed

# TC-024-3: Apply optimizations
# Update values.yaml based on kagent suggestions
helm upgrade todo-app helm/todo-app
# Expected: Deployment updated

# TC-024-4: Verify improvements
kagent "analyze resource allocation"
# Expected: Improved utilization metrics
```

**Acceptance Criteria**:
- ✅ kagent provides actionable optimization suggestions
- ✅ Resource limits adjusted based on data
- ✅ Cluster utilization <80% CPU and memory
- ✅ No resource starvation or throttling

**References**: [Plan § Phase 4 Task 2](./plan.md#phase-4-cluster-health-monitoring-with-kagent), [Spec § FR-030, SC-022](./spec.md#functional-requirements)

---

## Final Verification

### T-025: End-to-End Testing

**Description**: Comprehensive E2E test of deployed application

**Preconditions**:
- Application deployed via Helm (from T-022)
- All optimizations applied (from T-024)

**Steps**:
1. Access frontend: `http://localhost:30080` or `http://<minikube-ip>:30080`
2. Login with test credentials
3. Create a task using chatbot
4. Verify task appears in dashboard
5. Test voice interaction (if Phase III complete)
6. Verify backend health: `curl http://<backend-service>:8000/health`
7. Check logs: `kubectl logs -l app=todo-backend --tail=50`

**Expected Outputs**:
- Frontend accessible and functional
- Backend API responding
- Database operations working
- No errors in logs

**Test Cases**:
```bash
# TC-025-1: Frontend access
curl -I http://localhost:30080
# Expected: HTTP/1.1 200 OK

# TC-025-2: Backend health
kubectl run test-curl --image=curlimages/curl --rm -it --restart=Never \
  -- curl http://backend:8000/health
# Expected: {"status": "healthy"}

# TC-025-3: Check pod logs (no errors)
kubectl logs -l app=todo-backend --tail=20
# Expected: No ERROR level logs

# TC-025-4: Service endpoint test
minikube service frontend --url
# Open URL in browser
# Expected: Todo app loads
```

**Acceptance Criteria**:
- ✅ Frontend loads and is responsive
- ✅ Backend API accessible from frontend
- ✅ Database connectivity working
- ✅ Chatbot creates tasks successfully
- ✅ No critical errors in logs
- ✅ Application meets functional requirements

**References**: [Plan § Testing Strategy](./plan.md#testing-strategy), [Spec § SC-001-014](./spec.md#success-criteria)

---

## Summary

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| **Phase 0: Prerequisites** | T-001 to T-006 | 1-2 hours |
| **Phase 1: Containerization** | T-007 to T-013 | 2-3 hours |
| **Phase 2: Kubernetes Manifests** | T-014 to T-018 | 2-3 hours |
| **Phase 3: Helm Chart** | T-019 to T-022 | 2-3 hours |
| **Phase 4: Monitoring** | T-023 to T-024 | 1-2 hours |
| **Final Verification** | T-025 | 30 minutes |
| **TOTAL** | **25 tasks** | **8-13 hours** |

## Task Dependency Graph

```
T-001 (Docker)
  ├─> T-002 (Minikube) ──┐
  ├─> T-003 (Helm) ──────┼───> T-004 (Gordon) ──┐
  │                      │                       │
  │                      │                       ├─> T-007 (Backend Dockerfile) ─> T-008 (Gordon Optimize Backend) ─> T-009 (.dockerignore)
  │                      │                       │
  │                      │                       └─> T-010 (Frontend Dockerfile) ─> T-011 (Gordon Optimize Frontend) ─> T-012 (.dockerignore)
  │                      │
  │                      ├───> T-005 (kubectl-ai) ──┐
  │                      │                           │
  │                      └───> T-006 (kagent) ───────┼───> T-013 (Build Images) ──┐
  │                                                  │                             │
  │                                                  │                             ├─> T-014 (Backend Deployment)
  │                                                  │                             │     ├─> T-015 (Backend Service)
  │                                                  │                             │
  │                                                  │                             ├─> T-016 (Frontend Deployment)
  │                                                  │                             │     ├─> T-017 (Frontend Service)
  │                                                  │                             │
  │                                                  │                             └─> T-018 (Secrets)
  │                                                  │                                   │
  │                                                  │                                   ├─> T-019 (Helm Scaffold)
  │                                                  │                                   │     ├─> T-020 (Backend Templates)
  │                                                  │                                   │     ├─> T-021 (Frontend Templates)
  │                                                  │                                   │     └─> T-022 (Helm Install)
  │                                                  │                                   │           │
  │                                                  └───────────────────────────────────────────────├─> T-023 (Health Analysis)
  │                                                                                                  │     └─> T-024 (Optimize Resources)
  │                                                                                                  │           │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────> T-025 (E2E Testing)
```

## Notes

- **AI Tools Optional**: If Gordon, kubectl-ai, or kagent are unavailable, follow manual alternatives documented in plan.md
- **Secrets**: Never commit actual secrets to git. Use templates and `.gitignore`
- **Image Storage**: For production, push images to container registry (Docker Hub, GitHub Container Registry, etc.)
- **Minikube vs Docker Desktop**: Choose one based on OS and preference. Both are supported.
- **Resource Limits**: Adjust based on actual load testing and kagent recommendations
- **Next Phase**: Phase V will migrate to cloud Kubernetes (DOKS, GKE, or EKS) with production configurations
