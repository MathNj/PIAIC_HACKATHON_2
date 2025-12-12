# Todo App - Cloud-Native Deployment Blueprint

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Deployment Guide](#detailed-deployment-guide)
5. [Infrastructure Components](#infrastructure-components)
6. [Cost Optimization](#cost-optimization)
7. [Monitoring & Observability](#monitoring--observability)
8. [Disaster Recovery](#disaster-recovery)
9. [Security Best Practices](#security-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This blueprint provides a comprehensive guide for deploying the Todo App to production using Infrastructure as Code (Terraform) and cloud-native best practices.

### Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                     DigitalOcean Cloud                       │
│                                                               │
│  ┌─────────────────┐        ┌──────────────────┐            │
│  │  Load Balancer  │◄───────│  Ingress/Nginx   │            │
│  └────────┬────────┘        └─────────┬────────┘            │
│           │                            │                      │
│  ┌────────▼────────────────────────────▼─────────┐          │
│  │        Kubernetes Cluster (DOKS)               │          │
│  │                                                 │          │
│  │  ┌──────────┐  ┌────────────┐  ┌───────────┐ │          │
│  │  │ Frontend │  │  Backend   │  │ Notification│ │          │
│  │  │ (Next.js)│  │ (FastAPI)  │  │  Service   │ │          │
│  │  └──────────┘  └─────┬──────┘  └──────┬────┘ │          │
│  │                      │                 │       │          │
│  │  ┌───────────────────▼─────────────────▼────┐ │          │
│  │  │         Dapr Sidecars (Event Bus)        │ │          │
│  │  └─────────┬──────────────────┬─────────────┘ │          │
│  └────────────┼──────────────────┼────────────────┘          │
│               │                  │                            │
│  ┌────────────▼────┐  ┌─────────▼──────┐  ┌──────────────┐ │
│  │   PostgreSQL    │  │     Redis      │  │   Redpanda   │ │
│  │   (Managed)     │  │  (Managed)     │  │   (Cloud)    │ │
│  └─────────────────┘  └────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisites

### Required Tools

1. **Terraform** (>= 1.0)
   ```bash
   # macOS
   brew install terraform

   # Windows (Chocolatey)
   choco install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **kubectl** (Kubernetes CLI)
   ```bash
   # macOS
   brew install kubectl

   # Windows
   choco install kubernetes-cli

   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

3. **doctl** (DigitalOcean CLI)
   ```bash
   # macOS
   brew install doctl

   # Windows
   choco install doctl

   # Linux
   cd ~
   wget https://github.com/digitalocean/doctl/releases/download/v1.98.0/doctl-1.98.0-linux-amd64.tar.gz
   tar xf doctl-1.98.0-linux-amd64.tar.gz
   sudo mv doctl /usr/local/bin
   ```

4. **Docker** (for local testing)
   - Install from: https://docs.docker.com/get-docker/

5. **Helm** (Kubernetes package manager)
   ```bash
   # macOS
   brew install helm

   # Windows
   choco install kubernetes-helm

   # Linux
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

### Required Accounts

1. **DigitalOcean Account**
   - Sign up: https://cloud.digitalocean.com/
   - Create API token: https://cloud.digitalocean.com/account/api/tokens
   - Minimum balance: $100 (recommended for initial deployment)

2. **Redpanda Cloud Account**
   - Sign up: https://cloud.redpanda.com/
   - Create a Serverless cluster (free tier available)

3. **GitHub Account** (for CI/CD)
   - Repository: Your forked version of this repo

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd 0_Hackathon_2

# Navigate to Terraform directory
cd infrastructure/terraform
```

### 2. Configure Variables

```bash
# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your DigitalOcean API token
nano terraform.tfvars
```

**Required variables in `terraform.tfvars`:**
```hcl
do_token     = "dop_v1_YOUR_API_TOKEN_HERE"
project_name = "todo-app"
environment  = "production"
region       = "nyc3"
```

### 3. Initialize and Deploy

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure (takes 10-15 minutes)
terraform apply

# Save outputs
terraform output -json > outputs.json
```

### 4. Configure kubectl

```bash
# Get kubeconfig
terraform output -raw cluster_kubeconfig > kubeconfig.yaml
export KUBECONFIG=$(pwd)/kubeconfig.yaml

# Verify connection
kubectl get nodes
```

### 5. Deploy Application

```bash
# Navigate to Kubernetes manifests
cd ../../infrastructure/kubernetes

# Deploy Dapr
kubectl apply -f dapr/

# Wait for Dapr to be ready
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s

# Create secrets
kubectl apply -f secrets/

# Deploy Dapr components
kubectl apply -f dapr/components/

# Deploy application
kubectl apply -f deployments/
kubectl apply -f services/

# Check deployment status
kubectl get pods -n default
kubectl get svc -n default
```

### 6. Access Your Application

```bash
# Get LoadBalancer IP
kubectl get svc frontend-service -n default

# Visit in browser
# http://<EXTERNAL-IP>
```

---

## 📚 Detailed Deployment Guide

### Phase 1: Infrastructure Provisioning

#### 1.1 DigitalOcean Kubernetes Cluster

The Terraform configuration creates:
- **Kubernetes cluster** (DOKS) with 2 worker nodes
- **Auto-scaling** enabled (2-5 nodes)
- **Managed control plane** (free)
- **Automatic updates** on Sundays at 4 AM

#### 1.2 Managed Databases

**PostgreSQL:**
- Version: 16
- Size: 1vCPU, 1GB RAM
- Automatic backups: Daily
- Connection pooling: Enabled

**Redis (Valkey):**
- Version: 7
- Size: 1vCPU, 1GB RAM
- Persistence: Enabled
- Eviction policy: allkeys-lru

#### 1.3 Container Registry

- **Registry tier**: Basic ($5/month)
- **Storage**: 500MB included
- **Bandwidth**: Unlimited within DigitalOcean
- **Docker credentials**: Auto-generated

### Phase 2: Application Deployment

#### 2.1 Build and Push Docker Images

```bash
# Authenticate to DigitalOcean Container Registry
doctl registry login

# Get registry endpoint
REGISTRY_ENDPOINT=$(terraform output -raw registry_endpoint)

# Build and push backend
cd backend
docker build -t ${REGISTRY_ENDPOINT}/backend:latest .
docker push ${REGISTRY_ENDPOINT}/backend:latest

# Build and push frontend
cd ../frontend
docker build -t ${REGISTRY_ENDPOINT}/frontend:latest .
docker push ${REGISTRY_ENDPOINT}/frontend:latest

# Build and push notification service
cd ../notification-service
docker build -t ${REGISTRY_ENDPOINT}/notification-service:latest .
docker push ${REGISTRY_ENDPOINT}/notification-service:latest
```

#### 2.2 Configure Kubernetes Secrets

```bash
# Database credentials (auto-created by Terraform)
kubectl get secret database-credentials -n todo-app

# Redis credentials (auto-created by Terraform)
kubectl get secret redis-credentials -n todo-app

# Application secrets (manual)
kubectl create secret generic app-secrets \
  --from-literal=BETTER_AUTH_SECRET=$(openssl rand -hex 32) \
  --from-literal=GEMINI_API_KEY=your-gemini-key \
  --from-literal=OPENAI_API_KEY=your-openai-key \
  -n todo-app
```

#### 2.3 Install Dapr

```bash
# Install Dapr on Kubernetes
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm upgrade --install dapr dapr/dapr \
  --version=1.16 \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Verify Dapr installation
kubectl get pods -n dapr-system
```

#### 2.4 Deploy Application Components

```bash
# Deploy in order
kubectl apply -f infrastructure/kubernetes/deployments/backend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/deployments/frontend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/deployments/notification-service-deployment.yaml

# Deploy services
kubectl apply -f infrastructure/kubernetes/services/

# Verify deployments
kubectl get deployments -n todo-app
kubectl get pods -n todo-app
```

### Phase 3: Configure Ingress and SSL

#### 3.1 Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/do-loadbalancer-name"="todo-app-lb"
```

#### 3.2 Configure Domain (Optional)

```bash
# Get LoadBalancer IP
LB_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Configure your domain's A record to point to: $LB_IP"
```

#### 3.3 Install Cert-Manager for SSL

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app=cert-manager -n cert-manager --timeout=300s

# Create Let's Encrypt issuer
kubectl apply -f infrastructure/kubernetes/cert-manager/letsencrypt-issuer.yaml
```

---

## 💰 Cost Optimization

### Current Cost Breakdown (NYC3 Region)

| Component | Tier | Monthly Cost |
|-----------|------|--------------|
| Kubernetes (2 nodes) | s-2vcpu-4gb | $48 |
| PostgreSQL | db-s-1vcpu-1gb | $15 |
| Redis | db-s-1vcpu-1gb | $15 |
| Container Registry | Basic | $5 |
| Load Balancer | Standard | $12 |
| **Total** | | **~$95/month** |

### Optimization Strategies

#### Development/Staging Environment

```hcl
# terraform.tfvars for dev
node_size   = "s-1vcpu-2gb"  # $12/node
node_count  = 1              # $12 total
db_size     = "db-s-1vcpu-1gb" # $15
redis_size  = "db-s-1vcpu-1gb" # $15

# Total: ~$54/month
```

#### Production with High Availability

```hcl
# terraform.tfvars for production
node_size   = "s-4vcpu-8gb"  # $48/node
node_count  = 3              # $144 total
db_size     = "db-s-2vcpu-4gb" # $60
redis_size  = "db-s-2vcpu-4gb" # $60

# Total: ~$276/month
```

#### Cost-Saving Tips

1. **Use spot instances** for non-critical workloads
2. **Enable auto-scaling** to scale down during low traffic
3. **Use Neon PostgreSQL** free tier for development
4. **Implement aggressive caching** to reduce database load
5. **Use CDN** for static assets (Cloudflare free tier)
6. **Monitor resource usage** and right-size instances

---

## 📊 Monitoring & Observability

### Install Prometheus & Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin

# Access Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Visit http://localhost:3000 (admin/admin)
```

### Key Metrics to Monitor

1. **Application Metrics**:
   - Request rate
   - Error rate
   - Response time (p50, p95, p99)
   - Active users

2. **Infrastructure Metrics**:
   - CPU usage per node
   - Memory usage per node
   - Disk I/O
   - Network throughput

3. **Database Metrics**:
   - Connection pool utilization
   - Query performance
   - Replication lag (if using replicas)
   - Cache hit rate (Redis)

4. **Event Streaming Metrics**:
   - Message throughput
   - Consumer lag
   - Error rate

### Logging Stack

```bash
# Install Loki for log aggregation
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace \
  --set grafana.enabled=false \
  --set promtail.enabled=true
```

---

## 🔄 Disaster Recovery

### Backup Strategy

#### Database Backups

```bash
# PostgreSQL automatic backups (configured in Terraform)
# - Daily backups at 4 AM
# - 7-day retention
# - Point-in-time recovery available

# Manual backup
doctl databases backup list <database-id>
doctl databases backup create <database-id>
```

#### Application State Backups

```bash
# Backup Kubernetes resources
kubectl get all -n todo-app -o yaml > backup-$(date +%Y%m%d).yaml

# Backup secrets (encrypted)
kubectl get secrets -n todo-app -o yaml > secrets-$(date +%Y%m%d).yaml
```

### Recovery Procedures

#### Database Recovery

```bash
# Restore from backup
doctl databases restore <database-id> <backup-id>

# Restore to specific point in time
doctl databases restore <database-id> --time "2024-01-15T10:30:00Z"
```

#### Application Recovery

```bash
# Restore Kubernetes resources
kubectl apply -f backup-20240115.yaml

# Verify deployment
kubectl get pods -n todo-app
kubectl logs -f deployment/backend -n todo-app
```

---

## 🔒 Security Best Practices

### 1. Network Security

```yaml
# Network Policy (restrict pod-to-pod communication)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-netpol
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
    ports:
    - protocol: TCP
      port: 8000
```

### 2. Secret Management

```bash
# Use sealed secrets for GitOps
kubectl create secret generic db-password \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# Apply sealed secret
kubectl apply -f sealed-secret.yaml
```

### 3. RBAC (Role-Based Access Control)

```bash
# Create limited service account
kubectl create serviceaccount app-sa -n todo-app

# Create role with minimal permissions
kubectl create role pod-reader \
  --verb=get,list,watch \
  --resource=pods \
  -n todo-app

# Bind role to service account
kubectl create rolebinding app-sa-pod-reader \
  --role=pod-reader \
  --serviceaccount=todo-app:app-sa \
  -n todo-app
```

### 4. Pod Security Standards

```yaml
# Pod Security Policy
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# View pod details
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:16 --restart=Never -- \
  psql -h <db-host> -U <db-user> -d <db-name>

# Check database secret
kubectl get secret database-credentials -n todo-app -o yaml
```

#### 3. Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl get ingress -n todo-app
kubectl describe ingress <ingress-name> -n todo-app

# Check LoadBalancer IP
kubectl get svc -n ingress-nginx
```

#### 4. High Resource Usage

```bash
# Check resource consumption
kubectl top nodes
kubectl top pods -n todo-app

# Describe resource limits
kubectl describe deployment <deployment-name> -n todo-app
```

---

## 📖 Additional Resources

- [DigitalOcean Kubernetes Documentation](https://docs.digitalocean.com/products/kubernetes/)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Chart Guide](https://helm.sh/docs/topics/charts/)

---

## 🤝 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [GitHub Issues](https://github.com/yourusername/todo-app/issues)
3. Contact: your-email@example.com

---

**Last Updated**: December 2024
**Version**: 1.0.0
