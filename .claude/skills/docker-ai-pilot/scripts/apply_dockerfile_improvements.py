#!/usr/bin/env python3
"""
Apply Dockerfile Improvements

Automatically applies Gordon's Dockerfile suggestions with backup and validation.

Usage:
    python apply_dockerfile_improvements.py Dockerfile --suggestion-file suggestions.txt
    python apply_dockerfile_improvements.py Dockerfile --backup-dir backups/
"""

import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


class DockerfileImprover:
    """Applies and validates Dockerfile improvements."""

    def __init__(self, dockerfile_path: str, backup_dir: Optional[str] = None):
        self.dockerfile_path = Path(dockerfile_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.dockerfile_path.parent / "dockerfile_backups"

        if not self.dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found: {self.dockerfile_path}")

    def create_backup(self) -> Path:
        """
        Create timestamped backup of the Dockerfile.

        Returns:
            Path to backup file
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.dockerfile_path.name}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(self.dockerfile_path, backup_path)

        print(f"✅ Backup created: {backup_path}")
        return backup_path

    def apply_improvement(self, new_content: str) -> bool:
        """
        Apply improved Dockerfile content.

        Args:
            new_content: New Dockerfile content to write

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup first
            backup_path = self.create_backup()

            # Write new content
            self.dockerfile_path.write_text(new_content, encoding="utf-8")

            print(f"✅ Applied improvements to: {self.dockerfile_path}")
            return True

        except Exception as e:
            print(f"❌ Error applying improvements: {e}")
            return False

    def validate_dockerfile(self) -> dict:
        """
        Validate the Dockerfile using docker build (dry run).

        Returns:
            Dict with 'valid', 'output', 'error'
        """
        try:
            # Try to parse Dockerfile with docker build --dry-run
            # Note: Not all Docker versions support --dry-run
            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "--no-cache",
                    "--target", "NONEXISTENT_TARGET",  # Trick to parse without building
                    "-f", str(self.dockerfile_path),
                    str(self.dockerfile_path.parent),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # If error is "failed to reach build target", Dockerfile is syntactically valid
            if "failed to reach build target" in result.stderr.lower():
                return {
                    "valid": True,
                    "output": "Dockerfile syntax is valid",
                    "error": None,
                }

            # If error is something else, might be syntax error
            if result.returncode != 0:
                return {
                    "valid": False,
                    "output": result.stdout,
                    "error": result.stderr,
                }

            return {
                "valid": True,
                "output": result.stdout,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            return {
                "valid": False,
                "output": "",
                "error": "Validation timed out",
            }
        except FileNotFoundError:
            return {
                "valid": False,
                "output": "",
                "error": "Docker not found - cannot validate",
            }
        except Exception as e:
            return {
                "valid": False,
                "output": "",
                "error": str(e),
            }

    def rollback(self, backup_path: Path) -> bool:
        """
        Rollback to a previous backup.

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not backup_path.exists():
                print(f"❌ Backup not found: {backup_path}")
                return False

            shutil.copy2(backup_path, self.dockerfile_path)
            print(f"✅ Rolled back to: {backup_path}")
            return True

        except Exception as e:
            print(f"❌ Error during rollback: {e}")
            return False

    def list_backups(self) -> list[Path]:
        """List all available backups."""
        if not self.backup_dir.exists():
            return []

        backups = sorted(
            self.backup_dir.glob(f"{self.dockerfile_path.name}.backup_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        return backups

    def get_improvement_diff(self, new_content: str) -> str:
        """
        Generate diff between current and proposed Dockerfile.

        Args:
            new_content: Proposed new content

        Returns:
            Diff string
        """
        current_content = self.dockerfile_path.read_text(encoding="utf-8")

        current_lines = current_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        # Simple diff (line-by-line comparison)
        diff_lines = []
        diff_lines.append(f"--- {self.dockerfile_path} (original)")
        diff_lines.append(f"+++ {self.dockerfile_path} (improved)")
        diff_lines.append("")

        max_len = max(len(current_lines), len(new_lines))

        for i in range(max_len):
            current_line = current_lines[i] if i < len(current_lines) else ""
            new_line = new_lines[i] if i < len(new_lines) else ""

            if current_line != new_line:
                if current_line:
                    diff_lines.append(f"- {current_line.rstrip()}")
                if new_line:
                    diff_lines.append(f"+ {new_line.rstrip()}")

        return "\n".join(diff_lines)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python apply_dockerfile_improvements.py <dockerfile> [options]")
        print("\nOptions:")
        print("  --content <new-content>    New Dockerfile content (as string)")
        print("  --file <path>              New Dockerfile content (from file)")
        print("  --backup-dir <path>        Custom backup directory")
        print("  --validate                 Validate only (don't apply)")
        print("  --rollback <backup-path>   Rollback to specific backup")
        print("  --list-backups             List available backups")
        print("\nExamples:")
        print('  python apply_dockerfile_improvements.py Dockerfile --file improved.Dockerfile')
        print('  python apply_dockerfile_improvements.py Dockerfile --validate')
        print('  python apply_dockerfile_improvements.py Dockerfile --list-backups')
        sys.exit(1)

    dockerfile_path = sys.argv[1]

    # Parse options
    backup_dir = None
    new_content = None
    validate_only = False
    rollback_path = None
    list_backups = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--backup-dir" and i + 1 < len(sys.argv):
            backup_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--content" and i + 1 < len(sys.argv):
            new_content = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--file" and i + 1 < len(sys.argv):
            new_content = Path(sys.argv[i + 1]).read_text(encoding="utf-8")
            i += 2
        elif sys.argv[i] == "--validate":
            validate_only = True
            i += 1
        elif sys.argv[i] == "--rollback" and i + 1 < len(sys.argv):
            rollback_path = Path(sys.argv[i + 1])
            i += 1
        elif sys.argv[i] == "--list-backups":
            list_backups = True
            i += 1
        else:
            i += 1

    try:
        improver = DockerfileImprover(dockerfile_path, backup_dir)

        # List backups
        if list_backups:
            backups = improver.list_backups()
            if backups:
                print(f"📋 Available backups for {dockerfile_path}:")
                print("")
                for backup in backups:
                    mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                    print(f"  • {backup.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print("No backups found")
            sys.exit(0)

        # Rollback
        if rollback_path:
            success = improver.rollback(rollback_path)
            sys.exit(0 if success else 1)

        # Validate
        if validate_only:
            print(f"🔍 Validating {dockerfile_path}...")
            result = improver.validate_dockerfile()

            if result["valid"]:
                print("✅ Dockerfile is valid")
            else:
                print("❌ Dockerfile has errors:")
                print(result["error"])

            sys.exit(0 if result["valid"] else 1)

        # Apply improvements
        if new_content:
            print(f"📝 Applying improvements to {dockerfile_path}...")
            print("")

            # Show diff
            diff = improver.get_improvement_diff(new_content)
            print("📊 Changes:")
            print(diff)
            print("")

            # Apply
            success = improver.apply_improvement(new_content)

            if success:
                # Validate
                print("")
                print("🔍 Validating improved Dockerfile...")
                validation = improver.validate_dockerfile()

                if validation["valid"]:
                    print("✅ Improved Dockerfile is valid")
                else:
                    print("⚠️  Validation warnings:")
                    print(validation["error"])

            sys.exit(0 if success else 1)

        else:
            print("❌ No content provided. Use --content or --file")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
