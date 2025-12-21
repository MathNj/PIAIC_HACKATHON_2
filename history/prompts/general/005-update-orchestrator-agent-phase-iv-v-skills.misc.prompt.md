---
id: 005
title: Update orchestrator agent with Phase IV/V skills
stage: misc
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Najma-LP
command: agent-update
labels: ["orchestrator", "agent-configuration", "phase-iv", "phase-v", "skills", "workflow-patterns"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/orchestrator.md
tests:
  - Orchestrator agent configuration validation
  - Skill categorization verification (Phase III, IV, V)
---

## Prompt

Update orchestrator agent by adding new skill in its subagents and necessary changes

## Response snapshot

Successfully updated the orchestrator agent configuration to include all newly created Phase IV and Phase V infrastructure skills.

**Changes to Available Specialist Agents:**

1. **cloudops-engineer** - Updated with Phase IV/V skills:
   - Phase IV Skills: docker-ai-pilot, kubectl-ai-pilot
   - Phase V Skills: kafka-infra-provisioner, blueprint-architect
   - General Skills: k8s-deployer, k8s-troubleshoot, dapr-event-flow, dockerfile-optimizer

2. **deployment-engineer** - Updated with Phase IV/V skills:
   - Phase IV Skills: docker-ai-pilot, kubectl-ai-pilot, kagent-debugger
   - Phase V Skills: kafka-infra-provisioner
   - General Skills: k8s-deployer, k8s-troubleshoot, dapr-event-flow, deployment-validator, dockerfile-optimizer

3. **dapr-event-specialist** - Updated with Phase V skills:
   - Phase V Skills: dapr-scheduler, kafka-infra-provisioner
   - General Skills: dapr-event-flow

4. **architect** - Updated with Phase V skills:
   - Phase V Skills: blueprint-architect
   - General Skills: spec-architect, architecture-planner, adr-generator

**Updated "When to use" Sections:**

**cloudops-engineer:**
- Added: Phase IV - Optimizing Docker images with docker-ai-pilot
- Added: Phase IV - Managing Kubernetes cluster with kubectl-ai-pilot
- Added: Phase V - Provisioning Kafka infrastructure with kafka-infra-provisioner
- Added: Phase V - Extracting cloud-native blueprints with blueprint-architect

**deployment-engineer:**
- Added: Phase IV - Debugging Kubernetes agents with kagent-debugger
- Added: Phase IV - AI-assisted cluster operations with kubectl-ai-pilot
- Added: Phase IV - Docker container optimization with docker-ai-pilot
- Added: Phase V - Deploying Kafka clusters with kafka-infra-provisioner

**architect:**
- Added: Phase V - Extracting cloud-native blueprints with blueprint-architect
- Added: Phase V - Productizing architectural patterns for reuse

**dapr-event-specialist:**
- Added: Phase V - Scheduling exact-time jobs with dapr-scheduler
- Added: Phase V - Provisioning Kafka infrastructure with kafka-infra-provisioner
- Added: Phase V - Implementing task reminders with Dapr Jobs API

**New Workflow Patterns Added:**

**Pattern 12: Kubernetes Cluster Operations (Phase IV)**
- deployment-engineer (kubectl-ai-pilot): Inspect cluster resources
- deployment-engineer (kagent-debugger): Diagnose pod failures
- cloudops-engineer (kubectl-ai-pilot): Apply configuration changes
- deployment-engineer (deployment-validator): Validate deployment health

**Pattern 13: Docker Image Optimization (Phase IV)**
- cloudops-engineer (docker-ai-pilot): Analyze and optimize Dockerfiles
- deployment-engineer (docker-ai-pilot): Build and scan optimized images
- Parallel optimization for multiple services
- Target: FastAPI ~150MB, Next.js ~180MB

**Pattern 14: Kafka Infrastructure Provisioning (Phase V)**
- cloudops-engineer (kafka-infra-provisioner): Deploy Kafka cluster
- deployment-engineer (kafka-infra-provisioner): Run health checks
- dapr-event-specialist (kafka-infra-provisioner): Configure Dapr pub/sub
- deployment-engineer (deployment-validator): Validate cluster health

**Pattern 15: Dapr Job Scheduling (Phase V)**
- dapr-event-specialist (dapr-scheduler): Deploy job scheduler component
- backend-specialist (dapr-scheduler): Implement scheduling endpoints
- backend-specialist (dapr-scheduler): Implement job management endpoints
- dapr-event-specialist: Test exact-time scheduling and validation

**Pattern 16: Cloud-Native Blueprint Extraction (Phase V)**
- architect (blueprint-architect): Analyze project structure
- cloudops-engineer (blueprint-architect): Generate blueprint
- architect (blueprint-architect): Review BLUEPRINT.md
- Test blueprint deployment and package for distribution

**Pattern 17: Full Phase IV Transition (Microservices)**
- architect (architecture-planner): Design microservices decomposition
- Parallel: Extract services (Task, User, Agent)
- cloudops-engineer (docker-ai-pilot): Create optimized Dockerfiles
- cloudops-engineer (kubectl-ai-pilot): Create K8s manifests and Helm charts
- deployment-engineer (docker-ai-pilot): Build and push images
- deployment-engineer (kubectl-ai-pilot): Deploy services
- deployment-engineer (kagent-debugger): Monitor and debug
- deployment-engineer (deployment-validator): Validate all services

**Pattern 18: Full Phase V Transition (Event-Driven)**
- architect (architecture-planner): Design event-driven architecture
- cloudops-engineer (kafka-infra-provisioner): Deploy Kafka cluster
- dapr-event-specialist (kafka-infra-provisioner): Configure Dapr pub/sub
- dapr-event-specialist (dapr-scheduler): Deploy job scheduler
- backend-specialist (dapr-event-flow): Implement event publishers/subscribers
- deployment-engineer (deployment-validator): Validate event flow
- architect (blueprint-architect): Extract cloud-native blueprint

**Skills Categorization:**

All skills now properly categorized by phase:
- **Phase III Skills**: AI Agent Infrastructure (chatkit-integrator, openai-agents-sdk, mcp-tool-maker, etc.)
- **Phase IV Skills**: Containerization & Orchestration (docker-ai-pilot, kubectl-ai-pilot, kagent-debugger)
- **Phase V Skills**: Event-Driven Architecture (dapr-scheduler, kafka-infra-provisioner, blueprint-architect)
- **General Skills**: Cross-phase utilities (backend-scaffolder, crud-builder, api-schema-sync, etc.)

**Governance Impact:**

The orchestrator agent now has complete visibility into all Phase III, IV, and V skills, enabling it to:
1. Properly delegate tasks to specialist agents with appropriate skills
2. Coordinate multi-phase workflows (Phase III → IV → V transitions)
3. Follow phase discipline (not prematurely using Phase IV/V skills in Phase III)
4. Maximize parallelism across independent tasks
5. Ensure quality through proper agent selection and workflow patterns

Committed with hash `dc919b7`:
```
feat(orchestrator): add Phase IV/V skills to agent configuration

1 file changed, 217 insertions(+), 5 deletions(-)
```

## Outcome

- ✅ Impact: Orchestrator agent updated with 10 Phase IV/V skills across 4 specialist agents, 7 new workflow patterns added (217 insertions, 5 deletions)
- 🧪 Tests: Orchestrator configuration validated, skill categorization verified
- 📁 Files: 1 file modified (.claude/agents/orchestrator.md)
- 🔁 Next prompts: Test orchestrator with Phase IV deployment workflow, validate Phase V event-driven pattern orchestration, create orchestrator integration tests
- 🧠 Reflection: Orchestrator now has comprehensive Phase III-V skill awareness with clear workflow patterns for containerization, Kubernetes operations, Kafka provisioning, job scheduling, and blueprint extraction. Enables systematic multi-phase transitions while maintaining phase discipline.

## Evaluation notes (flywheel)

- Failure modes observed: None - orchestrator update completed successfully
- Graders run and results (PASS/FAIL): Manual validation - PASS (all skills categorized by phase, workflow patterns comprehensive, "When to use" sections updated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test orchestrator delegation to Phase IV/V skills, validate parallel execution of infrastructure workflows, document orchestrator decision-making patterns in ADR
