# Feature Specification: Helm Chart Orchestration

**Feature Branch**: `006-helm-chart`
**Created**: 2025-12-08
**Status**: Draft
**Input**: User description: "Helm chart orchestration for Todo App with umbrella chart (todo-app) containing Backend and Frontend microservices. Charts include Deployment templates with configurable replicas, imagePullPolicy: Never for Minikube local images, and livenessProbe HTTP GET checks. Backend uses ClusterIP service, Frontend uses NodePort for external access. Values.yaml defaults to todo-backend:latest and todo-frontend:latest images."

## User Scenarios & Testing

### User Story 1 - Deploy Application to Minikube with Helm (Priority: P1)

As a **Developer**, I want to **deploy the entire Todo App (Backend + Frontend) to a local Minikube cluster using a single Helm install command**, so that **I can test Kubernetes deployments locally without manual YAML configuration**.

**Why this priority**: This is the foundational capability for Phase IV. Without a working Helm chart, we cannot deploy to Kubernetes at all. This must work before any other Phase IV features.

**Independent Test**: Can be fully tested by running `helm install todo-app ./deploy/helm/todo-app` on a Minikube cluster with locally-built Docker images and verifying that both Backend and Frontend pods start successfully and are accessible.

**Acceptance Scenarios**:

1. **Given** Minikube cluster running and Docker images built locally, **When** I run `helm install todo-app ./deploy/helm/todo-app`, **Then** Helm creates Deployment and Service resources for both Backend and Frontend
2. **Given** Helm chart installed, **When** I run `kubectl get pods`, **Then** both `todo-backend` and `todo-frontend` pods show status `Running` within 60 seconds
3. **Given** deployed application, **When** I access Backend via ClusterIP service from within cluster, **Then** `/health` endpoint returns 200 OK
4. **Given** deployed application, **When** I access Frontend via NodePort at `$(minikube ip):NodePort`, **Then** the homepage renders successfully

---

### User Story 2 - Configure Deployment with Values (Priority: P1)

As a **DevOps Engineer**, I want to **customize deployments (replica counts, image tags, resource limits) via values.yaml without modifying templates**, so that **different environments (dev/staging/prod) can reuse the same Helm chart with environment-specific configurations**.

**Why this priority**: Configuration management is essential from the start. Hardcoding values in templates makes the chart unusable across environments.

**Independent Test**: Can be tested by creating custom values files (values-dev.yaml, values-prod.yaml) and verifying that `helm install` with `-f values-dev.yaml` produces different deployments (e.g., 1 replica for dev, 3 for prod).

**Acceptance Scenarios**:

1. **Given** custom values file with `backend.replicas: 3`, **When** I install with `helm install todo-app ./deploy/helm/todo-app -f values-prod.yaml`, **Then** Backend Deployment has 3 replicas
2. **Given** custom values file with `backend.image.tag: v1.2.3`, **When** I install the chart, **Then** Backend pod uses image `todo-backend:v1.2.3`
3. **Given** default values.yaml, **When** I install without custom values, **Then** Backend uses 1 replica and Frontend uses 1 replica (local dev defaults)
4. **Given** Helm chart installed with custom values, **When** I run `helm upgrade todo-app ./deploy/helm/todo-app -f values-prod.yaml --set backend.replicas=5`, **Then** Backend scales from 3 to 5 replicas without downtime

---

### User Story 3 - Health Checks and Self-Healing (Priority: P2)

As a **Site Reliability Engineer**, I want to **configure liveness and readiness probes in Helm templates**, so that **Kubernetes automatically restarts unhealthy pods and stops routing traffic to pods that aren't ready**.

**Why this priority**: Health checks are critical for production resilience but can be added after basic deployment works. Pods can run initially without probes.

**Independent Test**: Can be tested by deploying the Helm chart, simulating a pod failure (kill process inside container), and verifying that Kubernetes restarts the pod automatically via livenessProbe.

**Acceptance Scenarios**:

1. **Given** Backend Deployment with livenessProbe configured, **When** the Backend process crashes inside the container, **Then** Kubernetes restarts the pod within 30 seconds
2. **Given** Frontend Deployment with readinessProbe configured, **When** Frontend takes > 15 seconds to start, **Then** Kubernetes does not route traffic until readinessProbe succeeds
3. **Given** deployed Backend, **When** I inspect the Deployment with `kubectl describe deployment todo-backend`, **Then** livenessProbe shows HTTP GET to `/health` on port 8000
4. **Given** deployed Frontend, **When** readinessProbe fails 3 consecutive times, **Then** pod is marked as NotReady and removed from Service endpoints

---

### Edge Cases

