# Phase 5: Quickstart Guide - Cloud Deployment

**Branch**: `005-phase-5` | **Date**: 2025-12-11
**Phase**: Phase 1 - Design & Contracts
**Purpose**: Developer onboarding guide for Phase 5 cloud deployment to DOKS

---

## Overview

This quickstart guide walks you through deploying the Todo App to **DigitalOcean Kubernetes Service (DOKS)** with:
- **Dapr 1.13.0+** for service mesh (pub/sub, state store)
- **Redpanda Cloud** (AWS us-east-1) for event streaming with SASL/SCRAM-SHA-256
- **DigitalOcean Managed Redis** for state storage with TLS
- **Helm charts** for declarative Kubernetes deployment

**Estimated Time**: 90-120 minutes (first-time setup)

---

## Prerequisites

### Required Tools

Install the following CLI tools before starting:

```bash
# 1. kubectl (Kubernetes CLI)
# Download from: https://kubernetes.io/docs/tasks/tools/
kubectl version --client

# 2. doctl (DigitalOcean CLI)
# Download from: https://docs.digitalocean.com/reference/doctl/how-to/install/
doctl version

# 3. Dapr CLI
# Download from: https://docs.dapr.io/getting-started/install-dapr-cli/
dapr version

# 4. Helm (Kubernetes package manager)
# Download from: https://helm.sh/docs/intro/install/
helm version

# 5. rpk (Redpanda CLI - optional but recommended)
# Download from: https://docs.redpanda.com/current/get-started/rpk-install/
rpk version
```

### Required Accounts

1. **DigitalOcean Account**
   - Sign up: https://cloud.digitalocean.com/registrations/new
   - Required for: DOKS cluster, Managed Redis
   - Cost: ~$63/month (DOKS $48, Redis $15)

2. **Redpanda Cloud Account**
   - Sign up: https://redpanda.com/try-redpanda
   - Select: Serverless (Free tier)
   - Required for: Kafka-compatible event streaming

### Authentication Setup

```bash
# DigitalOcean CLI authentication
doctl auth init
# Enter your Personal Access Token when prompted
# Generate token: https://cloud.digitalocean.com/account/api/tokens

# Verify authentication
doctl account get
```

---

## Part 1: Local Development with Minikube (Recap)

**Skip this section if you've already completed Component 1 (Dapr Infrastructure).**

### 1.1 Start Minikube Cluster

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl get nodes
# Expected: minikube   Ready   control-plane   <age>   v1.28.x
```

### 1.2 Initialize Dapr on Minikube

```bash
# Install Dapr control plane (development mode)
dapr init --kubernetes

# Verify Dapr installation
kubectl get pods -n dapr-system
# Expected pods: dapr-operator, dapr-placement, dapr-sidecar-injector, dapr-sentry

# Verify Dapr CLI can connect
dapr status -k
```

### 1.3 Deploy Local Dapr Components

```bash
# Apply local development components (Kafka + Redis)
kubectl apply -f infrastructure/dapr/components/kafka-pubsub.yaml
kubectl apply -f infrastructure/dapr/components/statestore.yaml

# Verify components are registered
kubectl get components
# Expected: kafka-pubsub, statestore
```

### 1.4 Deploy Application to Minikube (Local Test)

```bash
# Build Docker images (use Minikube's Docker daemon)
eval $(minikube docker-env)
docker build -t todo-backend:local ./backend
docker build -t todo-frontend:local ./frontend

# Deploy using Helm (local values)
helm install todo-app ./infrastructure/helm/todo-app \
  --values ./infrastructure/helm/todo-app/values-local.yaml \
  --create-namespace --namespace default

# Verify deployment
kubectl get pods
kubectl get services

# Access application
minikube service todo-frontend --url
```

**Local Development Checkpoint**: Application should be running on Minikube with Dapr sidecars injected.

---

## Part 2: Cloud Deployment to DOKS

### 2.1 Provision DOKS Cluster

```bash
# Create DOKS cluster (2 nodes, s-2vcpu-4gb, NYC3 region)
doctl kubernetes cluster create todo-app-phase5 \
  --region nyc3 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2;auto-scale=false" \
  --wait

