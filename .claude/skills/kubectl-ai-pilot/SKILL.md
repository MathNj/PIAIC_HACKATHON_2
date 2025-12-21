---
name: kubectl-ai-pilot
description: Interface with kubectl-ai for AI-assisted Kubernetes operations in Phase IV deployment. Use when: (1) Deploying applications to Kubernetes/Minikube, (2) Generating Deployment or Service manifests from natural language, (3) Debugging pod crashes or failures, (4) Scaling deployments or managing replicas, (5) Troubleshooting service connectivity issues, (6) Querying cluster status with natural language, or (7) Any Kubernetes task requiring AI-assisted manifest generation. Wraps `kubectl-ai` CLI commands, handles confirmation prompts, verifies manifests before applying, and provides fallback to standard kubectl commands when kubectl-ai unavailable. Required for Phase IV Kubernetes deployment.
---

# kubectl-ai Pilot

AI-assisted Kubernetes operations using kubectl-ai for Phase IV deployment to Minikube.

## Overview

kubectl-ai Pilot interfaces with kubectl-ai (Kubernetes AI plugin) to provide intelligent cluster operations:
- Natural language manifest generation (Deployments, Services, Ingress)
- AI-powered pod debugging and crash diagnosis
- Automated manifest verification before applying
- Confirmation prompt handling
- Fallback to standard kubectl commands when kubectl-ai unavailable

**Phase IV Requirement:** This skill is mandatory for all Kubernetes deployment tasks in Phase IV.

## Quick Start

### Prerequisites

**kubectl-ai Available (Required):**
- kubectl installed and configured for Minikube
- kubectl-ai plugin installed (via krew)
- Minikube cluster running

**kubectl-ai Unavailable (Fallback):**
- Standard kubectl CLI
- Uses templates from `assets/k8s-templates/`

### Installation

```bash
# Install krew (kubectl plugin manager)
kubectl krew install ai

# Verify kubectl-ai
kubectl ai --version

# Start Minikube
minikube start
```

### Basic Workflow

1. **Describe Intent** in natural language
2. **kubectl-ai Generates** manifest
3. **Verify** manifest before applying
4. **Apply** to Minikube cluster
5. **Validate** deployment

## Common Use Cases

### 1. Deploy Application with Replicas

```bash
# Using kubectl_ai_wrapper.py
python scripts/kubectl_ai_wrapper.py "deploy todo-frontend with 2 replicas using image todo-frontend:latest"

# Direct kubectl-ai command
kubectl ai "deploy todo-frontend with 2 replicas using image todo-frontend:latest"
```

**kubectl-ai generates:**
- Deployment manifest with 2 replicas
- Resource limits and requests
- Health checks
- Security context (non-root user)

**Apply generated manifest:**
```bash
# Extract manifest from kubectl-ai output
python scripts/kubectl_ai_wrapper.py "deploy frontend" --json > response.json

# Apply with verification
python scripts/apply_k8s_manifest.py deployment.yaml
```

### 2. Create Service

```bash
# Generate Service manifest
python scripts/kubectl_ai_wrapper.py "create service for todo-frontend on port 80 targeting container port 3000"

# Or direct command
kubectl ai "expose deployment todo-frontend as nodeport service on port 30080"
```

**kubectl-ai provides:**
- Service manifest (ClusterIP/NodePort/LoadBalancer)
- Port mappings
- Selector matching Deployment labels

### 3. Debug Pod Crash

```bash
# Get crashed pod name
POD_NAME=$(kubectl get pods --field-selector=status.phase=Failed -o jsonpath='{.items[0].metadata.name}')

# Ask kubectl-ai to diagnose
python scripts/kubectl_ai_wrapper.py "why is pod ${POD_NAME} crashing?"

# Or direct
kubectl ai "analyze crashloopbackoff in pod frontend-abc123"
```

**kubectl-ai analyzes:**
- Exit codes and error messages
- Resource constraints (OOMKilled)
- Image pull failures
- Configuration issues

