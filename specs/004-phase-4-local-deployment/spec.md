# Feature Specification: Local Minikube Deployment with AI-Assisted DevOps

**Feature Branch**: `007-minikube-deployment`
**Created**: 2025-12-09
**Updated**: 2025-12-26
**Status**: In Progress
**Input**: User description: "Phase IV: Local Kubernetes Infrastructure - Containerize the Todo Chatbot (Phase III) and deploy it to a local Minikube cluster using AI-assisted DevOps tools (Gordon, kubectl-ai, kagent) with Helm Charts, multi-stage Docker builds, scalability support, and externalized configuration"

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Containerization** | Docker (Docker Desktop) |
| **Docker AI** | Docker AI Agent (Gordon) |
| **Orchestration** | Kubernetes (Minikube) |
| **Package Manager** | Helm Charts |
| **AI DevOps** | kubectl-ai, kagent |
| **Application** | Phase III Todo Chatbot |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Local Development Environment Setup (Priority: P1)

As a **developer**, I want to deploy the entire Todo application stack to my local Minikube cluster so that I can develop and test features in a production-like Kubernetes environment without relying on cloud resources.

**Why this priority**: Enables local-first development workflow, reduces cloud costs during development, and provides faster iteration cycles. This is the foundation for all subsequent deployment work.

**Independent Test**: Can be fully tested by starting Minikube, deploying the Helm chart, and accessing both frontend and backend services locally. Delivers a working local Kubernetes environment.

**Acceptance Scenarios**:

1. **Given** Minikube is installed and running, **When** I deploy the `todo-stack` Helm chart with local configuration, **Then** both frontend and backend pods start successfully and reach Ready state within 2 minutes
2. **Given** the stack is deployed locally, **When** I access `http://localhost:30080`, **Then** the frontend loads and can communicate with the backend API
3. **Given** local deployment is complete, **When** I check pod labels, **Then** all pods have `app: todo` and appropriate `tier` labels for AI ops compatibility

---

### User Story 2 - Container Image Management (Priority: P2)

As a **DevOps engineer**, I want both frontend and backend services to use multi-stage Docker builds so that the resulting container images are minimal, secure, and optimized for Kubernetes deployment.

**Why this priority**: Optimized images reduce deployment time, cluster resource usage, and attack surface. Essential for efficient local development and production deployments.

**Independent Test**: Can be tested by building Docker images, inspecting their sizes, and verifying multi-stage structure. Delivers production-ready container images.

**Acceptance Scenarios**:

1. **Given** backend Dockerfile exists, **When** I build the backend image, **Then** it uses Python 3.13-slim base and `uv` for package management with multi-stage optimization
2. **Given** frontend Dockerfile exists, **When** I build the frontend image, **Then** it uses Node 20-alpine with three stages: dependencies install, build, and minimal runtime
3. **Given** both images are built, **When** I inspect image sizes, **Then** backend image is under 200MB and frontend image is under 150MB (excluding base layers)

---

### User Story 3 - Environment Configuration Flexibility (Priority: P3)

As a **platform engineer**, I want the Helm chart to support toggling between local and production deployment modes so that the same chart can be used across all environments with appropriate service configurations.

**Why this priority**: Enables single-source-of-truth for deployments across environments, reduces configuration drift, and simplifies CI/CD pipelines.

**Independent Test**: Can be tested by deploying with different values files and verifying service types change correctly. Delivers environment-agnostic deployment configuration.

**Acceptance Scenarios**:

1. **Given** the Helm chart is configured for local mode, **When** I deploy with `--set environment=local`, **Then** frontend service uses NodePort type on port 30080
2. **Given** the Helm chart is configured for production mode, **When** I deploy with `--set environment=production`, **Then** frontend service uses LoadBalancer type
3. **Given** any deployment mode, **When** I inspect backend service, **Then** it always uses ClusterIP type (internal only)

---

### User Story 4 - Backend Scalability and High Availability (Priority: P2)

As a **platform engineer**, I want the backend service to support multiple replicas so that the system can handle increased load and provide high availability for API requests.

