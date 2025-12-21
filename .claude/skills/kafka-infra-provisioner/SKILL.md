---
name: kafka-infra-provisioner
description: Provision Kafka infrastructure (Strimzi or Redpanda) in Kubernetes for Phase V event-driven architecture. Use when: (1) Setting up Kafka cluster in Kubernetes for the first time, (2) Deploying event bus infrastructure before Dapr configuration, (3) Creating required Kafka topics (task-events, reminders, task-updates), (4) Installing Strimzi or Redpanda operators, (5) Configuring single-node ephemeral cluster for Minikube, (6) Setting up production-ready persistent cluster, or (7) Verifying Kafka broker health and connectivity. Dapr pub/sub cannot function until this infrastructure is provisioned.
---

# Kafka Infrastructure Provisioner

Automated Kafka cluster provisioning for Phase V event-driven architecture using Strimzi or Redpanda.

## Overview

This skill provides complete Kafka infrastructure setup in Kubernetes. Supports both Strimzi (Apache Kafka) and Redpanda (Kafka-compatible without ZooKeeper).

**Key Features:**
- Automated deployment scripts for Strimzi or Redpanda
- Single-node ephemeral cluster for Minikube
- Production-ready persistent cluster configurations
- Required topic creation (task-events, reminders, task-updates)
- Health check verification
- Bootstrap server configuration for Dapr

**Phase V Requirement:** Kafka infrastructure MUST be provisioned before Dapr pub/sub can function.

## Quick Start

### Option 1: Strimzi (Recommended for Minikube)

```bash
# Deploy Strimzi with ephemeral storage
bash scripts/deploy_kafka.sh

# Verify deployment
bash scripts/health_check.sh

# Bootstrap servers ready at:
# my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

### Option 2: Redpanda (Alternative)

```bash
# Deploy Redpanda
KAFKA_PROVIDER=redpanda bash scripts/deploy_kafka.sh

# Verify deployment
KAFKA_PROVIDER=redpanda bash scripts/health_check.sh
```

## Core Workflows

### Workflow 1: Initial Kafka Setup (Minikube)

Deploy single-node Kafka cluster with ephemeral storage:

```bash
# 1. Deploy Kafka infrastructure
cd .claude/skills/kafka-infra-provisioner
bash scripts/deploy_kafka.sh

# The script will:
# - Create kafka namespace
# - Deploy Strimzi operator
# - Deploy single-node Kafka cluster (ephemeral)
# - Create topics: task-events, reminders, task-updates
# - Run health verification

# 2. Verify deployment
bash scripts/health_check.sh

# Expected output:
# ✅ All health checks passed!
# Bootstrap Servers: my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
# Topics: task-events, reminders, task-updates
```

### Workflow 2: Production Cluster Setup

Deploy 3-node Kafka cluster with persistent storage:

```bash
# Set storage type to persistent
export STORAGE_TYPE=persistent

# Deploy cluster
bash scripts/deploy_kafka.sh

# This creates:
# - 3 Kafka brokers with persistent volumes
# - 3 ZooKeeper nodes (Strimzi only)
# - Replication factor: 3
# - Min ISR: 2
```

### Workflow 3: Manual Operator Installation

Step-by-step installation:

```bash
# 1. Create namespace
kubectl create namespace kafka

# 2. Deploy Strimzi operator
kubectl apply -f assets/strimzi/strimzi-operator.yaml -n kafka

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# 3. Deploy Kafka cluster
kubectl apply -f assets/strimzi/kafka-cluster-ephemeral.yaml -n kafka

# Wait for cluster
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=600s -n kafka

# 4. Create topics
kubectl apply -f assets/strimzi/kafka-topics.yaml -n kafka
```

### Workflow 4: Health Verification

Verify Kafka infrastructure is ready:

```bash
# Run automated health check
bash scripts/health_check.sh

# Manual checks
kubectl get pods -n kafka
kubectl get kafkatopics -n kafka
kubectl get svc my-cluster-kafka-bootstrap -n kafka

# Test connectivity
kubectl run kafka-test --image=confluentinc/cp-kafka:latest --rm -i -n kafka -- \
  kafka-broker-api-versions --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