# Cluster creation takes ~5-7 minutes
# Expected output: Cluster created successfully

# Verify cluster is ready
doctl kubernetes cluster list
# Status should show "running"

# Configure kubectl to use DOKS cluster
doctl kubernetes cluster kubeconfig save todo-app-phase5

# Verify connection
kubectl get nodes
# Expected: 2 nodes with Ready status
```

**Cluster Details**:
- Name: `todo-app-phase5`
- Region: NYC3 (New York)
- Nodes: 2x s-2vcpu-4gb (4 vCPU / 8GB RAM total)
- Cost: ~$48/month
- Kubernetes Version: 1.28.2-do.0

### 2.2 Initialize Dapr on DOKS

```bash
# Install Dapr control plane on DOKS (production mode)
dapr init --kubernetes --wait

# Verify Dapr installation
kubectl get pods -n dapr-system
# Expected: All pods in Running state (dapr-operator, dapr-placement, dapr-sidecar-injector, dapr-sentry)

# Verify Dapr version
kubectl get deployment -n dapr-system dapr-operator -o jsonpath='{.spec.template.spec.containers[0].image}'
# Expected: dapr:1.13.x or higher

# Check Dapr dashboard (optional)
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080
# Visit: http://localhost:8080
```

**DOKS Checkpoint**: Dapr control plane running on DOKS cluster.

---

## Part 3: Redpanda Cloud Setup

### 3.1 Create Redpanda Cloud Cluster

**Option A: Web Console (Recommended for first-time users)**

1. Log in to Redpanda Cloud: https://cloud.redpanda.com/
2. Click "Create Cluster"
3. Select **Serverless** (Free tier)
4. Choose:
   - **Cloud Provider**: AWS
   - **Region**: us-east-1 (Virginia)
   - **Cluster Name**: `todo-app-cluster`
5. Click "Create" (provisioning takes ~2-3 minutes)
6. Navigate to **Security** → **Users** → **Create User**:
   - Username: `todo-app-user`
   - Mechanism: SCRAM-SHA-256
   - Copy the generated password (32 characters)

**Option B: rpk CLI (For automation)**

```bash
# Login to Redpanda Cloud
rpk cloud login

# Create cluster
rpk cloud cluster create todo-app-cluster \
  --provider aws \
  --region us-east-1 \
  --tier tier-1-aws-v2-x86

# Wait for cluster to be ready (~2-3 minutes)
rpk cloud cluster list
# Status should show "running"

# Create SASL user
rpk cloud cluster user create todo-app-user \
  --mechanism SCRAM-SHA-256 \
  --cluster todo-app-cluster

# Save the generated password securely
# Format: 32-character alphanumeric string (e.g., "aBcD1234eFgH5678iJkL9012mNoP3456")
```

### 3.2 Get Connection Details

```bash
# Get broker URL
rpk cloud cluster info todo-app-cluster

# Expected output format:
# Brokers: seed-<cluster-id>.us-east-1.aws.redpanda.cloud:9092
# Example: seed-a1b2c3d4.us-east-1.aws.redpanda.cloud:9092

# Save these values for later:
# 1. BROKER_URL: seed-<cluster-id>.us-east-1.aws.redpanda.cloud:9092
# 2. SASL_USERNAME: todo-app-user
# 3. SASL_PASSWORD: <32-character password from step 3.1>
```

### 3.3 Create Kafka Topics

```bash
# Set environment variables for rpk
export REDPANDA_BROKERS="seed-<cluster-id>.us-east-1.aws.redpanda.cloud:9092"
export REDPANDA_SASL_USERNAME="todo-app-user"
export REDPANDA_SASL_PASSWORD="<your-password>"
export REDPANDA_SASL_MECHANISM="SCRAM-SHA-256"

# Create topics
rpk topic create task-events \
  --brokers $REDPANDA_BROKERS \
  --user $REDPANDA_SASL_USERNAME \
  --password $REDPANDA_SASL_PASSWORD \
  --sasl-mechanism $REDPANDA_SASL_MECHANISM \
  --tls-enabled \
  --partitions 3 \
  --replicas 3

