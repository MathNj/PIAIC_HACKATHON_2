---
name: kagent-debugger
description: AI-assisted Kubernetes SRE operations using kagent for Phase IV deployment. Use when: (1) Analyzing cluster health and detecting issues, (2) Optimizing resource allocation and reducing costs, (3) Diagnosing crash loops and pod failures, (4) Generating comprehensive SRE reports, (5) Investigating performance degradation or resource pressure, (6) Performing proactive cluster maintenance, or (7) Any Kubernetes SRE task requiring intelligent analysis. Wraps `kagent` CLI commands, provides structured health reports, identifies root causes, and offers actionable fixes. Serves as the project's AI-powered Site Reliability Engineer.
---

# kagent Debugger

AI-powered Site Reliability Engineer for Kubernetes cluster health, optimization, and troubleshooting.

## Overview

kagent Debugger acts as your AI-powered SRE, providing intelligent analysis of Kubernetes clusters:
- **Cluster Health Analysis** - AI-driven issue detection and health scoring
- **Resource Optimization** - Cost savings through intelligent resource allocation
- **Crash Loop Diagnosis** - Root cause analysis for failing pods
- **Structured SRE Reports** - Comprehensive reports with prioritized action items
- **Automatic Fallback** - Uses kubectl when kagent unavailable

**Phase IV Requirement:** This skill provides the SRE capabilities required for production Kubernetes operations.

## Quick Start

### Prerequisites

**kagent Available (Preferred):**
- kubectl configured for Minikube/Kubernetes
- kagent CLI installed
- Cluster access with appropriate RBAC permissions

**kagent Unavailable (Fallback):**
- Standard kubectl CLI
- Uses kubectl commands for analysis

### Basic Workflow

1. **Run Health Analysis** - Identify cluster issues
2. **Optimize Resources** - Find cost-saving opportunities
3. **Diagnose Crashes** - Fix failing pods
4. **Generate SRE Report** - Comprehensive assessment with action items

## Common Use Cases

### 1. Analyze Cluster Health

```bash
# Using kagent_wrapper.py
python scripts/kagent_wrapper.py analyze

# Output:
📊 Cluster Health Analysis

Health Score: 75/100

❌ Issues Detected:
  1. High CPU usage on node minikube (85%)
  2. 2 pods not in Running state

💡 Recommendations:
  1. Consider scaling up nodes
  2. Review pod configurations
```

**kagent analyzes:**
- Pod health across all namespaces
- Node resource utilization
- Deployment status and readiness
- Service connectivity
- Recent cluster events

### 2. Optimize Resource Allocation

```bash
# Run resource optimization analysis
python scripts/kagent_wrapper.py optimize

# Output:
⚡ Resource Optimization Analysis

💰 Estimated Savings:
  • Memory: 848Mi
  • CPU: 2000m
  • Cost: ~15% reduction

💡 Optimization Recommendations:
  1. frontend: reduce memory request 512Mi → 300Mi
  2. worker: reduce CPU limit 1000m → 500m
  3. api: implement HPA (Horizontal Pod Autoscaler)
```

**kagent identifies:**
- Over-provisioned resources
- Under-provisioned resources at risk of OOMKilled
- Autoscaling opportunities
- Cost optimization recommendations

### 3. Diagnose Crash Loops

```bash
# Diagnose all crash loops
python scripts/kagent_wrapper.py diagnose

# Diagnose specific pod
python scripts/kagent_wrapper.py diagnose --pod frontend-abc123

# Output:
🔍 Crash Loop Diagnosis

🔴 Detected Crash Loops:
  • Pod: frontend-abc123
    Status: CrashLoopBackOff

🔎 Root Causes:
  1. Connection refused to backend service on port 8000

🛠️  Recommended Fixes:
  1. Check backend service: kubectl get svc backend-service
  2. Verify BACKEND_URL environment variable
  3. Ensure backend pods are ready
```

**kagent diagnoses:**
- CrashLoopBackOff causes
- OOMKilled memory issues
- ImagePullBackOff errors
- Connectivity problems
- Configuration mistakes

### 4. Generate Comprehensive SRE Report

```bash
# Generate full SRE report
python scripts/generate_sre_report.py

# With specific namespace
python scripts/generate_sre_report.py --namespace production

# JSON format
python scripts/generate_sre_report.py --format json --output report.json

# Output:
🚀 Generating SRE Report...

🔍 Running cluster health analysis...
⚡ Running resource optimization analysis...
🔍 Running crash loop diagnosis...

✅ Analysis complete!

📄 Report saved to: sre-report-20250121_143000.md

📊 Summary:
   Status: WARNING
   Issues: 3
   Crashes: 1
   Optimizations: 5

🎯 Action Items:
   🔴 P0 (Critical): 1
   🟡 P1 (High): 2
   🟢 P2 (Medium): 5
```

