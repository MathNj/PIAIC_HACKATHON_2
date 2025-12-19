# Todo Stack Helm Chart

**Version**: 1.0.0
**App Version**: 4.0.0 (Phase IV)
**Type**: Kubernetes Application Chart

## Overview

This Helm chart deploys the Todo Chatbot application with AI Agent capabilities to Kubernetes. It includes:

- **Backend**: FastAPI application with AI agent and MCP tools (2 replicas)
- **Frontend**: Next.js application with OpenAI ChatKit integration (1 replica)
- **Services**: ClusterIP for backend, NodePort/LoadBalancer for frontend
- **Configuration**: Secrets management and environment-specific values

## Architecture

```
┌─────────────────────────────────────────────────┐
│               Frontend Service                   │
│          (NodePort 30080 / LoadBalancer)        │
└─────────────────┬───────────────────────────────┘
                  │
      ┌───────────▼──────────┐
      │ Frontend Deployment   │
      │   (Next.js, 1 pod)    │
      │  Port: 3000           │
      └───────────┬───────────┘
                  │
                  │ http://backend-service:8000
                  │
      ┌───────────▼──────────┐
      │ Backend Service       │
      │    (ClusterIP)        │
      └───────────┬───────────┘
                  │
      ┌───────────▼──────────┐
      │ Backend Deployment    │
      │  (FastAPI, 2 pods)    │
      │  Port: 8000           │
      └───────────────────────┘
                  │
      ┌───────────▼──────────┐
      │    Kubernetes Secret  │
      │    (todo-secrets)     │
      └───────────────────────┘
```

## Prerequisites

- Kubernetes cluster (Minikube 1.28+ or DigitalOcean Kubernetes)
- Helm 3.0+
- kubectl configured with cluster access
- Docker images built and available:
  - `todo-backend:local` (for local) or registry image (for production)
  - `todo-frontend:local` (for local) or registry image (for production)

## Installation

### 1. Create Kubernetes Secret (Required)

The chart requires a secret named `todo-secrets` with the following keys:

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/dbname' \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=BETTER_AUTH_SECRET='your-secret-key'
```

### 2. Install the Chart

**Local Development (Minikube)**:
```bash
helm install todo-stack . -f values-local.yaml
```

**Production Environment**:
```bash
helm install todo-stack . -f values-production.yaml
```

**Custom Namespace**:
```bash
helm install todo-stack . -f values-local.yaml --namespace todo --create-namespace
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=todo

# Check service status
kubectl get services -l app=todo

# View deployment details
kubectl get deployments -l app=todo
```

## Configuration

### Values Files

- **values.yaml**: Default configuration (local environment)
- **values-local.yaml**: Minikube-specific overrides
- **values-production.yaml**: Production environment configuration

### Key Configuration Options

| Parameter | Description | Default | Local | Production |
|-----------|-------------|---------|-------|------------|
| `global.environment` | Environment name | `local` | `local` | `production` |
| `backend.replicaCount` | Backend pod count | `2` | `2` | `3` |
| `backend.image.repository` | Backend image | `todo-backend` | `todo-backend` | `registry.digitalocean.com/todo/backend` |
| `backend.image.tag` | Backend image tag | `local` | `local` | `v1.0.0` |
| `backend.resources.requests.cpu` | Backend CPU request | `500m` | `500m` | `1000m` |
| `backend.resources.requests.memory` | Backend memory request | `512Mi` | `512Mi` | `1024Mi` |
| `frontend.replicaCount` | Frontend pod count | `1` | `1` | `2` |
| `frontend.image.repository` | Frontend image | `todo-frontend` | `todo-frontend` | `registry.digitalocean.com/todo/frontend` |
| `frontend.image.tag` | Frontend image tag | `local` | `local` | `v1.0.0` |
| `frontend.service.type` | Frontend service type | `NodePort` | `NodePort` | `LoadBalancer` |
| `frontend.service.nodePort` | NodePort number | `30080` | `30080` | N/A |
| `secrets.name` | Secret name | `todo-secrets` | `todo-secrets` | `todo-secrets` |
| `secrets.create` | Create secret via Helm | `false` | `false` | `false` |
| `ingress.enabled` | Enable Ingress | `false` | `false` | `true` |

### Environment Variables

**Backend**:
- `DATABASE_URL` (from secret)
- `OPENAI_API_KEY` (from secret)
- `BETTER_AUTH_SECRET` (from secret)
- `LOG_LEVEL` (from values)
- `WORKERS` (from values)
- `PORT` (auto-configured)

**Frontend**:
- `NEXT_PUBLIC_API_URL` (from values, defaults to `http://backend-service:8000`)
- `PORT` (auto-configured)

## Accessing the Application

### Local Development (Minikube)

**Method 1: NodePort (Default)**
```bash
# Access via NodePort
open http://localhost:30080

# Or get Minikube service URL
minikube service frontend-service --url
```