rpk topic create notification-events \
  --brokers $REDPANDA_BROKERS \
  --user $REDPANDA_SASL_USERNAME \
  --password $REDPANDA_SASL_PASSWORD \
  --sasl-mechanism $REDPANDA_SASL_MECHANISM \
  --tls-enabled \
  --partitions 1 \
  --replicas 3

rpk topic create reminder-events \
  --brokers $REDPANDA_BROKERS \
  --user $REDPANDA_SASL_USERNAME \
  --password $REDPANDA_SASL_PASSWORD \
  --sasl-mechanism $REDPANDA_SASL_MECHANISM \
  --tls-enabled \
  --partitions 1 \
  --replicas 3

# Verify topics
rpk topic list \
  --brokers $REDPANDA_BROKERS \
  --user $REDPANDA_SASL_USERNAME \
  --password $REDPANDA_SASL_PASSWORD \
  --sasl-mechanism $REDPANDA_SASL_MECHANISM \
  --tls-enabled

# Expected output:
# task-events (3 partitions, 3 replicas)
# notification-events (1 partition, 3 replicas)
# reminder-events (1 partition, 3 replicas)
```

**Redpanda Checkpoint**: Cluster running with SASL user and topics created.

---

## Part 4: DigitalOcean Managed Redis Setup

### 4.1 Create Redis Cluster

**Option A: Web Console**

1. Log in to DigitalOcean: https://cloud.digitalocean.com/
2. Navigate to **Databases** → **Create Database**
3. Select:
   - **Database Engine**: Redis
   - **Plan**: Basic (1GB RAM, 25 connections) - $15/month
   - **Datacenter**: NYC3 (same as DOKS cluster)
   - **Database Name**: `todo-app-redis-phase5`
4. Click "Create Database Cluster" (provisioning takes ~5-7 minutes)
5. Wait for status to show "Available"
6. Navigate to **Connection Details** tab
7. Copy the following values:
   - **Host**: `<cluster-name>-do-user-<id>-0.db.ondigitalocean.com`
   - **Port**: `25061` (TLS port)
   - **Password**: (shown in connection string)

**Option B: doctl CLI**

```bash
# Create Redis cluster
doctl databases create todo-app-redis-phase5 \
  --engine redis \
  --region nyc3 \
  --size db-s-1vcpu-1gb \
  --version 7

# Wait for cluster to be ready (~5-7 minutes)
doctl databases list
# Status should show "online"

# Get connection details
doctl databases connection todo-app-redis-phase5 \
  --format Host,Port,Password

# Expected output:
# Host: todo-app-redis-phase5-do-user-12345-0.db.ondigitalocean.com
# Port: 25061
# Password: <generated-password>

# Save these values for later:
# 1. REDIS_HOST: <cluster-name>-do-user-<id>-0.db.ondigitalocean.com
# 2. REDIS_PORT: 25061
# 3. REDIS_PASSWORD: <generated-password>
```

### 4.2 Test Redis Connection

```bash
# Test connection using redis-cli (requires redis installed locally)
redis-cli -h <REDIS_HOST> \
  -p 25061 \
  -a <REDIS_PASSWORD> \
  --tls \
  PING

# Expected output: PONG

# Test basic operations
redis-cli -h <REDIS_HOST> \
  -p 25061 \
  -a <REDIS_PASSWORD> \
  --tls \
  SET test-key "hello-redis"

redis-cli -h <REDIS_HOST> \
  -p 25061 \
  -a <REDIS_PASSWORD> \
  --tls \
  GET test-key

# Expected output: "hello-redis"

# Clean up test key
redis-cli -h <REDIS_HOST> \
  -p 25061 \
  -a <REDIS_PASSWORD> \
  --tls \
  DEL test-key
