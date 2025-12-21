# Kafka Infrastructure Setup Guide

Complete guide for provisioning Kafka infrastructure in Kubernetes for Phase V.

## Table of Contents
- Overview
- Strimzi Setup
- Redpanda Setup
- Topic Configuration
- Health Verification
- Troubleshooting

## Overview

Phase V requires a Kafka cluster for event-driven architecture. Two options:

1. **Strimzi** - Apache Kafka on Kubernetes (mature, feature-rich)
2. **Redpanda** - Kafka-compatible, no ZooKeeper (simpler, faster)

**Recommendation for Minikube:** Strimzi with ephemeral storage (single-node)
**Recommendation for Production:** Strimzi or Redpanda with persistent storage (3-node)

## Strimzi Setup

### Architecture

```
┌─────────────────────────────────────┐
│   Strimzi Cluster Operator          │
│   (Watches Kafka CRs)                │
└──────────┬──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│   Kafka Custom Resource              │
│   - Kafka brokers (StatefulSet)      │
│   - ZooKeeper (StatefulSet)          │
│   - Entity Operator (Deployment)     │
└──────────────────────────────────────┘
```

### Deployment Steps

**1. Install Strimzi Operator**

```bash
# Create namespace
kubectl create namespace kafka

# Deploy operator
kubectl apply -f assets/strimzi/strimzi-operator.yaml -n kafka

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

**2. Deploy Kafka Cluster (Ephemeral)**

```bash
# For Minikube - single node, ephemeral storage
kubectl apply -f assets/strimzi/kafka-cluster-ephemeral.yaml -n kafka

# Wait for Kafka cluster
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=600s -n kafka
```

**3. Create Topics**

```bash
# Create KafkaTopic CRs
kubectl apply -f assets/strimzi/kafka-topics.yaml -n kafka

# Verify topics
kubectl get kafkatopics -n kafka
```

### Cluster Configuration

**Ephemeral (Minikube):**
- 1 Kafka broker
- 1 ZooKeeper node
- Ephemeral storage (data lost on restart)
- Replication factor: 1
- Resources: 1GB RAM, 500m CPU

**Persistent (Production):**
- 3 Kafka brokers
- 3 ZooKeeper nodes
- Persistent volumes (10GB per broker)
- Replication factor: 3
- Resources: 2GB RAM, 1 CPU per broker

### Bootstrap Servers

```
my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

## Redpanda Setup

### Architecture

```
┌─────────────────────────────────────┐
│   Redpanda Operator                  │
│   (Watches Cluster CRs)              │
└──────────┬──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│   Redpanda Cluster                   │
│   - Redpanda brokers (StatefulSet)   │
│   - No ZooKeeper needed              │
│   - Built-in Raft consensus          │
└──────────────────────────────────────┘
```

### Deployment Steps

**1. Install Redpanda Operator**

```bash
# Deploy operator (creates redpanda-system namespace)
kubectl apply -f assets/redpanda/redpanda-operator.yaml

# Wait for operator
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda-operator -n redpanda-system --timeout=300s
```

**2. Deploy Redpanda Cluster**

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Deploy cluster
kubectl apply -f assets/redpanda/redpanda-cluster-ephemeral.yaml -n kafka

# Wait for cluster
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n kafka --timeout=600s
```

**3. Create Topics**

```bash
# Create topics via Job
kubectl apply -f assets/redpanda/kafka-topics.yaml -n kafka

# Check job completion
kubectl wait --for=condition=complete job/create-kafka-topics -n kafka --timeout=300s
```

### Bootstrap Servers

```
my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

## Topic Configuration

### Required Topics

**1. task-events**
- Purpose: Task lifecycle events (created, updated, deleted)
- Partitions: 3
- Replication: 1 (Minikube) / 3 (Production)
- Retention: 7 days
- Compression: Producer-side

**2. reminders**
- Purpose: Scheduled task reminders
- Partitions: 3
- Replication: 1 (Minikube) / 3 (Production)
- Retention: 30 days
- Compression: Producer-side

**3. task-updates**
- Purpose: Real-time task state updates
- Partitions: 3
- Replication: 1 (Minikube) / 3 (Production)
- Retention: 7 days
- Compression: Producer-side
- Optional: Enable compaction for latest state

### Topic Naming Convention

```
{domain}-{event-type}

Examples:
- task-events
- user-events
- notification-events
```

## Health Verification

### Automated Health Check

```bash
# Run health check script
bash scripts/health_check.sh

# Expected output:
# ✅ All health checks passed!
# Bootstrap Servers: my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
# Topics: task-events, reminders, task-updates
```

### Manual Verification

**Check Kafka Pods:**

```bash
# Strimzi
kubectl get pods -n kafka -l app.kubernetes.io/name=kafka

# Redpanda
kubectl get pods -n kafka -l app.kubernetes.io/name=redpanda
```

**Check Topics (Strimzi):**

```bash
kubectl get kafkatopics -n kafka

# Expected output:
# NAME            CLUSTER      PARTITIONS   REPLICATION FACTOR   READY
# task-events     my-cluster   3            1                    True
# reminders       my-cluster   3            1                    True
# task-updates    my-cluster   3            1                    True
```