### 4. Scale Deployment

```bash
# Scale with kubectl-ai
kubectl ai "scale todo-frontend deployment to 3 replicas"

# Or using wrapper
python scripts/kubectl_ai_wrapper.py "increase frontend replicas to 4" --auto-confirm
```

### 5. Query Cluster Status

```bash
# Natural language queries
kubectl ai "show all failed pods"
kubectl ai "which pods are using the most memory?"
kubectl ai "list deployments in namespace default"
```

## Workflow Patterns

### Pattern 1: Generate, Verify, Apply

```bash
# Step 1: Generate manifest with kubectl-ai
python scripts/kubectl_ai_wrapper.py "deploy backend on port 8000 with 2 replicas" --json > response.json

# Step 2: Extract manifest
jq -r '.manifests[0].content' response.json > deployment.yaml

# Step 3: Verify manifest (dry-run)
python scripts/apply_k8s_manifest.py deployment.yaml --dry-run

# Step 4: Review manifest
cat deployment.yaml

# Step 5: Apply to cluster
python scripts/apply_k8s_manifest.py deployment.yaml

# Step 6: Verify deployment
kubectl get deployments
kubectl get pods
```

### Pattern 2: Full Stack Deployment

```bash
# Deploy backend
python scripts/kubectl_ai_wrapper.py "deploy todo-backend with image todo-backend:latest on port 8000"
python scripts/apply_k8s_manifest.py backend-deployment.yaml

# Create backend service
python scripts/kubectl_ai_wrapper.py "create clusterip service for todo-backend on port 8000"
python scripts/apply_k8s_manifest.py backend-service.yaml

# Deploy frontend
python scripts/kubectl_ai_wrapper.py "deploy todo-frontend with 2 replicas on port 3000"
python scripts/apply_k8s_manifest.py frontend-deployment.yaml

# Expose frontend externally
python scripts/kubectl_ai_wrapper.py "create nodeport service for todo-frontend on port 30080"
python scripts/apply_k8s_manifest.py frontend-service.yaml

# Verify full stack
kubectl get all
minikube service todo-frontend-service --url
```

### Pattern 3: Troubleshooting with AI

```bash
# Check pod status
kubectl get pods

# Pod is failing - ask kubectl-ai
python scripts/kubectl_ai_wrapper.py "pod todo-backend-xyz is in CrashLoopBackOff, why?"

# kubectl-ai suggests:
# - Check logs: kubectl logs todo-backend-xyz
# - Verify env vars: DATABASE_URL might be missing
# - Check resource limits: Pod might be OOMKilled

# Apply fixes based on AI suggestions
kubectl ai "update todo-backend deployment with environment variable DATABASE_URL=..."
```

### Pattern 4: Fallback When kubectl-ai Unavailable

```python
# Automatic fallback in kubectl_ai_wrapper.py
from scripts.kubectl_ai_wrapper import KubectlAIWrapper

wrapper = KubectlAIWrapper()
response = wrapper.execute_prompt("deploy app with 2 replicas")

if response["fallback_used"]:
    print("⚠️  kubectl-ai unavailable - using template")
    # Use template from assets/k8s-templates/deployment.yaml
    import shutil
    shutil.copy("assets/k8s-templates/deployment.yaml", "deployment.yaml")
    print("✅ Customize deployment.yaml and apply manually")
else:
    print("✅ kubectl-ai generated manifest")
    # Use manifest from response
```

## Script Reference

### kubectl_ai_wrapper.py

**Purpose:** Execute kubectl-ai commands programmatically

**Usage:**
```bash
python scripts/kubectl_ai_wrapper.py <prompt> [options]

Options:
  --namespace <ns>     Kubernetes namespace (default: default)
  --auto-confirm       Auto-confirm kubectl-ai actions (use with caution)
  --json               Output JSON format
```