## Workflow Patterns

### Pattern 1: Daily Health Check

```bash
# Step 1: Quick health analysis
python scripts/kagent_wrapper.py analyze --json > daily-health.json

# Step 2: Check health score
HEALTH_SCORE=$(jq -r '.health_score' daily-health.json | cut -d'/' -f1)

# Step 3: If degraded, generate full report
if [ "$HEALTH_SCORE" -lt 70 ]; then
  echo "⚠️  Cluster health degraded (score: $HEALTH_SCORE)"
  python scripts/generate_sre_report.py --output incident-report.md
  # Alert SRE team
fi
```

### Pattern 2: Incident Response

```bash
# Step 1: Identify scope
python scripts/kagent_wrapper.py diagnose --namespace production

# Step 2: Root cause analysis
python scripts/kagent_wrapper.py diagnose --pod failing-pod-name

# Step 3: Generate incident report
python scripts/generate_sre_report.py --namespace production --output incident-$(date +%Y%m%d).md

# Step 4: Apply fixes based on recommendations
# (from SRE report action items)
```

### Pattern 3: Cost Optimization Review

```bash
# Step 1: Analyze resource usage
python scripts/kagent_wrapper.py optimize --namespace production --json > optimization.json

# Step 2: Review recommendations
jq '.recommendations' optimization.json

# Step 3: Estimate savings
jq '.savings' optimization.json

# Step 4: Implement optimizations
# - Adjust resource requests/limits
# - Enable autoscaling
# - Consolidate workloads
```

### Pattern 4: Proactive Monitoring

```bash
# Scheduled cron job (runs every hour)
# /etc/cron.d/k8s-health-check

0 * * * * python /path/to/scripts/kagent_wrapper.py analyze --json > /var/log/k8s-health-$(date +\%Y\%m\%d-\%H\%M).json

# Check for critical issues
0 * * * * python /path/to/scripts/check_critical.py
```

```python
# check_critical.py
import json
import sys
from datetime import datetime

with open(f"/var/log/k8s-health-{datetime.now().strftime('%Y%m%d-%H%M')}.json") as f:
    health = json.load(f)

if not health.get("success"):
    print("ALERT: Health check failed")
    sys.exit(1)

issues = len(health.get("issues", []))
if issues > 3:
    print(f"ALERT: {issues} issues detected")
    # Send alert to Slack/PagerDuty
    sys.exit(1)
```

## Script Reference

### kagent_wrapper.py

**Purpose:** Execute kagent commands programmatically

**Usage:**
```bash
python scripts/kagent_wrapper.py <command> [options]

Commands:
  analyze     Analyze cluster health
  optimize    Optimize resource allocation
  diagnose    Diagnose crash loops

Options:
  --namespace <ns>   Kubernetes namespace (default: default)
  --pod <name>       Specific pod to diagnose (for diagnose command)
  --json             Output JSON format
```

**Examples:**
```bash
# Health analysis
python scripts/kagent_wrapper.py analyze

# Resource optimization
python scripts/kagent_wrapper.py optimize --namespace production

# Crash diagnosis
python scripts/kagent_wrapper.py diagnose --pod frontend-abc123

# JSON output
python scripts/kagent_wrapper.py analyze --json
```

**Returns (JSON):**
```json
{
  "success": true,
  "health_score": "75/100",
  "issues": ["High CPU usage", "Pods not running"],
  "recommendations": ["Scale nodes", "Review configs"],
  "resources": {},
  "fallback_used": false,
  "error": null
}
```

### generate_sre_report.py

**Purpose:** Generate comprehensive SRE reports

**Usage:**
```bash
python scripts/generate_sre_report.py [options]

Options:
  --namespace <ns>     Kubernetes namespace (default: default)
  --output <file>      Output file path (default: sre-report-<timestamp>.md)
  --format <format>    Output format: markdown or json (default: markdown)
```

**Examples:**
```bash
# Generate report
python scripts/generate_sre_report.py

# Specific namespace
python scripts/generate_sre_report.py --namespace production

# Custom output
python scripts/generate_sre_report.py --output weekly-report.md

# JSON format
python scripts/generate_sre_report.py --format json --output report.json
```

**Report Structure:**
- **Executive Summary** - Status, key metrics, key findings
- **Action Items** - Prioritized by P0/P1/P2
- **Detailed Analysis** - Health, optimization, crash diagnosis
- **Appendix** - Commands used, next steps

## Report Template

For reference, see `assets/report-templates/health-report-template.md` which shows:
- Complete SRE report structure
- Executive summary format
- Action item prioritization (P0/P1/P2)
- Detailed analysis sections
- Next steps and remediation timeline

## Advanced Reference

For detailed kagent command patterns, see:

**`references/kagent-commands.md`**
- Complete kagent CLI reference
- Cluster health analysis commands
- Resource optimization techniques
- Crash loop diagnosis patterns
- Integration patterns

## Integration with cloudops-engineer

This skill is designed for the **cloudops-engineer** agent in Phase IV:

```python
# cloudops-engineer uses kagent-debugger
from scripts.kagent_wrapper import KagentWrapper
from scripts.generate_sre_report import SREReportGenerator

# Daily health check
wrapper = KagentWrapper(namespace="default")
health = wrapper.analyze_cluster_health()

if health["health_score"] < 70 or health["issues"]:
    # Generate detailed SRE report
    generator = SREReportGenerator(namespace="default")
    report = generator.generate_full_report()

    # Save report
    report_md = generator.format_markdown(report)
    with open("sre-alert-report.md", "w") as f:
        f.write(report_md)

    # Alert SRE team
    print(f"🚨 ALERT: Cluster health degraded")
    print(f"   Health Score: {health['health_score']}")
    print(f"   Issues: {len(health['issues'])}")
    print(f"   Report: sre-alert-report.md")
```

## Action Item Prioritization

### P0 - Critical (Immediate Action)
- Crash loops affecting production services
- Severe resource pressure causing evictions
- Critical security vulnerabilities
- Service outages

**SLA:** Fix within 1 hour

### P1 - High Priority
- Performance degradation
- Resource pressure warnings
- Failed deployments
- High error rates

**SLA:** Fix within 24 hours

### P2 - Medium Priority (Optimization)
- Resource optimization opportunities
- Cost reduction suggestions
- Autoscaling recommendations
- Consolidation opportunities

**SLA:** Review weekly, implement as capacity allows

## Best Practices

### 1. Regular Health Monitoring

```bash
# Daily health check
python scripts/kagent_wrapper.py analyze

# Weekly comprehensive report
python scripts/generate_sre_report.py
```

### 2. Proactive Issue Detection

```bash
# Monitor health score trend
python scripts/kagent_wrapper.py analyze --json | jq -r '.health_score'

# Alert on degradation
if [ health_score -lt 70 ]; then alert_sre_team; fi
```

### 3. Cost Optimization Cadence

**Weekly:** Review optimization recommendations
**Monthly:** Implement approved optimizations
**Quarterly:** Full cost analysis and planning

### 4. Incident Documentation

```bash
# Generate incident report
python scripts/generate_sre_report.py --output incident-$(date +%Y%m%d-%H%M).md

# Include in postmortem
```

## Troubleshooting

### kagent Not Available

```bash
# Check kagent installation
which kagent

# If unavailable, wrapper uses fallback automatically
python scripts/kagent_wrapper.py analyze
# Output: ⚠️  kagent unavailable - using fallback analysis
```

### Analysis Takes Too Long

```bash
# Analyze specific namespace only
python scripts/kagent_wrapper.py analyze --namespace default

# Skip optimization analysis
python scripts/kagent_wrapper.py analyze
# (instead of full report)
```

### Permission Issues

```bash
# Check kubectl access
kubectl auth can-i list pods --all-namespaces

# Ensure proper RBAC
kubectl create clusterrolebinding sre-view --clusterrole=view --serviceaccount=default:sre
```

## Automated Remediation

For common issues, implement automated fixes:

```python
# Example: Auto-scale on resource pressure
health = wrapper.analyze_cluster_health()

for issue in health["issues"]:
    if "High CPU usage" in issue:
        # Scale deployment
        subprocess.run(["kubectl", "scale", "deployment", "frontend", "--replicas=5"])

    if "OOMKilled" in issue:
        # Increase memory limits (requires manifest update)
        print("Manual intervention required: Update memory limits")
```

## Quick Command Reference

```bash
# Health analysis
python scripts/kagent_wrapper.py analyze

# Resource optimization
python scripts/kagent_wrapper.py optimize

# Crash diagnosis
python scripts/kagent_wrapper.py diagnose

# Full SRE report
python scripts/generate_sre_report.py

# JSON output
python scripts/kagent_wrapper.py analyze --json

# Specific namespace
python scripts/kagent_wrapper.py analyze --namespace production

# Specific pod diagnosis
python scripts/kagent_wrapper.py diagnose --pod frontend-abc123
```

## Phase IV Compliance

✅ **kagent First:** Always attempt kagent before fallback
✅ **Structured Reports:** SRE reports with prioritized action items
✅ **Root Cause Analysis:** AI-powered crash loop diagnosis
✅ **Resource Optimization:** Cost savings recommendations
✅ **Proactive Monitoring:** Regular health checks and alerts
✅ **Fallback Ready:** kubectl-based analysis when kagent unavailable
✅ **Integration Ready:** Designed for cloudops-engineer agent
✅ **Production SRE:** Serves as AI-powered Site Reliability Engineer
