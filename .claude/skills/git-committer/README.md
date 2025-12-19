# Git Committer Skill

Enforce Conventional Commits specification for all git commits in your project.

## Overview

The git-committer skill provides a complete toolkit for enforcing the Conventional Commits standard in your development workflow. It includes validation, interactive commit creation, and automatic enforcement via git hooks.

## Quick Start

### 1. Validate a Commit Message

```bash
python scripts/validate_commit.py "feat(auth): add JWT authentication"
```

### 2. Create a Conventional Commit Interactively

```bash
python scripts/create_commit.py
```

The script will guide you through:
- Selecting commit type (feat, fix, docs, etc.)
- Inferring scope from staged files
- Writing description, body, and footers
- Previewing and confirming the commit

### 3. Install Git Hook (Automatic Enforcement)

```bash
python scripts/commit_hook.py --install
```

This installs a commit-msg hook that validates every commit before it's created.

## What's Included

### Scripts

- **validate_commit.py**: Validates commit messages against Conventional Commits spec
- **create_commit.py**: Interactive CLI for creating well-formatted commits
- **commit_hook.py**: Git hook installer for automatic enforcement

### References

- **conventional-commits-spec.md**: Complete Conventional Commits v1.0.0 specification
- **examples.md**: Common commit message patterns and examples

### Documentation

- **SKILL.md**: Comprehensive skill documentation with workflow and scenarios

## Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Valid Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `build`: Build system or dependencies
- `ci`: CI/CD changes
- `chore`: Maintenance
- `revert`: Revert previous commit

## Examples

### Simple Feature
```
feat(auth): add OAuth2 support
```

### Bug Fix with Issue Reference
```
fix(api): resolve null pointer exception

Fixes #123
```

### Breaking Change
```
feat(api)!: redesign user endpoints

BREAKING CHANGE: endpoints moved from /api/users to /api/v2/users
```

## Benefits

- **Automated changelogs**: Generate release notes automatically
- **Semantic versioning**: Determine version bumps from commit types
- **Clear history**: Understand changes at a glance
- **Better collaboration**: Consistent format across team
- **Easier rollbacks**: Quickly identify commits to revert
- **CI/CD triggers**: Automate deployments based on commit types

## Requirements

- Python 3.7+
- Git repository

## Integration

### CI/CD

Add commit message validation to your CI pipeline:

```yaml
# GitHub Actions example
- name: Validate commit messages
  run: |
    python scripts/validate_commit.py --file .git/COMMIT_EDITMSG
```

### Pre-commit Framework

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: conventional-commits
      name: Conventional Commits
      entry: python scripts/validate_commit.py
      language: system
      stages: [commit-msg]
```

## Troubleshooting

### Hook not working on Windows

- Ensure Python is in PATH
- Check hook file has correct line endings (LF not CRLF)
- Try running hook manually to see error messages

### Validation too strict

- Review the error messages - they explain what's wrong
- Use `git commit --no-verify` to bypass (not recommended)
- Update the validation script if project has custom requirements

## License

Part of the Todo App Hackathon II project.
