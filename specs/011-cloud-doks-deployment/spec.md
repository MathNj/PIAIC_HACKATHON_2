# Feature Specification: DigitalOcean Kubernetes Deployment with Redpanda Cloud

**Feature Branch**: `011-cloud-doks-deployment`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "Create @specs/deployment/cloud-doks.md. Define the deployment strategy for DigitalOcean: 1. **Redpanda:** Instructions to connect to Redpanda Cloud (SASL/SSL). 2. **Dapr on K8s:** Instructions to init Dapr on the cluster. 3. **Helm Charts:** Update Helm charts to include the Dapr annotations (`dapr.io/enabled: 'true'`) in the deployment YAMLs. 4. **Secrets:** Define how to inject Redpanda credentials into Dapr components using Kubernetes Secrets."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Redpanda Cloud Integration (Priority: P1)

As a DevOps engineer, I need to securely connect the Todo App microservices running on DigitalOcean Kubernetes to Redpanda Cloud using SASL/SSL authentication, so that event-driven communication works reliably in production without exposing credentials.

**Why this priority**: This is the foundation for event-driven architecture in production. Without Redpanda Cloud connectivity, the Recurring Task Service and Notification Service cannot function, making this a blocking requirement.

**Independent Test**: Can be fully tested by deploying a single service with Dapr to DOKS, configuring Redpanda Cloud credentials via Kubernetes Secrets, and verifying successful pub/sub message delivery. Delivers immediate value by enabling production event streaming.

**Acceptance Scenarios**:

1. **Given** Redpanda Cloud cluster is provisioned with SASL/SCRAM-SHA-256 authentication, **When** DevOps creates Kubernetes Secret with broker URLs, username, and password, **Then** Dapr kafka-pubsub component successfully connects using the credentials
2. **Given** Dapr sidecar is running with kafka-pubsub component configured, **When** backend publishes a task_created event, **Then** the event is successfully delivered to Redpanda Cloud topic with SSL encryption
3. **Given** Redpanda Cloud topic exists, **When** Recurring Task Service subscribes via Dapr, **Then** service receives published events without authentication errors
4. **Given** Kubernetes Secret for Redpanda is updated with new credentials, **When** pods are restarted, **Then** Dapr components automatically pick up new credentials without manual configuration changes

---

### User Story 2 - Dapr-Enabled Kubernetes Deployment (Priority: P1)

As a DevOps engineer, I need to deploy Todo App microservices to DigitalOcean Kubernetes with Dapr sidecars automatically injected, so that services can use Dapr pub/sub, state management, and bindings without additional infrastructure setup.

**Why this priority**: Dapr sidecars are essential for microservices to access pub/sub and state store. Without proper Dapr initialization and annotations, services cannot leverage event-driven capabilities.

**Independent Test**: Can be tested by deploying Helm charts with Dapr annotations to DOKS and verifying that Dapr sidecars are automatically injected into pods. Delivers value by enabling Dapr features for all services.

**Acceptance Scenarios**:

1. **Given** Dapr control plane is not installed on DOKS cluster, **When** DevOps runs `dapr init --kubernetes --wait`, **Then** Dapr control plane components (operator, sidecar-injector, sentry, placement) are deployed successfully
2. **Given** Helm chart deployment YAML includes `dapr.io/enabled: "true"` annotation, **When** deployment is applied to cluster, **Then** Kubernetes automatically injects daprd sidecar container into the pod
3. **Given** Pod has Dapr sidecar injected, **When** application container starts, **Then** Dapr sidecar is accessible on localhost:3500 for HTTP API calls
4. **Given** Multiple services with Dapr enabled, **When** all are deployed, **Then** each service has its own isolated Dapr sidecar with correct app-id configuration

---

### User Story 3 - Centralized Secret Management (Priority: P2)

As a DevOps engineer, I need to manage Redpanda Cloud credentials and other sensitive configuration through Kubernetes Secrets, so that credentials are not hardcoded in Helm charts or version control and can be rotated without redeploying applications.

**Why this priority**: Security best practice for production deployments. While not blocking initial deployment, proper secret management is essential for production-grade operations and compliance.

**Independent Test**: Can be tested by creating Kubernetes Secrets for Redpanda credentials, referencing them in Dapr component YAMLs, and verifying that services connect successfully without exposing plaintext credentials. Delivers value by improving security posture.

**Acceptance Scenarios**:

1. **Given** Redpanda Cloud credentials (brokers, username, password, ca-cert), **When** DevOps creates Kubernetes Secret named `redpanda-credentials`, **Then** secret is stored encrypted in cluster with base64-encoded values
2. **Given** Dapr kafka-pubsub component YAML references `secretKeyRef` for credentials, **When** component is deployed, **Then** Dapr sidecar successfully reads credentials from Kubernetes Secret at runtime
3. **Given** Redpanda credentials need rotation, **When** DevOps updates Kubernetes Secret values, **Then** pods restart automatically and Dapr picks up new credentials without YAML changes
4. **Given** Multiple Dapr components need shared credentials, **When** all reference the same Kubernetes Secret, **Then** credential updates propagate to all components consistently

---

### Edge Cases

- What happens when Redpanda Cloud cluster is unreachable during pod startup?
- How does the system handle expired Redpanda Cloud credentials?
- What happens if Dapr control plane is installed but sidecar injection fails for a specific deployment?
- How does the system handle Kubernetes Secret rotation while pods are running?
- What happens if Helm chart deployment includes Dapr annotations but Dapr is not installed on the cluster?
- How does the system handle network connectivity issues between DOKS cluster and Redpanda Cloud (cross-cloud latency)?
- What happens if multiple deployments use the same Dapr app-id causing conflicts?

## Requirements *(mandatory)*

### Functional Requirements

#### Redpanda Cloud Integration

- **FR-001**: Deployment MUST support connecting to Redpanda Cloud using SASL/SCRAM-SHA-256 authentication mechanism
- **FR-002**: Deployment MUST enable TLS/SSL encryption for all connections to Redpanda Cloud brokers
- **FR-003**: Redpanda Cloud broker URLs MUST be configurable via Kubernetes Secret (not hardcoded in YAMLs)
- **FR-004**: Redpanda Cloud credentials (username, password) MUST be stored in Kubernetes Secret and referenced in Dapr component
- **FR-005**: Dapr kafka-pubsub component MUST include `authType: password` (SASL/SCRAM) configuration
- **FR-006**: Dapr kafka-pubsub component MUST reference TLS CA certificate for broker validation (if custom CA used)
- **FR-007**: Deployment documentation MUST include step-by-step instructions to obtain Redpanda Cloud credentials (broker URLs, SASL username/password)
- **FR-008**: Deployment documentation MUST include example `kubectl create secret` commands for Redpanda credentials

#### Dapr on Kubernetes

- **FR-009**: Deployment documentation MUST include instructions to initialize Dapr control plane on DOKS cluster using `dapr init --kubernetes`
- **FR-010**: Deployment documentation MUST specify required Dapr version (minimum: 1.12.0)
- **FR-011**: Deployment documentation MUST include verification steps to confirm Dapr control plane is running (e.g., `dapr status -k`)
- **FR-012**: Each Helm chart deployment YAML MUST include `dapr.io/enabled: "true"` annotation in pod template metadata
- **FR-013**: Each Helm chart deployment YAML MUST include `dapr.io/app-id: "<service-name>"` annotation with unique app ID per service
- **FR-014**: Helm charts MUST include `dapr.io/app-port: "<port>"` annotation specifying the application's HTTP port
- **FR-015**: Helm charts MUST include `dapr.io/config: "appconfig"` annotation referencing Dapr Configuration (if custom config needed)
- **FR-016**: Deployment documentation MUST explain how to verify Dapr sidecar injection (`kubectl get pods` shows 2/2 containers)

#### Helm Chart Updates

- **FR-017**: Backend service Helm chart MUST include Dapr annotations in `templates/deployment.yaml` pod spec
- **FR-018**: Recurring Task Service Helm chart MUST include Dapr annotations with `dapr.io/app-id: "recurring-task-service"`
- **FR-019**: Notification Service Helm chart MUST include Dapr annotations with `dapr.io/app-id: "notification-service"`
- **FR-020**: Helm charts MUST include `dapr.io/enable-api-logging: "true"` annotation for debugging (optional, can be disabled in production)
- **FR-021**: Helm charts MUST include `dapr.io/log-level: "info"` annotation (configurable via values.yaml)
- **FR-022**: Helm charts values.yaml MUST include `dapr.enabled` boolean flag to conditionally enable/disable Dapr annotations

#### Kubernetes Secrets Management

