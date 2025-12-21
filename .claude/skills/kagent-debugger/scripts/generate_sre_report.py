#!/usr/bin/env python3
"""
Generate SRE Report

Generates comprehensive Site Reliability Engineering reports by combining
cluster health analysis, resource optimization, and crash loop diagnosis.

Usage:
    python generate_sre_report.py
    python generate_sre_report.py --namespace production
    python generate_sre_report.py --output report.md
    python generate_sre_report.py --format json
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from kagent_wrapper import KagentWrapper


class SREReportGenerator:
    """Generates comprehensive SRE reports."""

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.wrapper = KagentWrapper(namespace=namespace)
        self.timestamp = datetime.now()

    def generate_full_report(self) -> Dict[str, Any]:
        """
        Generate complete SRE report with all analyses.

        Returns:
            Dict containing health, optimization, and diagnosis data
        """
        print("🔍 Running cluster health analysis...")
        health = self.wrapper.analyze_cluster_health()

        print("⚡ Running resource optimization analysis...")
        optimization = self.wrapper.optimize_resources()

        print("🔍 Running crash loop diagnosis...")
        diagnosis = self.wrapper.diagnose_crash_loop()

        # Compile report
        report = {
            "metadata": {
                "generated_at": self.timestamp.isoformat(),
                "namespace": self.namespace,
                "kagent_available": self.wrapper.kagent_available,
                "fallback_used": (
                    health.get("fallback_used", False)
                    or optimization.get("fallback_used", False)
                    or diagnosis.get("fallback_used", False)
                ),
            },
            "health_analysis": health,
            "resource_optimization": optimization,
            "crash_diagnosis": diagnosis,
            "summary": self._generate_summary(health, optimization, diagnosis),
            "action_items": self._generate_action_items(health, optimization, diagnosis),
        }

        return report

    def _generate_summary(
        self,
        health: Dict[str, Any],
        optimization: Dict[str, Any],
        diagnosis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        total_issues = len(health.get("issues", []))
        total_crashes = len(diagnosis.get("crashes", []))
        total_optimizations = len(optimization.get("optimizations", []))

        severity = "healthy"
        if total_crashes > 0 or total_issues > 3:
            severity = "critical"
        elif total_issues > 0 or total_optimizations > 5:
            severity = "warning"

        return {
            "overall_status": severity,
            "health_score": health.get("health_score", "unknown"),
            "total_issues": total_issues,
            "total_crashes": total_crashes,
            "optimization_opportunities": total_optimizations,
            "key_findings": self._extract_key_findings(health, optimization, diagnosis),
        }

    def _extract_key_findings(
        self,
        health: Dict[str, Any],
        optimization: Dict[str, Any],
        diagnosis: Dict[str, Any],
    ) -> List[str]:
        """Extract top 5 key findings."""
        findings = []

        # Critical crashes first
        crashes = diagnosis.get("crashes", [])
        if crashes:
            findings.append(f"🔴 {len(crashes)} pod(s) in CrashLoopBackOff state")

        # Health issues
        issues = health.get("issues", [])
        for issue in issues[:2]:  # Top 2 health issues
            findings.append(f"⚠️  {issue}")

        # Resource optimizations
        optimizations = optimization.get("recommendations", [])
        if optimizations:
            findings.append(f"💡 {len(optimizations)} resource optimization opportunities")

        return findings[:5]  # Limit to 5 key findings

    def _generate_action_items(
        self,
        health: Dict[str, Any],
        optimization: Dict[str, Any],
        diagnosis: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items."""
        actions = []

        # P0: Crash loops (critical)
        for fix in diagnosis.get("fixes", []):
            actions.append({
                "priority": "P0",
                "category": "crash_fix",
                "description": fix,
                "urgency": "immediate",
            })

        # P1: Health issues (high)
        for rec in health.get("recommendations", [])[:3]:  # Top 3
            actions.append({
                "priority": "P1",
                "category": "health",
                "description": rec,
                "urgency": "high",
            })

        # P2: Resource optimizations (medium)
        for rec in optimization.get("recommendations", [])[:5]:  # Top 5
            actions.append({
                "priority": "P2",
                "category": "optimization",
                "description": rec,
                "urgency": "medium",
            })

        return actions

    def format_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as Markdown."""
        md = []

        # Header
        md.append("# SRE Cluster Health Report")
        md.append("")
        md.append(f"**Generated:** {report['metadata']['generated_at']}")
        md.append(f"**Namespace:** {report['metadata']['namespace']}")
        md.append(f"**kagent Available:** {'✅' if report['metadata']['kagent_available'] else '⚠️  (using fallback)'}")
        md.append("")

        # Executive Summary
        summary = report["summary"]
        md.append("## Executive Summary")
        md.append("")
        md.append(f"**Overall Status:** `{summary['overall_status'].upper()}`")
        md.append(f"**Health Score:** {summary['health_score']}")
        md.append("")

        md.append("### Key Metrics")
        md.append("")
        md.append(f"- Total Issues: {summary['total_issues']}")
        md.append(f"- Crash Loops: {summary['total_crashes']}")
        md.append(f"- Optimization Opportunities: {summary['optimization_opportunities']}")
        md.append("")

        md.append("### Key Findings")
        md.append("")
        for finding in summary["key_findings"]:
            md.append(f"- {finding}")
        md.append("")

        # Action Items
        md.append("## Action Items")
        md.append("")

        # Group by priority
        p0_actions = [a for a in report["action_items"] if a["priority"] == "P0"]
        p1_actions = [a for a in report["action_items"] if a["priority"] == "P1"]
        p2_actions = [a for a in report["action_items"] if a["priority"] == "P2"]

        if p0_actions:
            md.append("### 🔴 P0 - Critical (Immediate Action Required)")
            md.append("")
            for i, action in enumerate(p0_actions, 1):
                md.append(f"{i}. {action['description']}")
            md.append("")

        if p1_actions:
            md.append("### 🟡 P1 - High Priority")
            md.append("")
            for i, action in enumerate(p1_actions, 1):
                md.append(f"{i}. {action['description']}")
            md.append("")

        if p2_actions:
            md.append("### 🟢 P2 - Medium Priority (Optimization)")
            md.append("")
            for i, action in enumerate(p2_actions, 1):
                md.append(f"{i}. {action['description']}")
            md.append("")

        # Detailed Analysis
        md.append("## Detailed Analysis")
        md.append("")

        # Health Analysis
        md.append("### Cluster Health")
        md.append("")
        health = report["health_analysis"]
        if health.get("issues"):
            md.append("**Issues Detected:**")
            md.append("")
            for issue in health["issues"]:
                md.append(f"- {issue}")
            md.append("")

        if health.get("recommendations"):
            md.append("**Recommendations:**")
            md.append("")
            for rec in health["recommendations"]:
                md.append(f"- {rec}")
            md.append("")

        # Resource Optimization
        md.append("### Resource Optimization")
        md.append("")
        optimization = report["resource_optimization"]
        if optimization.get("recommendations"):
            md.append("**Optimization Opportunities:**")
            md.append("")
            for rec in optimization["recommendations"]:
                md.append(f"- {rec}")
            md.append("")

        if optimization.get("savings"):
            md.append("**Estimated Savings:**")
            md.append("")
            for key, value in optimization["savings"].items():
                md.append(f"- {key}: {value}")
            md.append("")

        # Crash Diagnosis
        md.append("### Crash Loop Analysis")
        md.append("")
        diagnosis = report["crash_diagnosis"]
        if diagnosis.get("crashes"):
            md.append("**Detected Crash Loops:**")
            md.append("")
            for crash in diagnosis["crashes"]:
                if isinstance(crash, dict):
                    md.append(f"- Pod: `{crash.get('pod', 'unknown')}` - Status: {crash.get('status', 'unknown')}")
                else:
                    md.append(f"- {crash}")
            md.append("")

        if diagnosis.get("root_causes"):
            md.append("**Root Causes:**")
            md.append("")
            for cause in diagnosis["root_causes"]:
                md.append(f"- {cause}")
            md.append("")

        if diagnosis.get("fixes"):
            md.append("**Recommended Fixes:**")
            md.append("")
            for fix in diagnosis["fixes"]:
                md.append(f"- {fix}")
            md.append("")

        # Footer
        md.append("---")
        md.append("")
        md.append("*Generated by kagent-debugger SRE skill*")
        md.append("")

        return "\n".join(md)


def main():
    """CLI entry point."""
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python generate_sre_report.py [options]")
        print("\nOptions:")
        print("  --namespace <ns>    Kubernetes namespace (default: default)")
        print("  --output <file>     Output file path (default: sre-report-<timestamp>.md)")
        print("  --format <format>   Output format: markdown or json (default: markdown)")
        print("\nExamples:")
        print("  python generate_sre_report.py")
        print("  python generate_sre_report.py --namespace production")
        print("  python generate_sre_report.py --output report.md")
        print("  python generate_sre_report.py --format json --output report.json")
        sys.exit(0)

    # Parse arguments
    namespace = "default"
    output_file = None
    output_format = "markdown"

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--namespace" and i + 1 < len(sys.argv):
            namespace = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1].lower()
            i += 2
        else:
            i += 1

    # Generate default output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == "json":
            output_file = f"sre-report-{timestamp}.json"
        else:
            output_file = f"sre-report-{timestamp}.md"

    # Generate report
    print("🚀 Generating SRE Report...")
    print("")

    generator = SREReportGenerator(namespace=namespace)
    report = generator.generate_full_report()

    print("")
    print("✅ Analysis complete!")
    print("")

    # Format and save
    if output_format == "json":
        content = json.dumps(report, indent=2)
    else:
        content = generator.format_markdown(report)

    # Write to file
    output_path = Path(output_file)
    output_path.write_text(content, encoding="utf-8")

    print(f"📄 Report saved to: {output_path.absolute()}")
    print("")

    # Print summary
    summary = report["summary"]
    print("📊 Summary:")
    print(f"   Status: {summary['overall_status'].upper()}")
    print(f"   Issues: {summary['total_issues']}")
    print(f"   Crashes: {summary['total_crashes']}")
    print(f"   Optimizations: {summary['optimization_opportunities']}")
    print("")

    # Print action items count
    actions = report["action_items"]
    p0_count = len([a for a in actions if a["priority"] == "P0"])
    p1_count = len([a for a in actions if a["priority"] == "P1"])
    p2_count = len([a for a in actions if a["priority"] == "P2"])

    print("🎯 Action Items:")
    if p0_count > 0:
        print(f"   🔴 P0 (Critical): {p0_count}")
    if p1_count > 0:
        print(f"   🟡 P1 (High): {p1_count}")
    if p2_count > 0:
        print(f"   🟢 P2 (Medium): {p2_count}")

    sys.exit(0)


if __name__ == "__main__":
    main()
