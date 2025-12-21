#!/usr/bin/env python3
"""
kubectl-ai Wrapper - Interface for kubectl-ai CLI

This script wraps the `kubectl-ai` command to provide structured
interaction with kubectl's AI assistant for Kubernetes operations.

Usage:
    python kubectl_ai_wrapper.py "deploy todo frontend with 2 replicas"
    python kubectl_ai_wrapper.py "why is this pod crashing?" --pod mypod
    python kubectl_ai_wrapper.py "create service for backend on port 8000"
"""

import subprocess
import sys
import json
import shutil
import re
import yaml
from typing import Optional, Dict, Any, List
from pathlib import Path


class KubectlAIWrapper:
    """Wrapper for kubectl-ai CLI."""

    def __init__(self):
        self.kubectl_ai_available = self.check_kubectl_ai_availability()

    def check_kubectl_ai_availability(self) -> bool:
        """Check if kubectl-ai is available."""
        # Check if kubectl command exists
        if not shutil.which("kubectl"):
            return False

        try:
            # Check if 'kubectl-ai' plugin exists
            result = subprocess.run(
                ["kubectl", "ai", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def execute_prompt(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        namespace: str = "default",
        auto_confirm: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a natural language prompt with kubectl-ai.

        Args:
            prompt: Natural language prompt (e.g., "deploy frontend with 2 replicas")
            context: Additional context dict
            namespace: Kubernetes namespace
            auto_confirm: Automatically confirm kubectl-ai actions (use with caution)

        Returns:
            Dict with 'success', 'output', 'manifests', 'commands', 'fallback_used'
        """
        if not self.kubectl_ai_available:
            return self._fallback_response(prompt, context)

        try:
            cmd = ["kubectl", "ai", prompt]

            # Add namespace flag
            if namespace and namespace != "default":
                cmd.extend(["--namespace", namespace])

            # Execute kubectl-ai command
            # Note: kubectl-ai may prompt for confirmation
            if auto_confirm:
                # Pipe 'yes' to auto-confirm
                result = subprocess.run(
                    cmd,
                    input="yes\n",
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

            if result.returncode == 0:
                # Parse kubectl-ai output for manifests and commands
                manifests = self._extract_manifests(result.stdout)
                commands = self._extract_commands(result.stdout)

                return {
                    "success": True,
                    "output": result.stdout,
                    "manifests": manifests,
                    "commands": commands,
                    "fallback_used": False,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "output": result.stderr,
                    "manifests": [],
                    "commands": [],
                    "fallback_used": False,
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "manifests": [],
                "commands": [],
                "fallback_used": False,
                "error": "kubectl-ai timed out (60s limit exceeded)",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "manifests": [],
                "commands": [],
                "fallback_used": False,
                "error": str(e),
            }

    def _extract_manifests(self, output: str) -> List[Dict[str, Any]]:
        """
        Extract Kubernetes manifests from kubectl-ai output.

        kubectl-ai typically provides YAML manifests in code blocks.
        """
        manifests = []

        # Extract YAML code blocks
        yaml_blocks = self._extract_yaml_blocks(output)

        for yaml_str in yaml_blocks:
            try:
                # Parse YAML
                manifest = yaml.safe_load(yaml_str)
                if manifest and isinstance(manifest, dict):
                    manifests.append({
                        "kind": manifest.get("kind", "Unknown"),
                        "name": manifest.get("metadata", {}).get("name", "unnamed"),
                        "content": yaml_str,
                        "parsed": manifest,
                    })
            except yaml.YAMLError:
                # Skip invalid YAML
                continue

        return manifests

    def _extract_yaml_blocks(self, output: str) -> List[str]:
        """Extract YAML blocks from markdown-style output."""
        yaml_blocks = []
        in_yaml_block = False
        current_block = []

        for line in output.split("\n"):
            if line.strip().startswith("```yaml") or line.strip().startswith("```yml"):
                in_yaml_block = True
                continue
            elif line.strip().startswith("```") and in_yaml_block:
                # End of YAML block
                yaml_blocks.append("\n".join(current_block))
                current_block = []
                in_yaml_block = False
            elif in_yaml_block:
                current_block.append(line)

        return yaml_blocks

    def _extract_commands(self, output: str) -> List[str]:
        """Extract kubectl commands from output."""
        commands = []

        # Look for kubectl commands in output
        lines = output.split("\n")
        for line in lines:
            line = line.strip()

            # Match lines starting with kubectl
            if line.startswith("kubectl "):
                commands.append(line)

            # Match code blocks with kubectl commands
            if line.startswith("$ kubectl ") or line.startswith("> kubectl "):
                commands.append(line[2:].strip())

        return commands

    def _fallback_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fallback when kubectl-ai is unavailable.

        Returns guidance for standard kubectl commands or templates.
        """
        fallback_suggestions = []
        prompt_lower = prompt.lower()

        # Analyze prompt keywords
        if "deploy" in prompt_lower or "create deployment" in prompt_lower:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Use Deployment template from assets/k8s-templates/deployment.yaml",
                "description": "Standard Deployment manifest",
            })
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl create deployment <name> --image=<image> --replicas=<n>",
                "description": "Imperative deployment creation",
            })

        elif "service" in prompt_lower or "expose" in prompt_lower:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Use Service template from assets/k8s-templates/service.yaml",
                "description": "Standard Service manifest",
            })
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl expose deployment <name> --port=<port> --type=<type>",
                "description": "Imperative service creation",
            })

        elif "scale" in prompt_lower:
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl scale deployment <name> --replicas=<n>",
                "description": "Standard scaling command",
            })

        elif "crash" in prompt_lower or "debug" in prompt_lower or "why" in prompt_lower:
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl logs <pod-name>",
                "description": "Check pod logs",
            })
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl describe pod <pod-name>",
                "description": "Inspect pod details",
            })
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl get events --sort-by='.lastTimestamp'",
                "description": "Check cluster events",
            })

        elif "status" in prompt_lower or "show" in prompt_lower or "get" in prompt_lower:
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl get pods",
                "description": "List all pods",
            })
            fallback_suggestions.append({
                "type": "command",
                "content": "kubectl get all",
                "description": "List all resources",
            })

        else:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "kubectl-ai unavailable. Use standard kubectl commands or templates.",
                "description": "Generic fallback",
            })

        return {
            "success": True,
            "output": "kubectl-ai unavailable - using fallback suggestions",
            "manifests": [],
            "commands": [s["content"] for s in fallback_suggestions if s["type"] == "command"],
            "fallback_used": True,
            "error": None,
        }

    def format_output(self, response: Dict[str, Any]) -> str:
        """Format kubectl-ai response for human-readable output."""
        lines = []

        if response["fallback_used"]:
            lines.append("⚠️  kubectl-ai unavailable - using fallback")
            lines.append("")

        if response["success"]:
            lines.append("✅ kubectl-ai Response:")
            lines.append("")
            lines.append(response["output"])
            lines.append("")

            if response["manifests"]:
                lines.append("📋 Generated Manifests:")
                lines.append("")
                for i, manifest in enumerate(response["manifests"], 1):
                    lines.append(f"{i}. {manifest['kind']}: {manifest['name']}")
                    lines.append(f"   Preview:")
                    for line in manifest["content"].split("\n")[:5]:
                        lines.append(f"   {line}")
                    if len(manifest["content"].split("\n")) > 5:
                        lines.append(f"   ... ({len(manifest['content'].split('\n')) - 5} more lines)")
                    lines.append("")

            if response["commands"]:
                lines.append("💻 Suggested Commands:")
                lines.append("")
                for i, command in enumerate(response["commands"], 1):
                    lines.append(f"{i}. {command}")
                lines.append("")
        else:
            lines.append("❌ Error:")
            lines.append("")
            lines.append(response.get("error", "Unknown error"))

        return "\n".join(lines)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python kubectl_ai_wrapper.py <prompt> [--namespace <ns>] [--auto-confirm]")
        print("\nExamples:")
        print('  python kubectl_ai_wrapper.py "deploy todo frontend with 2 replicas"')
        print('  python kubectl_ai_wrapper.py "create service for backend on port 8000"')
        print('  python kubectl_ai_wrapper.py "why is my pod crashing?" --namespace production')
        print('  python kubectl_ai_wrapper.py "scale frontend to 3 replicas" --auto-confirm')
        sys.exit(1)

    # Parse arguments
    prompt = sys.argv[1]
    namespace = "default"
    auto_confirm = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--namespace" and i + 1 < len(sys.argv):
            namespace = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--auto-confirm":
            auto_confirm = True
            i += 1
        else:
            i += 1

    # Execute kubectl-ai
    wrapper = KubectlAIWrapper()
    response = wrapper.execute_prompt(
        prompt=prompt,
        namespace=namespace,
        auto_confirm=auto_confirm,
    )

    # Print formatted output
    print(wrapper.format_output(response))

    # Return JSON for programmatic use
    if "--json" in sys.argv:
        print("\n--- JSON OUTPUT ---")
        # Convert manifests to JSON-serializable format
        json_response = response.copy()
        if json_response.get("manifests"):
            json_response["manifests"] = [
                {
                    "kind": m["kind"],
                    "name": m["name"],
                    "content": m["content"],
                }
                for m in json_response["manifests"]
            ]
        print(json.dumps(json_response, indent=2))

    sys.exit(0 if response["success"] else 1)


if __name__ == "__main__":
    main()