- **FR-023**: Deployment MUST create Kubernetes Secret named `redpanda-credentials` in the same namespace as services
- **FR-024**: `redpanda-credentials` Secret MUST include keys: `brokers`, `sasl-username`, `sasl-password`, optionally `ca-cert`
- **FR-025**: Dapr kafka-pubsub component YAML MUST use `secretKeyRef` to reference `redpanda-credentials` Secret values
- **FR-026**: Deployment documentation MUST include example Kubernetes Secret manifest for Redpanda credentials
- **FR-027**: Dapr components YAML MUST be deployed as Kubernetes resources (not ConfigMap) to support secretKeyRef
- **FR-028**: Deployment documentation MUST include instructions to rotate Redpanda credentials by updating Secret and restarting pods

### Key Entities *(include if feature involves data)*

- **Kubernetes Secret**: Stores sensitive Redpanda Cloud credentials
  - Attributes: brokers (comma-separated URLs), sasl-username (string), sasl-password (string), ca-cert (optional PEM-encoded certificate)
  - Relationships: Referenced by Dapr kafka-pubsub component via secretKeyRef

- **Dapr Component**: Kubernetes custom resource defining pub/sub, state store, or binding
  - Attributes: component name, type (pubsub.kafka, state.redis, bindings.cron), metadata (connection parameters), scopes (list of app IDs)
  - Relationships: References Kubernetes Secrets for credentials, scoped to specific services

- **Helm Chart Deployment**: Kubernetes Deployment resource with Dapr annotations
  - Attributes: deployment name, replicas, container image, Dapr annotations (app-id, enabled, app-port)
  - Relationships: Triggers Dapr sidecar injection, associated with Dapr Components via app-id

- **Redpanda Cloud Cluster**: Managed Kafka-compatible streaming platform
  - Attributes: broker URLs (SASL), SASL username, SASL password, TLS enabled, topics (task-events, reminders)
  - Relationships: Accessed by Dapr kafka-pubsub component from all services with pub/sub needs

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: DevOps engineer can deploy Todo App to DOKS with Redpanda Cloud connectivity in under 30 minutes following documentation
- **SC-002**: All Dapr-enabled services successfully connect to Redpanda Cloud with 0 authentication errors after deployment
- **SC-003**: Events published from backend service are delivered to Redpanda Cloud with 99.9% reliability
- **SC-004**: Dapr sidecars are automatically injected into 100% of pods with `dapr.io/enabled: "true"` annotation
- **SC-005**: Redpanda credentials can be rotated by updating Kubernetes Secret without modifying Helm charts or Dapr component YAMLs
- **SC-006**: Pod startup time increases by less than 5 seconds with Dapr sidecar injection compared to non-Dapr deployments
- **SC-007**: All sensitive credentials (Redpanda username, password) are stored encrypted in Kubernetes Secrets with no plaintext exposure in version control
- **SC-008**: Deployment documentation passes review by a developer unfamiliar with Dapr on first read-through with 90% task completion success rate

## Assumptions

- DigitalOcean Kubernetes (DOKS) cluster is already provisioned and accessible via kubectl
- DevOps engineer has cluster-admin permissions to install Dapr control plane
- Redpanda Cloud cluster is already provisioned with SASL/SCRAM-SHA-256 enabled
- Redpanda Cloud broker URLs and credentials are available to DevOps team
- Kubernetes cluster has internet connectivity to reach Redpanda Cloud brokers
- Helm 3.x is installed and configured to deploy charts to DOKS
- Existing Helm charts for backend, recurring-task-service, and notification-service are available
- Kubernetes cluster has sufficient resources (CPU, memory) to run Dapr control plane and sidecars
- TLS certificates for Redpanda Cloud are trusted by cluster nodes (or CA cert is provided)
- Dapr version 1.12.0 or higher is compatible with DOKS Kubernetes version

## Out of Scope

- Provisioning DigitalOcean Kubernetes cluster (assumed to exist)
- Provisioning Redpanda Cloud cluster (assumed to exist)
- Configuring Redpanda Cloud topics and schemas (handled separately)
- Implementing monitoring and observability for Dapr components
- Setting up Dapr distributed tracing with Zipkin/Jaeger
- Configuring Dapr service invocation (focus is pub/sub only)
- Implementing Dapr actors or workflows
- Setting up Dapr API authentication/authorization
- Configuring horizontal pod autoscaling for services
- Setting up ingress controllers or load balancers for external access
- Database migration and schema deployment strategies
- Frontend deployment to Vercel or CDN (separate deployment)
- CI/CD pipeline setup for automated deployments
- Disaster recovery and backup strategies