**Why this priority**: Demonstrates horizontal scaling patterns essential for production deployments. Multiple backend replicas ensure service continuity if one pod fails and enable load distribution.

**Independent Test**: Can be tested by deploying backend with multiple replicas, verifying all replicas are healthy, and confirming requests are load-balanced across instances. Delivers a scalable backend architecture.

**Acceptance Scenarios**:

1. **Given** the Helm chart is deployed, **When** I check backend pods, **Then** at least 2 backend replicas are running and in Ready state
2. **Given** multiple backend replicas are running, **When** I send API requests, **Then** requests are distributed across different backend pod instances
3. **Given** one backend replica fails, **When** I continue sending requests, **Then** the system remains responsive using remaining healthy replicas

---

### User Story 5 - AI-Assisted Docker Containerization with Gordon (Priority: P1)

As a **developer**, I want to use Docker AI Agent (Gordon) to optimize and troubleshoot Docker container builds so that I can create production-ready, secure, and minimal container images without deep Docker expertise.

**Why this priority**: Gordon provides intelligent Dockerfile optimization, security scanning, and debugging capabilities. This reduces the learning curve for Docker best practices and ensures production-ready containers from day one.

**Independent Test**: Can be tested by using Gordon to analyze, optimize, and debug Dockerfiles. Delivers AI-assisted containerization workflow.

**Acceptance Scenarios**:

1. **Given** I have initial Dockerfiles for frontend and backend, **When** I run `docker ai "optimize the backend Dockerfile for production"`, **Then** Gordon suggests multi-stage build improvements, security hardening, and size optimizations
2. **Given** a container build fails, **When** I run `docker ai "debug why the backend container crashed"`, **Then** Gordon analyzes logs and provides actionable fix suggestions
3. **Given** I want to apply Gordon's suggestions, **When** I confirm the changes, **Then** the Dockerfile is automatically updated with AI-recommended optimizations

---

### User Story 6 - AI-Assisted Kubernetes Operations with kubectl-ai (Priority: P1)

As a **developer**, I want to use kubectl-ai for natural language Kubernetes operations so that I can deploy, scale, and troubleshoot applications without memorizing complex kubectl commands.

**Why this priority**: kubectl-ai dramatically lowers the Kubernetes learning curve by accepting natural language commands. This enables developers to be productive on day one and focus on application logic rather than YAML syntax.

**Independent Test**: Can be tested by executing natural language kubectl-ai commands and verifying correct Kubernetes resources are created/modified. Delivers intuitive Kubernetes workflow.

**Acceptance Scenarios**:

1. **Given** the application needs deployment, **When** I run `kubectl-ai "deploy the todo frontend with 2 replicas"`, **Then** kubectl-ai generates and applies the correct Deployment manifest
2. **Given** I need to scale the backend, **When** I run `kubectl-ai "scale the backend to handle more load"`, **Then** kubectl-ai increases backend replicas with proper load balancing
3. **Given** pods are failing, **When** I run `kubectl-ai "check why the pods are failing"`, **Then** kubectl-ai diagnoses the issue and suggests fixes

---

### User Story 7 - AI-Powered Cluster SRE with kagent (Priority: P2)

As a **platform engineer**, I want to use kagent for intelligent cluster health analysis and resource optimization so that I can maintain a healthy, cost-effective Kubernetes environment.

**Why this priority**: kagent provides advanced SRE capabilities including proactive health monitoring, resource optimization, and cost analysis. This ensures the cluster runs efficiently and issues are caught before they impact users.

**Independent Test**: Can be tested by running kagent analysis commands and verifying actionable insights are provided. Delivers AI-powered SRE operations.

**Acceptance Scenarios**:

1. **Given** the cluster is running, **When** I run `kagent "analyze the cluster health"`, **Then** kagent provides comprehensive health report including resource utilization, pod status, and potential issues
2. **Given** I want to optimize costs, **When** I run `kagent "optimize resource allocation"`, **Then** kagent identifies over-provisioned resources and suggests right-sizing recommendations
3. **Given** there are performance issues, **When** I run `kagent "investigate performance degradation"`, **Then** kagent identifies bottlenecks and provides optimization strategies

