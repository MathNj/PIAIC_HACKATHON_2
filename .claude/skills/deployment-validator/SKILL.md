---
name: "deployment-validator"
description: "Validates deployment configurations, health checks, resource limits, environment variables, and production readiness. Use after deployment to ensure services are running correctly, or before deployment to catch configuration errors."
version: "1.0.0"
---

# Deployment Validator Skill

## When to Use
- User says "Validate deployment" or "Check if deployment is working"
- After deploying to Kubernetes or cloud platform
- Before production deployment to catch issues early
- Troubleshooting deployment failures
- Verifying health checks and readiness probes
- Validating resource limits and scaling configuration
- Checking environment variables and secrets

## Context
This skill validates deployments for the Todo App across:
- **Kubernetes**: Pods, services, ingress, health checks
- **Docker**: Container health, networking, volumes
- **Environment**: Variables, secrets, configuration
- **Resources**: CPU, memory, storage limits
- **Networking**: Service connectivity, load balancing
- **Security**: RBAC, secrets management, TLS

## Workflow

### 1. Pre-Deployment Validation
- Check configuration files (YAML syntax)
- Validate resource definitions
- Verify environment variables
- Check image availability

### 2. Deployment Validation
- Verify pod status
- Check service endpoints
- Test health checks
- Validate networking

### 3. Post-Deployment Validation
- Run smoke tests
- Check logs for errors
- Verify database connectivity
- Test API endpoints

### 4. Performance Validation
- Check resource usage
- Verify autoscaling configuration
- Test load balancing

## Output Format

### Kubernetes Deployment Validation Script

