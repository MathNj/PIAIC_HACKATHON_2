---
id: 007
title: Update deployment-engineer agent with Phase IV/V skills
stage: misc
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Najma-LP
command: agent-update
labels: ["deployment-engineer", "agent-configuration", "phase-iv", "phase-v", "skills", "docker", "kubernetes", "kafka"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/deployment-engineer.md
tests:
  - deployment-engineer agent configuration validation
  - Skill documentation completeness check
---

## Prompt

update deployment-engineer agent

## Response snapshot

Successfully updated the deployment-engineer agent configuration with all Phase IV and Phase V deployment automation skills.

**Skills Added:**

**Phase IV - Containerization & Orchestration (3 skills):**

1. **docker-ai-pilot**
   - AI-assisted Docker container management and optimization
   - When to invoke:
     * "AI help with Docker" or "optimize my containers"
     * Building Docker images for multiple microservices
     * Troubleshooting Docker build failures or slow builds
     * Implementing advanced Docker features (BuildKit, multi-platform)
     * Running security scans on container images
     * Need to reduce image sizes significantly
   - What it provides (10 capabilities):
     * AI-assisted Dockerfile analysis and optimization recommendations
     * Automated multi-stage build creation with intelligent layer caching
     * Security scanning and hardening (trivy, docker scout, non-root, pinned versions)
     * BuildKit features (cache/secret/SSH mounts)
     * Image size optimization (87% reduction: 1.2GB → 150MB)
     * Production templates (FastAPI ~150MB, Next.js ~180MB)
     * Health check configuration and validation
     * Metadata label best practices (OCI annotations)
     * `.dockerignore` optimization
     * Build and push automation scripts
   - Example workflow with build, scan, and push commands

2. **kubectl-ai-pilot**
   - AI-assisted Kubernetes cluster operations and debugging
   - When to invoke:
     * "Help with Kubernetes" or "debug my cluster"
     * Managing Kubernetes resources (pods, deployments, services, ingress)
     * Troubleshooting deployment issues (pods not starting, crashes)
     * Inspecting and modifying resource configurations
     * Scaling deployments or updating rolling strategies
     * Investigating performance or connectivity issues
   - What it provides (10 capabilities):
     * Cluster resource inspection (pods, deployments, services, configmaps, secrets, quotas)
     * Pod troubleshooting (CrashLoopBackOff, ImagePullBackOff, OOMKilled, init failures)
     * Service connectivity debugging (endpoints, DNS, network policies, ingress)
     * Log aggregation and analysis (multi-pod, filtering, real-time, previous logs)
     * Resource quota and limit management
     * Deployment scaling and rolling updates (zero downtime, rollback)
     * ConfigMap and Secret management
     * Ingress configuration and debugging (TLS, 404/502 errors)
     * Network policy validation
     * Health check and liveness probe configuration
   - Example usage with kubectl commands

3. **kagent-debugger**
   - Kubernetes agent debugging specialist with deep pod inspection
   - When to invoke:
     * "Pods keep crashing" or "deployment stuck"
     * Need deep analysis beyond basic kubectl commands
     * Investigating Dapr sidecar issues (injection, communication errors)
     * Analyzing container logs for error patterns
     * Debugging resource usage spikes or memory leaks
     * Network connectivity issues between services
   - What it provides (10 capabilities):
     * Deep pod inspection (container states, exit codes, restart patterns, resource trends)
     * Advanced log analysis with error pattern detection (OOM, connection refused, DNS)
     * Resource usage monitoring and profiling (CPU, memory, leak detection)
     * Network connectivity testing (pod-to-pod, DNS resolution, ingress, packet tracing)
     * Dapr sidecar troubleshooting (injection, components, service invocation, pub/sub)
     * Init container and startup debugging
     * Event timeline analysis (scheduling, volumes, lifecycle)
     * Container filesystem inspection (exec, permissions, config files)
     * Automated remediation suggestions with kubectl commands
     * Health check validation (manual testing, endpoint verification)
   - Example workflow with deep analysis commands

**Phase V - Event-Driven Architecture (1 skill):**

4. **kafka-infra-provisioner**
   - Kafka cluster provisioning automation (Strimzi/Redpanda)
   - When to invoke:
     * "Deploy Kafka cluster" or "set up event streaming"
     * Setting up Phase V event-driven infrastructure
     * Provisioning Kafka for Dapr pub/sub integration
     * Creating event topics for microservices
     * Need high-throughput message broker
   - What it provides (8 capabilities):
     * Dual provider support (Strimzi - Kafka v3.6.0 with ZooKeeper, Redpanda - Kafka-compatible no ZooKeeper)
     * Automated deployment scripts (deploy_kafka.sh, health_check.sh)
     * Flexible configurations (ephemeral single-node for Minikube 1GB, persistent 3-node for production 2GB per broker)
     * Kubernetes manifests (operators, cluster CRs, topic definitions)
     * Topic management (task-events, reminders, task-updates with partitions, replicas, retention)
     * Comprehensive health checks (operators, brokers, ZooKeeper, topics, services)
     * Dapr integration preparation (bootstrap servers, connection strings)
     * Complete setup and troubleshooting documentation
   - Example usage with deployment and verification commands
   - Dapr integration YAML example for pub/sub component

**Existing Skills Retained:**
- k8s-deployer (deployment configurations)
- k8s-troubleshoot (pod troubleshooting)
- dapr-event-flow (pub/sub automation)
- deployment-validator (deployment validation)
- dockerfile-optimizer (Dockerfile optimization)

**Agent Capabilities Enhanced:**

The deployment-engineer agent now supports:
1. **Phase IV Containerization**: AI-assisted Docker optimization with security scanning and BuildKit features
2. **Phase IV Orchestration**: AI-assisted Kubernetes operations with deep debugging and troubleshooting
3. **Phase V Event Infrastructure**: Kafka cluster provisioning with dual provider support
4. **Complete Deployment Lifecycle**: From Docker build to Kubernetes deploy to event streaming setup

**Documentation Quality:**

All 4 new skills include:
- Clear "When to invoke" triggers with 5-6 specific scenarios
- Comprehensive "What it provides" lists (8-10 capabilities each)
- Example workflows with bash/kubectl commands
- Integration guidance (Dapr pub/sub, security scanning, health checks)
- Total documentation added: 290 lines

**Integration with Existing Infrastructure:**

Skills integrate with:
- Existing DOKS cluster (todo-app-cluster in nyc3)
- DigitalOcean Container Registry (registry.digitalocean.com/todo-chatbot-reg)
- Current services (frontend:3000, backend:8000, notification-service:8001)
- Dapr components (kafka-pubsub, statestore, reminder-cron)
- Deployment guides (MINIKUBE_DEPLOYMENT_GUIDE.md, DEPLOYMENT_GUIDE.md)

Committed with hash `656f78c`:
```
feat(deployment-engineer): add Phase IV/V skills for deployment automation

1 file changed, 290 insertions(+)
```

## Outcome

- ✅ Impact: deployment-engineer agent updated with 4 Phase IV/V skills, comprehensive deployment automation (290 insertions)
- 🧪 Tests: Agent configuration validated, skill documentation completeness verified
- 📁 Files: 1 file modified (.claude/agents/deployment-engineer.md)
- 🔁 Next prompts: Update dapr-event-specialist agent with Phase V skills, test deployment workflow with new skills, validate Kafka provisioning on real cluster
- 🧠 Reflection: deployment-engineer now has complete Phase IV-V deployment capabilities with AI-assisted Docker optimization, Kubernetes debugging, deep troubleshooting, and Kafka provisioning. Enables systematic deployment evolution from containerization to orchestration to event-driven infrastructure while maintaining production readiness.

## Evaluation notes (flywheel)

- Failure modes observed: None - deployment-engineer update completed successfully
- Graders run and results (PASS/FAIL): Manual validation - PASS (all 4 skills properly documented, comprehensive examples with commands, clear invocation triggers)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test deployment-engineer delegation from orchestrator, validate Phase IV Docker/K8s workflow end-to-end, test Phase V Kafka deployment on Minikube then DOKS