---

### Edge Cases

**Kubernetes Operations:**
- What happens when Minikube cluster has insufficient resources (CPU/memory) to schedule multiple backend replicas?
- How does the system handle image pull failures (e.g., Docker Hub rate limits)?
- What occurs if database connection to external Neon fails during pod startup?
- How are environment variable changes (secrets, config) applied to running pods?
- What happens when frontend tries to connect to backend before backend replicas are ready?
- How does the system behave when one backend replica is unhealthy but others are running?
- What occurs if required secrets (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET) are missing or invalid?
- How does the system handle updates to secrets without pod restarts?

**AI-Assisted Tools:**
- What happens when Gordon suggests Dockerfile changes that break the build?
- How does kubectl-ai handle ambiguous natural language commands (e.g., "fix the backend")?
- What occurs if kubectl-ai is not installed or not in PATH when attempting AI-assisted operations?
- How does kagent handle clusters with no resource metrics available?
- What happens when Gordon's security scan identifies critical vulnerabilities in base images?
- How does the system recover if kubectl-ai generates incorrect YAML manifests?
- What occurs when kagent recommendations conflict with current resource constraints?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide Dockerfiles for both frontend and backend services using multi-stage builds
- **FR-002**: Backend Dockerfile MUST use Python 3.13-slim base image and `uv` package manager for dependency installation
- **FR-003**: Frontend Dockerfile MUST use Node 20-alpine base image with separate stages for dependency installation, build, and runtime
- **FR-004**: Backend container MUST expose port 8000 for FastAPI application
- **FR-005**: Frontend container MUST expose port 3000 for Next.js application
- **FR-006**: System MUST provide a Helm chart named `todo-stack` that packages both frontend and backend deployments
- **FR-007**: Helm chart MUST support environment configuration via values with at least `local` and `production` modes
- **FR-008**: Frontend service MUST be accessible via NodePort on fixed port 30080 in local mode
- **FR-009**: Backend service MUST use ClusterIP type (not externally accessible) in all deployment modes
- **FR-010**: All Kubernetes pods MUST have standardized labels including `app: todo`, `tier: [frontend|backend]`, and `environment: [local|production]`
- **FR-011**: System MUST support connection to external Neon PostgreSQL database (no persistent volumes required)
- **FR-012**: Helm chart MUST inject database credentials and API keys via Kubernetes Secrets
- **FR-013**: Deployment MUST include readiness and liveness probes for both frontend and backend pods
- **FR-014**: System MUST support AI ops tooling compatibility (`kubectl-ai` and `kagent`) through descriptive labels and annotations
- **FR-015**: Backend deployment MUST support multiple replicas (minimum 2) for load distribution and high availability
- **FR-016**: Frontend deployment MUST run as single replica (1) for local development efficiency
- **FR-017**: System MUST inject the following environment variables via Kubernetes Secrets: `DATABASE_URL`, `OPENAI_API_KEY`, `BETTER_AUTH_SECRET`
- **FR-018**: Frontend build process MUST optimize for minimal runtime footprint (standalone output pattern)
- **FR-019**: All deployment configuration (replica counts, resource limits, environment variables) MUST be externalized to Helm values
- **FR-020**: System MUST support optional ingress configuration for advanced local networking scenarios
- **FR-021**: Backend replicas MUST share stateless architecture compatible with load balancing across instances
- **FR-022**: Helm chart MUST provide default values for all required configuration with clear documentation

**AI-Assisted DevOps Requirements:**
- **FR-023**: Docker AI Agent (Gordon) MUST be available for Dockerfile optimization and security scanning
- **FR-024**: Gordon MUST provide actionable suggestions for multi-stage build optimization, vulnerability remediation, and image size reduction
- **FR-025**: kubectl-ai MUST be installed and configured to accept natural language Kubernetes commands
- **FR-026**: kubectl-ai MUST generate valid Kubernetes manifests from natural language input (e.g., "deploy frontend with 2 replicas")
- **FR-027**: kubectl-ai MUST provide confirmation prompts before applying generated manifests to the cluster
- **FR-028**: kagent MUST be available for AI-powered cluster health analysis and SRE operations
- **FR-029**: kagent MUST provide cluster health reports including resource utilization, pod status, and performance metrics
- **FR-030**: kagent MUST identify resource optimization opportunities (over-provisioned pods, unused resources)
- **FR-031**: All AI tool commands (Gordon, kubectl-ai, kagent) MUST be documented with examples in quickstart guide
- **FR-032**: System MUST support fallback to standard Docker/kubectl commands when AI tools are unavailable