**File**: `scripts/validate-deployment.sh`
```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

NAMESPACE=${1:-default}
APP_NAME=${2:-todo-app}

echo "========================================="
echo "Deployment Validation for $APP_NAME"
echo "Namespace: $NAMESPACE"
echo "========================================="

# 1. Check if namespace exists
echo -e "\n${YELLOW}[1/10] Checking namespace...${NC}"
if kubectl get namespace $NAMESPACE &> /dev/null; then
  echo -e "${GREEN}✓${NC} Namespace '$NAMESPACE' exists"
else
  echo -e "${RED}✗${NC} Namespace '$NAMESPACE' not found"
  exit 1
fi

# 2. Check deployments
echo -e "\n${YELLOW}[2/10] Checking deployments...${NC}"
DEPLOYMENTS=$(kubectl get deployments -n $NAMESPACE -l app=$APP_NAME -o name 2>/dev/null || echo "")
if [ -z "$DEPLOYMENTS" ]; then
  echo -e "${RED}✗${NC} No deployments found for app=$APP_NAME"
  exit 1
fi

for deployment in $DEPLOYMENTS; do
  NAME=$(echo $deployment | cut -d/ -f2)
  READY=$(kubectl get deployment $NAME -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
  DESIRED=$(kubectl get deployment $NAME -n $NAMESPACE -o jsonpath='{.spec.replicas}')

  if [ "$READY" == "$DESIRED" ]; then
    echo -e "${GREEN}✓${NC} $NAME: $READY/$DESIRED replicas ready"
  else
    echo -e "${RED}✗${NC} $NAME: $READY/$DESIRED replicas ready"
    kubectl describe deployment $NAME -n $NAMESPACE | tail -20
    exit 1
  fi
done

# 3. Check pods
echo -e "\n${YELLOW}[3/10] Checking pods...${NC}"
PODS=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o jsonpath='{.items[*].metadata.name}')
if [ -z "$PODS" ]; then
  echo -e "${RED}✗${NC} No pods found"
  exit 1
fi

for pod in $PODS; do
  STATUS=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.status.phase}')
  READY=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')

  if [ "$STATUS" == "Running" ] && [ "$READY" == "True" ]; then
    echo -e "${GREEN}✓${NC} $pod: Running and Ready"
  else
    echo -e "${RED}✗${NC} $pod: Status=$STATUS, Ready=$READY"
    kubectl describe pod $pod -n $NAMESPACE | tail -20
    kubectl logs $pod -n $NAMESPACE --tail=50
    exit 1
  fi
done

# 4. Check services
echo -e "\n${YELLOW}[4/10] Checking services...${NC}"
SERVICES=$(kubectl get services -n $NAMESPACE -l app=$APP_NAME -o name 2>/dev/null || echo "")
if [ -z "$SERVICES" ]; then
  echo -e "${YELLOW}⚠${NC} No services found (may be expected)"
else
  for service in $SERVICES; do
    NAME=$(echo $service | cut -d/ -f2)
    TYPE=$(kubectl get service $NAME -n $NAMESPACE -o jsonpath='{.spec.type}')
    CLUSTER_IP=$(kubectl get service $NAME -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    echo -e "${GREEN}✓${NC} $NAME: Type=$TYPE, ClusterIP=$CLUSTER_IP"
  done
fi

# 5. Check ingress
echo -e "\n${YELLOW}[5/10] Checking ingress...${NC}"
INGRESSES=$(kubectl get ingress -n $NAMESPACE -l app=$APP_NAME -o name 2>/dev/null || echo "")
if [ -z "$INGRESSES" ]; then
  echo -e "${YELLOW}⚠${NC} No ingress found (may use LoadBalancer instead)"
else
  for ingress in $INGRESSES; do
    NAME=$(echo $ingress | cut -d/ -f2)
    HOSTS=$(kubectl get ingress $NAME -n $NAMESPACE -o jsonpath='{.spec.rules[*].host}')
    echo -e "${GREEN}✓${NC} $NAME: Hosts=$HOSTS"
  done
fi

# 6. Check ConfigMaps
echo -e "\n${YELLOW}[6/10] Checking ConfigMaps...${NC}"
CONFIGMAPS=$(kubectl get configmap -n $NAMESPACE -l app=$APP_NAME -o name 2>/dev/null || echo "")
if [ -z "$CONFIGMAPS" ]; then
  echo -e "${YELLOW}⚠${NC} No ConfigMaps found"
else
  for cm in $CONFIGMAPS; do
    NAME=$(echo $cm | cut -d/ -f2)
    echo -e "${GREEN}✓${NC} $NAME exists"
  done
fi

# 7. Check Secrets
echo -e "\n${YELLOW}[7/10] Checking Secrets...${NC}"
SECRETS=$(kubectl get secret -n $NAMESPACE -l app=$APP_NAME -o name 2>/dev/null || echo "")
if [ -z "$SECRETS" ]; then
  echo -e "${YELLOW}⚠${NC} No Secrets found (may use external secrets)"
else
  for secret in $SECRETS; do
    NAME=$(echo $secret | cut -d/ -f2)
    echo -e "${GREEN}✓${NC} $NAME exists"
  done
fi

# 8. Check PersistentVolumeClaims
echo -e "\n${YELLOW}[8/10] Checking PersistentVolumeClaims...${NC}"
PVCS=$(kubectl get pvc -n $NAMESPACE -l app=$APP_NAME -o name 2>/dev/null || echo "")
if [ -z "$PVCS" ]; then
  echo -e "${YELLOW}⚠${NC} No PVCs found"
else
  for pvc in $PVCS; do
    NAME=$(echo $pvc | cut -d/ -f2)
    STATUS=$(kubectl get pvc $NAME -n $NAMESPACE -o jsonpath='{.status.phase}')
    if [ "$STATUS" == "Bound" ]; then
      echo -e "${GREEN}✓${NC} $NAME: Bound"
    else
      echo -e "${RED}✗${NC} $NAME: Status=$STATUS"
      exit 1
    fi
  done
fi

# 9. Check resource limits
echo -e "\n${YELLOW}[9/10] Checking resource limits...${NC}"
for pod in $PODS; do
  CONTAINERS=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.spec.containers[*].name}')
  for container in $CONTAINERS; do
    LIMITS=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath="{.spec.containers[?(@.name=='$container')].resources.limits}")
    REQUESTS=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath="{.spec.containers[?(@.name=='$container')].resources.requests}")

    if [ -z "$LIMITS" ] || [ "$LIMITS" == "{}" ]; then
      echo -e "${YELLOW}⚠${NC} $pod/$container: No resource limits set"
    else
      echo -e "${GREEN}✓${NC} $pod/$container: Limits set"
    fi
  done
done

# 10. Check logs for errors
echo -e "\n${YELLOW}[10/10] Checking logs for errors...${NC}"
ERROR_COUNT=0
for pod in $PODS; do
  ERRORS=$(kubectl logs $pod -n $NAMESPACE --tail=100 | grep -i "error\|exception\|fatal" | wc -l)
  if [ "$ERRORS" -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} $pod: Found $ERRORS error messages in logs"
    ERROR_COUNT=$((ERROR_COUNT + ERRORS))
  else
    echo -e "${GREEN}✓${NC} $pod: No errors in recent logs"
  fi
done

if [ "$ERROR_COUNT" -gt 10 ]; then
  echo -e "${RED}✗${NC} Too many errors found in logs ($ERROR_COUNT)"
  exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}✓ Deployment validation passed!${NC}"
echo "========================================="
```

