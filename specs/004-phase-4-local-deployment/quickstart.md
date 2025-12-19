# Quickstart: Local Minikube Deployment

**Feature**: 007-minikube-deployment
**Date**: 2025-12-09
**Audience**: Developers setting up local Kubernetes environment

## Overview

This guide walks through deploying the Phase III Todo Chatbot to a local Minikube cluster using Helm Charts. Total setup time: **~10-15 minutes** (including image builds).

---

## Prerequisites

### Required Tools
- **Minikube**: `brew install minikube` (Mac) or [Download](https://minikube.sigs.k8s.io/docs/start/)
- **Docker**: [Docker Desktop](https://www.docker.com/products/docker-desktop) or Docker Engine
- **Helm 3.x**: `brew install helm` (Mac) or [Download](https://helm.sh/docs/intro/install/)
- **kubectl**: Installed with Minikube or `brew install kubectl`

### Resource Requirements
- **CPU**: 4 cores minimum
- **RAM**: 6GB minimum
- **Disk**: 20GB free space

### Verify Installations
```bash
minikube version  # Should show v1.32.0 or later
docker version    # Docker Engine or Desktop
helm version      # v3.13.0 or later
kubectl version --client  # v1.28.0 or later
```

---

## Step 1: Start Minikube Cluster

Start Minikube with sufficient resources:

```bash
minikube start --cpus=4 --memory=6144 --driver=docker
```

**Expected Output**:
```
=  minikube v1.32.0 on Darwin 14.1
(  Using the docker driver based on existing profile
=M  Starting control plane node minikube in cluster minikube
=  Restarting existing docker container for "minikube" ...
=3  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
=  Configuring bridge CNI (Container Networking Interface) ...
=  Verifying Kubernetes components...
<  Enabled addons: storage-provisioner, default-storageclass
<Ä  Done! kubectl is now configured to use "minikube" cluster
```

**Verify cluster is running**:
```bash
kubectl cluster-info
kubectl get nodes
```

---

## Step 2: Configure Docker to Use Minikube

Point your Docker CLI to Minikube's Docker daemon:

```bash
eval $(minikube docker-env)
```

**Verify connection**:
```bash
docker ps  # Should show Minikube containers
```

> **Note**: This command must be run in every new terminal session. Images built in this mode are available directly to Minikube without a registry.

---

## Step 3: Build Docker Images

Navigate to the project root and build both images:

### Backend Image
```bash
cd backend
docker build -t todo-backend:local .
```

**Expected build time**: 2-3 minutes (first build), <1 minute (with cache)

**Verify image size**:
```bash
docker images | grep todo-backend
# Should show ~150MB (excluding base layers)
```

### Frontend Image
```bash
cd ../frontend
docker build -t todo-frontend:local .
```

**Expected build time**: 3-4 minutes (first build), <1 minute (with cache)

**Verify image size**:
```bash
docker images | grep todo-frontend
# Should show ~120MB (excluding base layers)
```

**Verify both images**:
```bash
docker images | grep todo-
```

Expected output:
```
todo-frontend    local    abc123def456    2 minutes ago    120MB
todo-backend     local    def456ghi789    5 minutes ago    150MB
```

---

## Step 4: Create Kubernetes Secrets

Create the secret containing database URL and API keys:

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host.minikube.internal:5432/todo_db" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-key-here" \
  --from-literal=BETTER_AUTH_SECRET="your-jwt-secret-here"
```

> **Important**: Replace the placeholder values with your actual credentials.

**For Neon Database**: Use your Neon connection string from Phase II/III deployment.

**Verify secret created**:
```bash
kubectl get secrets
kubectl describe secret todo-secrets
```

Expected output:
```
Name:         todo-secrets
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
DATABASE_URL:         65 bytes
OPENAI_API_KEY:       56 bytes
BETTER_AUTH_SECRET:   32 bytes
```

---

## Step 5: Deploy with Helm

Navigate to the Helm chart directory and install:

```bash
cd ../infrastructure/helm/todo-stack

# Install with local configuration
helm install todo-stack . -f values-local.yaml
```

**Expected Output**:
```
NAME: todo-stack
LAST DEPLOYED: Mon Dec 09 14:30:00 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
Todo Stack has been deployed to your Minikube cluster!

Access the application:
  Frontend: http://localhost:30080

Check deployment status:
  kubectl get pods -l app=todo

Backend replicas: 2
Frontend replicas: 1
```

---

## Step 6: Verify Deployment

### Check Pod Status
```bash
kubectl get pods -l app=todo
```

Expected output (wait ~2 minutes for Ready state):
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-5d7c8f9b4-abc12     1/1     Running   0          90s
backend-5d7c8f9b4-def34     1/1     Running   0          90s
frontend-6f8d9a2c3-ghi56    1/1     Running   0          90s
```

### Check Services
```bash
kubectl get services -l app=todo
```

Expected output:
```
NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
backend-service    ClusterIP   10.96.123.45    <none>        8000/TCP         2m
frontend-service   NodePort    10.96.234.56    <none>        3000:30080/TCP   2m
```

### Verify Health
```bash
# Backend health check (via port-forward)
kubectl port-forward svc/backend-service 8000:8000 &
curl http://localhost:8000/health/ready
# Expected: {"status":"ready","database":"connected"}

# Stop port-forward
kill %1

# Frontend access (via NodePort)
open http://localhost:30080  # Mac
# Or visit http://localhost:30080 in browser
```

---

## Step 7: Access the Application

### Frontend UI
Open your browser to:
```
http://localhost:30080
```

You should see the Todo Chatbot interface with:
- Task list view
- AI chat interface (OpenAI ChatKit)
- User authentication

### Verify Backend Communication
In the browser console, check that API requests go to `http://backend-service:8000` (internal DNS).

---

## Troubleshooting

### Pods Not Starting

**Check pod logs**:
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

**Common issues**:
- Missing secrets: Verify secret exists (`kubectl get secrets`)
- Image not found: Rebuild images with `eval $(minikube docker-env)` active
- Resource constraints: Increase Minikube resources (`minikube delete && minikube start --cpus=4 --memory=8192`)

### Cannot Access Frontend

**Verify NodePort**:
```bash
minikube service frontend-service --url
```

**Alternative access (if NodePort fails)**:
```bash
kubectl port-forward svc/frontend-service 3000:3000
# Then access http://localhost:3000
```

### Database Connection Fails

**Check secret values**:
```bash
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 --decode
```

**Verify Neon database is accessible**:
- Ensure database allows connections from your network
- Test connection from host machine first

### Images Not Found

**Verify Docker environment**:
```bash
eval $(minikube docker-env)
docker images | grep todo-
```

If images missing, rebuild them (Step 3).

---

## Useful Commands

### View Logs
```bash
# All backend pods
kubectl logs -l app=todo,tier=backend -f

# Specific pod
kubectl logs <pod-name> -f
```

### Scale Replicas
```bash
# Increase backend replicas to 3
kubectl scale deployment backend --replicas=3

# Or update Helm values and upgrade
helm upgrade todo-stack . -f values-local.yaml --set backend.replicaCount=3
```

### Restart Deployment
```bash
kubectl rollout restart deployment backend
kubectl rollout restart deployment frontend
```

### Delete Deployment
```bash
helm uninstall todo-stack
```

### Stop Minikube
```bash
minikube stop
```

### Reset Minikube (clean slate)
```bash
minikube delete
minikube start --cpus=4 --memory=6144 --driver=docker
```

---

## Helm Values Customization

To customize deployment, create your own values file:

```bash
# Copy local values as template
cp values-local.yaml values-custom.yaml

# Edit as needed
# - Change replica counts
# - Adjust resource limits
# - Modify labels/annotations

# Deploy with custom values
helm install todo-stack . -f values-custom.yaml
```

---

## AI Ops Commands

### kubectl-ai Examples
```bash
# Query pods with AI
kubectl ai "show me all todo app pods"

# Describe deployment with AI
kubectl ai "explain the backend deployment"

# Debug with AI
kubectl ai "why is the frontend pod not starting"
```

### kagent Examples
```bash
# Intelligent operations
kagent analyze deployment backend
kagent suggest scaling backend
kagent diagnose pod <pod-name>
```

---

## Next Steps

1. **Development Workflow**:
   - Make code changes in `backend/` or `frontend/`
   - Rebuild Docker images (Step 3)
   - Restart deployments: `kubectl rollout restart deployment backend frontend`

2. **Monitoring**:
   - Enable metrics-server: `minikube addons enable metrics-server`
   - View resource usage: `kubectl top pods`

3. **Production Deployment**:
   - Use `values-production.yaml` for LoadBalancer service type
   - Deploy to DigitalOcean Kubernetes (DOKS) for production
   - Configure Ingress with TLS certificates

4. **Advanced Features**:
   - Add Horizontal Pod Autoscaler (HPA)
   - Configure custom domain with Ingress
   - Integrate monitoring (Prometheus/Grafana)

---

## Success Criteria Verification

 **SC-001**: Deployment completes in <5 minutes (Steps 3-5)
 **SC-002**: Backend image <200MB (verify in Step 3)
 **SC-003**: Frontend image <150MB (verify in Step 3)
 **SC-004**: Pods ready within 2 minutes (verify in Step 6)
 **SC-005**: Frontend accessible at localhost:30080 within 30 seconds (verify in Step 7)
 **SC-007**: Zero hardcoded credentials (secrets in Step 4)
 **SC-011**: 2 backend replicas healthy (verify in Step 6)

---

**Deployment Complete!** <‰

Your Phase III Todo Chatbot is now running on Kubernetes with:
- Multi-stage optimized Docker images
- 2 backend replicas for scalability
- Kubernetes Secrets for secure configuration
- AI ops compatibility

For questions or issues, refer to the troubleshooting section or check the deployment guide at `infrastructure/docs/deployment-guide.md`.