### Key Entities

**Container & Orchestration Resources:**
- **Docker Image (Backend)**: Multi-stage containerized Python FastAPI application with minimal runtime dependencies
- **Docker Image (Frontend)**: Multi-stage containerized Next.js application with static asset optimization
- **Helm Chart**: Kubernetes package containing Deployment, Service, ConfigMap, and Secret resources for the full stack
- **Kubernetes Deployment (Backend)**: Orchestration resource managing backend pod replicas with health checks
- **Kubernetes Deployment (Frontend)**: Orchestration resource managing frontend pod replicas with health checks
- **Kubernetes Service (Backend)**: ClusterIP service for internal backend API access
- **Kubernetes Service (Frontend)**: NodePort (local) or LoadBalancer (production) service for external frontend access
- **Kubernetes Secret**: Secure storage for database URLs, JWT secrets, and API keys

**AI-Assisted DevOps Tools:**
- **Gordon (Docker AI Agent)**: AI-powered tool for Dockerfile optimization, security scanning, and container debugging
- **kubectl-ai**: Natural language interface for Kubernetes operations, manifest generation, and troubleshooting
- **kagent**: AI-powered SRE agent for cluster health monitoring, resource optimization, and performance analysis
- **Minikube**: Local single-node Kubernetes cluster for development and testing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can deploy the entire stack to Minikube in under 5 minutes from chart installation command
- **SC-002**: Backend Docker image size is under 200MB (excluding base layers)
- **SC-003**: Frontend Docker image size is under 150MB (excluding base layers)
- **SC-004**: All pods reach Ready state within 2 minutes of deployment
- **SC-005**: Frontend is accessible at `http://localhost:30080` within 30 seconds of pods becoming ready
- **SC-006**: System supports switching between local and production configurations with a single Helm value change
- **SC-007**: 100% of required environment variables and secrets are injected via Kubernetes Secrets (zero hardcoded credentials)
- **SC-008**: AI ops tools (`kubectl-ai`, `kagent`) can successfully query and describe deployed resources using standard labels
- **SC-009**: Backend container build time is under 3 minutes with warm Docker cache
- **SC-010**: Frontend container build time is under 4 minutes with warm Docker cache
- **SC-011**: Backend scales to 2 replicas with all instances healthy and receiving traffic within 3 minutes
- **SC-012**: System remains responsive when one backend replica fails (requests continue to be served by remaining replicas)
- **SC-013**: All required secrets (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET) are successfully injected and accessible to pods
- **SC-014**: Configuration changes can be applied by updating Helm values without modifying chart templates

**AI-Assisted DevOps Success Criteria:**
- **SC-015**: Gordon successfully analyzes Dockerfiles and provides at least 3 actionable optimization suggestions per file
- **SC-016**: Gordon-optimized Docker images are at least 20% smaller than manually optimized images
- **SC-017**: kubectl-ai successfully deploys the application from natural language commands in under 2 minutes
- **SC-018**: kubectl-ai correctly interprets and executes 90% of common deployment/scaling/troubleshooting commands
- **SC-019**: kagent cluster health report completes in under 30 seconds and identifies all resource bottlenecks
- **SC-020**: kagent resource optimization recommendations result in at least 15% resource efficiency improvement
- **SC-021**: Developer can use kubectl-ai without prior Kubernetes YAML knowledge (zero learning curve validation)
- **SC-022**: All AI tools (Gordon, kubectl-ai, kagent) are properly installed and functional before deployment begins

## Assumptions