### Health Check Validator

**File**: `scripts/health-check.sh`
```bash
#!/bin/bash
set -e

BACKEND_URL=${1:-http://localhost:8000}
FRONTEND_URL=${2:-http://localhost:3000}

echo "Validating health endpoints..."

# Backend health check
echo -n "Backend health ($BACKEND_URL/health): "
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health)
if [ "$BACKEND_STATUS" == "200" ]; then
  echo "✓ OK"
else
  echo "✗ Failed (HTTP $BACKEND_STATUS)"
  exit 1
fi

# Backend API endpoint
echo -n "Backend API ($BACKEND_URL/api/v1/tasks): "
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/api/v1/tasks)
if [ "$API_STATUS" == "200" ] || [ "$API_STATUS" == "401" ]; then
  echo "✓ OK (HTTP $API_STATUS)"
else
  echo "✗ Failed (HTTP $API_STATUS)"
  exit 1
fi

# Frontend health check
echo -n "Frontend health ($FRONTEND_URL): "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ "$FRONTEND_STATUS" == "200" ]; then
  echo "✓ OK"
else
  echo "✗ Failed (HTTP $FRONTEND_STATUS)"
  exit 1
fi

echo ""
echo "All health checks passed!"
```

### Environment Variable Validator

**File**: `scripts/validate-env.py`
```python
#!/usr/bin/env python3
"""Validate environment variables for deployment."""

import os
import sys
from typing import List, Dict

# Required environment variables
REQUIRED_VARS = {
    "backend": [
        "DATABASE_URL",
        "JWT_SECRET",
        "CORS_ORIGINS",
    ],
    "frontend": [
        "NEXT_PUBLIC_API_URL",
    ]
}

# Optional but recommended
RECOMMENDED_VARS = {
    "backend": [
        "SENTRY_DSN",
        "LOG_LEVEL",
    ],
    "frontend": [
        "NEXT_PUBLIC_SENTRY_DSN",
    ]
}

def validate_env(service: str) -> bool:
    """Validate environment variables for a service."""
    print(f"\n{'='*50}")
    print(f"Validating environment for: {service}")
    print('='*50)

    missing_required = []
    missing_recommended = []

    # Check required variables
    print("\n[Required Variables]")
    for var in REQUIRED_VARS.get(service, []):
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            display_value = "*" * 8 if "SECRET" in var or "KEY" in var else value[:50]
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: MISSING")
            missing_required.append(var)

    # Check recommended variables
    print("\n[Recommended Variables]")
    for var in RECOMMENDED_VARS.get(service, []):
        value = os.getenv(var)
        if value:
            display_value = "*" * 8 if "SECRET" in var or "KEY" in var else value[:50]
            print(f"✓ {var}: {display_value}")
        else:
            print(f"⚠ {var}: Not set (recommended)")
            missing_recommended.append(var)

    # Summary
    print(f"\n{'='*50}")
    if missing_required:
        print(f"✗ Validation FAILED")
        print(f"Missing required variables: {', '.join(missing_required)}")
        return False
    elif missing_recommended:
        print(f"⚠ Validation PASSED with warnings")
        print(f"Missing recommended variables: {', '.join(missing_recommended)}")
        return True
    else:
        print(f"✓ All validations PASSED")
        return True

if __name__ == "__main__":
    service = sys.argv[1] if len(sys.argv) > 1 else "backend"

    if service not in REQUIRED_VARS:
        print(f"Unknown service: {service}")
        print(f"Available services: {', '.join(REQUIRED_VARS.keys())}")
        sys.exit(1)

    success = validate_env(service)
    sys.exit(0 if success else 1)
```

