---
name: "k8s-troubleshoot"
description: "Diagnoses and fixes Kubernetes deployment issues: pod failures, ImagePullBackOff, CrashLoopBackOff, service connectivity, resource limits, and Dapr sidecar problems."
version: "1.0.0"
---

# Kubernetes Troubleshooting Skill

## When to Use
- User reports "pod not starting" or "deployment failed"
- Error messages show ImagePullBackOff, CrashLoopBackOff, or OOMKilled
- Services not accessible via LoadBalancer or ClusterIP
- Dapr sidecar not injecting (0/2 or 1/2 pods)
- Resource quota exceeded or node resources exhausted
- Environment variables or secrets not loading
- Health checks failing repeatedly

## Context
This skill handles Kubernetes troubleshooting following:
- **Orchestration**: Kubernetes 1.28+
- **Local**: Minikube (Docker driver)
- **Production**: DigitalOcean Kubernetes Service (DOKS)
- **Service Mesh**: Dapr 1.13+ (sidecar injection)
- **Container Registry**: DigitalOcean Container Registry
- **Deployments**: Backend, Frontend, Notification Service, Recurring Task Service

## Workflow
1. **Check Pod Status**: Identify which pods are failing
2. **Read Pod Events**: Get detailed error messages
3. **Check Logs**: Review container and sidecar logs
4. **Inspect Configuration**: Verify deployment manifests
5. **Test Connectivity**: Check service networking
6. **Review Resources**: Ensure CPU/memory limits not exceeded
7. **Fix Root Cause**: Apply targeted solution
8. **Verify Fix**: Confirm pods running and healthy

## Diagnostic Commands

### 1. Check Pod Status

```bash
# List all pods
kubectl get pods

# List pods for specific deployment
kubectl get pods -l app=backend

# Wide output with node and IP
kubectl get pods -o wide

# Watch pod status in real-time
kubectl get pods -w
```

**Expected Output**:
```
NAME                       READY   STATUS    RESTARTS   AGE
backend-5787c9f954-zc72w   2/2     Running   0          2h
frontend-6b8d4c9f7d-8xk2m  1/1     Running   0          2h
```

**Problem Indicators**:
- `0/2` or `1/2` READY: Container not starting or Dapr sidecar not injecting
- `CrashLoopBackOff`: Container starting then crashing repeatedly
- `ImagePullBackOff`: Cannot pull image from registry
- `Pending`: Pod cannot be scheduled (resource constraints)
- `OOMKilled`: Container exceeded memory limit
- `Error`: Container exited with error code

### 2. Describe Pod (Detailed Events)

```bash
# Get detailed pod information including events
kubectl describe pod <pod-name>

# Example
kubectl describe pod backend-5787c9f954-zc72w
```

**Key Sections to Check**:

**Events** (bottom of output):
```
Events:
  Type     Reason     Age   From               Message
  ----     ------     ----  ----               -------
  Normal   Scheduled  2m    default-scheduler  Successfully assigned default/backend-xxx to node1
  Normal   Pulling    2m    kubelet            Pulling image "registry.digitalocean.com/todo-chatbot-reg/backend:latest"
  Normal   Pulled     1m    kubelet            Successfully pulled image
  Normal   Created    1m    kubelet            Created container backend
  Normal   Started    1m    kubelet            Started container backend
```

**Error Examples**:
```
Warning  Failed     1m    kubelet  Failed to pull image "backend:latest": rpc error: code = Unknown desc = Error response from daemon: pull access denied
Warning  BackOff    30s   kubelet  Back-off pulling image "backend:latest"
```

### 3. Check Container Logs

```bash
# Get logs from main container
kubectl logs <pod-name>

# Get logs from specific container (for multi-container pods)
kubectl logs <pod-name> -c backend
kubectl logs <pod-name> -c daprd  # Dapr sidecar

# Follow logs in real-time
kubectl logs <pod-name> -f

# Get previous container logs (if crashed)
kubectl logs <pod-name> --previous

# Tail last 100 lines
kubectl logs <pod-name> --tail=100
```

**Example - Backend Startup Logs**:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Example - Error Logs**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused
ERROR: Database connection failed
```

### 4. Check Deployment Configuration

```bash
# Get deployment YAML
kubectl get deployment backend -o yaml

# Check deployment status
kubectl rollout status deployment/backend

# Check deployment history
kubectl rollout history deployment/backend

# Check replica count
kubectl get deployment backend
```

### 5. Check Service Configuration

```bash
# List services
kubectl get svc

# Describe service
kubectl describe svc backend