**Examples:**
```bash
# Basic deployment
python scripts/kubectl_ai_wrapper.py "deploy app with 2 replicas"

# With namespace
python scripts/kubectl_ai_wrapper.py "create service for backend" --namespace production

# Auto-confirm (skip prompts)
python scripts/kubectl_ai_wrapper.py "scale frontend to 3" --auto-confirm

# JSON output
python scripts/kubectl_ai_wrapper.py "deploy app" --json
```

**Returns:**
```json
{
  "success": true,
  "output": "kubectl-ai natural language response",
  "manifests": [
    {
      "kind": "Deployment",
      "name": "app",
      "content": "apiVersion: apps/v1\nkind: Deployment\n..."
    }
  ],
  "commands": ["kubectl apply -f deployment.yaml"],
  "fallback_used": false,
  "error": null
}
```

### apply_k8s_manifest.py

**Purpose:** Apply and validate Kubernetes manifests

**Usage:**
```bash
python scripts/apply_k8s_manifest.py <manifest> [options]

Options:
  --namespace <ns>      Kubernetes namespace (default: default)
  --dry-run             Validate only (don't apply)
  --validate            Validate YAML syntax only
  --rollback <resource> Delete specified resource
  --status <resource>   Get resource status
  --history             List apply history
```

**Examples:**
```bash
# Apply manifest
python scripts/apply_k8s_manifest.py deployment.yaml

# Dry-run (validate)
python scripts/apply_k8s_manifest.py deployment.yaml --dry-run

# Apply to specific namespace
python scripts/apply_k8s_manifest.py deployment.yaml --namespace production

# Rollback (delete resource)
python scripts/apply_k8s_manifest.py --rollback deployment/frontend

# Check resource status
python scripts/apply_k8s_manifest.py --status deployment/frontend

# View apply history
python scripts/apply_k8s_manifest.py --history
```

**Features:**
- ✅ YAML syntax validation
- ✅ kubectl dry-run before applying
- ✅ Apply history tracking
- ✅ Resource status checking
- ✅ Rollback capability

## Manifest Templates

When kubectl-ai unavailable, use production-ready templates:

### Deployment Template

```bash
cp assets/k8s-templates/deployment.yaml ./deployment.yaml
# Edit TODOs: app name, image, ports, replicas
kubectl apply -f deployment.yaml
```

**Includes:**
- Resource limits/requests
- Liveness and readiness probes
- Security context (non-root)
- ConfigMap example

### Service Template

```bash
cp assets/k8s-templates/service.yaml ./service.yaml
# Edit: service name, ports, type (ClusterIP/NodePort/LoadBalancer)
kubectl apply -f service.yaml
```

**Includes:**
- ClusterIP (internal)
- NodePort (external - Minikube)
- LoadBalancer (cloud)

## Advanced Reference

For detailed kubectl-ai command patterns and best practices, see:

**`references/kubectl-ai-commands.md`**
- Complete kubectl-ai command reference
- Deployment, service, and networking commands
- Debugging and troubleshooting patterns
- Scaling and update strategies

## Integration with cloudops-engineer

This skill is designed for the **cloudops-engineer** agent in Phase IV:

```python
# cloudops-engineer uses kubectl-ai-pilot
from scripts.kubectl_ai_wrapper import KubectlAIWrapper
from scripts.apply_k8s_manifest import K8sManifestApplier

# Generate Deployment manifest
kubectl_ai = KubectlAIWrapper()
response = kubectl_ai.execute_prompt(
    "deploy todo-frontend with 2 replicas using image todo-frontend:latest",
    namespace="default"
)

# Extract and save manifest
if response["success"] and response["manifests"]:
    deployment = response["manifests"][0]
    with open("deployment.yaml", "w") as f:
        f.write(deployment["content"])

    # Verify and apply
    applier = K8sManifestApplier(namespace="default")
    result = applier.apply_manifest(Path("deployment.yaml"))

    if result["success"]:
        print(f"✅ Deployed: {result['applied_resources']}")
```

