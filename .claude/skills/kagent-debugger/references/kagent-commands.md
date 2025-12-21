# kagent Command Reference

Comprehensive guide to using kagent for AI-assisted Kubernetes operations and SRE tasks.

## Table of Contents
- Getting Started
- Cluster Health Analysis
- Resource Optimization
- Crash Loop Diagnosis
- Advanced Usage
- Best Practices

## Getting Started

### Installation

kagent is a Kubernetes AI operations tool. Installation varies by environment:

```bash
# Check if kagent is installed
kagent --version

# Or check via which
which kagent
```

### Basic Usage

```bash
# Analyze cluster health
kagent analyze cluster

# Optimize resources
kagent optimize resources

# Diagnose crash loops
kagent diagnose crashloop

# Help
kagent --help
```

## Cluster Health Analysis

### Basic Health Check

**Command:**
```bash
kagent analyze cluster
```

**Output:**
- Health score (0-100)
- List of detected issues
- Recommended actions
- Resource status

**Example:**
```bash
$ kagent analyze cluster

Cluster Health Score: 75/100

Issues Detected:
  - High CPU usage on node minikube (85%)
  - 2 pods not in Running state
  - 1 deployment has insufficient replicas

Recommendations:
  - Consider scaling up nodes
  - Review pod configurations
  - Increase replica count for critical services
```

### Namespace-Specific Analysis

```bash
# Analyze specific namespace
kagent analyze cluster --namespace production

# All namespaces
kagent analyze cluster --all-namespaces
```

### JSON Output

```bash
# Get JSON output for programmatic use
kagent analyze cluster --output json

# Save to file
kagent analyze cluster --output json > health-report.json
```

## Resource Optimization

### Analyze Resource Usage

**Command:**
```bash
kagent optimize resources
```

**Output:**
- Current resource allocation
- Over-provisioned resources
- Under-provisioned resources
- Estimated cost savings
- Optimization recommendations

**Example:**
```bash
$ kagent optimize resources

Resource Optimization Analysis
==============================

Over-Provisioned Resources:
  - frontend deployment: memory request 512Mi → recommended 300Mi (save 212Mi/pod)
  - worker deployment: CPU limit 1000m → recommended 500m (save 500m/pod)

Under-Provisioned Resources:
  - database deployment: memory limit 256Mi → recommended 512Mi (avoid OOMKilled)
  - api deployment: CPU request 100m → recommended 200m (avoid throttling)

Estimated Savings:
  - Memory: 848Mi total
  - CPU: 2000m total
  - Cost: ~15% reduction in cluster costs

Recommendations:
  - Implement HPA (Horizontal Pod Autoscaler) for api deployment
  - Review memory usage patterns for frontend pods
  - Consider VPA (Vertical Pod Autoscaler) for database
```

### Namespace-Specific Optimization

```bash
# Specific namespace
kagent optimize resources --namespace production

# Focus on memory
kagent optimize resources --focus memory

# Focus on CPU
kagent optimize resources --focus cpu
```

## Crash Loop Diagnosis

### Diagnose All Crash Loops

**Command:**
```bash
kagent diagnose crashloop
```

**Output:**
- List of pods in CrashLoopBackOff
- Root cause analysis
- Log analysis
- Recommended fixes

**Example:**
```bash
$ kagent diagnose crashloop

Crash Loop Analysis
===================

Detected Crash Loops:
  1. frontend-abc123 (CrashLoopBackOff)
  2. worker-def456 (CrashLoopBackOff)

Root Causes:
  - frontend-abc123: Connection refused to backend service
    Log: "Error: ECONNREFUSED 10.96.0.1:8000"
    Reason: Backend service pods are not ready

  - worker-def456: Out of Memory (OOMKilled)
    Log: "Killed by kernel (OOM)"
    Reason: Memory limit 128Mi exceeded

Recommended Fixes:
  1. For frontend-abc123:
     - Check backend service: kubectl get svc backend-service
     - Verify backend pods: kubectl get pods -l app=backend
     - Review BACKEND_URL environment variable

  2. For worker-def456:
     - Increase memory limit to 256Mi
     - Add memory request: 128Mi
     - Review application for memory leaks
```

### Diagnose Specific Pod

```bash
# Specific pod
kagent diagnose crashloop --pod frontend-abc123

# With namespace
kagent diagnose crashloop --pod frontend-abc123 --namespace production
```

### Deep Analysis

```bash
# Include full log analysis
kagent diagnose crashloop --pod frontend-abc123 --verbose

# Include historical data
kagent diagnose crashloop --pod frontend-abc123 --history 24h
```