# Check service endpoints
kubectl get endpoints backend
```

**Expected Service Output**:
```
NAME       TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)        AGE
backend    LoadBalancer   10.245.123.45    174.138.120.69    80:30123/TCP   2h
frontend   LoadBalancer   10.245.67.89     144.126.255.56    80:30456/TCP   2h
```

**Problem Indicators**:
- `<pending>` EXTERNAL-IP: LoadBalancer provisioning or no available IPs
- No endpoints: No healthy pods behind the service
- Wrong PORT mapping: Service port doesn't match container port

### 6. Check Resource Usage

```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods

# Deployment resource limits
kubectl describe deployment backend | grep -A 5 "Limits\|Requests"
```

## Common Issues and Fixes

### Issue 1: ImagePullBackOff

**Symptom**: Pod status shows `ImagePullBackOff`

**Diagnosis**:
```bash
kubectl describe pod <pod-name>
```

**Error Message**:
```
Failed to pull image "registry.digitalocean.com/todo-chatbot-reg/backend:latest": rpc error: code = Unknown desc = Error response from daemon: pull access denied
```

**Root Causes**:
1. **Registry credentials missing or expired**
2. **Image doesn't exist in registry**
3. **Wrong image name or tag**

**Fix - Recreate Registry Secret**:
```bash
# Delete old secret
kubectl delete secret registry-todo-chatbot-reg

# Create new secret with valid token
kubectl create secret docker-registry registry-todo-chatbot-reg \
  --docker-server=registry.digitalocean.com \
  --docker-username=<token> \
  --docker-password=<token>

# Verify secret exists
kubectl get secret registry-todo-chatbot-reg

# Restart deployment to retry pull
kubectl rollout restart deployment/backend
```

**Fix - Verify Image Exists**:
```bash
# List images in registry (using doctl CLI)
doctl registry repository list-tags todo-chatbot-reg/backend

# Or manually check DigitalOcean Container Registry UI
```

### Issue 2: CrashLoopBackOff

**Symptom**: Pod status shows `CrashLoopBackOff`, restarts keep incrementing

**Diagnosis**:
```bash
# Check current logs
kubectl logs <pod-name>

# Check previous crash logs
kubectl logs <pod-name> --previous

# Check exit code
kubectl describe pod <pod-name> | grep "Exit Code"
```

**Common Exit Codes**:
- `Exit Code: 1` - Application error (check logs)
- `Exit Code: 137` - OOMKilled (memory limit exceeded)
- `Exit Code: 143` - SIGTERM (graceful shutdown)

**Root Causes**:
1. **Application startup error** (database connection failed, missing env vars)
2. **Memory limit exceeded** (OOMKilled)
3. **Port already in use**
4. **Dependency not available** (database, Redis, Kafka)

**Fix - Missing Environment Variables**:
```bash
# Check deployment env vars
kubectl get deployment backend -o yaml | grep -A 20 "env:"

# Update secret
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=GEMINI_API_KEY="..."

# Restart deployment
kubectl rollout restart deployment/backend
```

**Fix - Increase Resource Limits**:
```yaml
# Edit deployment
kubectl edit deployment backend

# Update resources section:
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"  # Increased from 512Mi
    cpu: "1000m"
```

### Issue 3: Dapr Sidecar Not Injecting

**Symptom**: Pod shows `1/1` instead of `2/2` (missing Dapr sidecar)

**Diagnosis**:
```bash
# Check Dapr annotations
kubectl get deployment backend -o yaml | grep dapr.io
```

**Expected Annotations**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"
```

**Root Causes**:
1. **Dapr not installed on cluster**
2. **Missing Dapr annotations**
3. **Dapr control plane not running**

**Fix - Install Dapr**:
```bash
# Check if Dapr is installed
kubectl get pods -n dapr-system

# If not installed, install Dapr
dapr init -k

# Verify Dapr components
kubectl get components
```

**Fix - Add Dapr Annotations**:
```bash
# Edit deployment
kubectl edit deployment backend

# Add annotations under spec.template.metadata:
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "8000"
    dapr.io/log-level: "info"
```

### Issue 4: Service Not Accessible

**Symptom**: Cannot reach service via LoadBalancer IP or ClusterIP

**Diagnosis**:
```bash
# Check service
kubectl get svc backend

# Check endpoints
kubectl get endpoints backend

# Check pod labels match service selector
kubectl get pods -l app=backend
kubectl get svc backend -o yaml | grep selector -A 2
```