```

**Redis Checkpoint**: Managed Redis cluster running and accessible with TLS.

---

## Part 5: Kubernetes Secrets Configuration

### 5.1 Create Redpanda Credentials Secret

```bash
# Replace placeholders with actual values from Part 3
REDPANDA_BROKER_URL="seed-<cluster-id>.us-east-1.aws.redpanda.cloud:9092"
REDPANDA_SASL_USERNAME="todo-app-user"
REDPANDA_SASL_PASSWORD="<your-32-character-password>"

# Create Kubernetes Secret
kubectl create secret generic redpanda-credentials \
  --from-literal=brokers="$REDPANDA_BROKER_URL" \
  --from-literal=sasl-username="$REDPANDA_SASL_USERNAME" \
  --from-literal=sasl-password="$REDPANDA_SASL_PASSWORD" \
  --namespace default

# Verify secret was created
kubectl get secret redpanda-credentials -o yaml

# Expected: data.brokers, data.sasl-username, data.sasl-password (base64 encoded)
```

### 5.2 Create Redis Credentials Secret

```bash
# Replace placeholders with actual values from Part 4
REDIS_HOST="todo-app-redis-phase5-do-user-12345-0.db.ondigitalocean.com"
REDIS_PORT="25061"
REDIS_PASSWORD="<your-generated-password>"

# Create Kubernetes Secret
kubectl create secret generic redis-credentials \
  --from-literal=redis-host="$REDIS_HOST" \
  --from-literal=redis-port="$REDIS_PORT" \
  --from-literal=redis-password="$REDIS_PASSWORD" \
  --from-literal=redis-tls="true" \
  --namespace default

# Verify secret was created
kubectl get secret redis-credentials -o yaml

# Expected: data.redis-host, data.redis-port, data.redis-password, data.redis-tls (base64 encoded)
```

### 5.3 Create Application Secrets

```bash
# Database credentials (Neon PostgreSQL)
DATABASE_URL="postgresql://user:password@host:5432/database?sslmode=require"

kubectl create secret generic app-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="<generate-32-character-secret>" \
  --from-literal=gemini-api-key="<your-gemini-api-key>" \
  --namespace default

# Verify all secrets
kubectl get secrets
# Expected: redpanda-credentials, redis-credentials, app-secrets
```

**Secrets Checkpoint**: All credentials securely stored in Kubernetes Secrets.

---

## Part 6: Deploy Dapr Components to DOKS

### 6.1 Deploy Production Dapr Components

```bash
# Apply production Dapr components (with secretKeyRef)
kubectl apply -f specs/005-phase-5/contracts/kafka-pubsub-prod.yaml
kubectl apply -f specs/005-phase-5/contracts/statestore-prod.yaml

# Verify components are registered
kubectl get components
# Expected:
# NAME           AGE
# kafka-pubsub   <seconds>
# statestore     <seconds>

# Check component details
kubectl describe component kafka-pubsub
kubectl describe component statestore

# Verify no errors in Dapr operator logs
kubectl logs -n dapr-system deployment/dapr-operator --tail=50
```

### 6.2 Verify Dapr Component Connectivity

```bash
# Test Redpanda connection via Dapr sidecar (requires test pod)
kubectl run dapr-test --image=curlimages/curl:latest --rm -it -- sh

# Inside the pod:
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"test": "hello-redpanda"}'

# Expected: HTTP 204 No Content (success)

# Test Redis connection via Dapr sidecar
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test-key","value":"hello-redis"}]'

# Expected: HTTP 204 No Content (success)

curl http://localhost:3500/v1.0/state/statestore/test-key
# Expected: "hello-redis"

# Clean up test key
curl -X DELETE http://localhost:3500/v1.0/state/statestore/test-key

# Exit test pod
exit
```

**Dapr Components Checkpoint**: Kafka pub/sub and Redis state store connected to cloud services.

---

## Part 7: Deploy Application with Helm

### 7.1 Build and Push Docker Images

```bash
# Option A: Build and push to DigitalOcean Container Registry (DOCR)

# Create container registry (if not already created)
doctl registry create todo-app-registry

# Log in to DOCR
doctl registry login

# Build and tag images
docker build -t registry.digitalocean.com/todo-app-registry/backend:latest ./backend
docker build -t registry.digitalocean.com/todo-app-registry/frontend:latest ./frontend

