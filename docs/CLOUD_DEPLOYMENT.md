# Cloud Deployment Guide

This guide covers deploying the Todo Chatbot application to production Kubernetes clusters on major cloud providers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Cloud Provider Guides](#cloud-provider-guides)
   - [DigitalOcean Kubernetes (DOKS)](#digitalocean-kubernetes-doks)
   - [Google Kubernetes Engine (GKE)](#google-kubernetes-engine-gke)
   - [Amazon Elastic Kubernetes Service (EKS)](#amazon-elastic-kubernetes-service-eks)
4. [Production Configuration](#production-configuration)
5. [Post-Deployment](#post-deployment)
6. [Monitoring & Scaling](#monitoring--scaling)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# Helm 3.x
helm version

# kubectl 1.28+
kubectl version --client

# Cloud CLI (choose one)
doctl version          # DigitalOcean
gcloud version         # Google Cloud
aws --version          # AWS
```

### Docker Images

**Option 1: Use Docker Hub (Recommended for Production)**

```bash
# Tag and push images to Docker Hub
docker tag todo-backend:latest yourusername/todo-backend:v1.0.0
docker tag todo-frontend:latest yourusername/todo-frontend:v1.0.0

docker push yourusername/todo-backend:v1.0.0
docker push yourusername/todo-frontend:v1.0.0
```

**Option 2: Use Cloud Provider Registry**

- **DigitalOcean**: Container Registry
- **Google Cloud**: Artifact Registry (gcr.io)
- **AWS**: Elastic Container Registry (ECR)

See provider-specific guides below for details.

### Kubernetes Secrets

Create a `production-secrets.yaml` file:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:password@host:5432/database?sslmode=require"
  jwt-secret: "your-production-jwt-secret-min-32-chars"
```

**Security Note**: Never commit this file to git! Add to `.gitignore`.

---

## Quick Start

### 1. Prepare Helm Values

Create `values-production.yaml`:

```yaml
backend:
  enabled: true
  replicaCount: 3
  image:
    repository: yourusername/todo-backend
    pullPolicy: Always
    tag: v1.0.0
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

frontend:
  enabled: true
  replicaCount: 3
  image:
    repository: yourusername/todo-frontend
    pullPolicy: Always
    tag: v1.0.0
  service:
    type: LoadBalancer  # Or use Ingress
    port: 3000
  env:
    - name: NEXT_PUBLIC_API_URL
      value: "https://api.yourdomain.com"  # Update with your domain
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: app.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.yourdomain.com

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### 2. Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-app

# Apply secrets
kubectl apply -f production-secrets.yaml -n todo-app

# Install Helm chart
helm install todo-app helm/todo-app \
  --namespace todo-app \
  --values values-production.yaml

# Check deployment status
kubectl get pods -n todo-app
```

### 3. Verify Deployment

```bash
# Check all resources
kubectl get all -n todo-app

# Check pod logs
kubectl logs -f deployment/todo-app-backend -n todo-app
kubectl logs -f deployment/todo-app-frontend -n todo-app

# Test backend health
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app
curl http://localhost:8000/health
```

---

## Cloud Provider Guides

### DigitalOcean Kubernetes (DOKS)

**Best for**: Simple setup, predictable pricing, excellent documentation

#### 1. Create Kubernetes Cluster

```bash
# Install doctl
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create cluster (3 nodes, 2 vCPU, 4GB RAM each)
doctl kubernetes cluster create todo-app-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --size s-2vcpu-4gb \
  --count 3 \
  --wait

# Configure kubectl
doctl kubernetes cluster kubeconfig save todo-app-cluster

# Verify
kubectl cluster-info
kubectl get nodes
```

#### 2. Create Container Registry

```bash
# Create registry
doctl registry create todo-app-registry

# Login to registry
doctl registry login

# Tag and push images
docker tag todo-backend:latest registry.digitalocean.com/todo-app-registry/backend:v1.0.0
docker tag todo-frontend:latest registry.digitalocean.com/todo-app-registry/frontend:v1.0.0

docker push registry.digitalocean.com/todo-app-registry/backend:v1.0.0
docker push registry.digitalocean.com/todo-app-registry/frontend:v1.0.0

# Integrate registry with cluster (automatic pull access)
doctl kubernetes cluster registry add todo-app-cluster
```

#### 3. Set up Load Balancer & Ingress

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/do/deploy.yaml

# Wait for LoadBalancer external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller --watch

# Get the external IP
export LB_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "LoadBalancer IP: $LB_IP"
```

#### 4. Configure DNS

```bash
# Add A record in DigitalOcean DNS:
# app.yourdomain.com -> $LB_IP
# api.yourdomain.com -> $LB_IP

# Verify DNS
nslookup app.yourdomain.com
```

#### 5. Install Cert-Manager (SSL/TLS)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create Let's Encrypt ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

#### 6. Deploy Application

Update `values-production.yaml`:

```yaml
backend:
  image:
    repository: registry.digitalocean.com/todo-app-registry/backend
    tag: v1.0.0

frontend:
  image:
    repository: registry.digitalocean.com/todo-app-registry/frontend
    tag: v1.0.0
  env:
    - name: NEXT_PUBLIC_API_URL
      value: "https://api.yourdomain.com"

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: app.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.yourdomain.com
```

```bash
# Deploy
kubectl create namespace todo-app
kubectl apply -f production-secrets.yaml -n todo-app
helm install todo-app helm/todo-app -n todo-app -f values-production.yaml

# Check status
kubectl get all -n todo-app
kubectl get ingress -n todo-app
kubectl get certificate -n todo-app
```

#### 7. Verify SSL Certificate

```bash
# Wait for certificate to be issued (2-5 minutes)
kubectl describe certificate app-tls -n todo-app

# Test HTTPS
curl -I https://app.yourdomain.com
```

**Cost Estimate (DigitalOcean)**:
- Kubernetes Cluster (3 nodes): $72/month
- Load Balancer: $12/month
- Container Registry: $5-20/month (depends on storage)
- **Total**: ~$89-104/month

---

### Google Kubernetes Engine (GKE)

**Best for**: Advanced features, integration with Google Cloud services, autoscaling

#### 1. Create GKE Cluster

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create cluster (autopilot mode - fully managed)
gcloud container clusters create-auto todo-app-cluster \
  --region us-central1 \
  --release-channel regular

# OR create standard cluster (more control)
gcloud container clusters create todo-app-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 5

# Configure kubectl
gcloud container clusters get-credentials todo-app-cluster --zone us-central1-a

# Verify
kubectl cluster-info
```

#### 2. Set up Artifact Registry

```bash
# Create repository
gcloud artifacts repositories create todo-app-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Todo App Docker images"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Tag and push images
docker tag todo-backend:latest us-central1-docker.pkg.dev/YOUR_PROJECT_ID/todo-app-repo/backend:v1.0.0
docker tag todo-frontend:latest us-central1-docker.pkg.dev/YOUR_PROJECT_ID/todo-app-repo/frontend:v1.0.0

docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/todo-app-repo/backend:v1.0.0
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/todo-app-repo/frontend:v1.0.0
```

#### 3. Install Ingress & SSL

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create Let's Encrypt ClusterIssuer (same as DOKS example above)
```

#### 4. Configure Cloud DNS

```bash
# Get LoadBalancer IP
export LB_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Create DNS zone (if not exists)
gcloud dns managed-zones create todo-app-zone \
  --dns-name="yourdomain.com." \
  --description="Todo App DNS zone"

# Add A record
gcloud dns record-sets create app.yourdomain.com. \
  --zone=todo-app-zone \
  --type=A \
  --ttl=300 \
  --rrdatas=$LB_IP
```

#### 5. Deploy Application

Update `values-production.yaml` with GCR image paths and deploy:

```bash
kubectl create namespace todo-app
kubectl apply -f production-secrets.yaml -n todo-app
helm install todo-app helm/todo-app -n todo-app -f values-production.yaml
```

**Cost Estimate (GKE Autopilot)**:
- Autopilot cluster: ~$72/month (based on resource usage)
- Load Balancer: ~$18/month
- Artifact Registry: ~$0.10/GB/month
- **Total**: ~$90-110/month

---

### Amazon Elastic Kubernetes Service (EKS)

**Best for**: AWS ecosystem integration, enterprise features, scalability

#### 1. Create EKS Cluster

```bash
# Install eksctl
# https://eksctl.io/installation/

# Create cluster
eksctl create cluster \
  --name todo-app-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed

# Configure kubectl (automatic with eksctl)
kubectl cluster-info
```

#### 2. Set up ECR (Elastic Container Registry)

```bash
# Create repositories
aws ecr create-repository --repository-name todo-backend --region us-east-1
aws ecr create-repository --repository-name todo-frontend --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push images
docker tag todo-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/todo-backend:v1.0.0
docker tag todo-frontend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/todo-frontend:v1.0.0

docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/todo-backend:v1.0.0
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/todo-frontend:v1.0.0
```

#### 3. Install AWS Load Balancer Controller

```bash
# Create IAM policy
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.2/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Create service account
eksctl create iamserviceaccount \
  --cluster=todo-app-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

# Install controller via Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=todo-app-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

#### 4. Install Cert-Manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

#### 5. Configure Route 53 (DNS)

```bash
# Get ALB DNS name after deployment
export ALB_DNS=$(kubectl get ingress -n todo-app -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}')

# Create hosted zone (if not exists)
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Add CNAME record pointing app.yourdomain.com to ALB
# Use AWS Console or CLI to create A alias record
```

#### 6. Deploy Application

Update `values-production.yaml` for EKS:

```yaml
ingress:
  enabled: true
  className: alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID
```

```bash
kubectl create namespace todo-app
kubectl apply -f production-secrets.yaml -n todo-app
helm install todo-app helm/todo-app -n todo-app -f values-production.yaml
```

**Cost Estimate (EKS)**:
- EKS Control Plane: $73/month
- EC2 instances (3x t3.medium): ~$90/month
- ALB: ~$22/month
- ECR storage: ~$1/month
- **Total**: ~$186/month

---

## Production Configuration

### Environment-Specific Values

Create separate values files for each environment:

```
helm/
└── values/
    ├── values-dev.yaml
    ├── values-staging.yaml
    └── values-production.yaml
```

### High Availability Configuration

```yaml
backend:
  replicaCount: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi

  # Pod anti-affinity (spread across nodes)
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - todo-backend
          topologyKey: kubernetes.io/hostname

frontend:
  replicaCount: 3
  # Similar affinity rules
```

### Autoscaling Configuration

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-app-quota
  namespace: todo-app
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "30"
```

---

## Post-Deployment

### Verify Deployment

```bash
# Check all resources
kubectl get all -n todo-app

# Check ingress
kubectl get ingress -n todo-app
kubectl describe ingress -n todo-app

# Check certificates
kubectl get certificate -n todo-app
kubectl describe certificate -n todo-app

# Test endpoints
curl https://app.yourdomain.com
curl https://api.yourdomain.com/health
```

### Set up Monitoring

See [MONITORING.md](./MONITORING.md) for:
- Prometheus & Grafana setup
- Custom dashboards
- Alerting rules
- Log aggregation with ELK or Loki

### Configure CI/CD

See [CICD.md](./CICD.md) for:
- GitHub Actions workflows
- GitLab CI/CD pipelines
- Automated testing
- Rolling deployments

---

## Monitoring & Scaling

### Install Prometheus & Grafana

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Default credentials: admin / prom-operator
```

### Horizontal Pod Autoscaler

```bash
# HPA is automatically created if autoscaling.enabled=true in values

# Check HPA status
kubectl get hpa -n todo-app

# Manual scaling (if HPA disabled)
kubectl scale deployment todo-app-backend --replicas=5 -n todo-app
```

### Vertical Pod Autoscaler (Optional)

```bash
# Install VPA
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/vertical-pod-autoscaler/deploy/vpa-v1-crd-gen.yaml

# Apply VPA to deployment
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: todo-app-backend-vpa
  namespace: todo-app
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-app-backend
  updatePolicy:
    updateMode: "Auto"
EOF
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod POD_NAME -n todo-app

# Check logs
kubectl logs POD_NAME -n todo-app

# Common causes:
# - Image pull errors (check registry authentication)
# - Resource limits too low
# - Missing secrets or configmaps
# - Liveness/readiness probe failures
```

#### Image Pull Errors

```bash
# DigitalOcean
doctl kubernetes cluster registry add todo-app-cluster

# GKE (usually automatic)
# Ensure service account has artifactregistry.reader role

# EKS
# Verify ECR permissions in node IAM role
```

#### Certificate Not Issuing

```bash
# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check certificate status
kubectl describe certificate app-tls -n todo-app

# Check challenges
kubectl get challenges -n todo-app

# Common issues:
# - DNS not propagated
# - Ingress misconfigured
# - Rate limiting (use staging issuer for testing)
```

#### Backend Cannot Connect to Database

```bash
# Check secret
kubectl get secret app-secrets -n todo-app -o yaml

# Decode and verify database URL
kubectl get secret app-secrets -n todo-app -o jsonpath='{.data.database-url}' | base64 -d

# Test connection from pod
kubectl exec -it POD_NAME -n todo-app -- /bin/sh
# (inside pod) curl $DATABASE_URL
```

### Debugging Commands

```bash
# Get pod shell
kubectl exec -it POD_NAME -n todo-app -- /bin/sh

# View pod events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Restart deployment
kubectl rollout restart deployment/todo-app-backend -n todo-app
```

---

## Backup & Disaster Recovery

### Database Backups

```bash
# For PostgreSQL (Neon)
# - Neon provides automatic backups
# - Configure retention policy in Neon dashboard

# Manual backup
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup-20241227.sql
```

### Kubernetes Backup

```bash
# Install Velero for cluster backups
# https://velero.io/docs/v1.12/basic-install/

# Backup namespace
velero backup create todo-app-backup --include-namespaces todo-app

# Restore
velero restore create --from-backup todo-app-backup
```

---

## Security Best Practices

1. **Network Policies**: Restrict pod-to-pod communication
2. **Pod Security Standards**: Enforce restricted policies
3. **Secret Management**: Use external secret managers (AWS Secrets Manager, Google Secret Manager)
4. **Image Scanning**: Scan images for vulnerabilities before deployment
5. **RBAC**: Implement least-privilege access control
6. **TLS Everywhere**: Use mTLS for service-to-service communication

---

## Next Steps

- [ ] Set up production database (managed PostgreSQL)
- [ ] Configure monitoring and alerting
- [ ] Implement CI/CD pipeline
- [ ] Set up log aggregation
- [ ] Configure backup strategy
- [ ] Implement rate limiting and DDoS protection
- [ ] Set up APM (Application Performance Monitoring)
- [ ] Configure CDN for frontend assets

---

## Support & Resources

- **Documentation**: [specs/004-phase-4-local-deployment/](../specs/004-phase-4-local-deployment/)
- **Helm Chart**: [helm/todo-app/](../helm/todo-app/)
- **GitHub Issues**: Report bugs and request features
- **Community**: Join discussions on GitHub Discussions

---

**Last Updated**: 2025-12-27
**Version**: 1.0.0
