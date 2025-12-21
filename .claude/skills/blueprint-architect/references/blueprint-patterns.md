# Cloud-Native Blueprint Patterns

Reference guide for common architectural patterns extracted as blueprints.

## Blueprint Components

### 1. Microservices Stack

**Pattern**: FastAPI + Next.js + Dapr + Kafka

**Components**:
- Backend API (FastAPI with SQLModel)
- Frontend SPA (Next.js with App Router)
- Event bus (Kafka with Dapr pub/sub)
- State management (Redis with Dapr state store)
- Job scheduling (Dapr Jobs API)

**Use Cases**:
- Todo/Task management applications
- CRM systems
- Project management tools
- Collaboration platforms

### 2. Event-Driven Architecture

**Pattern**: Pub/Sub with Dapr and Kafka

**Components**:
- Kafka cluster (Strimzi or Redpanda)
- Dapr pub/sub component
- Event publishers
- Event subscribers
- Dead letter queues

**Use Cases**:
- Real-time notifications
- Analytics pipelines
- Audit logging
- Workflow automation

### 3. Authentication & Authorization

**Pattern**: JWT with Better Auth

**Components**:
- Better Auth integration
- JWT token management
- Protected routes
- Role-based access control

**Use Cases**:
- Multi-tenant applications
- User management systems
- Secure API access

### 4. AI Agent Integration

**Pattern**: OpenAI Agents SDK with MCP Tools

**Components**:
- Agent runner
- MCP server
- Tool definitions
- Conversation persistence

**Use Cases**:
- AI-powered assistants
- Chatbots
- Intelligent automation
- Knowledge management

## Blueprint Structure

```
blueprint-name/
├── infrastructure/
│   ├── helm/
│   │   └── {app}-stack/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-local.yaml
│   │       ├── values-production.yaml
│   │       └── templates/
│   │           ├── backend-deployment.yaml
│   │           ├── backend-service.yaml
│   │           ├── frontend-deployment.yaml
│   │           ├── frontend-service.yaml
│   │           ├── ingress.yaml
│   │           ├── configmap.yaml
│   │           └── secrets.yaml
│   ├── kubernetes/
│   │   ├── secrets-template.yaml
│   │   └── services.yaml
│   ├── dapr/
│   │   └── components/
│   │       ├── kafka-pubsub.yaml
│   │       ├── statestore.yaml
│   │       └── job-scheduler.yaml
│   └── kafka/
│       ├── deploy_kafka.sh
│       └── topics.yaml
├── specs/
│   ├── feature-template.md
│   ├── api-spec-template.md
│   └── database-schema-template.md
├── BLUEPRINT.md
└── blueprint.json
```

## Deployment Patterns

### Pattern 1: Minikube Development

```bash
# 1. Deploy Kafka
cd infrastructure/kafka
bash deploy_kafka.sh

# 2. Apply Dapr components
kubectl apply -f infrastructure/dapr/components/

# 3. Install Helm chart
helm install app infrastructure/helm/{app}-stack/ \
  --values infrastructure/helm/{app}-stack/values-local.yaml
```

### Pattern 2: Production Kubernetes

```bash
# 1. Deploy Kafka with persistent storage
STORAGE_TYPE=persistent bash infrastructure/kafka/deploy_kafka.sh

# 2. Configure production secrets
kubectl apply -f infrastructure/kubernetes/secrets.yaml

# 3. Deploy with production values
helm install app infrastructure/helm/{app}-stack/ \
  --namespace production \
  --values infrastructure/helm/{app}-stack/values-production.yaml
```

## Customization Patterns

### Adding Event-Driven Features

1. Define new Kafka topic in `infrastructure/kafka/topics.yaml`
2. Configure Dapr subscription in `backend/app/main.py`
3. Implement event handler endpoint
4. Publish events from relevant endpoints

### Adding AI Agent Features

1. Define MCP tools in `backend/mcp/tools.py`
2. Configure agent runner in `backend/agent_runner/`
3. Add frontend chat interface
4. Integrate with OpenAI Agents SDK

### Adding Authentication

1. Configure Better Auth in backend
2. Add JWT middleware
3. Protect routes with dependencies
4. Add frontend auth provider

## Testing Patterns

### Unit Testing

```python
# pytest with mocks
def test_create_task(client, mock_db):
    response = client.post("/api/tasks", json={...})
    assert response.status_code == 201
```

### Integration Testing

```python
# Test with Dapr
def test_publish_event(dapr_client):
    dapr_client.publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="task-events",
        data={...}
    )
```

### E2E Testing

```bash
# Cypress or Playwright
npm run test:e2e
```

## Monitoring Patterns

### Prometheus Metrics

```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-metrics
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
    - port: metrics
      path: /metrics
```

### Logging

```yaml
# Fluent Bit configuration
[OUTPUT]
    Name es
    Match *
    Host elasticsearch
    Port 9200
    Index k8s-logs
```

## Scaling Patterns

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Kafka Scaling

- Increase topic partitions for higher throughput
- Add more consumer group instances
- Configure consumer fetch settings

## Security Patterns

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
```

### Secret Management

```yaml
# External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  secretStoreRef:
    name: vault-backend
  target:
    name: app-secrets
  data:
    - secretKey: database-url
      remoteRef:
        key: /app/database-url
```

## CI/CD Patterns

### GitHub Actions

```yaml
name: Deploy Blueprint
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy with Helm
        run: |
          helm upgrade --install app \
            infrastructure/helm/{app}-stack/ \
            --values infrastructure/helm/{app}-stack/values-production.yaml
```

## Cost Optimization Patterns

1. **Ephemeral Storage**: Use for development/staging
2. **Right-sizing**: Configure resource requests/limits
3. **Autoscaling**: Scale down during low traffic
4. **Spot Instances**: Use for non-critical workloads
5. **Resource Pooling**: Share Kafka cluster across apps