# Push images
docker push registry.digitalocean.com/todo-app-registry/backend:latest
docker push registry.digitalocean.com/todo-app-registry/frontend:latest

# Verify images
doctl registry repository list-v2

# Option B: Use existing Docker Hub or GitHub Container Registry
# Update image references in values-prod.yaml accordingly
```

### 7.2 Configure Helm Values for Production

Create `infrastructure/helm/todo-app/values-prod.yaml`:

```yaml
# Production values for DOKS deployment
global:
  environment: production
  domain: todo-app.example.com  # Replace with your domain

backend:
  image:
    repository: registry.digitalocean.com/todo-app-registry/backend
    tag: latest
    pullPolicy: Always

  replicas: 2

  dapr:
    enabled: true
    appId: backend-service
    appPort: 8000
    logLevel: info

  envFrom:
    - secretRef:
        name: app-secrets

  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi

  service:
    type: ClusterIP
    port: 8000

frontend:
  image:
    repository: registry.digitalocean.com/todo-app-registry/frontend
    tag: latest
    pullPolicy: Always

  replicas: 2

  dapr:
    enabled: true
    appId: frontend-service
    appPort: 3000
    logLevel: info

  env:
    - name: NEXT_PUBLIC_API_URL
      value: "http://backend-service:8000"

  resources:
    requests:
      cpu: 200m
      memory: 384Mi
    limits:
      cpu: 400m
      memory: 768Mi

  service:
    type: LoadBalancer
    port: 80
    targetPort: 3000

ingress:
  enabled: false  # Use LoadBalancer for simplicity in Phase 5
  # For production with custom domain, set enabled: true and configure below
  # className: nginx
  # hosts:
  #   - host: todo-app.example.com
  #     paths:
  #       - path: /
  #         pathType: Prefix
```

### 7.3 Deploy Application

```bash
# Install Helm chart with production values
helm install todo-app ./infrastructure/helm/todo-app \
  --values ./infrastructure/helm/todo-app/values-prod.yaml \
  --create-namespace --namespace default

# Wait for deployment to complete (~2-3 minutes)
kubectl rollout status deployment/backend-service
kubectl rollout status deployment/frontend-service

# Verify pods are running with Dapr sidecars
kubectl get pods
# Expected: Each pod should have 2/2 containers (app + daprd)

# Check pod details (should show Dapr sidecar)
kubectl describe pod <backend-pod-name>
# Look for: daprd container with image dapr/daprd:1.13.x
```

### 7.4 Get LoadBalancer IP

```bash
# Get frontend LoadBalancer external IP
kubectl get service frontend-service

# Wait for EXTERNAL-IP to be assigned (~1-2 minutes)
# Expected output:
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)        AGE
# frontend-service   LoadBalancer   10.245.x.x      <PUBLIC_IP>      80:xxxxx/TCP   <age>

# Access application
echo "Visit: http://<EXTERNAL-IP>"
```

**Deployment Checkpoint**: Application running on DOKS with Dapr sidecars.

---

## Part 8: Verification and Testing

### 8.1 Verify Dapr Sidecars

```bash
# Check Dapr sidecar status for backend
kubectl logs deployment/backend-service -c daprd --tail=50

# Expected logs:
# - "Dapr sidecar is up and running"
# - "Component loaded: kafka-pubsub (pubsub.kafka)"
# - "Component loaded: statestore (state.redis)"
# - "Application protocol: http"

# Check Dapr sidecar status for frontend
kubectl logs deployment/frontend-service -c daprd --tail=50
```

### 8.2 Test Event Publishing

```bash
# Port-forward backend service for testing
kubectl port-forward deployment/backend-service 8000:8000

# In another terminal, create a task (triggers event publishing)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "title": "Test task for event publishing",
    "description": "Verify Kafka event flow",
    "completed": false,
    "priority_id": 2
  }'

# Expected: HTTP 201 Created with task object

# Check backend logs for event publishing
kubectl logs deployment/backend-service -c backend-service --tail=50
# Look for: "Published event to kafka-pubsub" or similar