**Root Causes**:
1. **No healthy pods** (all pods failing health checks)
2. **Label mismatch** (service selector doesn't match pod labels)
3. **Port mismatch** (service port doesn't match container port)
4. **LoadBalancer provisioning failed**

**Fix - Port Mismatch**:
```yaml
# Service configuration
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend  # Must match pod label
  ports:
  - protocol: TCP
    port: 80  # External port
    targetPort: 8000  # Container port (must match)
```

**Fix - Test Internal Connectivity**:
```bash
# Create test pod
kubectl run test-pod --rm -it --image=curlimages/curl -- sh

# Inside test pod, test service
curl http://backend:80/health
```

### Issue 5: Pending Pods (Resource Constraints)

**Symptom**: Pod status shows `Pending` for extended time

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check node resources
kubectl top nodes
kubectl describe nodes
```

**Error Message**:
```
Warning  FailedScheduling  1m  default-scheduler  0/2 nodes are available: 2 Insufficient cpu.
```

**Root Causes**:
1. **Insufficient CPU/memory on nodes**
2. **Resource requests too high**
3. **No nodes available**

**Fix - Reduce Resource Requests**:
```yaml
# Edit deployment
kubectl edit deployment backend

# Reduce requests:
resources:
  requests:
    memory: "128Mi"  # Reduced from 256Mi
    cpu: "100m"  # Reduced from 250m
```

**Fix - Scale Cluster** (DigitalOcean):
```bash
# Add more nodes via DOKS UI or doctl
doctl kubernetes cluster node-pool update <cluster-id> <pool-id> --count 3
```

### Issue 6: Environment Variables Not Loading

**Symptom**: Application logs show "Environment variable not found"

**Diagnosis**:
```bash
# Check deployment env vars
kubectl get deployment backend -o yaml | grep -A 30 "env:"

# Check secret exists
kubectl get secret todo-secrets

# Check secret contents (base64 encoded)
kubectl get secret todo-secrets -o yaml
```

**Fix - Verify Secret Key Names**:
```bash
# Describe secret
kubectl describe secret todo-secrets

# Deployment must reference correct keys:
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: todo-secrets
      key: DATABASE_URL  # Key name must match exactly
```

**Fix - Recreate Secret**:
```bash
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=GEMINI_API_KEY="..."

kubectl rollout restart deployment/backend
```

## Verification Steps

After applying fixes:

```bash
# 1. Check pod status
kubectl get pods -l app=backend
# Should show 2/2 READY (with Dapr) or 1/1 (without)

# 2. Check logs for errors
kubectl logs deployment/backend -c backend --tail=50

# 3. Test health endpoint
kubectl exec deployment/backend -c backend -- curl http://localhost:8000/health

# 4. Test service externally
curl http://<EXTERNAL-IP>/health

# 5. Check resource usage
kubectl top pod <pod-name>

# 6. Verify Dapr components loaded (if using Dapr)
kubectl logs <pod-name> -c daprd | grep "component loaded"
```

## Emergency Commands

**Force delete stuck pod**:
```bash
kubectl delete pod <pod-name> --force --grace-period=0
```

**Restart deployment (zero-downtime)**:
```bash
kubectl rollout restart deployment/backend
```

**Rollback to previous version**:
```bash
kubectl rollout undo deployment/backend
```

**Scale to 0 and back** (force recreation):
```bash
kubectl scale deployment/backend --replicas=0
kubectl scale deployment/backend --replicas=1
```

**Get all resources in namespace**:
```bash
kubectl get all
```

## Example Troubleshooting Session

**User Report**: "Backend pod not starting"

**Step 1: Check Status**
```bash
kubectl get pods -l app=backend
# Output: backend-xxx  0/2  CrashLoopBackOff  5  10m
```

**Step 2: Check Logs**
```bash
kubectl logs backend-xxx -c backend
# Output: sqlalchemy.exc.OperationalError: could not connect to server
```

**Step 3: Check Environment**
```bash
kubectl get deployment backend -o yaml | grep DATABASE_URL
# Output: Nothing found - env var missing!
```

**Step 4: Fix Secret**
```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..."

kubectl rollout restart deployment/backend
```

**Step 5: Verify**
```bash
kubectl get pods -l app=backend
# Output: backend-yyy  2/2  Running  0  1m

kubectl logs backend-yyy -c backend
# Output: INFO: Uvicorn running on http://0.0.0.0:8000
```

## Quality Checklist
Before closing issue:
- [ ] Pod status shows READY (2/2 for Dapr, 1/1 otherwise)
- [ ] No restarts or minimal restarts
- [ ] Logs show successful startup
- [ ] Health endpoint responding
- [ ] Service accessible via LoadBalancer/ClusterIP
- [ ] Dapr sidecar injected (if expected)
- [ ] Resource usage within limits
- [ ] No error events in `kubectl describe pod`
- [ ] Environment variables loading correctly
- [ ] External dependencies reachable (database, Redis, Kafka)
