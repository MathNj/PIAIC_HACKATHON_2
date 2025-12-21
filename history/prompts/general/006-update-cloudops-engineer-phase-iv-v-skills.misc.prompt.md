---
id: 006
title: Update cloudops-engineer agent with Phase IV/V skills
stage: misc
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Najma-LP
command: agent-update
labels: ["cloudops-engineer", "agent-configuration", "phase-iv", "phase-v", "skills", "docker", "kubernetes", "kafka"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/cloudops-engineer.md
tests:
  - cloudops-engineer agent configuration validation
  - Skill documentation completeness check
---

## Prompt

update cloudops-engineer agent

## Response snapshot

Successfully updated the cloudops-engineer agent configuration with all Phase IV and Phase V infrastructure skills.

**Skills Added:**

**Phase IV - Containerization & Orchestration:**

1. **docker-ai-pilot**
   - AI-assisted Docker container management and optimization
   - When to invoke:
     * "AI help with Docker" or "optimize my Dockerfiles"
     * Build and manage Docker images for multiple services
     * Troubleshoot Docker build failures
     * Implement advanced Docker features (BuildKit, multi-platform)
     * Security scanning and image hardening
   - What it provides:
     * AI-assisted Dockerfile analysis and optimization
     * Multi-stage build creation with intelligent layer caching
     * Security hardening (non-root, trivy/docker scout scanning)
     * BuildKit features (cache/secret/SSH mounts)
     * Image size optimization (87% reduction target)
     * Production templates (FastAPI ~150MB, Next.js ~180MB)
     * Health check configuration
     * Metadata label best practices
     * `.dockerignore` optimization
     * Build and push automation scripts

2. **kubectl-ai-pilot**
   - AI-assisted Kubernetes cluster operations and debugging
   - When to invoke:
     * "Help with Kubernetes" or "debug K8s cluster"
     * Managing Kubernetes resources (pods, deployments, services)
     * Troubleshooting cluster issues
     * Inspecting resource configurations
     * Scaling and updating deployments
   - What it provides:
     * Cluster resource inspection and management
     * Pod troubleshooting (CrashLoopBackOff, ImagePullBackOff, resource limits)
     * Service connectivity debugging
     * Log aggregation and analysis
     * Resource quota and limit management
     * Deployment scaling and rolling updates
     * ConfigMap and Secret management
     * Ingress configuration and debugging
     * Network policy validation
     * Health check and liveness probe configuration

**Phase V - Event-Driven Architecture:**

3. **kafka-infra-provisioner**
   - Kafka cluster provisioning automation (Strimzi/Redpanda)
   - When to invoke:
     * "Deploy Kafka" or "set up event infrastructure"
     * Provision Kafka cluster for Phase V
     * Set up event streaming backbone
     * Configure Kafka topics for microservices
     * Dapr pub/sub integration with Kafka
   - What it provides:
     * Dual provider support (Strimzi - Apache Kafka v3.6.0, Redpanda - Kafka-compatible)
     * Automated deployment scripts (deploy_kafka.sh, health_check.sh)
     * Cluster configurations:
       - Single-node ephemeral for Minikube (1GB RAM)
       - 3-node persistent for production (2GB RAM per broker)
     * Kubernetes manifests (operator, cluster CRs, topics)
     * Topic configuration (partitions, replicas, retention, compression)
     * Health checks (pods, services, topics)
     * Bootstrap server endpoints for Dapr integration
     * Comprehensive setup and troubleshooting docs
   - Example usage:
     ```bash
     # Deploy Strimzi with ephemeral storage (Minikube)
     cd .claude/skills/kafka-infra-provisioner
     bash scripts/deploy_kafka.sh

     # Deploy Redpanda in production
     KAFKA_PROVIDER=redpanda STORAGE_TYPE=persistent bash scripts/deploy_kafka.sh
     ```

4. **blueprint-architect**
   - Cloud-native architectural pattern extraction and productization
   - When to invoke:
     * "Extract architecture patterns" or "create blueprint"
     * Productize project architecture for reuse
     * Document cloud-native patterns
     * Create deployment templates for other teams
     * Claim bonus points for cloud-native blueprints
   - What it provides:
     * Project structure analysis:
       - Backend features (FastAPI, JWT Auth, SQLModel, MCP Tools)
       - Frontend features (Next.js, ChatKit, i18n, Voice Input)
       - Infrastructure (Helm charts, K8s manifests, Dapr components)
       - Event-driven components (Kafka, Dapr pub/sub, Jobs API)
     * Blueprint generation script (generate_blueprint.py)
     * Blueprint output structure:
       ```
       blueprints/<name>/
       ├── infrastructure/ (helm, kubernetes, dapr)
       ├── specs/ (feature-template.md)
       ├── BLUEPRINT.md
       └── blueprint.json
       ```
     * BLUEPRINT.md documentation:
       - Architecture overview, technology stack, use cases
       - Step-by-step deployment guide
       - Configuration options, customization guide
       - Troubleshooting, production checklist
     * Architectural pattern documentation:
       - Microservices Stack (FastAPI + Next.js + Dapr + Kafka)
       - Event-Driven Architecture, AI Agent patterns
       - Authentication patterns
   - Example usage:
     ```bash
     python scripts/generate_blueprint.py \
       --project-root . \
       --name "fastapi-nextjs-dapr-stack" \
       --description "Full-stack microservices with event-driven architecture" \
       --use-cases \
         "Task management applications" \
         "CRM systems" \
         "Project management tools"
     ```

**Existing Skills Retained:**
- k8s-deployer (deployment configurations)
- k8s-troubleshoot (pod troubleshooting)
- dapr-event-flow (pub/sub automation)
- dockerfile-optimizer (Dockerfile optimization)

**Agent Capabilities Enhanced:**

The cloudops-engineer agent now supports:
1. **Phase IV Microservices**: Complete containerization with AI-assisted optimization and Kubernetes orchestration with intelligent debugging
2. **Phase V Event-Driven**: Full Kafka infrastructure provisioning with dual provider support and cloud-native blueprint extraction for architectural reuse
3. **Cross-Phase Infrastructure**: Comprehensive tooling from Docker to Kubernetes to Kafka with production-ready configurations and deployment automation

**Documentation Quality:**

All skills include:
- Clear "When to invoke" triggers for proper agent delegation
- Comprehensive "What it provides" lists (10+ capabilities each)
- Example usage with bash commands and expected outputs
- Integration guidance with existing Phase II/III systems

Committed with hash `fba102a`:
```
feat(cloudops-engineer): add Phase IV/V skills for infrastructure automation

1 file changed, 163 insertions(+)
```

## Outcome

- ✅ Impact: cloudops-engineer agent updated with 4 Phase IV/V skills, comprehensive infrastructure automation capabilities (163 insertions)
- 🧪 Tests: Agent configuration validated, skill documentation completeness verified
- 📁 Files: 1 file modified (.claude/agents/cloudops-engineer.md)
- 🔁 Next prompts: Update deployment-engineer agent with Phase IV/V skills, test cloudops-engineer skill invocation patterns, validate infrastructure workflow orchestration
- 🧠 Reflection: cloudops-engineer now has complete Phase IV-V infrastructure capabilities with Docker AI assistance, Kubernetes AI operations, Kafka provisioning, and blueprint extraction. Enables systematic infrastructure evolution while maintaining phase discipline and production readiness.

## Evaluation notes (flywheel)

- Failure modes observed: None - cloudops-engineer update completed successfully
- Graders run and results (PASS/FAIL): Manual validation - PASS (all skills properly documented, comprehensive examples, clear invocation triggers)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test cloudops-engineer delegation from orchestrator, validate Phase IV Docker/K8s workflow, test Phase V Kafka deployment with real cluster