- What happens when imagePullPolicy: Never is used but Docker image doesn't exist locally? (Pod stuck in ImagePullBackOff - must build images before helm install)
- How does Helm handle upgrades when template changes are incompatible? (Helm may fail upgrade - use `helm rollback` to revert)
- What happens when NodePort conflicts with existing services? (Helm install fails with port conflict error - must specify different nodePort in values)
- How does the system handle Helm chart validation errors? (Use `helm lint` before install to catch template errors early)
- What happens when Backend pod starts before database is ready? (Pod crashes and restarts via livenessProbe until database is available - consider init containers)
- How does Helm handle secret injection for database credentials? (Out of scope - use Kubernetes Secrets created manually before helm install)
- What happens when Minikube runs out of resources? (Pods stuck in Pending state - check with `kubectl describe pod` and scale down replicas)

## Requirements

### Functional Requirements

**Helm Chart Structure**:
- **FR-001**: Helm chart MUST be named `todo-app` and be an umbrella chart (Application type) containing Backend and Frontend as sub-components
- **FR-002**: Chart.yaml MUST specify `apiVersion: v2`, `name: todo-app`, `version: 0.1.0`, `appVersion: 1.0.0`, `type: application`
- **FR-003**: Chart directory structure MUST follow standard Helm layout: `Chart.yaml`, `values.yaml`, `templates/deployment.yaml`, `templates/service.yaml`, `templates/_helpers.tpl`

**Backend Deployment Template**:
- **FR-004**: Backend Deployment MUST use `apiVersion: apps/v1`, `kind: Deployment` with `metadata.name: {{ include "todo-app.backend.fullname" . }}`
- **FR-005**: Backend Deployment MUST have configurable `replicas: {{ .Values.backend.replicas }}` (default: 1)
- **FR-006**: Backend Deployment MUST use `imagePullPolicy: {{ .Values.backend.image.pullPolicy }}` with default value `Never` for Minikube local images
- **FR-007**: Backend Deployment MUST reference image as `{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}`
- **FR-008**: Backend Deployment MUST include `livenessProbe` with `httpGet` to path `/health` on port 8000
- **FR-009**: Backend Deployment MUST include `readinessProbe` with `httpGet` to path `/health` on port 8000
- **FR-010**: Backend Deployment MUST expose containerPort 8000

**Frontend Deployment Template**:
- **FR-011**: Frontend Deployment MUST use `apiVersion: apps/v1`, `kind: Deployment` with `metadata.name: {{ include "todo-app.frontend.fullname" . }}`
- **FR-012**: Frontend Deployment MUST have configurable `replicas: {{ .Values.frontend.replicas }}` (default: 1)
- **FR-013**: Frontend Deployment MUST use `imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}` with default value `Never` for Minikube local images
- **FR-014**: Frontend Deployment MUST reference image as `{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}`
- **FR-015**: Frontend Deployment MUST include `livenessProbe` with `httpGet` to path `/` on port 3000
- **FR-016**: Frontend Deployment MUST include `readinessProbe` with `httpGet` to path `/` on port 3000
- **FR-017**: Frontend Deployment MUST expose containerPort 3000

**Service Templates**:
- **FR-018**: Backend Service MUST use `apiVersion: v1`, `kind: Service`, `type: ClusterIP` (internal access only)
- **FR-019**: Backend Service MUST expose port 8000 with `targetPort: 8000` mapping to Backend pods
- **FR-020**: Frontend Service MUST use `apiVersion: v1`, `kind: Service`, `type: NodePort` (external access via Minikube IP)
- **FR-021**: Frontend Service MUST expose port 80 with `targetPort: 3000` mapping to Frontend pods and configurable `nodePort: {{ .Values.frontend.service.nodePort }}`
- **FR-022**: Both Services MUST use selector labels matching their respective Deployments (e.g., `app: todo-backend`)

**Values.yaml Defaults**:
- **FR-023**: values.yaml MUST define `backend.image.repository: todo-backend`
- **FR-024**: values.yaml MUST define `backend.image.tag: latest`
- **FR-025**: values.yaml MUST define `backend.image.pullPolicy: Never`
- **FR-026**: values.yaml MUST define `backend.replicas: 1`
- **FR-027**: values.yaml MUST define `frontend.image.repository: todo-frontend`
- **FR-028**: values.yaml MUST define `frontend.image.tag: latest`
- **FR-029**: values.yaml MUST define `frontend.image.pullPolicy: Never`
- **FR-030**: values.yaml MUST define `frontend.replicas: 1`
- **FR-031**: values.yaml MUST define `frontend.service.nodePort: 30080` (default NodePort for local Minikube access)

### Key Entities

- **Helm Chart**: A package of Kubernetes resource templates with configurable values
  - **Attributes**: Name (todo-app), version, apiVersion, type (application), templates directory, values.yaml
  - **Relationships**: Contains Deployment and Service templates for Backend and Frontend

- **Umbrella Chart**: A Helm chart that packages multiple sub-components as a single deployable unit
  - **Attributes**: Chart.yaml with dependencies (Backend, Frontend as sub-charts or templates)
  - **Relationships**: Manages Backend and Frontend as unified application