## Bundled Resources

### Scripts

**`scripts/deploy_kafka.sh`**
- Complete deployment automation
- Supports Strimzi and Redpanda
- Environment variable configuration
- Health verification

**`scripts/health_check.sh`**
- Automated health checks
- Verifies pods, services, topics
- Bootstrap server validation
- Connectivity testing

### Assets

**Strimzi (`assets/strimzi/`)**:

1. **`strimzi-operator.yaml`**
   - Operator deployment with RBAC
   - ServiceAccount, ClusterRole, ClusterRoleBinding
   - ConfigMap for logging

2. **`kafka-cluster-ephemeral.yaml`**
   - Single-node Kafka cluster
   - Ephemeral storage (Minikube)
   - 1GB RAM, 500m CPU
   - Replication factor: 1

3. **`kafka-cluster-persistent.yaml`**
   - 3-node Kafka cluster
   - Persistent volumes (10GB per broker)
   - 2GB RAM, 1 CPU per broker
   - Replication factor: 3, Min ISR: 2

4. **`kafka-topics.yaml`**
   - KafkaTopic CRs for task-events, reminders, task-updates
   - 3 partitions per topic
   - Retention: 7-30 days
   - Compression enabled

**Redpanda (`assets/redpanda/`)**:

1. **`redpanda-operator.yaml`**
   - Operator deployment
   - RBAC configuration

2. **`redpanda-cluster-ephemeral.yaml`**
   - Single-node Redpanda cluster
   - Developer mode enabled
   - 1GB RAM, 500m CPU

3. **`redpanda-cluster-persistent.yaml`**
   - 3-node Redpanda cluster
   - Production configuration
   - 2GB RAM, 1 CPU per node

4. **`kafka-topics.yaml`**
   - Job-based topic creation
   - Uses `rpk topic create` commands
   - 3 topics with configuration

### References

**`references/kafka-setup-guide.md`**
- Complete setup guide
- Strimzi vs Redpanda comparison
- Topic configuration details
- Troubleshooting guide
- Production considerations

## Configuration

### Environment Variables

```bash
# Provider selection
export KAFKA_PROVIDER=strimzi        # or redpanda

# Deployment configuration
export NAMESPACE=kafka
export KAFKA_CLUSTER_NAME=my-cluster
export STORAGE_TYPE=ephemeral        # or persistent
```

### Bootstrap Servers

**For Dapr pub/sub component:**

```yaml
metadata:
  - name: brokers
    value: "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
```

**Full service name:**
```
my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

## Topics

### task-events

**Purpose:** Task lifecycle events (created, updated, deleted, completed)

**Configuration:**
- Partitions: 3
- Replication: 1 (Minikube) / 3 (Production)
- Retention: 7 days
- Compression: Producer-side
- Cleanup policy: Delete

**Use Case:** Publish events when tasks are modified for analytics, audit logs, or downstream processing.

### reminders

**Purpose:** Scheduled task reminder events

**Configuration:**
- Partitions: 3
- Replication: 1 (Minikube) / 3 (Production)
- Retention: 30 days
- Compression: Producer-side
- Cleanup policy: Delete

**Use Case:** Store reminder notifications triggered by Dapr Jobs API for delivery to users.

### task-updates

**Purpose:** Real-time task state updates

**Configuration:**
- Partitions: 3
- Replication: 1 (Minikube) / 3 (Production)
- Retention: 7 days
- Compression: Producer-side
- Cleanup policy: Delete (or compact for latest state)

**Use Case:** Broadcast task changes to frontend clients via SSE or WebSocket for real-time UI updates.

## Strimzi vs Redpanda

### Strimzi

**Pros:**
- Mature, production-ready
- Full Apache Kafka features
- Excellent operator with auto-scaling
- Rich ecosystem (connectors, monitoring)

**Cons:**
- Requires ZooKeeper (more resources)
- Slower startup time
- More complex architecture

**Recommended for:** Production deployments, large-scale systems

### Redpanda

**Pros:**
- No ZooKeeper needed
- Faster startup and performance
- Lower resource usage
- Simpler architecture

**Cons:**
- Newer project (less mature)
- Fewer ecosystem integrations
- Limited community support

**Recommended for:** Development, Minikube, lightweight deployments

## Troubleshooting

### Pods Not Starting

**Symptoms:** Kafka/ZooKeeper pods in Pending or CrashLoopBackOff

**Checks:**
```bash
kubectl get pods -n kafka
kubectl get events -n kafka --sort-by='.lastTimestamp'
kubectl logs -n kafka <pod-name>
```

**Common Causes:**
- Insufficient resources
- Storage class not available
- Image pull errors

**Solution:** Check node resources, storage classes, adjust YAML

### Topics Not Created

**Strimzi:**
```bash
# Check topic operator logs
kubectl logs -n kafka <cluster>-entity-operator -c topic-operator

