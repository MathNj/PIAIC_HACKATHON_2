# kubectl-ai Command Reference

Comprehensive guide to using kubectl-ai for AI-assisted Kubernetes operations.

## Table of Contents
- Getting Started
- Deployment Commands
- Service and Networking
- Debugging and Troubleshooting
- Scaling and Updates
- Best Practices

## Getting Started

### Installation

kubectl-ai is a kubectl plugin. Install it via krew:

```bash
# Install krew (kubectl plugin manager)
# See: https://krew.sigs.k8s.io/docs/user-guide/setup/install/

# Install kubectl-ai
kubectl krew install ai

# Verify installation
kubectl ai --version
```

### Basic Usage

```bash
# Basic prompt
kubectl ai "deploy my app with 2 replicas"

# With namespace
kubectl ai "create service for backend" --namespace production

# Auto-confirm (skip prompts)
kubectl ai "scale frontend to 3" --auto-confirm
```

## Deployment Commands

### Create Deployment

**Basic Deployment:**
```bash
kubectl ai "deploy todo-frontend using image todo-frontend:latest with 2 replicas"
kubectl ai "create deployment for backend app on port 8000"
kubectl ai "deploy fastapi app with 3 replicas using python:3.13 image"
```

**With Resource Limits:**
```bash
kubectl ai "deploy app with memory limit 256Mi and cpu limit 200m"
kubectl ai "create deployment with resource requests: 100m cpu, 128Mi memory"
```

**With Environment Variables:**
```bash
kubectl ai "deploy app with environment variable DATABASE_URL=postgres://..."
kubectl ai "create deployment with env vars from configmap app-config"
```

**With Health Checks:**
```bash
kubectl ai "deploy app with liveness probe on /health endpoint"
kubectl ai "create deployment with readiness probe checking port 8000"
```

### Update Deployment

```bash
kubectl ai "update frontend deployment image to todo-frontend:v2"
kubectl ai "change backend replicas to 4"
kubectl ai "rollout restart deployment frontend"
```

## Service and Networking

### Create Service

**ClusterIP (Internal):**
```bash
kubectl ai "create service for frontend deployment"
kubectl ai "expose deployment backend on port 80 targeting container port 8000"
```

**NodePort (External Access):**
```bash
kubectl ai "create nodeport service for frontend on port 30080"
kubectl ai "expose deployment as nodeport service"
```

**LoadBalancer:**
```bash
kubectl ai "create loadbalancer service for api on port 80"
kubectl ai "expose deployment with loadbalancer type"
```

### Ingress

```bash
kubectl ai "create ingress for frontend service with host todo.example.com"
kubectl ai "setup ingress routing /api to backend and / to frontend"
```

## Debugging and Troubleshooting

### Pod Issues

**Crash Diagnosis:**
```bash
kubectl ai "why is my pod crashing?"
kubectl ai "debug pod frontend-abc123"
kubectl ai "analyze crashloopbackoff in pod backend-xyz789"
```

**Log Analysis:**
```bash
kubectl ai "show me the logs from frontend pod"
kubectl ai "what errors are in the backend pod logs?"
kubectl ai "analyze pod events for frontend"
```

**Resource Issues:**
```bash
kubectl ai "why is my pod stuck in pending state?"
kubectl ai "pod is being evicted, why?"
kubectl ai "container is OOMKilled, what's happening?"
```

### Service Connectivity

```bash
kubectl ai "why can't frontend connect to backend service?"
kubectl ai "debug service connectivity for api"
kubectl ai "test if backend service is reachable"
```

### Network Policies

```bash
kubectl ai "why is network policy blocking traffic?"
kubectl ai "debug network connectivity between pods"
```

## Scaling and Updates

### Scaling

**Manual Scaling:**
```bash
kubectl ai "scale frontend to 5 replicas"
kubectl ai "reduce backend replicas to 2"
kubectl ai "set deployment replicas to 3"
```

**Autoscaling:**
```bash
kubectl ai "setup horizontal pod autoscaler for frontend"
kubectl ai "create HPA with min 2 max 10 replicas at 80% CPU"
kubectl ai "enable autoscaling for backend targeting 70% memory"
```

### Rolling Updates

```bash
kubectl ai "update frontend image to v2 with rolling update"
kubectl ai "rollback deployment frontend to previous version"
kubectl ai "check rollout status of backend deployment"
```

### Resource Management

```bash
kubectl ai "update deployment resource limits to 512Mi memory"
kubectl ai "change cpu requests to 200m for frontend"
```