### Docker Container Validator

**File**: `scripts/validate-docker.sh`
```bash
#!/bin/bash
set -e

CONTAINER_NAME=${1:-todo-backend}

echo "Validating Docker container: $CONTAINER_NAME"

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "✗ Container '$CONTAINER_NAME' not found"
  exit 1
fi

# Check if container is running
STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER_NAME)
if [ "$STATUS" != "running" ]; then
  echo "✗ Container is not running (status: $STATUS)"
  docker logs $CONTAINER_NAME --tail=50
  exit 1
fi
echo "✓ Container is running"

# Check health status (if health check configured)
HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null || echo "none")
if [ "$HEALTH" != "none" ]; then
  if [ "$HEALTH" == "healthy" ]; then
    echo "✓ Health check: $HEALTH"
  else
    echo "✗ Health check: $HEALTH"
    exit 1
  fi
fi

# Check resource usage
CPU=$(docker stats $CONTAINER_NAME --no-stream --format "{{.CPUPerc}}" | sed 's/%//')
MEM=$(docker stats $CONTAINER_NAME --no-stream --format "{{.MemPerc}}" | sed 's/%//')

echo "✓ Resource usage: CPU=${CPU}%, Memory=${MEM}%"

# Check logs for errors
ERROR_COUNT=$(docker logs $CONTAINER_NAME --tail=100 2>&1 | grep -i "error\|exception\|fatal" | wc -l)
if [ "$ERROR_COUNT" -gt 10 ]; then
  echo "⚠ Warning: Found $ERROR_COUNT error messages in logs"
else
  echo "✓ No significant errors in logs ($ERROR_COUNT errors found)"
fi

# Check exposed ports
PORTS=$(docker port $CONTAINER_NAME)
if [ -n "$PORTS" ]; then
  echo "✓ Exposed ports:"
  echo "$PORTS"
else
  echo "⚠ No exposed ports"
fi

echo ""
echo "Container validation passed!"
```

## Validation Checklist

### Pre-Deployment
```markdown
## Pre-Deployment Checklist

### Configuration
- [ ] All YAML files are valid
- [ ] Image tags are specified (not :latest)
- [ ] Resource limits defined (CPU, memory)
- [ ] Health checks configured (liveness, readiness)
- [ ] Environment variables set
- [ ] Secrets created

### Security
- [ ] Non-root user in containers
- [ ] Read-only root filesystem where possible
- [ ] Security context configured
- [ ] Network policies defined
- [ ] RBAC roles configured

### Networking
- [ ] Service definitions correct
- [ ] Ingress rules configured
- [ ] TLS certificates available
- [ ] DNS records updated

### Data
- [ ] Database migrations run
- [ ] Persistent volumes configured
- [ ] Backup strategy defined
```

