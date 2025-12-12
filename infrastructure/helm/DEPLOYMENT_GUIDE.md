# Helm Chart Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Todo Chatbot application to Kubernetes using the `todo-stack` Helm chart.

## Chart Information

- **Chart Name**: todo-stack
- **Chart Version**: 1.0.0
- **App Version**: 4.0.0 (Phase IV)
- **Location**: `infrastructure/helm/todo-stack/`

## Prerequisites

### Required Tools

1. **Kubernetes Cluster**:
   - Minikube 1.28+ (for local development)
   - DigitalOcean Kubernetes (for production)

2. **CLI Tools**:
   - kubectl 1.28+
   - Helm 3.0+
   - Docker (for image building)

3. **Docker Images**:
   - Backend: `todo-backend:local`
   - Frontend: `todo-frontend:local`

### Verify Prerequisites

```bash
# Check Kubernetes cluster
kubectl cluster-info

# Check Helm version
helm version

# Check Docker
docker --version
```

## Quick Start (Minikube)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=6144 --driver=docker

# Verify cluster is running
kubectl get nodes
```

### Step 2: Build Docker Images

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t todo-backend:local .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:local .

# Verify images
docker images | grep todo
```

### Step 3: Create Kubernetes Secret

```bash
# Create secret with required environment variables
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='sqlite:///./todo.db' \
  --from-literal=OPENAI_API_KEY='sk-your-openai-key' \
  --from-literal=BETTER_AUTH_SECRET='your-secret-key-min-32-chars'

# Verify secret
kubectl get secret todo-secrets
kubectl describe secret todo-secrets
```

### Step 4: Install Helm Chart

```bash
# Navigate to chart directory
cd infrastructure/helm/todo-stack

# Lint the chart (optional but recommended)
helm lint .

# Install with local values
helm install todo-stack . -f values-local.yaml

# Watch deployment progress
kubectl get pods -l app=todo -w
```

### Step 5: Access the Application

```bash
# Get frontend URL
minikube service frontend-service --url

# Or use NodePort directly
# Access: http://localhost:30080

# Check backend health
kubectl port-forward svc/backend-service 8000:8000
curl http://localhost:8000/health/ready
```

## Production Deployment (DigitalOcean Kubernetes)

### Step 1: Configure Container Registry

```bash
# Tag and push backend image
docker tag todo-backend:local registry.digitalocean.com/your-registry/backend:v1.0.0
docker push registry.digitalocean.com/your-registry/backend:v1.0.0

# Tag and push frontend image
docker tag todo-frontend:local registry.digitalocean.com/your-registry/frontend:v1.0.0
docker push registry.digitalocean.com/your-registry/frontend:v1.0.0
```

### Step 2: Update values-production.yaml

Edit `values-production.yaml` to match your registry:

```yaml
backend:
  image:
    repository: registry.digitalocean.com/your-registry/backend
    tag: v1.0.0

frontend:
  image:
    repository: registry.digitalocean.com/your-registry/frontend
    tag: v1.0.0

ingress:
  enabled: true
  hosts:
    - host: todo.yourdomain.com
```

### Step 3: Create Production Secret

```bash
# Create production secret with actual credentials
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/dbname' \
  --from-literal=OPENAI_API_KEY='sk-your-production-key' \
  --from-literal=BETTER_AUTH_SECRET='your-production-secret-key' \
  --namespace production

# Or use kubectl apply with encrypted secret
kubectl apply -f production-secrets.yaml
```

### Step 4: Install to Production

```bash
# Create production namespace
kubectl create namespace production

# Install chart with production values
helm install todo-stack . \
  -f values-production.yaml \
  --namespace production

# Verify deployment
kubectl get all -n production -l app=todo
```

## Configuration Options

### Environment Variables

**Backend** (from secret):
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key for AI agent
- `BETTER_AUTH_SECRET`: Authentication secret key

**Frontend**:
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://backend-service:8000)

### Resource Configuration

#### Local (Minikube)
- Backend: 2 replicas, 500m CPU / 512Mi RAM (requests)
- Frontend: 1 replica, 250m CPU / 256Mi RAM (requests)

#### Production
- Backend: 3 replicas, 1000m CPU / 1024Mi RAM (requests)
- Frontend: 2 replicas, 500m CPU / 512Mi RAM (requests)

### Service Configuration

#### Local
- Backend: ClusterIP (internal only)
- Frontend: NodePort 30080 (external access)

#### Production
- Backend: ClusterIP (internal only)
- Frontend: LoadBalancer (cloud-managed external access)

## Common Operations