# Check KafkaTopic status
kubectl get kafkatopic task-events -n kafka -o yaml
```

**Redpanda:**
```bash
# Check job logs
kubectl logs -n kafka job/create-kafka-topics

# Manually create
kubectl exec -n kafka my-cluster-0 -- rpk topic create task-events --partitions 3
```

### Connection Refused

**Checks:**
```bash
kubectl get svc my-cluster-kafka-bootstrap -n kafka
kubectl get endpoints my-cluster-kafka-bootstrap -n kafka
```

**Solution:** Ensure service exists, use full DNS name, check network policies

## Testing

### Manual Topic Creation

```bash
# Strimzi - create KafkaTopic CR
kubectl apply -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: test-topic
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 1
  replicas: 1
EOF

# Redpanda - exec into pod
kubectl exec -n kafka my-cluster-0 -- \
  rpk topic create test-topic --partitions 1
```

### Produce/Consume Test

```bash
# Producer
kubectl run kafka-producer --image=confluentinc/cp-kafka:latest -it --rm -n kafka -- \
  kafka-console-producer --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic task-events

# Consumer (separate terminal)
kubectl run kafka-consumer --image=confluentinc/cp-kafka:latest -it --rm -n kafka -- \
  kafka-console-consumer --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic task-events --from-beginning
```

## Integration with Dapr

After Kafka is provisioned, configure Dapr pub/sub:

```yaml
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
    - name: clientId
      value: "todo-app-client"
```

See `dapr-event-flow` skill for complete Dapr integration.

## Production Recommendations

### High Availability

- Min 3 Kafka brokers
- Min 3 ZooKeeper nodes (Strimzi)
- Replication factor: 3
- Min ISR: 2
- Across availability zones

### Resources

**Per Broker:**
- CPU: 2 cores minimum
- Memory: 4GB minimum (8GB recommended)
- Storage: 100GB+
- Network: 1Gbps+

### Monitoring

**Metrics:**
- Under-replicated partitions
- ISR shrink rate
- Leader election rate
- Request latency (p99)
- Disk usage
- Network throughput

**Tools:**
- Prometheus + Grafana
- Strimzi Kafka Exporter
- Redpanda Metrics

## Advanced Features

### Custom Topic Configuration

Edit `kafka-topics.yaml` to add custom topics:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: custom-topic
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 604800000
    compression.type: lz4
    cleanup.policy: compact
```

### External Access

For external client access (outside Kubernetes):

```yaml
# Add to Kafka CR
listeners:
  - name: external
    port: 9094
    type: loadbalancer
    tls: true
```

## Reference Documentation

For detailed information:
- **Setup Guide**: See `references/kafka-setup-guide.md` for complete Strimzi/Redpanda setup instructions
- **Strimzi Docs**: https://strimzi.io/docs/
- **Redpanda Docs**: https://docs.redpanda.com/

## Phase V Compliance

✅ **Kafka First:** Infrastructure must be provisioned before Dapr
✅ **Required Topics:** task-events, reminders, task-updates created
✅ **Health Checks:** Automated verification scripts
✅ **Minikube Ready:** Single-node ephemeral configuration
✅ **Production Ready:** 3-node persistent configuration available
✅ **Bootstrap Configuration:** Service endpoints for Dapr integration
✅ **Event-Driven:** Enables Phase V pub/sub architecture