### Post-Deployment
```markdown
## Post-Deployment Checklist

### Pods
- [ ] All pods in Running state
- [ ] All pods pass readiness checks
- [ ] No CrashLoopBackOff or ImagePullBackOff
- [ ] Resource usage within limits

### Services
- [ ] Services have endpoints
- [ ] LoadBalancer has external IP (if applicable)
- [ ] DNS resolution works

### Logs
- [ ] No critical errors in logs
- [ ] Application started successfully
- [ ] Database connections established

### Endpoints
- [ ] Health check returns 200
- [ ] API endpoints respond correctly
- [ ] Frontend loads successfully

### Monitoring
- [ ] Metrics being collected
- [ ] Alerts configured
- [ ] Dashboards accessible
```

## Common Issues and Fixes

### Issue 1: ImagePullBackOff
```bash
# Check image availability
docker pull [image-name]:[tag]

# Verify image secret
kubectl get secret regcred -n [namespace] -o yaml

# Check pod events
kubectl describe pod [pod-name] -n [namespace]
```

### Issue 2: CrashLoopBackOff
```bash
# Check logs
kubectl logs [pod-name] -n [namespace] --previous

# Check liveness probe configuration
kubectl get pod [pod-name] -n [namespace] -o yaml | grep -A 10 livenessProbe

# Increase initialDelaySeconds if app needs more startup time
```

### Issue 3: Service Not Reachable
```bash
# Check service endpoints
kubectl get endpoints [service-name] -n [namespace]

# Verify selector matches pods
kubectl get pods -n [namespace] --show-labels
kubectl get service [service-name] -n [namespace] -o yaml | grep selector

# Test connectivity from another pod
kubectl run test-pod --image=busybox -it --rm -- wget -O- http://[service-name]:[port]
```

### Issue 4: High Resource Usage
```bash
# Check resource usage
kubectl top pods -n [namespace]

# Check limits
kubectl describe pod [pod-name] -n [namespace] | grep -A 5 "Limits\|Requests"

# Scale down replicas if needed
kubectl scale deployment [deployment-name] --replicas=2 -n [namespace]
```

## Quality Checklist

Before marking deployment as validated:
- [ ] All pods running and ready
- [ ] Services have endpoints
- [ ] Health checks passing
- [ ] No errors in recent logs
- [ ] Resource usage normal
- [ ] Environment variables correct
- [ ] Database connectivity verified
- [ ] API endpoints responding
- [ ] Frontend accessible
- [ ] TLS certificates valid
- [ ] Monitoring active
- [ ] Backups configured

## Automated Validation Script

**File**: `scripts/full-validation.sh`
```bash
#!/bin/bash
# Complete deployment validation pipeline

set -e

NAMESPACE=${1:-default}
APP_NAME=${2:-todo-app}

echo "Running full deployment validation..."

# 1. Kubernetes resources
./scripts/validate-deployment.sh $NAMESPACE $APP_NAME

# 2. Health checks
BACKEND_URL=$(kubectl get service ${APP_NAME}-backend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
FRONTEND_URL=$(kubectl get service ${APP_NAME}-frontend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
./scripts/health-check.sh "http://$BACKEND_URL:8000" "http://$FRONTEND_URL:3000"

# 3. Environment variables
kubectl exec -n $NAMESPACE deployment/${APP_NAME}-backend -- python scripts/validate-env.py backend

# 4. Run smoke tests
pytest tests/smoke/ -v

echo ""
echo "========================================="
echo "✓ Full deployment validation complete!"
echo "========================================="
```

## Post-Validation

After validating deployment:
1. **Document Results**: Save validation output
2. **Monitor**: Set up alerts for issues
3. **Test**: Run integration and E2E tests
4. **Verify**: Check metrics and dashboards
5. **Notify**: Inform team of deployment status
6. **Create PHR**: Document validation process