### View Logs

```bash
# Backend logs
kubectl logs -l tier=backend -f

# Frontend logs
kubectl logs -l tier=frontend -f

# Specific pod logs
kubectl logs backend-deployment-<pod-id> -f
```

### Scale Deployments

```bash
# Scale backend
kubectl scale deployment backend-deployment --replicas=3

# Scale frontend
kubectl scale deployment frontend-deployment --replicas=2

# Or use Helm upgrade
helm upgrade todo-stack . --set backend.replicaCount=3
```

### Update Configuration

```bash
# Update values file
vim values-local.yaml

# Apply changes
helm upgrade todo-stack . -f values-local.yaml

# Rollback if needed
helm rollback todo-stack
```

### Debug Pods

```bash
# Describe pod
kubectl describe pod backend-deployment-<pod-id>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Execute commands in pod
kubectl exec -it backend-deployment-<pod-id> -- /bin/sh

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://backend-service:8000/health/ready
```

## Troubleshooting

### Issue: Pods in ImagePullBackOff

**Cause**: Docker images not available

**Solution**:
```bash
# For Minikube, ensure using Minikube's Docker daemon
eval $(minikube docker-env)
docker images | grep todo

# Rebuild images if missing
cd backend && docker build -t todo-backend:local .
cd ../frontend && docker build -t todo-frontend:local .
```

### Issue: Pods in CrashLoopBackOff

**Cause**: Application failing to start

**Solution**:
```bash
# Check logs
kubectl logs backend-deployment-<pod-id>

# Common issues:
# 1. Missing secret
kubectl get secret todo-secrets

# 2. Invalid environment variables
kubectl describe pod backend-deployment-<pod-id> | grep -A 10 Environment

# 3. Health check failing
kubectl exec -it backend-deployment-<pod-id> -- curl localhost:8000/health/ready
```

### Issue: Secret Not Found

**Cause**: Secret `todo-secrets` not created

**Solution**:
```bash
# Create the secret
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='...' \
  --from-literal=OPENAI_API_KEY='...' \
  --from-literal=BETTER_AUTH_SECRET='...'

# Restart deployments
kubectl rollout restart deployment/backend-deployment
kubectl rollout restart deployment/frontend-deployment
```

### Issue: Frontend Can't Connect to Backend

**Cause**: Service DNS or network issue

**Solution**:
```bash
# Verify backend service exists
kubectl get svc backend-service

# Test DNS resolution from frontend pod
kubectl exec -it frontend-deployment-<pod-id> -- nslookup backend-service

# Test connectivity
kubectl exec -it frontend-deployment-<pod-id> -- wget -O- http://backend-service:8000/health/ready

# Check frontend environment variables
kubectl exec -it frontend-deployment-<pod-id> -- env | grep API_URL
```

## Validation Checklist

Before deploying to production, verify:

- [ ] Helm chart passes lint: `helm lint .`
- [ ] Template renders correctly: `helm template . --debug`
- [ ] Secret created with valid values
- [ ] Docker images pushed to registry
- [ ] Registry credentials configured (if private)
- [ ] Resource limits appropriate for workload
- [ ] Health check endpoints working
- [ ] Database connection string valid
- [ ] OpenAI API key valid
- [ ] Ingress configured with TLS (production)
- [ ] Monitoring and logging configured
- [ ] Backup strategy in place

## Uninstall

```bash
# Uninstall release
helm uninstall todo-stack

# Delete secret
kubectl delete secret todo-secrets

# Clean up namespace (if dedicated)
kubectl delete namespace production
```

## Next Steps

After successful deployment:

1. **Configure Monitoring**: Set up Prometheus/Grafana for metrics
2. **Enable Autoscaling**: Configure HPA for automatic scaling
3. **Set Up CI/CD**: Automate deployments with GitHub Actions
4. **Configure Backup**: Set up database backup strategy
5. **Enable Logging**: Configure centralized logging (ELK/Loki)
6. **Security Hardening**: Implement NetworkPolicy, PodSecurityPolicy
7. **Load Testing**: Verify performance under load

## Support

For issues or questions:
- Review Helm chart README: `infrastructure/helm/todo-stack/README.md`
- Check Kubernetes events: `kubectl get events`
- View application logs: `kubectl logs -l app=todo`
- Consult project documentation: `specs/007-minikube-deployment/`

## References

- Helm Documentation: https://helm.sh/docs/
- Kubernetes Documentation: https://kubernetes.io/docs/
- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- DigitalOcean Kubernetes: https://www.digitalocean.com/products/kubernetes