- **Deployment Template**: A Kubernetes resource template for managing pod replicas
  - **Attributes**: Replica count, image reference, imagePullPolicy, liveness/readiness probes, container ports
  - **Relationships**: Creates pods from container images, managed by Helm chart

- **Service Template**: A Kubernetes resource template for networking and load balancing
  - **Attributes**: Service type (ClusterIP/NodePort), port mappings, selector labels, nodePort
  - **Relationships**: Routes traffic to pods created by Deployments

- **values.yaml**: A configuration file with default values for Helm template variables
  - **Attributes**: Image repository, image tag, imagePullPolicy, replica count, service nodePort
  - **Relationships**: Provides default values for Helm templates, can be overridden with custom values files

## Success Criteria

### Measurable Outcomes

- **SC-001**: Helm chart installs successfully with `helm install todo-app ./deploy/helm/todo-app` and both Backend and Frontend pods reach Running state within 60 seconds
- **SC-002**: Backend service is accessible from within the cluster at `todo-backend:8000` and `/health` endpoint returns 200 OK
- **SC-003**: Frontend service is accessible externally at `$(minikube ip):30080` and homepage renders successfully
- **SC-004**: Helm chart validates successfully with `helm lint ./deploy/helm/todo-app` showing zero errors or warnings
- **SC-005**: Deployment with custom values (e.g., `--set backend.replicas=3`) results in 3 Backend pods running
- **SC-006**: Helm upgrade with changed values completes within 30 seconds without downtime (verified by continuous health check monitoring)
- **SC-007**: When Backend pod is manually deleted, Kubernetes recreates it within 10 seconds (self-healing via Deployment controller)
- **SC-008**: When Backend process crashes, livenessProbe detects failure and Kubernetes restarts the pod within 30 seconds
- **SC-009**: Helm uninstall `helm uninstall todo-app` removes all resources (Deployments, Services, Pods) within 10 seconds
- **SC-010**: Helm chart works identically on fresh Minikube cluster with no manual kubectl configuration required

## Assumptions

- **A-001**: Minikube cluster is running and accessible via `kubectl`
- **A-002**: Docker images for Backend and Frontend are built locally and available to Minikube Docker daemon (via `eval $(minikube docker-env)`)
- **A-003**: Helm 3.x is installed on the local machine
- **A-004**: Backend exposes `/health` endpoint on port 8000 (already implemented in Phase II/III)
- **A-005**: Frontend serves content on port 3000 and homepage is accessible at `/`
- **A-006**: Minikube has sufficient resources (2 CPU, 4GB RAM minimum) to run both services
- **A-007**: Database (PostgreSQL/Neon) connection is handled via environment variables (not part of Helm chart - injected via Kubernetes Secrets)
- **A-008**: No persistent storage required for stateless Backend/Frontend (database is external)
- **A-009**: Local development uses `imagePullPolicy: Never` to avoid pulling from Docker Hub

## Out of Scope

- **OOS-001**: Database deployment (PostgreSQL/Neon) - Database is external service, not part of Helm chart
- **OOS-002**: Secrets management (JWT secrets, database credentials) - Use Kubernetes Secrets created manually before helm install
- **OOS-003**: Ingress configuration for production routing - Use NodePort for Minikube, Ingress is Phase IV advanced feature
- **OOS-004**: Horizontal Pod Autoscaler (HPA) configuration - Advanced scaling feature, not needed for local Minikube
- **OOS-005**: Persistent Volume Claims for stateful services - Backend/Frontend are stateless
- **OOS-006**: ConfigMaps for application configuration - Use environment variables in Deployment templates
- **OOS-007**: Network Policies for pod-to-pod communication - Minikube default networking is sufficient
- **OOS-008**: Resource limits and requests optimization - Use Kubernetes manifest defaults initially
- **OOS-009**: Helm chart repository publishing - Local chart installation only for now
- **OOS-010**: Multi-namespace deployments - Deploy to default namespace initially

## Dependencies

- **D-001**: Minikube cluster running and accessible via kubectl
- **D-002**: Helm 3.x installed on local machine
- **D-003**: Docker images built locally: `todo-backend:latest` and `todo-frontend:latest`
- **D-004**: Backend application with `/health` endpoint (Phase II/III)
- **D-005**: Frontend Next.js application serving on port 3000
- **D-006**: Kubernetes Secrets created for database credentials (if needed)
- **D-007**: Minikube Docker environment configured (`eval $(minikube docker-env)`)

## References

- **Helm Documentation**: https://helm.sh/docs/
- **Helm Chart Best Practices**: https://helm.sh/docs/chart_best_practices/
- **Kubernetes Deployments**: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- **Kubernetes Services**: https://kubernetes.io/docs/concepts/services-networking/service/
- **Minikube**: https://minikube.sigs.k8s.io/docs/
- **Liveness and Readiness Probes**: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