**Test Connectivity:**

```bash
# Create test pod
kubectl run kafka-test --image=confluentinc/cp-kafka:latest --rm -i -n kafka -- \
  kafka-broker-api-versions --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092

# Should show broker versions
```

**List Topics:**

```bash
# Strimzi
kubectl run kafka-test --image=confluentinc/cp-kafka:latest --rm -i -n kafka -- \
  kafka-topics --list --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092

# Redpanda
kubectl exec -n kafka my-cluster-0 -- rpk topic list
```

## Troubleshooting

### Pods Not Starting

**Symptoms:** Kafka/ZooKeeper pods in Pending or CrashLoopBackOff

**Checks:**
```bash
# Check pod status
kubectl get pods -n kafka

# Check events
kubectl get events -n kafka --sort-by='.lastTimestamp'

# Check pod logs
kubectl logs -n kafka <pod-name>
```

**Common Causes:**
- Insufficient resources (increase memory/CPU limits)
- Storage class not available (check PVCs)
- Image pull errors (check image name/registry)

**Solution:**
```bash
# Check node resources
kubectl top nodes

# Check storage classes
kubectl get storageclass

# Adjust resources in cluster YAML
```

### Topics Not Created

**Symptoms:** KafkaTopic CRs exist but topics not in Kafka

**Strimzi:**
```bash
# Check topic operator logs
kubectl logs -n kafka <cluster-name>-entity-operator -c topic-operator

# Check KafkaTopic status
kubectl get kafkatopic task-events -n kafka -o yaml
```

**Redpanda:**
```bash
# Check job logs
kubectl logs -n kafka job/create-kafka-topics

# Manually create topic
kubectl exec -n kafka my-cluster-0 -- rpk topic create task-events --partitions 3
```

### Connection Refused

**Symptoms:** Cannot connect to Kafka from pods

**Checks:**
```bash
# Check service
kubectl get svc my-cluster-kafka-bootstrap -n kafka

# Check endpoints
kubectl get endpoints my-cluster-kafka-bootstrap -n kafka

# Test DNS resolution
kubectl run dns-test --image=busybox:1.28 --rm -it -n kafka -- \
  nslookup my-cluster-kafka-bootstrap.kafka.svc.cluster.local
```

**Solution:**
- Ensure service exists and has endpoints
- Use full service name: `<service>.<namespace>.svc.cluster.local:9092`
- Check network policies if enabled

### Operator Not Running

**Symptoms:** Operator pod not starting

**Strimzi:**
```bash
# Check operator pod
kubectl get pods -n kafka -l name=strimzi-cluster-operator

# Check logs
kubectl logs -n kafka -l name=strimzi-cluster-operator

# Check RBAC
kubectl get clusterrolebinding strimzi-cluster-operator
```

**Redpanda:**
```bash
# Check operator pod
kubectl get pods -n redpanda-system -l app.kubernetes.io/name=redpanda-operator

# Check logs
kubectl logs -n redpanda-system -l app.kubernetes.io/name=redpanda-operator
```

**Solution:**
- Verify RBAC permissions
- Check operator deployment spec
- Ensure namespace exists

## Production Considerations

### High Availability

**Kafka:**
- Min 3 brokers for fault tolerance
- Replication factor: 3
- Min ISR: 2
- Multiple availability zones

**ZooKeeper:**
- Min 3 nodes
- Across availability zones
- Persistent storage

### Resource Planning

**Per Broker:**
- CPU: 2 cores minimum
- Memory: 4GB minimum (8GB recommended)
- Storage: 100GB+ (depends on retention)
- Network: 1Gbps+

### Monitoring

**Metrics to Monitor:**
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

### Backup & Recovery

**Strimzi:**
- Persistent volumes for data
- Regular snapshots of PVs
- Backup ZooKeeper data
- Test restoration procedures

**Redpanda:**
- Persistent volumes
- Raft snapshots
- Topic configuration backup

## Quick Reference

### Strimzi Commands

```bash
# Deploy
bash scripts/deploy_kafka.sh

# Health check
bash scripts/health_check.sh

# List topics
kubectl get kafkatopics -n kafka

# Describe cluster
kubectl get kafka my-cluster -n kafka -o yaml

# Check operator logs
kubectl logs -n kafka -l name=strimzi-cluster-operator
```

### Redpanda Commands

```bash
# Deploy
KAFKA_PROVIDER=redpanda bash scripts/deploy_kafka.sh

# Health check
KAFKA_PROVIDER=redpanda bash scripts/health_check.sh

# List topics
kubectl exec -n kafka my-cluster-0 -- rpk topic list

# Cluster info
kubectl exec -n kafka my-cluster-0 -- rpk cluster info
```

### Environment Variables

```bash
export KAFKA_PROVIDER=strimzi     # or redpanda
export NAMESPACE=kafka
export KAFKA_CLUSTER_NAME=my-cluster
export STORAGE_TYPE=ephemeral     # or persistent
```
