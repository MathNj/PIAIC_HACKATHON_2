#!/usr/bin/env python3
"""
Apply Kubernetes Manifest

Validates and applies Kubernetes manifests to Minikube cluster with rollback capability.

Usage:
    python apply_k8s_manifest.py manifest.yaml
    python apply_k8s_manifest.py manifest.yaml --namespace production
    python apply_k8s_manifest.py manifest.yaml --dry-run
    python apply_k8s_manifest.py --rollback deployment/frontend
"""

import subprocess
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class K8sManifestApplier:
    """Applies and manages Kubernetes manifests."""

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.history_dir = Path(".k8s_history")
        self.history_dir.mkdir(exist_ok=True)

    def validate_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """
        Validate Kubernetes manifest YAML syntax and structure.

        Returns:
            Dict with 'valid', 'resources', 'error'
        """
        try:
            # Read and parse YAML
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML (supports multiple documents)
            documents = list(yaml.safe_load_all(content))

            if not documents:
                return {
                    "valid": False,
                    "resources": [],
                    "error": "No valid YAML documents found",
                }

            resources = []
            for doc in documents:
                if doc and isinstance(doc, dict):
                    kind = doc.get("kind", "Unknown")
                    name = doc.get("metadata", {}).get("name", "unnamed")
                    resources.append(f"{kind}/{name}")

            return {
                "valid": True,
                "resources": resources,
                "error": None,
            }

        except yaml.YAMLError as e:
            return {
                "valid": False,
                "resources": [],
                "error": f"YAML syntax error: {str(e)}",
            }
        except Exception as e:
            return {
                "valid": False,
                "resources": [],
                "error": str(e),
            }

    def dry_run(self, manifest_path: Path) -> Dict[str, Any]:
        """
        Perform kubectl apply --dry-run to validate manifest.

        Returns:
            Dict with 'valid', 'output', 'error'
        """
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "apply",
                    "-f", str(manifest_path),
                    "--dry-run=client",
                    "--namespace", self.namespace,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "valid": True,
                    "output": result.stdout,
                    "error": None,
                }
            else:
                return {
                    "valid": False,
                    "output": result.stdout,
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "valid": False,
                "output": "",
                "error": "kubectl dry-run timed out",
            }
        except FileNotFoundError:
            return {
                "valid": False,
                "output": "",
                "error": "kubectl not found - is it installed?",
            }
        except Exception as e:
            return {
                "valid": False,
                "output": "",
                "error": str(e),
            }

    def apply_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """
        Apply Kubernetes manifest to cluster.

        Returns:
            Dict with 'success', 'applied_resources', 'output', 'error'
        """
        try:
            # Validate first
            validation = self.validate_manifest(manifest_path)
            if not validation["valid"]:
                return {
                    "success": False,
                    "applied_resources": [],
                    "output": "",
                    "error": f"Validation failed: {validation['error']}",
                }

            # Dry run
            dry_run_result = self.dry_run(manifest_path)
            if not dry_run_result["valid"]:
                return {
                    "success": False,
                    "applied_resources": [],
                    "output": dry_run_result["output"],
                    "error": f"Dry run failed: {dry_run_result['error']}",
                }

            # Save to history before applying
            self._save_to_history(manifest_path, validation["resources"])

            # Apply manifest
            result = subprocess.run(
                [
                    "kubectl",
                    "apply",
                    "-f", str(manifest_path),
                    "--namespace", self.namespace,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "applied_resources": validation["resources"],
                    "output": result.stdout,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "applied_resources": [],
                    "output": result.stdout,
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "applied_resources": [],
                "output": "",
                "error": "kubectl apply timed out",
            }
        except Exception as e:
            return {
                "success": False,
                "applied_resources": [],
                "output": "",
                "error": str(e),
            }

    def delete_resource(self, resource: str) -> Dict[str, Any]:
        """
        Delete a Kubernetes resource.

        Args:
            resource: Resource in format "kind/name" (e.g., "deployment/frontend")

        Returns:
            Dict with 'success', 'output', 'error'
        """
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "delete",
                    resource,
                    "--namespace", self.namespace,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
            }

    def get_resource_status(self, resource: str) -> Dict[str, Any]:
        """
        Get status of a Kubernetes resource.

        Args:
            resource: Resource in format "kind/name"

        Returns:
            Dict with 'exists', 'status', 'error'
        """
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    resource,
                    "--namespace", self.namespace,
                    "-o", "json",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                return {
                    "exists": True,
                    "status": status_data,
                    "error": None,
                }
            else:
                return {
                    "exists": False,
                    "status": None,
                    "error": result.stderr,
                }

        except Exception as e:
            return {
                "exists": False,
                "status": None,
                "error": str(e),
            }

    def _save_to_history(self, manifest_path: Path, resources: List[str]):
        """Save applied manifest to history."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_entry = {
            "timestamp": timestamp,
            "manifest": manifest_path.name,
            "resources": resources,
            "namespace": self.namespace,
        }

        history_file = self.history_dir / f"apply_{timestamp}.json"
        history_file.write_text(json.dumps(history_entry, indent=2))

        # Copy manifest to history
        manifest_copy = self.history_dir / f"{manifest_path.stem}_{timestamp}.yaml"
        manifest_copy.write_text(manifest_path.read_text())

    def list_history(self) -> List[Dict[str, Any]]:
        """List all applied manifests from history."""
        history_files = sorted(self.history_dir.glob("apply_*.json"), reverse=True)

        history = []
        for file in history_files:
            try:
                entry = json.loads(file.read_text())
                history.append(entry)
            except:
                continue

        return history


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python apply_k8s_manifest.py <manifest> [options]")
        print("\nOptions:")
        print("  --namespace <ns>      Kubernetes namespace (default: default)")
        print("  --dry-run             Validate only (don't apply)")
        print("  --validate            Validate YAML syntax only")
        print("  --rollback <resource> Delete specified resource")
        print("  --status <resource>   Get resource status")
        print("  --history             List apply history")
        print("\nExamples:")
        print("  python apply_k8s_manifest.py deployment.yaml")
        print("  python apply_k8s_manifest.py deployment.yaml --namespace production")
        print("  python apply_k8s_manifest.py deployment.yaml --dry-run")
        print("  python apply_k8s_manifest.py deployment.yaml --validate")
        print("  python apply_k8s_manifest.py --rollback deployment/frontend")
        print("  python apply_k8s_manifest.py --status deployment/frontend")
        print("  python apply_k8s_manifest.py --history")
        sys.exit(1)

    # Parse arguments
    manifest_path = None
    namespace = "default"
    dry_run_mode = False
    validate_only = False
    rollback_resource = None
    status_resource = None
    show_history = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--namespace" and i + 1 < len(sys.argv):
            namespace = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--dry-run":
            dry_run_mode = True
            i += 1
        elif sys.argv[i] == "--validate":
            validate_only = True
            i += 1
        elif sys.argv[i] == "--rollback" and i + 1 < len(sys.argv):
            rollback_resource = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
            status_resource = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--history":
            show_history = True
            i += 1
        elif not manifest_path and not sys.argv[i].startswith("--"):
            manifest_path = Path(sys.argv[i])
            i += 1
        else:
            i += 1

    applier = K8sManifestApplier(namespace=namespace)

    # Show history
    if show_history:
        history = applier.list_history()
        if history:
            print("📋 Apply History:")
            print("")
            for entry in history:
                print(f"  • {entry['timestamp']}")
                print(f"    Manifest: {entry['manifest']}")
                print(f"    Resources: {', '.join(entry['resources'])}")
                print(f"    Namespace: {entry['namespace']}")
                print("")
        else:
            print("No apply history found")
        sys.exit(0)

    # Rollback (delete resource)
    if rollback_resource:
        print(f"🗑️  Deleting resource: {rollback_resource}")
        result = applier.delete_resource(rollback_resource)

        if result["success"]:
            print(f"✅ Resource deleted successfully")
            print(result["output"])
        else:
            print(f"❌ Failed to delete resource:")
            print(result["error"])

        sys.exit(0 if result["success"] else 1)

    # Get resource status
    if status_resource:
        print(f"🔍 Checking status: {status_resource}")
        result = applier.get_resource_status(status_resource)

        if result["exists"]:
            print(f"✅ Resource exists")
            print(json.dumps(result["status"], indent=2))
        else:
            print(f"❌ Resource not found")
            if result["error"]:
                print(result["error"])

        sys.exit(0 if result["exists"] else 1)

    # Validate or apply manifest
    if not manifest_path:
        print("❌ Error: No manifest file provided")
        sys.exit(1)

    if not manifest_path.exists():
        print(f"❌ Error: Manifest file not found: {manifest_path}")
        sys.exit(1)

    # Validate only
    if validate_only:
        print(f"🔍 Validating {manifest_path}...")
        validation = applier.validate_manifest(manifest_path)

        if validation["valid"]:
            print("✅ Manifest is valid")
            print(f"Resources: {', '.join(validation['resources'])}")
        else:
            print("❌ Manifest has errors:")
            print(validation["error"])

        sys.exit(0 if validation["valid"] else 1)

    # Dry run
    if dry_run_mode:
        print(f"🔍 Dry run for {manifest_path}...")
        result = applier.dry_run(manifest_path)

        if result["valid"]:
            print("✅ Dry run successful")
            print(result["output"])
        else:
            print("❌ Dry run failed:")
            print(result["error"])

        sys.exit(0 if result["valid"] else 1)

    # Apply manifest
    print(f"📝 Applying {manifest_path} to namespace: {namespace}...")
    print("")

    result = applier.apply_manifest(manifest_path)

    if result["success"]:
        print("✅ Manifest applied successfully")
        print("")
        print("Applied resources:")
        for resource in result["applied_resources"]:
            print(f"  • {resource}")
        print("")
        print(result["output"])
    else:
        print("❌ Failed to apply manifest:")
        print(result["error"])

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
