# Data Model: Local Minikube Deployment

**Feature**: 007-minikube-deployment
**Date**: 2025-12-09
**Phase**: Phase 1 - Design

## Overview

This document defines the data structures and configuration entities for Phase IV containerization and Kubernetes deployment. Note that application-level data models (Task, User, Conversation, Message) are inherited from Phase II/III and remain unchanged. This document focuses on **infrastructure configuration entities**.

---

## 1. Docker Image Entities

### Backend Image
**Purpose**: Containerized FastAPI application with AI agent and MCP tools

**Attributes**:
- `name`: todo-backend
- `tag`: local | v{version} | latest
- `base_image`: python:3.13-slim
- `exposed_port`: 8000
- `entrypoint`: uvicorn app.main:app
- `size_limit`: <200MB (excluding base layers)
- `build_stages`: builder, runtime

**Build Configuration**:
```yaml
stages:
  builder:
    base: python:3.13-slim
    package_manager: uv
    dependencies: requirements.txt
    build_artifacts: /app/.venv

  runtime:
    base: python:3.13-slim
    copy_from_builder: /app/.venv
    working_dir: /app
    user: nonroot (1000:1000)
```

**Environment Variables**:
- DATABASE_URL (from Kubernetes Secret)
- OPENAI_API_KEY (from Kubernetes Secret)
- BETTER_AUTH_SECRET (from Kubernetes Secret)
- PORT (default: 8000)

---

### Frontend Image
**Purpose**: Containerized Next.js application with OpenAI ChatKit integration

**Attributes**:
- `name`: todo-frontend
- `tag`: local | v{version} | latest
- `base_image`: node:20-alpine
- `exposed_port`: 3000
- `entrypoint`: node server.js
- `size_limit`: <150MB (excluding base layers)
- `build_stages`: dependencies, builder, runner

**Build Configuration**:
```yaml
stages:
  dependencies:
    base: node:20-alpine
    package_manager: npm
    install_type: ci (production only)

  builder:
    base: node:20-alpine
    build_command: npm run build
    output_mode: standalone
    build_artifacts: .next/standalone, .next/static, public

  runner:
    base: node:20-alpine
    copy_from_builder: standalone artifacts
    working_dir: /app
    user: nextjs (1001:1001)
```

