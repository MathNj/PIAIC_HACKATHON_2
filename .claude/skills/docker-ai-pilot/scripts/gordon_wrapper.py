#!/usr/bin/env python3
"""
Gordon Wrapper - Interface for Docker AI CLI

This script wraps the `docker ai` command to provide structured
interaction with Docker's Gordon AI assistant.

Usage:
    python gordon_wrapper.py "optimize this dockerfile"
    python gordon_wrapper.py "why did my container crash?" --container-id abc123
    python gordon_wrapper.py "generate dockerfile for fastapi app"
"""

import subprocess
import sys
import json
import shutil
from typing import Optional, Dict, Any
from pathlib import Path


class GordonWrapper:
    """Wrapper for Docker AI (Gordon) CLI."""

    def __init__(self):
        self.gordon_available = self.check_gordon_availability()

    def check_gordon_availability(self) -> bool:
        """Check if Docker AI (Gordon) is available."""
        # Check if docker command exists
        if not shutil.which("docker"):
            return False

        try:
            # Check if 'docker ai' subcommand exists
            result = subprocess.run(
                ["docker", "ai", "--help"],
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
        dockerfile_path: Optional[str] = None,
        container_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a natural language prompt with Gordon.

        Args:
            prompt: Natural language prompt (e.g., "optimize this dockerfile")
            context: Additional context dict
            dockerfile_path: Path to Dockerfile for analysis
            container_id: Container ID for debugging

        Returns:
            Dict with 'success', 'output', 'suggestions', 'fallback_used'
        """
        if not self.gordon_available:
            return self._fallback_response(prompt, context)

        try:
            cmd = ["docker", "ai", prompt]

            # Add context flags if provided
            if dockerfile_path:
                cmd.extend(["--file", dockerfile_path])
            if container_id:
                cmd.extend(["--container", container_id])

            # Execute docker ai command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "suggestions": self._parse_suggestions(result.stdout),
                    "fallback_used": False,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "output": result.stderr,
                    "suggestions": [],
                    "fallback_used": False,
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "suggestions": [],
                "fallback_used": False,
                "error": "Gordon timed out (30s limit exceeded)",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "suggestions": [],
                "fallback_used": False,
                "error": str(e),
            }

    def _parse_suggestions(self, output: str) -> list[Dict[str, str]]:
        """
        Parse Gordon's natural language output for actionable suggestions.

        Gordon typically provides suggestions in formats like:
        - "You should..." or "Consider..."
        - Numbered lists (1., 2., 3.)
        - Bulleted lists (-, *, •)
        - Code blocks (```...```)
        """
        suggestions = []

        # Extract code blocks (Dockerfiles, commands, etc.)
        code_blocks = self._extract_code_blocks(output)
        for i, code in enumerate(code_blocks):
            suggestions.append({
                "type": "code",
                "content": code,
                "description": f"Code suggestion {i + 1}",
            })

        # Extract bullet points and numbered items
        lines = output.split("\n")
        for line in lines:
            line = line.strip()

            # Numbered list items (1., 2., 3.)
            if line and line[0].isdigit() and ". " in line[:4]:
                suggestions.append({
                    "type": "recommendation",
                    "content": line,
                    "description": "Numbered recommendation",
                })

            # Bullet points (-, *, •)
            elif line.startswith(("- ", "* ", "• ")):
                suggestions.append({
                    "type": "recommendation",
                    "content": line[2:],
                    "description": "Bullet point recommendation",
                })

            # Action phrases
            elif any(line.lower().startswith(phrase) for phrase in [
                "you should",
                "consider",
                "recommendation:",
                "try",
                "use",
            ]):
                suggestions.append({
                    "type": "action",
                    "content": line,
                    "description": "Action item",
                })

        return suggestions

    def _extract_code_blocks(self, output: str) -> list[str]:
        """Extract code blocks from markdown-style output."""
        code_blocks = []
        in_code_block = False
        current_block = []

        for line in output.split("\n"):
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    code_blocks.append("\n".join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)

        return code_blocks

    def _fallback_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fallback when Gordon is unavailable.

        Returns guidance for standard Docker commands.
        """
        fallback_suggestions = []

        # Analyze prompt keywords for fallback suggestions
        prompt_lower = prompt.lower()

        if "optimize" in prompt_lower or "size" in prompt_lower:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Use multi-stage builds to reduce image size",
                "description": "Standard optimization technique",
            })
            fallback_suggestions.append({
                "type": "code",
                "content": (
                    "# Multi-stage Dockerfile example\n"
                    "FROM python:3.13 AS builder\n"
                    "WORKDIR /app\n"
                    "COPY requirements.txt .\n"
                    "RUN pip install --no-cache-dir -r requirements.txt\n\n"
                    "FROM python:3.13-slim\n"
                    "WORKDIR /app\n"
                    "COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages\n"
                    "COPY . .\n"
                    "CMD ['python', 'app.py']"
                ),
                "description": "Multi-stage build template",
            })

        elif "crash" in prompt_lower or "debug" in prompt_lower:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Check container logs: docker logs <container-id>",
                "description": "Standard debugging command",
            })
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Inspect container: docker inspect <container-id>",
                "description": "Standard inspection command",
            })

        elif "generate" in prompt_lower or "create" in prompt_lower:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Use Dockerfile templates from assets/dockerfile-templates/",
                "description": "Template-based approach",
            })

        else:
            fallback_suggestions.append({
                "type": "fallback",
                "content": "Gordon (Docker AI) is unavailable. Use standard Docker commands.",
                "description": "Generic fallback",
            })

        return {
            "success": True,
            "output": "Gordon unavailable - using fallback suggestions",
            "suggestions": fallback_suggestions,
            "fallback_used": True,
            "error": None,
        }

    def format_output(self, response: Dict[str, Any]) -> str:
        """Format Gordon's response for human-readable output."""
        lines = []

        if response["fallback_used"]:
            lines.append("⚠️  Docker AI (Gordon) unavailable - using fallback")
            lines.append("")

        if response["success"]:
            lines.append("✅ Gordon Response:")
            lines.append("")
            lines.append(response["output"])
            lines.append("")

            if response["suggestions"]:
                lines.append("📋 Actionable Suggestions:")
                lines.append("")
                for i, suggestion in enumerate(response["suggestions"], 1):
                    lines.append(f"{i}. [{suggestion['type'].upper()}]")
                    lines.append(f"   {suggestion['content']}")
                    lines.append("")
        else:
            lines.append("❌ Error:")
            lines.append("")
            lines.append(response.get("error", "Unknown error"))

        return "\n".join(lines)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python gordon_wrapper.py <prompt> [--file <path>] [--container <id>]")
        print("\nExamples:")
        print('  python gordon_wrapper.py "optimize this dockerfile" --file Dockerfile')
        print('  python gordon_wrapper.py "why did my container crash?" --container abc123')
        print('  python gordon_wrapper.py "generate fastapi dockerfile"')
        sys.exit(1)

    # Parse arguments
    prompt = sys.argv[1]
    dockerfile_path = None
    container_id = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--file" and i + 1 < len(sys.argv):
            dockerfile_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--container" and i + 1 < len(sys.argv):
            container_id = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Execute Gordon
    wrapper = GordonWrapper()
    response = wrapper.execute_prompt(
        prompt=prompt,
        dockerfile_path=dockerfile_path,
        container_id=container_id,
    )

    # Print formatted output
    print(wrapper.format_output(response))

    # Return JSON for programmatic use
    if "--json" in sys.argv:
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(response, indent=2))

    sys.exit(0 if response["success"] else 1)


if __name__ == "__main__":
    main()