**Infrastructure & Tools:**
- Minikube is already installed and running on the developer's machine
- Docker Desktop is installed and configured for local image builds
- Helm 3.x is installed on the developer's machine
- kubectl is configured to access the Minikube cluster
- **Gordon (Docker AI)** is installed and functional (part of Docker Desktop AI features)
- **kubectl-ai** is installed and in system PATH
- **kagent** is installed and configured for Kubernetes cluster access
- Developer has network access to pull base images from Docker Hub (python:3.13-slim, node:20-alpine)

**Application & Credentials:**
- Neon PostgreSQL database is already provisioned and accessible from the local network
- OpenAI API key is available for Phase III AI agent functionality
- Better Auth secret is generated and available for JWT authentication
- Database credentials, OpenAI API key, and Better Auth secret are available for Kubernetes Secret creation
- Phase III Todo Chatbot application is complete with AI agent and MCP integration

**Resources:**
- Sufficient local resources: minimum 6GB RAM and 4 CPU cores allocated to Minikube (to support multiple backend replicas)
- Developer machine has sufficient CPU/memory for running AI-assisted tools alongside Minikube cluster

## Dependencies

**External Services:**
- **External**: Neon PostgreSQL database (already provisioned in Phase II)
- **External**: OpenAI API (required for Phase III AI agent functionality)
- **External**: Docker Hub for base images (python:3.13-slim, node:20-alpine)

**Infrastructure & Orchestration:**
- **Infrastructure**: Minikube cluster (assumed pre-installed)
- **Infrastructure**: Helm 3.x (assumed pre-installed)
- **Infrastructure**: kubectl CLI (assumed pre-installed)

