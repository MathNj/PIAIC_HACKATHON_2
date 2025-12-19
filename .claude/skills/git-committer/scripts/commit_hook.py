#!/usr/bin/env python3
"""
Git commit-msg hook to enforce Conventional Commits format.

Installation:
    1. Copy this file to .git/hooks/commit-msg
    2. Make it executable: chmod +x .git/hooks/commit-msg

Or use the install command:
    python commit_hook.py --install

Usage (as git hook):
    This script is automatically called by git after commit message is written.
"""

import sys
import os
import argparse
import shutil
from pathlib import Path

# Import validation logic
from validate_commit import validate_commit_message

def install_hook():
    """Install this script as a git commit-msg hook."""
    # Find git directory
    git_dir = None
    current = Path.cwd()

    while current != current.parent:
        git_candidate = current / '.git'
        if git_candidate.exists():
            git_dir = git_candidate
            break
        current = current.parent

    if not git_dir:
        print("Error: Not in a git repository")
        sys.exit(1)

    # Create hooks directory if it doesn't exist
    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)

    # Copy this script to commit-msg hook
    hook_path = hooks_dir / 'commit-msg'
    script_path = Path(__file__).resolve()

    # Check if validate_commit.py exists
    validate_script = script_path.parent / 'validate_commit.py'
    if not validate_script.exists():
        print(f"Error: validate_commit.py not found at {validate_script}")
        sys.exit(1)

    # Copy validation script
    shutil.copy(validate_script, hooks_dir / 'validate_commit.py')

    # Create hook script
    hook_content = f"""#!/usr/bin/env python3
import sys
from pathlib import Path

# Add hooks directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from validate_commit import validate_commit_message

def main():
    # Read commit message from file
    commit_msg_file = sys.argv[1]

    with open(commit_msg_file, 'r', encoding='utf-8') as f:
        message = f.read()

    # Validate
    is_valid, errors = validate_commit_message(message)

    if not is_valid:
        print("\\n[ERROR] Invalid Conventional Commit message:\\n")
        for error in errors:
            print(f"  - {{error}}")
        print("\\nCommit rejected. Fix the message and try again.\\n")
        sys.exit(1)

    print("[OK] Valid Conventional Commit message")
    sys.exit(0)

if __name__ == '__main__':
    main()
"""

    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    # Make executable (Unix-like systems)
    if os.name != 'nt':  # Not Windows
        os.chmod(hook_path, 0o755)

    print(f"[OK] Commit hook installed at: {hook_path}")
    print("\nAll commits will now be validated against Conventional Commits spec.")
    print("To bypass the hook (not recommended): git commit --no-verify")

def uninstall_hook():
    """Uninstall the commit-msg hook."""
    # Find git directory
    git_dir = None
    current = Path.cwd()

    while current != current.parent:
        git_candidate = current / '.git'
        if git_candidate.exists():
            git_dir = git_candidate
            break
        current = current.parent

    if not git_dir:
        print("Error: Not in a git repository")
        sys.exit(1)

    hook_path = git_dir / 'hooks' / 'commit-msg'

    if hook_path.exists():
        hook_path.unlink()
        print(f"[OK] Commit hook removed from: {hook_path}")
    else:
        print("No commit hook found")

def main():
    parser = argparse.ArgumentParser(description='Conventional Commits git hook')
    parser.add_argument('--install', action='store_true', help='Install as git commit-msg hook')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall git commit-msg hook')

    # If called by git, first argument is the commit message file
    if len(sys.argv) == 2 and not sys.argv[1].startswith('--'):
        # Running as git hook
        commit_msg_file = sys.argv[1]

        with open(commit_msg_file, 'r', encoding='utf-8') as f:
            message = f.read()

        # Validate
        is_valid, errors = validate_commit_message(message)

        if not is_valid:
            print("\n[ERROR] Invalid Conventional Commit message:\n")
            for error in errors:
                print(f"  - {error}")
            print("\nCommit rejected. Fix the message and try again.")
            print("\nExample: feat(auth): add JWT authentication")
            print("To bypass: git commit --no-verify (not recommended)\n")
            sys.exit(1)

        print("[OK] Valid Conventional Commit message")
        sys.exit(0)

    # Otherwise, parse as installation command
    args = parser.parse_args()

    if args.install:
        install_hook()
    elif args.uninstall:
        uninstall_hook()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
