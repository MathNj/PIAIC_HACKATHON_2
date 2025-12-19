---
name: git-committer
description: Enforce Conventional Commits specification for git commit messages. Use when Claude needs to create git commits, validate commit message format, set up commit hooks, or help users follow Conventional Commits standard (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert types with optional scopes, breaking changes, and issue references). Automatically triggered when user says "make a commit", "create a conventional commit", "commit with proper format", or "enforce commit standards".
---

# Git Committer

Enforce Conventional Commits specification for all git commits.

## Quick Start

### Create a Conventional Commit

Use the interactive script to guide commit creation:

```bash
python scripts/create_commit.py
```

The script will:
1. Show staged files
2. Prompt for commit type (feat, fix, docs, etc.)
3. Infer scope from files
4. Guide you through description, body, breaking changes, and issue references
5. Preview the commit message
6. Create the commit

### Validate a Commit Message

```bash
# Validate from command line
python scripts/validate_commit.py "feat(auth): add JWT authentication"

# Validate from file
python scripts/validate_commit.py --file commit-msg.txt
```

### Install Git Hook (Automated Enforcement)

```bash
python scripts/commit_hook.py --install
```

This installs a commit-msg hook that automatically validates all commits before they're created.

## Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style (formatting, semicolons, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvement
- **test**: Adding/updating tests
- **build**: Build system or dependencies
- **ci**: CI/CD changes
- **chore**: Maintenance
- **revert**: Revert previous commit

### Examples

Simple feature:
```
feat(auth): add OAuth2 support
```

Bug fix with issue reference:
```
fix(api): resolve null pointer exception

Fixes #123
```

Breaking change:
```
feat(api)!: redesign user endpoints

BREAKING CHANGE: endpoints moved from /api/users to /api/v2/users
```

## Guidelines

1. **Description**: Start with lowercase, no period at end, under 72 characters
2. **Scope**: Use parentheses for affected module (optional but recommended)
3. **Breaking Changes**: Use `!` after type/scope AND include `BREAKING CHANGE:` footer
4. **Issue References**: Use `Closes #123`, `Fixes #456`, or `Refs #789` in footer

## Detailed Documentation

- **Full specification**: See [references/conventional-commits-spec.md](references/conventional-commits-spec.md)
- **More examples**: See [references/examples.md](references/examples.md)

## Workflow

When user requests a commit:

1. **Check staged files**: Run `git diff --cached --name-only` to see what's being committed
2. **Analyze changes**: Review the staged files to understand the nature of changes
3. **Determine type**: Classify as feat, fix, docs, refactor, etc.
4. **Infer scope**: Extract scope from file paths (e.g., `backend/auth/` → scope: auth)
5. **Generate description**: Create concise description starting with lowercase
6. **Add body if needed**: For complex changes, explain the "why" in the body
7. **Check for breaking changes**: Identify if this breaks existing functionality
8. **Reference issues**: Link to issue tracker items if applicable
9. **Format commit**: Assemble the commit message following Conventional Commits spec
10. **Validate**: Run through validation checks before committing
11. **Create commit**: Use `git commit -m "message"` or the create_commit.py script

## Common Scenarios

### Scenario 1: User asks to commit staged changes

```
User: "Commit these changes"

Steps:
1. Check staged files: git diff --cached --name-only
2. Analyze: "Added JWT authentication to backend/auth/jwt.py"
3. Classify: feat (new feature)
4. Scope: auth (from file path)
5. Description: "add JWT authentication support"
6. Body: Explain implementation if complex
7. Generate: "feat(auth): add JWT authentication support"
8. Commit: git commit -m "feat(auth): add JWT authentication support"
```

### Scenario 2: User wants to enforce commit standards

```
User: "Set up conventional commits for this project"

Steps:
1. Install git hook: python scripts/commit_hook.py --install
2. Inform: "Git hook installed. All commits will be validated automatically."
3. Test: Create a test commit to verify it works
```

### Scenario 3: User provides commit message to validate

```
User: "Check this commit message: 'Added new feature'"

Steps:
1. Validate: python scripts/validate_commit.py "Added new feature"
2. Report errors: "Invalid format. Missing type, description should be lowercase"
3. Suggest: "feat: add new feature" or ask for more details about the feature
```

### Scenario 4: Breaking change commit

```
User: "Commit this API redesign, it breaks backward compatibility"

Steps:
1. Identify: This is a breaking change
2. Type: feat (new design) with ! indicator
3. Scope: api
4. Description: "redesign user endpoints"
5. Add footer: "BREAKING CHANGE: endpoints moved to /api/v2/"
6. Generate:
   feat(api)!: redesign user endpoints

   BREAKING CHANGE: User endpoints moved from /api/users
   to /api/v2/users. Update all API clients accordingly.
```

## Validation Rules

The validation script checks:

- ✓ Commit message not empty
- ✓ Matches format: `<type>(<scope>): <description>`
- ✓ Type is valid (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
- ✓ Description starts with lowercase letter
- ✓ Description doesn't end with period
- ✓ Header length under 72 characters
- ✓ Breaking changes use both `!` and `BREAKING CHANGE:` footer
- ✓ Footer uses valid tokens (BREAKING CHANGE, Refs, Closes, Fixes, etc.)

## Tips for Users

1. **Be specific with scopes**: Use `feat(auth)` not `feat(backend)`
2. **Keep descriptions concise**: Aim for under 50 characters
3. **Use body for complex changes**: Explain the "why" not the "what"
4. **Always reference issues**: Link commits to issue tracker
5. **Test before committing**: Ensure code works before commit
6. **Group related changes**: One commit per logical change
7. **Use imperative mood**: "add feature" not "added feature" or "adding feature"

## Troubleshooting

### Hook not working on Windows
- Ensure Python is in PATH
- Check hook file has correct line endings (LF not CRLF)
- Try running hook manually to see error messages

### Validation too strict
- Review the error messages - they explain what's wrong
- Use `git commit --no-verify` to bypass (not recommended)
- Update the validation script if project has custom requirements

### Can't determine scope automatically
- Look at the directory structure of changed files
- Use the most specific module name
- When in doubt, ask the user or use a general scope

## Integration with Tools

### CI/CD
Add commit message validation to your CI pipeline:

```yaml
# GitHub Actions example
- name: Validate commit messages
  run: |
    python scripts/validate_commit.py --file .git/COMMIT_EDITMSG
```

### Pre-commit framework
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

### VSCode extension
Recommend the "Conventional Commits" extension for VSCode users to get autocomplete and validation in the editor.

## Benefits

- **Automated changelogs**: Generate release notes automatically
- **Semantic versioning**: Determine version bumps from commit types
- **Clear history**: Understand changes at a glance
- **Better collaboration**: Consistent format across team
- **Easier rollbacks**: Quickly identify commits to revert
- **CI/CD triggers**: Automate deployments based on commit types