**AI-Assisted DevOps Tools:**
- **Tool**: Gordon (Docker AI Agent) - Part of Docker Desktop
- **Tool**: kubectl-ai - Natural language Kubernetes interface ([kubectl-ai installation](https://github.com/sozercan/kubectl-ai))
- **Tool**: kagent - AI-powered Kubernetes SRE agent ([kagent installation](https://github.com/kubiyabot/kagent))

**Codebase:**
- **Codebase**: Phase III Todo Chatbot application (Next.js frontend with OpenAI ChatKit integration)
- **Codebase**: Phase III Backend application (FastAPI with MCP tools and AI agent orchestration)
- **Codebase**: Better Auth JWT authentication system (Phase II/III)

## Out of Scope

- Production Kubernetes cluster setup (DigitalOcean Kubernetes Service) - deferred to later phase
- Automated CI/CD pipeline for image builds - deferred to later phase
- Mandatory ingress controller configuration - optional for advanced users, primary access via NodePort
- Horizontal Pod Autoscaling (HPA) - using fixed replica counts for local development
- Persistent volume provisioning - using external Neon database
- Certificate management (TLS/SSL) - HTTP only for local development
- Monitoring and logging infrastructure (Prometheus, Grafana) - deferred to later phase
- Multi-region or multi-cluster deployments - single Minikube cluster only
- Service mesh implementation (Istio, Linkerd) - deferred to later phase
- Custom resource definitions (CRDs) or Operators - using standard Kubernetes resources only

---

## AI-Assisted DevOps Workflow

This section documents the recommended workflow for using Gordon, kubectl-ai, and kagent throughout the Phase IV deployment lifecycle.

### Phase 1: Container Optimization with Gordon

**Step 1: Analyze Dockerfiles**
```bash
# Analyze backend Dockerfile
docker ai "review the backend/Dockerfile and suggest optimizations"

# Analyze frontend Dockerfile
docker ai "review the frontend/Dockerfile for production readiness"
```

**Step 2: Apply Optimizations**
```bash
# Optimize for size and security
docker ai "optimize backend/Dockerfile for minimal size and security"

# Verify multi-stage build structure
docker ai "check if the Dockerfile uses proper multi-stage builds"
```

**Step 3: Security Scanning**
```bash
# Scan for vulnerabilities
docker ai "scan the backend image for security vulnerabilities"

# Get remediation suggestions
docker ai "how can I fix the vulnerabilities in the base image"
```

**Expected Outcomes:**
- Dockerfiles optimized with multi-stage builds
- Security vulnerabilities identified and remediated
- Container images 20%+ smaller than baseline
- Production-ready containerization without deep Docker expertise

---

### Phase 2: Deployment with kubectl-ai

**Step 1: Deploy Application**
```bash
# Deploy frontend with natural language
kubectl-ai "deploy the todo frontend with 2 replicas"

# Deploy backend with scaling
kubectl-ai "deploy the todo backend with 3 replicas and 500m CPU limit"
```

**Step 2: Configure Services**
```bash
# Expose frontend via NodePort
kubectl-ai "expose the frontend on port 30080 using NodePort"

# Create backend ClusterIP service
kubectl-ai "create an internal service for the backend on port 8000"
```

**Step 3: Manage Secrets**
```bash
# Create database secret
kubectl-ai "create a secret named todo-secrets with DATABASE_URL from my .env file"

# Verify secrets are mounted
kubectl-ai "check if the backend pods have access to todo-secrets"
```

**Expected Outcomes:**
- Zero YAML written manually
- Deployments created from natural language in under 2 minutes
- Developer productive on day one without Kubernetes expertise
- 90%+ command success rate for common operations

---

### Phase 3: Scaling and Troubleshooting

**Scaling Operations:**
```bash
# Scale up for load testing
kubectl-ai "scale the backend to handle more load"

# Scale down to save resources
kubectl-ai "reduce backend replicas to 2"
```

**Troubleshooting:**
```bash
# Diagnose pod failures
kubectl-ai "check why the pods are failing"

# Investigate crashlooping containers
kubectl-ai "why is the backend pod crashlooping"

# Debug networking issues
kubectl-ai "can the frontend connect to the backend service"
```

**Expected Outcomes:**
- Instant scaling without memorizing kubectl scale syntax
- AI-powered root cause analysis for failures
- Actionable fix suggestions within seconds
- Reduced time-to-resolution for common issues

---

### Phase 4: Cluster Health & Optimization with kagent

**Health Monitoring:**
```bash
# Get comprehensive cluster health report
kagent "analyze the cluster health"

# Check resource utilization
kagent "show me resource usage across all pods"

# Identify performance bottlenecks
kagent "what's causing slow performance in the cluster"
```

**Resource Optimization:**
```bash
# Find over-provisioned resources
kagent "optimize resource allocation"

# Get cost optimization recommendations
kagent "how can I reduce resource costs"

# Right-size pod requests/limits
kagent "suggest better CPU and memory limits for my pods"
```

**Proactive SRE:**
```bash
# Performance investigation
kagent "investigate performance degradation"

# Capacity planning
kagent "can the cluster handle 10x traffic"

# Best practices audit
kagent "review my deployments for best practices"
```

**Expected Outcomes:**
- Cluster health insights in under 30 seconds
- 15%+ resource efficiency improvement
- Proactive issue detection before user impact
- SRE-level operations accessible to all developers

---

### Integration Pattern: The Complete Workflow

**Day 1: Initial Deployment**
1. **Gordon**: Optimize Dockerfiles → Build minimal, secure images
2. **kubectl-ai**: Deploy application → Natural language deployment
3. **kagent**: Health check → Verify cluster is healthy

**Day 2: Scaling for Load Test**
1. **kubectl-ai**: "scale backend to 10 replicas"
2. **kagent**: "analyze cluster health under load"
3. **kagent**: "optimize resource allocation"

**Day 3: Troubleshooting Production Issue**
1. **kubectl-ai**: "why are backend pods failing"
2. **Gordon**: "debug the backend container logs"
3. **kagent**: "investigate performance degradation"

**Day 4: Optimization Iteration**
1. **Gordon**: "can we reduce the image size further"
2. **kubectl-ai**: "apply the new image to backend deployment"
3. **kagent**: "verify the optimization improved performance"

**Workflow Philosophy:**
- **Start with kubectl-ai** → Feel empowered from day one
- **Layer in kagent** → Add advanced SRE use cases
- **Gordon throughout** → Continuous container optimization
- **Pair with Minikube** → Zero-cost learning environment

This integrated approach reduces the Kubernetes learning curve from months to days while maintaining production-grade quality and security standards.
