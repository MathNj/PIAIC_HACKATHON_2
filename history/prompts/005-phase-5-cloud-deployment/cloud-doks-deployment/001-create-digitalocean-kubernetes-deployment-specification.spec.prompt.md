---
id: 001
title: Create DigitalOcean Kubernetes Deployment Specification
stage: spec
date: 2025-12-11
surface: agent
model: claude-sonnet-4.5
feature: 011-cloud-doks-deployment
branch: 011-cloud-doks-deployment
user: Najma-LP
command: /sp.specify
labels: ["deployment", "digitalocean", "kubernetes", "doks", "redpanda", "dapr", "helm", "secrets", "spec", "sasl", "ssl", "tls"]
links:
  spec: specs/011-cloud-doks-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/011-cloud-doks-deployment/spec.md
  - specs/011-cloud-doks-deployment/checklists/requirements.md
tests:
  - Specification quality validation (all checks passed)
  - Content quality assessment (technology-appropriate, user-centric)
  - Requirement completeness verification (28 FRs, all testable and measurable)
  - Feature readiness evaluation (3 user stories with acceptance criteria)
---

## Prompt

/sp.specify "Create @specs/deployment/cloud-doks.md. Define the deployment strategy for DigitalOcean: 1. **Redpanda:** Instructions to connect to Redpanda Cloud (SASL/SSL). 2. **Dapr on K8s:** Instructions to init Dapr on the cluster. 3. **Helm Charts:** Update Helm charts to include the Dapr annotations (dapr.io/enabled: 'true') in the deployment YAMLs. 4. **Secrets:** Define how to inject Redpanda credentials into Dapr components using Kubernetes Secrets."

## Response snapshot

Successfully created comprehensive deployment specification on branch `011-cloud-doks-deployment`:

**Specification** (`specs/011-cloud-doks-deployment/spec.md`):

**User Stories** (3 prioritized):
1. **P1: Secure Redpanda Cloud Integration** - Connect Todo App microservices to Redpanda Cloud using SASL/SCRAM-SHA-256 and TLS/SSL
   - 4 acceptance scenarios covering authentication, SSL encryption, subscription, and credential rotation
   - Independent test: Single service with Dapr to DOKS, verify pub/sub delivery
   - Blocking requirement: Without Redpanda connectivity, Recurring Task Service and Notification Service cannot function

2. **P1: Dapr-Enabled Kubernetes Deployment** - Deploy with Dapr sidecars automatically injected
   - 4 acceptance scenarios covering control plane init, sidecar injection, API accessibility, and isolated sidecars
   - Independent test: Deploy Helm charts with annotations, verify sidecar injection
   - Essential: Sidecars required for pub/sub and state store access

3. **P2: Centralized Secret Management** - Manage credentials through Kubernetes Secrets for security and rotation
   - 4 acceptance scenarios covering Secret creation, component referencing, credential rotation, and shared secrets
   - Independent test: Create Secrets, verify connection without plaintext exposure
   - Security best practice: Not blocking but essential for production-grade operations

**Functional Requirements** (28 total, organized by category):

*Redpanda Cloud Integration (FR-001 to FR-008)*:
- SASL/SCRAM-SHA-256 authentication mechanism
- TLS/SSL encryption for all broker connections
- Configurable broker URLs and credentials via Kubernetes Secret
- authType: password configuration in Dapr component
- TLS CA certificate reference for broker validation
- Step-by-step documentation for credential acquisition
- Example kubectl create secret commands

*Dapr on Kubernetes (FR-009 to FR-016)*:
- Dapr control plane initialization instructions (dapr init --kubernetes)
- Minimum version: 1.12.0
- Verification steps (dapr status -k)
- Required annotations: dapr.io/enabled, app-id, app-port, config
- Sidecar injection verification (2/2 containers)

*Helm Chart Updates (FR-017 to FR-022)*:
- Dapr annotations in backend, recurring-task-service, notification-service charts
- Unique app-id per service
- Optional API logging and configurable log level
- values.yaml dapr.enabled flag for conditional enablement

