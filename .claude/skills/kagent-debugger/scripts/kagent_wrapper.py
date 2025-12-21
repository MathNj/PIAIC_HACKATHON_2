#!/usr/bin/env python3
"""
kagent Wrapper - Interface for kagent CLI (Kubernetes AI Operations)

This script wraps the `kagent` command to provide AI-assisted SRE operations
for Kubernetes cluster health analysis and resource optimization.

Usage:
    python kagent_wrapper.py analyze
    python kagent_wrapper.py optimize
    python kagent_wrapper.py diagnose --pod frontend-abc123
"""

import subprocess
import sys
import json
import shutil
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime


class KagentWrapper:
    """Wrapper for kagent CLI - Kubernetes AI Operations."""

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.kagent_available = self.check_kagent_availability()

    def check_kagent_availability(self) -> bool:
        """Check if kagent is available."""
        if not shutil.which("kagent"):
            return False

        try:
            result = subprocess.run(
                ["kagent", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def analyze_cluster_health(self) -> Dict[str, Any]:
        """
        Analyze overall cluster health using kagent.

        Returns:
            Dict with 'success', 'health_score', 'issues', 'recommendations'
        """
        if not self.kagent_available:
            return self._fallback_cluster_health()

        try:
            cmd = ["kagent", "analyze", "cluster", "--namespace", self.namespace, "--output", "json"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # Parse kagent JSON output
                analysis = json.loads(result.stdout)

                return {
                    "success": True,
                    "health_score": analysis.get("health_score", "unknown"),
                    "issues": analysis.get("issues", []),
                    "recommendations": analysis.get("recommendations", []),
                    "resources": analysis.get("resources", {}),
                    "fallback_used": False,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "health_score": None,
                    "issues": [],
                    "recommendations": [],
                    "resources": {},
                    "fallback_used": False,
                    "error": result.stderr,
                }

        except json.JSONDecodeError:
            # Parse non-JSON output
            return self._parse_text_output(result.stdout)
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "health_score": None,
                "issues": [],
                "recommendations": [],
                "resources": {},
                "fallback_used": False,
                "error": "kagent analyze timed out (60s limit)",
            }
        except Exception as e:
            return {
                "success": False,
                "health_score": None,
                "issues": [],
                "recommendations": [],
                "resources": {},
                "fallback_used": False,
                "error": str(e),
            }

    def optimize_resources(self) -> Dict[str, Any]:
        """
        Analyze and recommend resource optimizations using kagent.

        Returns:
            Dict with 'success', 'optimizations', 'savings', 'recommendations'
        """
        if not self.kagent_available:
            return self._fallback_resource_optimization()

        try:
            cmd = ["kagent", "optimize", "resources", "--namespace", self.namespace, "--output", "json"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                optimization = json.loads(result.stdout)

                return {
                    "success": True,
                    "optimizations": optimization.get("optimizations", []),
                    "savings": optimization.get("estimated_savings", {}),
                    "recommendations": optimization.get("recommendations", []),
                    "current_usage": optimization.get("current_usage", {}),
                    "fallback_used": False,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "optimizations": [],
                    "savings": {},
                    "recommendations": [],
                    "current_usage": {},
                    "fallback_used": False,
                    "error": result.stderr,
                }

        except json.JSONDecodeError:
            return self._parse_text_output(result.stdout, mode="optimize")
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "optimizations": [],
                "savings": {},
                "recommendations": [],
                "current_usage": {},
                "fallback_used": False,
                "error": "kagent optimize timed out (60s limit)",
            }
        except Exception as e:
            return {
                "success": False,
                "optimizations": [],
                "savings": {},
                "recommendations": [],
                "current_usage": {},
                "fallback_used": False,
                "error": str(e),
            }

    def diagnose_crash_loop(self, pod_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Diagnose crash loop issues using kagent.

        Args:
            pod_name: Specific pod to diagnose (optional)

        Returns:
            Dict with 'success', 'crashes', 'root_causes', 'fixes'
        """
        if not self.kagent_available:
            return self._fallback_crash_diagnosis(pod_name)

        try:
            if pod_name:
                cmd = ["kagent", "diagnose", "crashloop", "--pod", pod_name, "--namespace", self.namespace, "--output", "json"]
            else:
                cmd = ["kagent", "diagnose", "crashloop", "--namespace", self.namespace, "--output", "json"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                diagnosis = json.loads(result.stdout)

                return {
                    "success": True,
                    "crashes": diagnosis.get("crash_loops", []),
                    "root_causes": diagnosis.get("root_causes", []),
                    "fixes": diagnosis.get("recommended_fixes", []),
                    "logs_analysis": diagnosis.get("logs_analysis", {}),
                    "fallback_used": False,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "crashes": [],
                    "root_causes": [],
                    "fixes": [],
                    "logs_analysis": {},
                    "fallback_used": False,
                    "error": result.stderr,
                }

        except json.JSONDecodeError:
            return self._parse_text_output(result.stdout, mode="diagnose")
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "crashes": [],
                "root_causes": [],
                "fixes": [],
                "logs_analysis": {},
                "fallback_used": False,
                "error": "kagent diagnose timed out (60s limit)",
            }
        except Exception as e:
            return {
                "success": False,
                "crashes": [],
                "root_causes": [],
                "fixes": [],
                "logs_analysis": {},
                "fallback_used": False,
                "error": str(e),
            }

    def _parse_text_output(self, output: str, mode: str = "analyze") -> Dict[str, Any]:
        """Parse non-JSON kagent output."""
        issues = []
        recommendations = []

        lines = output.split("\n")
        for line in lines:
            line = line.strip()

            # Extract issues
            if any(keyword in line.lower() for keyword in ["issue:", "problem:", "error:", "warning:"]):
                issues.append(line)

            # Extract recommendations
            if any(keyword in line.lower() for keyword in ["recommendation:", "suggest:", "fix:", "solution:"]):
                recommendations.append(line)

        if mode == "analyze":
            return {
                "success": True,
                "health_score": "unknown",
                "issues": issues,
                "recommendations": recommendations,
                "resources": {},
                "fallback_used": False,
                "error": None,
            }
        elif mode == "optimize":
            return {
                "success": True,
                "optimizations": recommendations,
                "savings": {},
                "recommendations": recommendations,
                "current_usage": {},
                "fallback_used": False,
                "error": None,
            }
        else:  # diagnose
            return {
                "success": True,
                "crashes": issues,
                "root_causes": issues,
                "fixes": recommendations,
                "logs_analysis": {},
                "fallback_used": False,
                "error": None,
            }

    def _fallback_cluster_health(self) -> Dict[str, Any]:
        """Fallback cluster health check using kubectl."""
        issues = []
        recommendations = []

        try:
            # Check for failed pods
            result = subprocess.run(
                ["kubectl", "get", "pods", "--namespace", self.namespace, "--field-selector=status.phase!=Running,status.phase!=Succeeded"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                if lines and lines[0]:
                    issues.append(f"Found {len(lines)} pods not in Running state")
                    recommendations.append("Check pod logs and events for failed pods")

            # Check for resource pressure
            result = subprocess.run(
                ["kubectl", "top", "nodes"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3:
                        cpu_usage = parts[2]
                        if cpu_usage.endswith("%") and int(cpu_usage[:-1]) > 80:
                            issues.append(f"High CPU usage on node: {parts[0]}")
                            recommendations.append(f"Consider scaling or optimizing workloads on {parts[0]}")

        except Exception as e:
            issues.append(f"Error during health check: {str(e)}")

        health_score = "healthy" if not issues else "degraded"

        return {
            "success": True,
            "health_score": health_score,
            "issues": issues,
            "recommendations": recommendations,
            "resources": {},
            "fallback_used": True,
            "error": None,
        }

    def _fallback_resource_optimization(self) -> Dict[str, Any]:
        """Fallback resource optimization using kubectl."""
        optimizations = []
        recommendations = []

        try:
            # Get pod resource usage
            result = subprocess.run(
                ["kubectl", "top", "pods", "--namespace", self.namespace],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                recommendations.append("Review pod resource requests and limits")
                recommendations.append("Consider using Vertical Pod Autoscaler (VPA) for recommendations")
                optimizations.append({
                    "type": "manual_review",
                    "description": "Check 'kubectl top pods' output and adjust resource specifications",
                })

        except Exception as e:
            recommendations.append(f"Unable to fetch resource metrics: {str(e)}")

        return {
            "success": True,
            "optimizations": optimizations,
            "savings": {},
            "recommendations": recommendations,
            "current_usage": {},
            "fallback_used": True,
            "error": None,
        }

    def _fallback_crash_diagnosis(self, pod_name: Optional[str] = None) -> Dict[str, Any]:
        """Fallback crash diagnosis using kubectl."""
        crashes = []
        root_causes = []
        fixes = []

        try:
            if pod_name:
                pods = [pod_name]
            else:
                # Find crash looping pods
                result = subprocess.run(
                    ["kubectl", "get", "pods", "--namespace", self.namespace, "-o", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    pods_data = json.loads(result.stdout)
                    pods = []
                    for item in pods_data.get("items", []):
                        container_statuses = item.get("status", {}).get("containerStatuses", [])
                        for status in container_statuses:
                            if status.get("state", {}).get("waiting", {}).get("reason") == "CrashLoopBackOff":
                                pods.append(item["metadata"]["name"])
                                crashes.append({
                                    "pod": item["metadata"]["name"],
                                    "status": "CrashLoopBackOff",
                                })

            # Analyze each crashing pod
            for pod in pods:
                # Get pod logs
                result = subprocess.run(
                    ["kubectl", "logs", pod, "--namespace", self.namespace, "--tail=50"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    logs = result.stdout

                    # Simple pattern matching for common issues
                    if "OOMKilled" in logs or "out of memory" in logs.lower():
                        root_causes.append(f"Pod {pod}: Out of Memory (OOM)")
                        fixes.append(f"Increase memory limits for pod {pod}")
                    elif "connection refused" in logs.lower() or "cannot connect" in logs.lower():
                        root_causes.append(f"Pod {pod}: Connection refused to dependency")
                        fixes.append(f"Check service connectivity and environment variables for {pod}")
                    elif "permission denied" in logs.lower():
                        root_causes.append(f"Pod {pod}: Permission denied")
                        fixes.append(f"Check security context and file permissions for {pod}")
                    elif "image" in logs.lower() and ("pull" in logs.lower() or "not found" in logs.lower()):
                        root_causes.append(f"Pod {pod}: Image pull error")
                        fixes.append(f"Verify image name and registry credentials for {pod}")
                    else:
                        root_causes.append(f"Pod {pod}: Application error (check logs)")
                        fixes.append(f"Review full logs: kubectl logs {pod}")

        except Exception as e:
            root_causes.append(f"Error during diagnosis: {str(e)}")
            fixes.append("Use kubectl describe pod <name> for more details")

        return {
            "success": True,
            "crashes": crashes,
            "root_causes": root_causes,
            "fixes": fixes,
            "logs_analysis": {},
            "fallback_used": True,
            "error": None,
        }

    def format_output(self, response: Dict[str, Any], mode: str = "analyze") -> str:
        """Format kagent response for human-readable output."""
        lines = []

        if response.get("fallback_used"):
            lines.append("⚠️  kagent unavailable - using fallback analysis")
            lines.append("")

        if response.get("success"):
            if mode == "analyze":
                lines.append("📊 Cluster Health Analysis")
                lines.append("")
                lines.append(f"Health Score: {response.get('health_score', 'unknown')}")
                lines.append("")

                if response.get("issues"):
                    lines.append("❌ Issues Detected:")
                    for i, issue in enumerate(response["issues"], 1):
                        lines.append(f"  {i}. {issue}")
                    lines.append("")

                if response.get("recommendations"):
                    lines.append("💡 Recommendations:")
                    for i, rec in enumerate(response["recommendations"], 1):
                        lines.append(f"  {i}. {rec}")
                    lines.append("")

            elif mode == "optimize":
                lines.append("⚡ Resource Optimization Analysis")
                lines.append("")

                if response.get("savings"):
                    lines.append("💰 Estimated Savings:")
                    for key, value in response["savings"].items():
                        lines.append(f"  • {key}: {value}")
                    lines.append("")

                if response.get("recommendations"):
                    lines.append("💡 Optimization Recommendations:")
                    for i, rec in enumerate(response["recommendations"], 1):
                        lines.append(f"  {i}. {rec}")
                    lines.append("")

            elif mode == "diagnose":
                lines.append("🔍 Crash Loop Diagnosis")
                lines.append("")

                if response.get("crashes"):
                    lines.append("🔴 Detected Crash Loops:")
                    for crash in response["crashes"]:
                        if isinstance(crash, dict):
                            lines.append(f"  • Pod: {crash.get('pod', 'unknown')}")
                            lines.append(f"    Status: {crash.get('status', 'unknown')}")
                        else:
                            lines.append(f"  • {crash}")
                    lines.append("")

                if response.get("root_causes"):
                    lines.append("🔎 Root Causes:")
                    for i, cause in enumerate(response["root_causes"], 1):
                        lines.append(f"  {i}. {cause}")
                    lines.append("")

                if response.get("fixes"):
                    lines.append("🛠️  Recommended Fixes:")
                    for i, fix in enumerate(response["fixes"], 1):
                        lines.append(f"  {i}. {fix}")
                    lines.append("")

        else:
            lines.append("❌ Error:")
            lines.append("")
            lines.append(response.get("error", "Unknown error"))

        return "\n".join(lines)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python kagent_wrapper.py <command> [options]")
        print("\nCommands:")
        print("  analyze                Analyze cluster health")
        print("  optimize               Optimize resource allocation")
        print("  diagnose               Diagnose crash loops")
        print("\nOptions:")
        print("  --namespace <ns>       Kubernetes namespace (default: default)")
        print("  --pod <name>           Specific pod to diagnose (for diagnose command)")
        print("  --json                 Output JSON format")
        print("\nExamples:")
        print("  python kagent_wrapper.py analyze")
        print("  python kagent_wrapper.py optimize --namespace production")
        print("  python kagent_wrapper.py diagnose --pod frontend-abc123")
        print("  python kagent_wrapper.py analyze --json")
        sys.exit(1)

    # Parse arguments
    command = sys.argv[1]
    namespace = "default"
    pod_name = None
    json_output = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--namespace" and i + 1 < len(sys.argv):
            namespace = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--pod" and i + 1 < len(sys.argv):
            pod_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--json":
            json_output = True
            i += 1
        else:
            i += 1

    # Execute command
    wrapper = KagentWrapper(namespace=namespace)

    if command == "analyze":
        response = wrapper.analyze_cluster_health()
        mode = "analyze"
    elif command == "optimize":
        response = wrapper.optimize_resources()
        mode = "optimize"
    elif command == "diagnose":
        response = wrapper.diagnose_crash_loop(pod_name=pod_name)
        mode = "diagnose"
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    # Print output
    if json_output:
        print(json.dumps(response, indent=2))
    else:
        print(wrapper.format_output(response, mode=mode))

    sys.exit(0 if response.get("success") else 1)


if __name__ == "__main__":
    main()