# Verify event in Redpanda Cloud (via rpk or web console)
rpk topic consume task-events \
  --brokers $REDPANDA_BROKERS \
  --user $REDPANDA_SASL_USERNAME \
  --password $REDPANDA_SASL_PASSWORD \
  --sasl-mechanism $REDPANDA_SASL_MECHANISM \
  --tls-enabled \
  --num 1

# Expected: JSON event with event_type: "task.created"
```

### 8.3 Test State Store (Redis Cache)

```bash
# Port-forward backend service (if not already done)
kubectl port-forward deployment/backend-service 8000:8000

# In another terminal, initiate AI chat (uses Redis state store for conversation history)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "What tasks do I have today?",
    "conversation_id": "test-conversation-123"
  }'

# Expected: HTTP 200 OK with AI response

# Verify conversation state in Redis
redis-cli -h <REDIS_HOST> \
  -p 25061 \
  -a <REDIS_PASSWORD> \
  --tls \
  KEYS "todo-app::conversation::*"

# Expected: todo-app::conversation::test-conversation-123

# Check conversation data
redis-cli -h <REDIS_HOST> \
  -p 25061 \
  -a <REDIS_PASSWORD> \
  --tls \
  GET "todo-app::conversation::test-conversation-123"

# Expected: JSON with conversation history
```

### 8.4 Verify Pod Health

```bash
# Check all pods are healthy
kubectl get pods
# All pods should show 2/2 Ready and Running status

# Check resource usage
kubectl top pods
# Verify CPU/memory usage is within limits