*Kubernetes Secrets Management (FR-023 to FR-028)*:
- redpanda-credentials Secret with brokers, sasl-username, sasl-password, ca-cert
- secretKeyRef usage in Dapr kafka-pubsub component
- Deployment as Kubernetes resources (not ConfigMap)
- Credential rotation documentation

**Success Criteria** (8 measurable outcomes):
- SC-001: Deploy to DOKS with Redpanda connectivity in under 30 minutes
- SC-002: 0 authentication errors after deployment
- SC-003: 99.9% event delivery reliability
- SC-004: 100% sidecar injection success rate
- SC-005: Credential rotation without YAML modifications
- SC-006: <5s pod startup time increase with Dapr
- SC-007: All credentials encrypted in Secrets, 0 plaintext exposure
- SC-008: 90% documentation task completion success rate on first read

**Key Entities**:
- Kubernetes Secret: Stores encrypted Redpanda credentials
- Dapr Component: Custom resource defining pub/sub, state store, bindings
- Helm Chart Deployment: Kubernetes Deployment with Dapr annotations
- Redpanda Cloud Cluster: Managed Kafka-compatible streaming platform

**Edge Cases** (7 identified):
- Unreachable Redpanda Cloud during pod startup
- Expired Redpanda Cloud credentials
- Dapr sidecar injection failures
- Secret rotation while pods running
- Dapr annotations without Dapr installed
- Cross-cloud network connectivity issues (DOKS to Redpanda)
- Conflicting Dapr app-id usage

**Assumptions** (10):
- DOKS cluster provisioned and accessible via kubectl
- Cluster-admin permissions for Dapr installation
- Redpanda Cloud cluster provisioned with SASL/SCRAM-SHA-256
- Broker URLs and credentials available
- Internet connectivity to Redpanda Cloud
- Helm 3.x installed and configured
- Existing Helm charts available for all services
- Sufficient cluster resources for Dapr control plane
- Trusted TLS certificates or CA cert provided
- Dapr 1.12.0+ compatible with DOKS K8s version

**Out of Scope** (14 items):
- DOKS cluster provisioning
- Redpanda Cloud cluster provisioning
- Topic and schema configuration
- Monitoring and observability setup
- Distributed tracing (Zipkin/Jaeger)
- Dapr service invocation
- Dapr actors or workflows
- API authentication/authorization
- Horizontal pod autoscaling
- Ingress controllers/load balancers
- Database migration strategies
- Frontend deployment (Vercel/CDN)
- CI/CD pipeline setup
- Disaster recovery/backup strategies

**Quality Validation** (`specs/011-cloud-doks-deployment/checklists/requirements.md`):

All validation checks passed:
- ✅ Content Quality (4/4): No implementation details, user-centric, appropriate technology specificity, clear and concise
- ✅ Requirement Completeness (8/8): Testable, measurable, unambiguous, prioritized, complete, consistent, traceable, no clarifications needed
- ✅ Feature Readiness (4/4): Acceptance criteria defined, realistic scenarios, dependencies identified, measurable outcomes

**Validation Summary**: Specification is complete and ready for planning phase

## Outcome

- ✅ Impact: Created production-ready deployment specification for DigitalOcean Kubernetes with Redpanda Cloud, covering authentication, Dapr integration, Helm configuration, and secret management
- 🧪 Tests: Specification quality validation passed all checks (content quality, requirement completeness, feature readiness)
- 📁 Files: 2 files created (spec.md with 175 lines, checklists/requirements.md)
- 🔁 Next prompts: Run /sp.plan to create architectural design and implementation strategy for cloud deployment
- 🧠 Reflection: Specification balances security (SASL/SSL, encrypted Secrets), operational simplicity (Dapr sidecars, Helm annotations), and production readiness (credential rotation, measurable outcomes). Edge cases and assumptions provide clear boundaries. Ready for architectural planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification created successfully with comprehensive requirements
- Graders run and results (PASS/FAIL): All specification quality checks PASS (content quality, requirement completeness, feature readiness)
- Prompt variant (if applicable): Standard /sp.specify workflow with cloud deployment focus
- Next experiment (smallest change to try): Run /sp.plan to translate deployment requirements into concrete architectural design with Helm chart templates, Secret manifests, and Dapr component configurations