## Configuration Management

### ConfigMaps

```bash
kubectl ai "create configmap from file app.conf"
kubectl ai "create configmap with key-value pairs"
kubectl ai "mount configmap as volume in deployment"
```

### Secrets

```bash
kubectl ai "create secret for database credentials"
kubectl ai "use secret in deployment as environment variable"
kubectl ai "mount secret as file in pod"
```

## Cluster Status and Queries

### List Resources

```bash
kubectl ai "show all deployments"
kubectl ai "list all services in namespace production"
kubectl ai "get pods that are not running"
kubectl ai "show failed pods"
```

### Resource Status

```bash
kubectl ai "check status of frontend deployment"
kubectl ai "is backend service running?"
kubectl ai "show deployment rollout history"
```

### Resource Usage

```bash
kubectl ai "show pod resource usage"
kubectl ai "which pods are using the most memory?"
kubectl ai "check node resource allocation"
```

## Best Practices

### Effective Prompts

**Be Specific:**
```bash
# ❌ Too vague
kubectl ai "deploy app"

# ✅ Specific
kubectl ai "deploy todo-frontend using image todo-frontend:latest with 2 replicas on port 3000"
```

**Include Context:**
```bash
# ❌ No context
kubectl ai "why isn't this working?"

# ✅ With context
kubectl ai "frontend pod shows ImagePullBackOff error, image is todo-frontend:latest"
```

### Confirmation Handling

kubectl-ai requires confirmation for destructive operations:

```bash
# Interactive (asks for confirmation)
kubectl ai "delete deployment frontend"

# Auto-confirm (use with caution!)
kubectl ai "delete deployment frontend" --auto-confirm
```

### Using with kubectl_ai_wrapper.py

```bash
# Generate manifest without applying
python scripts/kubectl_ai_wrapper.py "deploy frontend with 2 replicas" --json > manifest.json

# Extract manifest from JSON response
jq -r '.manifests[0].content' manifest.json > deployment.yaml

# Review and apply manually
kubectl apply -f deployment.yaml
```

## Output Parsing

kubectl-ai provides output in these formats:

### YAML Manifests

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
  ...
```

### Imperative Commands

```bash
kubectl create deployment frontend --image=frontend:latest --replicas=2
kubectl expose deployment frontend --port=80 --target-port=3000
```

### Diagnostic Information

```
Pod frontend-abc123 is in CrashLoopBackOff state.
Reason: Container failed with exit code 1
Last log line: Error: Cannot connect to database
Suggestion: Check DATABASE_URL environment variable
```

## Troubleshooting kubectl-ai

### kubectl-ai Not Found

```bash
# Check if kubectl-ai is installed
kubectl plugin list | grep ai

# Install via krew
kubectl krew install ai

# Or add to PATH
export PATH="${PATH}:${HOME}/.krew/bin"
```

### Confirmation Prompts Not Working

```bash
# Use --auto-confirm flag
kubectl ai "deploy app" --auto-confirm

# Or pipe 'yes'
echo "yes" | kubectl ai "deploy app"
```

### Generated Manifest Has Errors

```bash
# Validate before applying
kubectl ai "deploy app" > manifest.yaml
kubectl apply --dry-run=client -f manifest.yaml

# Or use apply_k8s_manifest.py
python scripts/apply_k8s_manifest.py manifest.yaml --dry-run
```

## Integration with cloudops-engineer

```python
# Example: cloudops-engineer using kubectl-ai-pilot
from scripts.kubectl_ai_wrapper import KubectlAIWrapper

# Generate Deployment manifest
wrapper = KubectlAIWrapper()
response = wrapper.execute_prompt(
    "deploy todo-frontend with 2 replicas using image todo-frontend:latest",
    namespace="default"
)

# Extract and save manifest
if response["success"] and response["manifests"]:
    manifest = response["manifests"][0]
    with open("deployment.yaml", "w") as f:
        f.write(manifest["content"])

    # Apply manifest
    import subprocess
    subprocess.run(["python", "scripts/apply_k8s_manifest.py", "deployment.yaml"])
```

## Quick Reference

```bash
# Deploy
kubectl ai "deploy <app> with <n> replicas"

# Expose
kubectl ai "create service for <deployment>"

# Scale
kubectl ai "scale <deployment> to <n> replicas"

# Debug
kubectl ai "why is <pod> crashing?"

# Update
kubectl ai "update <deployment> image to <image:tag>"

# Delete
kubectl ai "delete deployment <name>"

# Status
kubectl ai "show status of <resource>"
```