# Check Dapr dashboard (optional)
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080
# Visit: http://localhost:8080
# Verify: Components loaded, Applications registered
```

### 8.5 Test Frontend Access

```bash
# Get frontend LoadBalancer IP
FRONTEND_IP=$(kubectl get service frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Frontend URL: http://$FRONTEND_IP"

# Test frontend health
curl -I http://$FRONTEND_IP

# Expected: HTTP 200 OK

# Visit in browser: http://$FRONTEND_IP
# Expected: Todo App login page
```

**Verification Checkpoint**: All components healthy, events flowing, state stored.

---

## Part 9: Monitoring and Troubleshooting

### 9.1 View Logs

```bash
# Backend application logs
kubectl logs deployment/backend-service -c backend-service --tail=100 --follow

# Backend Dapr sidecar logs
kubectl logs deployment/backend-service -c daprd --tail=100 --follow

# Frontend application logs
kubectl logs deployment/frontend-service -c frontend-service --tail=100 --follow

# Frontend Dapr sidecar logs
kubectl logs deployment/frontend-service -c daprd --tail=100 --follow

# Dapr control plane logs
kubectl logs -n dapr-system deployment/dapr-operator --tail=100
```

### 9.2 Common Issues and Fixes

**Issue 1: Pods stuck in Init or CrashLoopBackOff**

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common causes:
# - Secret not found: Verify secrets exist (kubectl get secrets)
# - Image pull error: Check image repository access (doctl registry login)
# - Dapr sidecar not injecting: Verify annotations in deployment YAML
```

**Issue 2: Dapr component not loading**

```bash
# Check component status
kubectl get components
kubectl describe component kafka-pubsub

# Verify secrets are accessible
kubectl get secret redpanda-credentials -o yaml

# Check Dapr operator logs
kubectl logs -n dapr-system deployment/dapr-operator --tail=100

# Common causes:
# - Secret key mismatch: Ensure secretKeyRef.key matches Secret data key
# - Invalid credentials: Test credentials manually (rpk, redis-cli)
# - Network issue: Verify cluster can reach Redpanda/Redis (use test pod with curl)
```

**Issue 3: Events not publishing to Redpanda**

```bash
# Check Dapr sidecar logs for errors
kubectl logs deployment/backend-service -c daprd | grep -i error

# Test Redpanda connectivity from pod
kubectl run kafka-test --image=confluentinc/cp-kafka:latest --rm -it -- sh

# Inside pod:
kafka-console-producer --broker-list $REDPANDA_BROKERS \
  --producer-property security.protocol=SASL_SSL \
  --producer-property sasl.mechanism=SCRAM-SHA-256 \
  --producer-property sasl.jaas.config='org.apache.kafka.common.security.scram.ScramLoginModule required username="todo-app-user" password="<password>";' \
  --topic task-events

# Type a test message and press Enter
# If connection successful: Message will be sent
# If connection fails: Check credentials and network
```

**Issue 4: Redis state store not working**

```bash
# Test Redis connectivity from pod
kubectl run redis-test --image=redis:alpine --rm -it -- sh

# Inside pod:
redis-cli -h <REDIS_HOST> -p 25061 -a <REDIS_PASSWORD> --tls PING

# Expected: PONG
# If fails: Check credentials and network

# Verify Dapr can write to Redis
kubectl exec -it <backend-pod-name> -c daprd -- sh
apk add curl
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test","value":"hello"}]'

# Expected: HTTP 204 No Content
```

### 9.3 Useful Commands

```bash
# Get all resources in namespace
kubectl get all

# Describe pod for detailed status
kubectl describe pod <pod-name>

# Execute command in container
kubectl exec -it <pod-name> -c <container-name> -- sh

# Port-forward to service
kubectl port-forward service/<service-name> <local-port>:<service-port>

# View resource usage
kubectl top pods
kubectl top nodes

# Restart deployment (for secret/config changes)
kubectl rollout restart deployment/<deployment-name>

# View Helm release status
helm list
helm status todo-app

# Rollback Helm release (if needed)
helm rollback todo-app <revision>
```

---

## Part 10: Next Steps

### Phase 5 Component 3 (Microservices)

After verifying cloud deployment, proceed with building microservices:

1. **notification-service**: Email/push notification sender (subscribes to `notification-events`)
2. **recurring-task-service**: Automated task generation (subscribes to `reminder-events`)

Follow the spec at `specs/010-microservices-notification-recurring/spec.md`.

### Production Hardening (Post-Phase 5)

**Security**:
- Enable RBAC for Kubernetes
- Implement network policies (isolate namespaces)
- Use sealed-secrets or external-secrets for GitOps-friendly secret management
- Enable mTLS between services via Dapr

**Monitoring**:
- Set up Prometheus + Grafana for metrics
- Configure alerts for pod failures, high latency, resource exhaustion
- Enable Dapr metrics scraping

**Scaling**:
- Configure Horizontal Pod Autoscaler (HPA) based on CPU/memory
- Enable DOKS cluster autoscaling
- Implement rate limiting and circuit breakers

**CI/CD**:
- Automate Docker image builds (GitHub Actions, GitLab CI)
- Implement blue-green or canary deployments
- Add automated smoke tests after deployment

---

## Summary

**What You've Deployed**:
- ✅ DOKS cluster (2 nodes, NYC3)
- ✅ Dapr control plane on DOKS
- ✅ Redpanda Cloud (AWS us-east-1) with SASL/SSL
- ✅ DigitalOcean Managed Redis with TLS
- ✅ Kubernetes Secrets for credentials
- ✅ Dapr components (kafka-pubsub, statestore) with secretKeyRef
- ✅ Todo App backend + frontend with Dapr sidecars
- ✅ Event publishing to Kafka (task.created, task.updated, task.completed)
- ✅ Conversation state caching in Redis

**Estimated Monthly Cost**: ~$63
- DOKS: $48/month (2x s-2vcpu-4gb nodes)
- Redis: $15/month (Basic plan, 1GB RAM)
- Redpanda: $0/month (Tier 1 free tier)

**Performance Metrics**:
- Task API response time: <200ms p95
- Event publish latency: <100ms
- State store operations: <50ms p95
- Cross-cloud latency (DOKS ↔ Redpanda): 15-20ms

**Next Step**: Run `/sp.tasks` to generate actionable implementation tasks for Component 4.

---

**Created**: 2025-12-11
**Author**: Claude Sonnet 4.5
**Phase**: Phase 1 - Design & Contracts
**Status**: ✅ Complete