**Environment Variables**:
- NEXT_PUBLIC_API_URL (default: http://backend-service:8000)
- PORT (default: 3000)

---

## 2. Helm Chart Entities

### Chart Metadata
**Entity**: Chart.yaml

**Attributes**:
- `apiVersion`: v2
- `name`: todo-stack
- `description`: Todo Chatbot with AI Agent (Phase III) containerized for Kubernetes
- `type`: application
- `version`: 1.0.0 (chart version)
- `appVersion`: 4.0.0 (Phase IV application version)
- `keywords`: [todo, kubernetes, helm, ai, chatbot, minikube]
- `maintainers`: [project team]

---

### Values Configuration
**Entity**: values.yaml (default values)

**Structure**:
```yaml
global:
  environment: local
  labels:
    app: todo
    managedBy: helm

backend:
  enabled: true
  replicaCount: 2
  image:
    repository: todo-backend
    tag: local
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000

  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1024Mi

  healthProbes:
    readiness:
      path: /health/ready
      initialDelaySeconds: 10
      periodSeconds: 5
    liveness:
      path: /health/live
      initialDelaySeconds: 30
      periodSeconds: 10

frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: local
    pullPolicy: IfNotPresent

  service:
    type: NodePort
    port: 3000
    targetPort: 3000
    nodePort: 30080  # Fixed for local development

  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  healthProbes:
    readiness:
      path: /
      initialDelaySeconds: 5
      periodSeconds: 5
    liveness:
      path: /
      initialDelaySeconds: 15
      periodSeconds: 10

secrets:
  name: todo-secrets
  create: false  # Manually created via kubectl
  keys:
    - DATABASE_URL
    - OPENAI_API_KEY
    - BETTER_AUTH_SECRET

ingress:
  enabled: false  # Optional for advanced users
  className: nginx
  annotations: {}
  hosts: []
  tls: []
```

**Environment Overrides**:
- **values-local.yaml**: NodePort 30080, minimal resources
- **values-production.yaml**: LoadBalancer, increased resources, TLS

---

## 3. Kubernetes Resource Entities

### Backend Deployment
**Kind**: Deployment
**API Version**: apps/v1

**Key Attributes**:
- `replicas`: 2 (configurable via Helm values)
- `selector.matchLabels`: app=todo, tier=backend
- `strategy`: RollingUpdate (maxUnavailable: 0, maxSurge: 1)
- `template.spec.containers[0]`:
  - `name`: backend
  - `image`: {{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}
  - `ports`: [8000]
  - `env`: From secret todo-secrets
  - `resources`: From values
  - `readinessProbe`, `livenessProbe`: Health check endpoints

**Labels and Annotations**:
```yaml
labels:
  app: todo
  tier: backend
  environment: {{ .Values.global.environment }}
  managed-by: helm
  version: {{ .Chart.AppVersion }}

annotations:
  description: "Todo Chatbot backend API with AI agent and MCP tools"
  ai-ops/enabled: "true"
  ai-ops/tools: "kubectl-ai,kagent"
```

---

### Frontend Deployment
**Kind**: Deployment
**API Version**: apps/v1

**Key Attributes**:
- `replicas`: 1 (local development efficiency)
- `selector.matchLabels`: app=todo, tier=frontend
- `strategy`: RollingUpdate
- `template.spec.containers[0]`:
  - `name`: frontend
  - `image`: {{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}
  - `ports`: [3000]
  - `env`: NEXT_PUBLIC_API_URL=http://backend-service:8000
  - `resources`: From values
  - `readinessProbe`, `livenessProbe`: HTTP get /

**Labels and Annotations**:
```yaml
labels:
  app: todo
  tier: frontend
  environment: {{ .Values.global.environment }}
  managed-by: helm
  version: {{ .Chart.AppVersion }}

annotations:
  description: "Todo Chatbot frontend UI with OpenAI ChatKit"
  ai-ops/enabled: "true"
  ai-ops/tools: "kubectl-ai,kagent"
```

---

### Backend Service
**Kind**: Service
**API Version**: v1

**Attributes**:
- `type`: ClusterIP (internal only)
- `selector`: app=todo, tier=backend
- `ports`:
  - `name`: http
  - `port`: 8000
  - `targetPort`: 8000
  - `protocol`: TCP

---

### Frontend Service
**Kind**: Service
**API Version**: v1

**Attributes (Local)**:
- `type`: NodePort
- `selector`: app=todo, tier=frontend
- `ports`:
  - `name`: http
  - `port`: 3000
  - `targetPort`: 3000
  - `nodePort`: 30080
  - `protocol`: TCP

**Attributes (Production)**:
- `type`: LoadBalancer (cloud provider managed)
- Same port configuration without fixed nodePort

---

### Secrets
**Kind**: Secret
**API Version**: v1

**Attributes**:
- `type`: Opaque
- `name`: todo-secrets
- `data`: Base64-encoded secret values
  - DATABASE_URL
  - OPENAI_API_KEY
  - BETTER_AUTH_SECRET

**Lifecycle**:
- Created manually via kubectl before Helm install
- Referenced in Deployment manifests via envFrom.secretRef
- Not managed by Helm (create: false in values)

---

## 4. Configuration Entities

### Minikube Cluster Configuration

**Entity**: Minikube cluster settings

**Attributes**:
- `cpus`: 4 minimum
- `memory`: 6144 MB (6GB) minimum
- `driver`: docker | hyperkit | kvm2 (platform-specific)
- `kubernetes_version`: 1.28+ (latest stable)
- `container_runtime`: docker
- `addons`: metrics-server (optional for resource monitoring)

**Initialization**:
```bash
minikube start \
  --cpus=4 \
  --memory=6144 \
  --driver=docker \
  --kubernetes-version=stable
```

---

### Docker Build Context

**Entity**: Build environment configuration

**Attributes**:
- `docker_daemon`: Minikube internal Docker (eval $(minikube docker-env))
- `build_context`: ./backend or ./frontend
- `dockerfile_path`: ./Dockerfile
- `build_args`: None (secrets via Kubernetes, not build-time)
- `cache`: Enabled (layer caching)
- `platform`: linux/amd64 (Minikube default)

---

## 5. Health Check Entities

### Backend Health Endpoints

**Entity**: FastAPI health check routes

**Readiness Endpoint**:
- Path: `/health/ready`
- Method: GET
- Response: `{"status": "ready", "database": "connected"}`
- Status Code: 200 (ready) | 503 (not ready)
- Purpose: Database connectivity verification

**Liveness Endpoint**:
- Path: `/health/live`
- Method: GET
- Response: `{"status": "alive"}`
- Status Code: 200 (alive) | 500 (dead)
- Purpose: Process health verification

---

### Frontend Health Check

**Entity**: Next.js root path health

**Endpoint**:
- Path: `/`
- Method: GET
- Response: HTML page render
- Status Code: 200 (healthy) | 500 (unhealthy)
- Purpose: Next.js server responsiveness

---

## Summary

**Infrastructure Entities** (new in Phase IV):
- 2 Docker Images (backend, frontend)
- 1 Helm Chart (todo-stack)
- 3 Values files (values.yaml, values-local.yaml, values-production.yaml)
- 2 Deployments (backend, frontend)
- 2 Services (backend ClusterIP, frontend NodePort/LoadBalancer)
- 1 Secret (todo-secrets, manually created)
- 7 Helm templates (deployments, services, secrets, configmap, ingress optional)

**Application Entities** (inherited from Phase II/III, unchanged):
- User, Task, Conversation, Message (database models)
- JWT tokens, API endpoints, MCP tools

**Configuration Entities**:
- Minikube cluster settings
- Docker build contexts
- Health check endpoints

All entities align with Constitution Section IV (Infrastructure & DevOps Standards) and support the functional requirements defined in the specification.
