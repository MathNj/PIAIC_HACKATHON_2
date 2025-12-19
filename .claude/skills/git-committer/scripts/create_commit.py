#!/usr/bin/env python3
"""
Interactive CLI for creating Conventional Commits.

Usage:
    python create_commit.py
    python create_commit.py --dry-run  # Preview without committing
"""

import subprocess
import sys
import argparse
from typing import Optional

COMMIT_TYPES = {
    'feat': 'A new feature',
    'fix': 'A bug fix',
    'docs': 'Documentation only changes',
    'style': 'Code style changes (formatting, semicolons, etc)',
    'refactor': 'Code refactoring (neither fixes bug nor adds feature)',
    'perf': 'Performance improvement',
    'test': 'Adding or updating tests',
    'build': 'Build system or dependency changes',
    'ci': 'CI/CD configuration changes',
    'chore': 'Other changes (maintenance, tools, etc)',
    'revert': 'Revert a previous commit'
}

def get_staged_files() -> list:
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return [f for f in result.stdout.strip().split('\n') if f]
    except subprocess.CalledProcessError:
        return []

def infer_scope_from_files(files: list) -> Optional[str]:
    """Infer scope from staged files."""
    if not files:
        return None

    # Extract directory or module names
    scopes = set()
    for file in files:
        parts = file.split('/')
        if len(parts) > 1:
            scopes.add(parts[0])
        elif '.' in file:
            # Use file extension as scope
            ext = file.split('.')[-1]
            if ext in ['py', 'js', 'ts', 'java', 'go']:
                scopes.add(ext)

    if len(scopes) == 1:
        return scopes.pop()
    return None

def prompt_choice(prompt: str, choices: dict, default: Optional[str] = None) -> str:
    """Prompt user to select from choices."""
    print(f"\n{prompt}")
    for key, value in choices.items():
        marker = " (default)" if key == default else ""
        print(f"  {key}: {value}{marker}")

    while True:
        choice = input(f"\nSelect [{'/'.join(choices.keys())}]: ").strip().lower()

        if not choice and default:
            return default

        if choice in choices:
            return choice

        print(f"Invalid choice. Please select from: {', '.join(choices.keys())}")

def prompt_text(prompt: str, default: Optional[str] = None, required: bool = True) -> str:
    """Prompt user for text input."""
    default_str = f" (default: {default})" if default else ""
    full_prompt = f"\n{prompt}{default_str}: "

    while True:
        value = input(full_prompt).strip()

        if not value and default:
            return default

        if not value and required:
            print("This field is required. Please enter a value.")
            continue

        return value

def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Prompt user for yes/no question."""
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"\n{prompt} [{default_str}]: "

    while True:
        value = input(full_prompt).strip().lower()

        if not value:
            return default

        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False

        print("Please answer 'y' or 'n'")

def build_commit_message(
    commit_type: str,
    scope: Optional[str],
    description: str,
    body: Optional[str],
    breaking: bool,
    issue_refs: Optional[str]
) -> str:
    """Build conventional commit message."""
    # Header
    header = commit_type
    if scope:
        header += f"({scope})"
    if breaking:
        header += "!"
    header += f": {description}"

    # Full message
    parts = [header]

    # Body
    if body:
        parts.append("")
        parts.append(body)

    # Footer
    footer_parts = []

    if breaking:
        breaking_desc = prompt_text(
            "Describe the breaking change",
            required=True
        )
        footer_parts.append(f"BREAKING CHANGE: {breaking_desc}")

    if issue_refs:
        footer_parts.append(issue_refs)

    if footer_parts:
        parts.append("")
        parts.extend(footer_parts)

    return "\n".join(parts)

def main():
    parser = argparse.ArgumentParser(description='Create Conventional Commits interactively')
    parser.add_argument('--dry-run', action='store_true', help='Preview without committing')
    args = parser.parse_args()

    # Check for staged files
    staged_files = get_staged_files()

    if not staged_files and not args.dry_run:
        print("Error: No files staged for commit")
        print("Stage files with: git add <files>")
        sys.exit(1)

    print("=== Conventional Commit Creator ===")

    if staged_files:
        print(f"\nStaged files ({len(staged_files)}):")
        for file in staged_files[:5]:
            print(f"  - {file}")
        if len(staged_files) > 5:
            print(f"  ... and {len(staged_files) - 5} more")

    # Prompt for commit components
    commit_type = prompt_choice("Select commit type", COMMIT_TYPES)

    inferred_scope = infer_scope_from_files(staged_files)
    scope_prompt = "Enter scope (optional)"
    scope = prompt_text(scope_prompt, default=inferred_scope, required=False)

    description = prompt_text(
        "Enter short description (lowercase, no period)",
        required=True
    )

    # Validate description format
    if description and description[0].isupper():
        print("Warning: Description should start with lowercase")
        if not prompt_yes_no("Continue anyway?", default=False):
            sys.exit(0)

    if description.endswith('.'):
        print("Warning: Description should not end with period")
        if not prompt_yes_no("Continue anyway?", default=False):
            sys.exit(0)

    add_body = prompt_yes_no("Add detailed body?", default=False)
    body = None
    if add_body:
        print("\nEnter body (empty line to finish):")
        body_lines = []
        while True:
            line = input()
            if not line:
                break
            body_lines.append(line)
        body = "\n".join(body_lines) if body_lines else None

    breaking = prompt_yes_no("Is this a breaking change?", default=False)

    add_refs = prompt_yes_no("Reference issues?", default=False)
    issue_refs = None
    if add_refs:
        issue_refs = prompt_text(
            "Enter issue references (e.g., 'Closes #123, Fixes #456')",
            required=False
        )

    # Build commit message
    message = build_commit_message(
        commit_type,
        scope,
        description,
        body,
        breaking,
        issue_refs
    )

    # Preview
    print("\n" + "="*60)
    print("Commit message preview:")
    print("="*60)
    print(message)
    print("="*60)

    if args.dry_run:
        print("\n[Dry run - no commit created]")
        sys.exit(0)

    # Confirm
    if not prompt_yes_no("\nProceed with commit?", default=True):
        print("Commit cancelled")
        sys.exit(0)

    # Create commit
    try:
        subprocess.run(
            ['git', 'commit', '-m', message],
            check=True
        )
        print("\n[OK] Commit created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Commit failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