**Method 2: Port Forwarding**
```bash
kubectl port-forward svc/frontend-service 3000:3000
open http://localhost:3000
```

### Production

```bash
# Get LoadBalancer external IP
kubectl get svc frontend-service

# Access via external IP
open http://<EXTERNAL-IP>:3000
```

## Upgrading

```bash
# Upgrade with same values file
helm upgrade todo-stack . -f values-local.yaml

# Upgrade with custom values
helm upgrade todo-stack . --set backend.replicaCount=3

# Upgrade and wait for pods to be ready
helm upgrade todo-stack . -f values-local.yaml --wait --timeout 5m
```

## Rollback

```bash
# View release history
helm history todo-stack

# Rollback to previous version
helm rollback todo-stack

# Rollback to specific revision
helm rollback todo-stack 2
```

## Uninstalling

```bash
# Uninstall release
helm uninstall todo-stack

# Uninstall and delete namespace
helm uninstall todo-stack -n todo && kubectl delete namespace todo
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status and events
kubectl describe pod -l app=todo

# View pod logs
kubectl logs -l tier=backend -f
kubectl logs -l tier=frontend -f

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Secret Issues

```bash
# Verify secret exists
kubectl get secret todo-secrets

# Check secret keys
kubectl describe secret todo-secrets

# Recreate secret if needed
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='...' \
  --from-literal=OPENAI_API_KEY='...' \
  --from-literal=BETTER_AUTH_SECRET='...'
```

### Image Pull Errors

```bash
# Check if images are available
docker images | grep todo

# For Minikube, ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)
docker images
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints

# Test backend service internally
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://backend-service:8000/health/ready

# Test frontend service
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://frontend-service:3000
```

## Testing

### Validate Chart Syntax

```bash
# Lint the chart
helm lint .

# Dry-run installation
helm install todo-stack . --dry-run --debug -f values-local.yaml

# Template rendering
helm template todo-stack . -f values-local.yaml > rendered.yaml
```

### Health Checks

```bash
# Check backend health
kubectl exec -it deployment/backend-deployment -- curl localhost:8000/health/ready
kubectl exec -it deployment/backend-deployment -- curl localhost:8000/health/live

# Check frontend health
kubectl exec -it deployment/frontend-deployment -- curl localhost:3000
```

## Labels and Annotations

### Standard Labels

All resources include:
- `app: todo`
- `tier: backend|frontend`
- `environment: local|production`
- `version: 4.0.0`
- `app.kubernetes.io/name: todo-stack`
- `app.kubernetes.io/instance: <release-name>`
- `app.kubernetes.io/version: 4.0.0`
- `app.kubernetes.io/managed-by: Helm`

### AI Ops Annotations

Deployments include AI ops compatibility annotations:
- `ai-ops/enabled: "true"`
- `ai-ops/tools: "kubectl-ai,kagent"`

These annotations enable integration with kubectl-ai and kagent for intelligent cluster operations.

## Security

### Non-Root Users

- Backend runs as user `1000` (nonroot)
- Frontend runs as user `1001` (nextjs)
- Both containers drop ALL capabilities
- `allowPrivilegeEscalation: false`

### Secrets Management

- Secrets are referenced, not embedded in charts
- Manual secret creation required before deployment
- Secrets injected via `envFrom.secretRef`

### Network Policies

For production deployments, consider adding NetworkPolicy resources to restrict pod-to-pod communication.

## Resource Management

### Default Resource Limits

**Backend** (per pod):
- Requests: 500m CPU, 512Mi memory
- Limits: 1000m CPU, 1024Mi memory

**Frontend** (per pod):
- Requests: 250m CPU, 256Mi memory
- Limits: 500m CPU, 512Mi memory

### Autoscaling

The chart supports HPA (Horizontal Pod Autoscaler). To enable:

```bash
kubectl autoscale deployment backend-deployment --cpu-percent=80 --min=2 --max=5
kubectl autoscale deployment frontend-deployment --cpu-percent=80 --min=1 --max=3
```

## Monitoring

### Health Probes

**Backend**:
- Readiness: `/health/ready` (checks database connectivity)
- Liveness: `/health/live` (checks process health)

**Frontend**:
- Readiness: `/` (checks Next.js server)
- Liveness: `/` (checks process health)

### Metrics

Enable Prometheus metrics collection (requires Prometheus operator):

```bash
# Add ServiceMonitor for backend
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-metrics
spec:
  selector:
    matchLabels:
      app: todo
      tier: backend
  endpoints:
  - port: http
    path: /metrics
EOF
```

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/your-org/todo-app/issues
- Documentation: https://github.com/your-org/todo-app/wiki
- Email: team@example.com

## License

[Your License Here]

## Maintainers

- Todo App Team <team@example.com>