## Advanced Usage

### Combined Analysis (Full SRE Report)

Generate comprehensive SRE report:

```bash
# Using generate_sre_report.py
python scripts/generate_sre_report.py

# With namespace
python scripts/generate_sre_report.py --namespace production

# JSON format
python scripts/generate_sre_report.py --format json --output report.json
```

### Scheduled Health Checks

```bash
# Run hourly health check
*/60 * * * * kagent analyze cluster --output json > /var/log/k8s-health-$(date +\%Y\%m\%d-\%H\%M).json

# Daily optimization report
0 9 * * * python scripts/generate_sre_report.py --output daily-report-$(date +\%Y\%m\%d).md
```

### Integration with Monitoring

```bash
# Export metrics to Prometheus format
kagent analyze cluster --export-metrics > /tmp/kagent-metrics.prom

# Send to Slack webhook
kagent analyze cluster --format slack | curl -X POST -H 'Content-type: application/json' --data @- $SLACK_WEBHOOK_URL
```

## Best Practices

### Regular Health Checks

Run health analysis regularly:

```bash
# Daily summary
kagent analyze cluster --summary

# Weekly detailed report
python scripts/generate_sre_report.py --output weekly-report.md
```

### Proactive Monitoring

Set up alerts for critical issues:

```bash
# Check for critical issues
HEALTH_SCORE=$(kagent analyze cluster --output json | jq -r '.health_score')

if [ $HEALTH_SCORE -lt 70 ]; then
  echo "ALERT: Cluster health degraded (score: $HEALTH_SCORE)"
  # Send alert
fi
```

### Resource Review Cadence

**Daily:**
- Check for crash loops
- Review resource pressure

**Weekly:**
- Full health analysis
- Resource optimization review

**Monthly:**
- Cost analysis
- Long-term optimization planning

### Fallback Strategy

When kagent is unavailable, use kubectl directly:

```bash
# Health check
kubectl get pods --all-namespaces | grep -v Running

# Resource usage
kubectl top nodes
kubectl top pods

# Crash diagnosis
kubectl get pods --field-selector=status.phase=Failed
kubectl logs <pod-name> --previous
```

## Output Formats

### JSON

```bash
kagent analyze cluster --output json
```

**Example output:**
```json
{
  "health_score": 75,
  "issues": [
    "High CPU usage on node minikube",
    "2 pods not in Running state"
  ],
  "recommendations": [
    "Scale up nodes",
    "Review pod configurations"
  ],
  "resources": {
    "nodes": 1,
    "pods_total": 15,
    "pods_running": 13
  }
}
```

### Markdown

```bash
kagent analyze cluster --output markdown > health-report.md
```

### Plain Text

```bash
kagent analyze cluster
```

## Troubleshooting

### kagent Not Found

```bash
# Check installation
which kagent

# If not installed, use fallback
python scripts/kagent_wrapper.py analyze
```

### Timeout Issues

```bash
# Increase timeout
kagent analyze cluster --timeout 120s

# Analyze specific namespace only
kagent analyze cluster --namespace default
```

### Permission Errors

```bash
# Check RBAC permissions
kubectl auth can-i list pods --all-namespaces

# Ensure service account has required permissions
kubectl create clusterrolebinding kagent-view --clusterrole=view --serviceaccount=default:kagent
```

## Integration with Cloud Ops Engineer

```python
# Example: cloudops-engineer using kagent-debugger
from scripts.kagent_wrapper import KagentWrapper
from scripts.generate_sre_report import SREReportGenerator

# Run health analysis
wrapper = KagentWrapper(namespace="default")
health = wrapper.analyze_cluster_health()

if health["health_score"] < 70:
    # Generate detailed SRE report
    generator = SREReportGenerator(namespace="default")
    report = generator.generate_full_report()

    # Save report
    with open("sre-report.md", "w") as f:
        f.write(generator.format_markdown(report))

    # Alert SRE team
    print(f"ALERT: Cluster health degraded (score: {health['health_score']})")
```

## Quick Reference

```bash
# Health analysis
kagent analyze cluster
python scripts/kagent_wrapper.py analyze

# Resource optimization
kagent optimize resources
python scripts/kagent_wrapper.py optimize

# Crash diagnosis
kagent diagnose crashloop
python scripts/kagent_wrapper.py diagnose

# Full SRE report
python scripts/generate_sre_report.py

# JSON output
python scripts/kagent_wrapper.py analyze --json

# Specific namespace
python scripts/kagent_wrapper.py analyze --namespace production
```
