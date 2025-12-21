---
id: 003
title: Create kafka-infra-provisioner skill for Phase V
stage: misc
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Najma-LP
command: skill-creator
labels: ["skills", "phase-v", "kafka", "strimzi", "redpanda", "infrastructure", "event-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/kafka-infra-provisioner.skill
  - .claude/skills/kafka-infra-provisioner/SKILL.md
  - .claude/skills/kafka-infra-provisioner/scripts/deploy_kafka.sh
  - .claude/skills/kafka-infra-provisioner/scripts/health_check.sh
  - .claude/skills/kafka-infra-provisioner/assets/strimzi/strimzi-operator.yaml
  - .claude/skills/kafka-infra-provisioner/assets/strimzi/kafka-cluster-ephemeral.yaml
  - .claude/skills/kafka-infra-provisioner/assets/strimzi/kafka-cluster-persistent.yaml
  - .claude/skills/kafka-infra-provisioner/assets/strimzi/kafka-topics.yaml
  - .claude/skills/kafka-infra-provisioner/assets/redpanda/redpanda-operator.yaml
  - .claude/skills/kafka-infra-provisioner/assets/redpanda/redpanda-cluster-ephemeral.yaml
  - .claude/skills/kafka-infra-provisioner/assets/redpanda/redpanda-cluster-persistent.yaml
  - .claude/skills/kafka-infra-provisioner/assets/redpanda/kafka-topics.yaml
  - .claude/skills/kafka-infra-provisioner/references/kafka-setup-guide.md
tests:
  - Bash script syntax validation (deploy_kafka.sh, health_check.sh)
  - Skill package created successfully (18KB)
---

## Prompt

Skill: kafka-infra-provisioner (Phase V Infrastructure)

Use the skill-creator to generate a skill called kafka-infra-provisioner.

Context: Phase V requires a Kafka cluster (Self-hosted Strimzi or Redpanda) within Kubernetes. Dapr cannot function until this infrastructure is provisioned.

Process:
1. Generate the Kubernetes manifests to install the Strimzi Operator or Redpanda Operator.
2. Create the Kafka Custom Resource (CR) YAML to spin up a single-node cluster (ephemeral storage for Minikube).
3. Create KafkaTopic CRs for the required topics: task-events, reminders, task-updates.
4. Include a health check command to verify the brokers are ready.

Goal: Generate the kafka-infra-provisioner.skill file to set up the event bus infrastructure.

## Response snapshot

Successfully created the `kafka-infra-provisioner` skill (18KB) following the Skill Creation Process.

**Deployment Scripts (Bash):**

1. **`deploy_kafka.sh`** (5.0KB)
   - Automated deployment for Strimzi or Redpanda
   - Environment variable configuration (KAFKA_PROVIDER, NAMESPACE, STORAGE_TYPE)
   - Deployment workflow:
     - Check prerequisites (kubectl, cluster connectivity)
     - Create namespace
     - Deploy operator (Strimzi or Redpanda)
     - Deploy Kafka cluster (ephemeral or persistent)
     - Create topics
     - Verify deployment
   - Color-coded logging (INFO, WARN, ERROR)
   - Prints bootstrap servers on success

2. **`health_check.sh`** (6.6KB)
   - Comprehensive health verification
   - Checks:
     - Namespace exists
     - Kafka pods running and ready
     - ZooKeeper pods ready (Strimzi only)
     - Kafka service accessible
     - Topics created and ready
     - Optional connectivity test
   - Prints cluster information on success
   - Exit code 0 on success, 1 on failure

**Strimzi Assets (Kubernetes YAML):**

3. **`strimzi-operator.yaml`** (3.8KB)
   - ServiceAccount, ClusterRole, ClusterRoleBinding
   - Deployment with Strimzi operator v0.38.0
   - ConfigMap for logging configuration
   - Resource limits: 1 CPU, 384Mi RAM
   - Liveness and readiness probes

4. **`kafka-cluster-ephemeral.yaml`** (2.4KB)
   - Single-node Kafka cluster (Kafka v3.6.0)
   - Ephemeral storage (data lost on restart)
   - Listeners: plain (9092), tls (9093)
   - Replication factor: 1
   - Resources: 1Gi RAM, 500m-1000m CPU
   - Single ZooKeeper node: 512Mi RAM, 250m-500m CPU
   - Entity operator (topic + user): 256Mi each
   - JMX Prometheus exporter for metrics

5. **`kafka-cluster-persistent.yaml`** (2.7KB)
   - 3-node Kafka cluster
   - Persistent volumes (10Gi per broker, JBOD storage)
   - Replication factor: 3, Min ISR: 2
   - Resources: 2Gi RAM, 1-2 CPU per broker
   - 3 ZooKeeper nodes: 1Gi RAM, 500m-1000m CPU each
   - Production optimizations (auto.create.topics.enable: false)
   - Persistent storage with deleteClaim: false

6. **`kafka-topics.yaml`** (1.1KB)
   - KafkaTopic CRs for Strimzi:
     - task-events: 3 partitions, 1 replica, 7 days retention
     - reminders: 3 partitions, 1 replica, 30 days retention
     - task-updates: 3 partitions, 1 replica, 7 days retention
   - Configuration: compression.type=producer, cleanup.policy=delete
   - Label: strimzi.io/cluster=my-cluster

**Redpanda Assets (Kubernetes YAML):**

7. **`redpanda-operator.yaml`** (1.9KB)
   - Namespace: redpanda-system
   - ServiceAccount, ClusterRole, ClusterRoleBinding
   - Deployment with Redpanda operator v23.2.1
   - Resource limits: 500m CPU, 256Mi RAM

8. **`redpanda-cluster-ephemeral.yaml`** (0.7KB)
   - Single-node Redpanda cluster
   - Redpanda v23.2.1
   - Resources: 1Gi RAM, 500m-1000m CPU
   - Storage: 10Gi (ephemeral with default storage class)
   - Developer mode enabled for Minikube
   - Ports: RPC (33145), Kafka API (9092), Pandaproxy (8082), Schema Registry (8081), Admin API (9644)

9. **`redpanda-cluster-persistent.yaml`** (0.8KB)
   - 3-node Redpanda cluster
   - Production mode (developerMode: false)
   - Resources: 2Gi RAM, 1-2 CPU per node
   - Persistent storage: 50Gi with standard storage class
   - Tolerations for dedicated node scheduling

10. **`kafka-topics.yaml`** (2.1KB)
    - Kubernetes Job for topic creation
    - Uses `rpk topic create` commands
    - Creates task-events, reminders, task-updates
    - Waits for Kafka to be ready with retry loop
    - Topic configuration:
      - retention.ms: 604800000 (7 days) or 2592000000 (30 days)
      - compression.type: producer
      - cleanup.policy: delete

**References (Documentation):**

11. **`kafka-setup-guide.md`** (10.6KB)
    - Complete setup guide for Strimzi and Redpanda
    - Architecture diagrams
    - Deployment steps with commands
    - Topic configuration details
    - Health verification procedures
    - Troubleshooting guide:
      - Pods not starting
      - Topics not created
      - Connection refused
      - Operator not running
    - Production considerations:
      - High availability (min 3 brokers)
      - Resource planning (2 CPU, 4GB RAM per broker)
      - Monitoring metrics (under-replicated partitions, ISR shrink rate, latency)
      - Backup & recovery strategies
    - Quick reference commands

12. **`SKILL.md`** (12.2KB)
    - Complete skill documentation with frontmatter
    - Quick start for Strimzi and Redpanda
    - 4 core workflows:
      - Initial Kafka setup (Minikube)
      - Production cluster setup
      - Manual operator installation
      - Health verification
    - Topic descriptions with use cases
    - Strimzi vs Redpanda comparison
    - Troubleshooting guide
    - Integration with Dapr pub/sub
    - Production recommendations
    - Advanced features (custom topics, external access)

**Key Features:**

✅ **Dual Provider Support** - Strimzi (Apache Kafka) or Redpanda (Kafka-compatible)
✅ **Automated Deployment** - Single script deploys entire cluster
✅ **Minikube Ready** - Single-node ephemeral configuration (1GB RAM)
✅ **Production Ready** - 3-node persistent configuration (2GB RAM per broker)
✅ **Required Topics** - task-events, reminders, task-updates created automatically
✅ **Health Verification** - Comprehensive checks for pods, services, topics
✅ **Bootstrap Configuration** - Service endpoints ready for Dapr integration
✅ **Phase V Compliant** - Infrastructure provisioned before Dapr deployment

**Usage Example:**

```bash
# Deploy Strimzi with ephemeral storage (Minikube)
cd .claude/skills/kafka-infra-provisioner
bash scripts/deploy_kafka.sh

# Verify deployment
bash scripts/health_check.sh

# Expected output:
# ✅ All health checks passed!
# Bootstrap Servers: my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
# Topics: task-events, reminders, task-updates

# Alternative: Deploy Redpanda
KAFKA_PROVIDER=redpanda bash scripts/deploy_kafka.sh

# Production deployment with persistent storage
STORAGE_TYPE=persistent bash scripts/deploy_kafka.sh
```

**Dapr Integration:**

```yaml
# Configure Dapr pub/sub component after Kafka is ready
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app"
```

Committed with hash `4bfcaf3`:
```
feat(skills): add kafka-infra-provisioner for Phase V event infrastructure

13 files changed, 2,015 insertions(+)
```

## Outcome

- ✅ Impact: Created production-ready Kafka infrastructure provisioning skill for Phase V event-driven architecture (18KB, 13 files, 2,015 insertions)
- 🧪 Tests: Bash script syntax validation passed for deploy_kafka.sh and health_check.sh
- 📁 Files: 13 files created (1 .skill package, 2 scripts, 8 YAML manifests, 1 reference, 1 SKILL.md)
- 🔁 Next prompts: Deploy Kafka infrastructure to Minikube, configure Dapr pub/sub component, test event publishing
- 🧠 Reflection: Skill provides complete Kafka setup with dual provider support (Strimzi/Redpanda), automated deployment scripts, health verification, and production-ready configurations. Enables Phase V event-driven architecture as prerequisite for Dapr pub/sub.

## Evaluation notes (flywheel)

- Failure modes observed: None - all scripts validated, skill packaged successfully
- Graders run and results (PASS/FAIL): Manual validation - PASS (proper YAML frontmatter, comprehensive description, complete bundled resources, SKILL.md under 500 lines)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test kafka-infra-provisioner in actual Minikube deployment, verify topic creation, integrate with Dapr pub/sub component
