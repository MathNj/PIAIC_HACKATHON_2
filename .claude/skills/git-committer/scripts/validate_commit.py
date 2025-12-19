#!/usr/bin/env python3
"""
Validate commit messages against Conventional Commits specification.

Usage:
    python validate_commit.py "feat(auth): add JWT authentication"
    python validate_commit.py --file commit-msg.txt
"""

import re
import sys
import argparse
from typing import Tuple, Optional, List

# Conventional Commits regex pattern
COMMIT_PATTERN = re.compile(
    r'^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)'
    r'(?:\((?P<scope>[a-z0-9\-]+)\))?'
    r'(?P<breaking>!)?'
    r': '
    r'(?P<description>.+)'
    r'(?:\n\n(?P<body>[\s\S]+))?'
    r'(?:\n\n(?P<footer>[\s\S]+))?$'
)

VALID_TYPES = [
    'feat',     # New feature
    'fix',      # Bug fix
    'docs',     # Documentation only
    'style',    # Code style (formatting, semicolons, etc)
    'refactor', # Code refactoring
    'perf',     # Performance improvement
    'test',     # Adding/updating tests
    'build',    # Build system or dependencies
    'ci',       # CI/CD changes
    'chore',    # Other changes (maintenance, tools, etc)
    'revert'    # Revert previous commit
]

def validate_commit_message(message: str) -> Tuple[bool, List[str]]:
    """
    Validate commit message against Conventional Commits spec.

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check for empty message
    if not message or not message.strip():
        errors.append("Commit message cannot be empty")
        return False, errors

    # Split into header and rest
    lines = message.split('\n')
    header = lines[0]

    # Validate header length (recommended 50 chars, max 72)
    if len(header) > 72:
        errors.append(f"Header too long ({len(header)} chars). Keep under 72 characters.")

    # Try to match pattern
    match = COMMIT_PATTERN.match(message)

    if not match:
        errors.append("Commit message does not match Conventional Commits format")
        errors.append("Expected format: <type>(<scope>): <description>")
        errors.append(f"Valid types: {', '.join(VALID_TYPES)}")
        return False, errors

    # Extract components
    commit_type = match.group('type')
    scope = match.group('scope')
    breaking = match.group('breaking')
    description = match.group('description')
    body = match.group('body')
    footer = match.group('footer')

    # Validate type
    if commit_type not in VALID_TYPES:
        errors.append(f"Invalid type '{commit_type}'. Must be one of: {', '.join(VALID_TYPES)}")

    # Validate description
    if not description or not description.strip():
        errors.append("Description cannot be empty")
    elif description[0].isupper():
        errors.append("Description should start with lowercase letter")
    elif description.endswith('.'):
        errors.append("Description should not end with a period")

    # Validate breaking change
    if breaking or (footer and 'BREAKING CHANGE:' in footer):
        if not (breaking and footer and 'BREAKING CHANGE:' in footer):
            errors.append("Breaking changes must use both '!' and 'BREAKING CHANGE:' footer")

    # Validate body format (if present)
    if body:
        if not body.strip():
            errors.append("Body should not be just whitespace")

    # Validate footer format (if present)
    if footer:
        # Check for valid footer tokens
        footer_pattern = re.compile(
            r'^(BREAKING CHANGE|Refs?|Closes?|Fixes?|Resolves?|See also):\s+.+',
            re.MULTILINE
        )
        if not footer_pattern.search(footer):
            errors.append("Footer must use valid tokens (BREAKING CHANGE, Refs, Closes, etc.)")

    return len(errors) == 0, errors

def main():
    parser = argparse.ArgumentParser(description='Validate Conventional Commits message')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('message', nargs='?', help='Commit message to validate')
    group.add_argument('--file', '-f', help='Read commit message from file')

    args = parser.parse_args()

    # Get commit message
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                message = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
    else:
        message = args.message

    # Validate
    is_valid, errors = validate_commit_message(message)

    # Output results
    if is_valid:
        print("[OK] Valid Conventional Commit message")
        sys.exit(0)
    else:
        print("[ERROR] Invalid Conventional Commit message\n")
        for error in errors:
            print(f"  - {error}")
        print("\nExample valid commit:")
        print("  feat(auth): add JWT authentication support")
        print("\n  Implement JWT token generation and validation")
        print("  for user authentication endpoints.")
        print("\n  Closes #123")
        sys.exit(1)

if __name__ == '__main__':
    main()