## Confirmation Handling

kubectl-ai requires confirmation for certain operations. Handle it automatically:

```bash
# Auto-confirm mode (use with caution)
python scripts/kubectl_ai_wrapper.py "deploy app" --auto-confirm

# Or pipe 'yes'
echo "yes" | kubectl ai "deploy app"
```

**Recommended:** Review manifests before applying:
```bash
# Generate manifest
kubectl ai "deploy app" > deployment.yaml

# Review
cat deployment.yaml

# Apply after review
kubectl apply -f deployment.yaml
```

## Minikube-Specific Patterns

### Accessing Services

```bash
# NodePort service access
minikube service <service-name> --url

# Or get URL
URL=$(minikube service <service-name> --url)
curl $URL
```

### Local Image Loading

```bash
# Load local image to Minikube
minikube image load todo-frontend:latest

# Or use Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-frontend:latest .
```

## Best Practices

### 1. Always Verify Before Applying

```bash
# Dry-run first
python scripts/apply_k8s_manifest.py deployment.yaml --dry-run

# Review manifest
cat deployment.yaml

# Then apply
python scripts/apply_k8s_manifest.py deployment.yaml
```

### 2. Use Specific Prompts

```bash
# ❌ Vague
kubectl ai "deploy app"

# ✅ Specific
kubectl ai "deploy todo-frontend with 2 replicas using image todo-frontend:latest on port 3000 with health check on /health"
```

### 3. Track Applied Resources

```bash
# View history
python scripts/apply_k8s_manifest.py --history

# Check status before changes
python scripts/apply_k8s_manifest.py --status deployment/frontend
```

### 4. Handle Namespace Consistently

```bash
# Always specify namespace
kubectl ai "deploy app" --namespace production

# Or set default namespace
kubectl config set-context --current --namespace=production
```

## Troubleshooting

### kubectl-ai Not Found

```bash
# Install kubectl-ai
kubectl krew install ai

# Verify
kubectl ai --version
```

### Manifest Generation Fails

```bash
# Check kubectl-ai output
kubectl ai "deploy app" 2>&1 | tee error.log

# Fallback to template
cp assets/k8s-templates/deployment.yaml ./deployment.yaml
```

### Apply Fails

```bash
# Validate YAML
python scripts/apply_k8s_manifest.py deployment.yaml --validate

# Dry-run
python scripts/apply_k8s_manifest.py deployment.yaml --dry-run

# Check cluster connection
kubectl cluster-info
```

### Pod Not Starting

```bash
# Ask kubectl-ai to diagnose
kubectl ai "why is pod <pod-name> not starting?"

# Check logs
kubectl logs <pod-name>

# Describe pod
kubectl describe pod <pod-name>
```

## Quick Command Reference

```bash
# Deploy
python scripts/kubectl_ai_wrapper.py "deploy <app> with <n> replicas"

# Service
python scripts/kubectl_ai_wrapper.py "create service for <app>"

# Scale
kubectl ai "scale <deployment> to <n> replicas"

# Debug
kubectl ai "why is pod <name> crashing?"

# Apply manifest
python scripts/apply_k8s_manifest.py <manifest>.yaml

# Verify
python scripts/apply_k8s_manifest.py <manifest>.yaml --dry-run

# Rollback
python scripts/apply_k8s_manifest.py --rollback deployment/<name>
```

## Phase IV Compliance

✅ **kubectl-ai First:** Always attempt kubectl-ai before fallback
✅ **Manifest Verification:** All manifests validated before applying
✅ **Confirmation Handling:** Auto-confirm support with --auto-confirm flag
✅ **Minikube Ready:** Optimized for local Minikube deployment
✅ **Fallback Available:** Templates when kubectl-ai unavailable
✅ **History Tracking:** All applies tracked for rollback
✅ **Integration Ready:** Designed for cloudops-engineer agent
