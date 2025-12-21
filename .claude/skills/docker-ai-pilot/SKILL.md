---
name: docker-ai-pilot
description: Interface with Docker AI (Gordon) for intelligent containerization in Phase IV deployment. Use when: (1) Optimizing Dockerfiles for size or performance, (2) Debugging container crashes or failures, (3) Generating production-ready Dockerfiles, (4) Analyzing security vulnerabilities in images, (5) Troubleshooting container networking or connectivity issues, (6) Applying AI-suggested improvements to containers, or (7) Any Docker/containerization task requiring intelligent analysis. Wraps `docker ai` CLI commands, parses natural language output, and provides actionable fixes with automatic application capability. Falls back to standard Docker commands if Gordon unavailable.
---

# Docker AI Pilot

Intelligent containerization using Docker AI (Gordon) for Phase IV deployment tasks.

## Overview

Docker AI Pilot interfaces with Gordon (Docker's AI assistant) to provide intelligent container operations:
- Natural language Dockerfile optimization
- AI-powered crash diagnosis
- Automated improvement application
- Security vulnerability detection
- Fallback to standard Docker commands when Gordon unavailable

**Phase IV Requirement:** This skill is the preferred method for all containerization tasks in Phase IV.

## Quick Start

### Prerequisites

**Gordon Available (Preferred):**
- Docker Desktop 4.26+ installed
- Docker AI feature enabled in settings

**Gordon Unavailable (Fallback):**
- Standard Docker CLI installed
- Uses templates and heuristics

### Basic Workflow

1. **Ask Gordon a Question**
2. **Review Suggestions**
3. **Apply Improvements (Optional)**
4. **Validate Changes**

## Common Use Cases

### 1. Optimize Dockerfile for Size

```bash
# Using gordon_wrapper.py
python scripts/gordon_wrapper.py "optimize this dockerfile for smaller image size" --file Dockerfile

# Direct docker ai command
docker ai "reduce image size" --file Dockerfile
```

**Gordon will suggest:**
- Multi-stage builds
- Alpine/slim base images
- Dependency cleanup
- Layer optimization

**Apply automatically:**
```bash
# Extract suggested Dockerfile from Gordon's output
python scripts/apply_dockerfile_improvements.py Dockerfile --file improved.Dockerfile
```

### 2. Debug Container Crash

```bash
# Get container ID
CONTAINER_ID=$(docker ps -a --filter status=exited --format "{{.ID}}" | head -1)

# Ask Gordon why it crashed
python scripts/gordon_wrapper.py "why did this container crash?" --container $CONTAINER_ID

# Or direct command
docker ai "analyze container failure" --container $CONTAINER_ID
```

**Gordon analyzes:**
- Exit codes
- Error logs
- Resource constraints
- Misconfiguration

### 3. Generate Production Dockerfile

```bash
# Ask Gordon to create Dockerfile
python scripts/gordon_wrapper.py "generate production dockerfile for fastapi app with postgresql"

# Fallback: Use template
cp assets/dockerfile-templates/fastapi.Dockerfile ./Dockerfile
```

**Gordon creates:**
- Multi-stage optimized Dockerfile
- Security hardening (non-root user)
- Health checks
- Proper signal handling

### 4. Security Scan and Fix

```bash
# Scan for vulnerabilities
docker ai "identify security issues in this dockerfile" --file Dockerfile

# Apply Gordon's security suggestions
python scripts/apply_dockerfile_improvements.py Dockerfile --file secured.Dockerfile
```

### 5. Troubleshoot Networking

```bash
# Diagnose connectivity issues
docker ai "container can't connect to database on port 5432, why?"

# Network configuration help
docker ai "how do I configure custom network for my containers?"
```

## Workflow Patterns

### Pattern 1: Interactive Optimization

```bash
# Step 1: Initial analysis
python scripts/gordon_wrapper.py "analyze this dockerfile" --file Dockerfile --json > analysis.json

# Step 2: Review suggestions
cat analysis.json | jq '.suggestions'

# Step 3: Ask for specific improvements
python scripts/gordon_wrapper.py "how can I reduce build time?"

# Step 4: Apply improvements
python scripts/apply_dockerfile_improvements.py Dockerfile --file optimized.Dockerfile

# Step 5: Validate
python scripts/apply_dockerfile_improvements.py Dockerfile --validate

# Step 6: Build and test
docker build -t myapp:optimized .
```

### Pattern 2: Automated CI/CD Integration

```yaml
# .github/workflows/docker-optimize.yml
name: Optimize Dockerfile

on:
  pull_request:
    paths:
      - 'Dockerfile'

jobs:
  optimize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Optimize with Gordon
        run: |
          python scripts/gordon_wrapper.py \
            "optimize this dockerfile for production" \
            --file Dockerfile \
            --json > suggestions.json

      - name: Review suggestions
        run: |
          echo "Gordon Suggestions:"
          cat suggestions.json | jq '.suggestions'

      - name: Post as PR comment
        uses: actions/github-script@v6
        with:
          script: |
            const suggestions = require('./suggestions.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: suggestions.output
            });
```

### Pattern 3: Fallback Strategy

```python
# Automatic fallback when Gordon unavailable
from scripts.gordon_wrapper import GordonWrapper

wrapper = GordonWrapper()

# Automatically uses fallback if Gordon not available
response = wrapper.execute_prompt(
    "optimize dockerfile",
    dockerfile_path="Dockerfile"
)

if response["fallback_used"]:
    print("⚠️  Using fallback suggestions (Gordon unavailable)")
    # Fallback provides template-based suggestions
else:
    print("✅ Gordon analysis complete")

# Apply suggestions regardless of source
for suggestion in response["suggestions"]:
    if suggestion["type"] == "code":
        # Apply code suggestion
        with open("Dockerfile.improved", "w") as f:
            f.write(suggestion["content"])
```

## Script Reference

### gordon_wrapper.py

**Purpose:** Execute Docker AI commands programmatically

**Usage:**
```bash
python scripts/gordon_wrapper.py <prompt> [options]

Options:
  --file <path>        Path to Dockerfile for analysis
  --container <id>     Container ID for debugging
  --json               Output JSON format
```

**Examples:**
```bash
# Basic prompt
python scripts/gordon_wrapper.py "optimize dockerfile"

# With file context
python scripts/gordon_wrapper.py "analyze this dockerfile" --file Dockerfile

# With container context
python scripts/gordon_wrapper.py "why did this crash?" --container abc123

# JSON output
python scripts/gordon_wrapper.py "security scan" --file Dockerfile --json
```

**Returns:**
```json
{
  "success": true,
  "output": "Gordon's natural language response",
  "suggestions": [
    {
      "type": "code",
      "content": "Suggested Dockerfile content",
      "description": "Multi-stage build"
    }
  ],
  "fallback_used": false,
  "error": null
}
```

### apply_dockerfile_improvements.py

**Purpose:** Apply and validate Dockerfile changes

**Usage:**
```bash
python scripts/apply_dockerfile_improvements.py <dockerfile> [options]

Options:
  --content <text>       New Dockerfile content (string)
  --file <path>          New Dockerfile content (from file)
  --backup-dir <path>    Custom backup directory
  --validate             Validate only (don't apply)
  --rollback <path>      Rollback to specific backup
  --list-backups         List available backups
```

**Examples:**
```bash
# Apply from file
python scripts/apply_dockerfile_improvements.py Dockerfile --file improved.Dockerfile

# Validate only
python scripts/apply_dockerfile_improvements.py Dockerfile --validate

# List backups
python scripts/apply_dockerfile_improvements.py Dockerfile --list-backups

# Rollback
python scripts/apply_dockerfile_improvements.py Dockerfile --rollback dockerfile_backups/Dockerfile.backup_20250121_120000
```

**Features:**
- ✅ Automatic backup with timestamp
- ✅ Diff preview before applying
- ✅ Validation after apply
- ✅ Rollback capability
- ✅ Backup management

## Dockerfile Templates

When Gordon unavailable, use production-ready templates:

### FastAPI Application

```bash
cp assets/dockerfile-templates/fastapi.Dockerfile ./Dockerfile
```

**Features:**
- Multi-stage build (builder + runtime)
- Non-root user
- Health check
- Optimized for production

### Next.js Application

```bash
cp assets/dockerfile-templates/nextjs.Dockerfile ./Dockerfile
```

**Features:**
- Standalone output support
- Multi-stage (deps + builder + runner)
- Minimal runtime image
- Proper Next.js 16+ configuration

### Python CLI Tool

```bash
cp assets/dockerfile-templates/python-cli.Dockerfile ./Dockerfile
```

**Features:**
- Minimal CLI-optimized image
- ENTRYPOINT configuration
- Volume mount support

## Advanced References

For detailed information, see reference files:

### Docker AI Commands (`references/docker-ai-commands.md`)

Comprehensive Gordon command reference:
- Common prompts and use cases
- Output parsing patterns
- Best practices
- Troubleshooting

**When to read:** When crafting effective Gordon prompts or parsing complex output

### Optimization Strategies (`references/optimization-strategies.md`)

Production Dockerfile optimization patterns:
- Multi-stage builds
- Layer caching
- Image size reduction
- Security hardening
- Build performance

**When to read:** When manually optimizing Dockerfiles or understanding Gordon's suggestions

## Integration with cloudops-engineer

This skill is designed for use by the **cloudops-engineer** agent in Phase IV:

```python
# cloudops-engineer uses docker-ai-pilot
from skills.docker_ai_pilot import GordonWrapper

# Optimize Dockerfile for deployment
gordon = GordonWrapper()
result = gordon.execute_prompt(
    "optimize this dockerfile for kubernetes deployment",
    dockerfile_path="backend/Dockerfile"
)

# Apply improvements
if result["success"]:
    apply_improvements(result["suggestions"])
```

**Agent responsibilities:**
- Use Gordon for all containerization tasks first
- Fall back to templates if Gordon unavailable
- Validate all changes before deployment
- Document optimization decisions in ADRs

## Fallback Decision Matrix

| Gordon Status | Task | Action |
|--------------|------|--------|
| ✅ Available | Any task | Use `docker ai` command |
| ❌ Unavailable | Dockerfile generation | Use template from `assets/` |
| ❌ Unavailable | Optimization | Use patterns from `references/optimization-strategies.md` |
| ❌ Unavailable | Debugging | Standard `docker logs`, `docker inspect` |
| ❌ Unavailable | Security scan | Use `docker scout` or `trivy` |

## Best Practices

### 1. Always Validate Before Deploying

```bash
# Validate Dockerfile syntax
python scripts/apply_dockerfile_improvements.py Dockerfile --validate

# Build to ensure it works
docker build -t test-image .

# Run to ensure it starts
docker run --rm test-image
```

### 2. Use Specific Prompts

```bash
# ❌ Vague
docker ai "fix dockerfile"

# ✅ Specific
docker ai "optimize dockerfile to reduce build time by caching pip dependencies"
```

### 3. Iterate with Gordon

```bash
# Start broad
docker ai "optimize dockerfile"

# Refine based on response
docker ai "how much can multi-stage build reduce the size?"

# Apply and verify
docker ai "validate this optimized dockerfile"
```

### 4. Backup Before Applying

```bash
# Automatic backup before changes
python scripts/apply_dockerfile_improvements.py Dockerfile --file new.Dockerfile

# Manual backup
cp Dockerfile Dockerfile.backup.$(date +%Y%m%d_%H%M%S)
```

### 5. Document Decisions

When Gordon suggests significant changes, document the decision:

```bash
# Create ADR for architectural decisions
/sp.adr "switch-to-multistage-builds"
```

## Troubleshooting

### Gordon Not Responding

**Check Gordon availability:**
```bash
docker ai --version
```

**Enable Gordon:**
1. Open Docker Desktop
2. Settings → Features
3. Enable "Docker AI (Beta)"
4. Restart Docker Desktop

**Use fallback:**
```bash
# gordon_wrapper.py automatically falls back
python scripts/gordon_wrapper.py "optimize dockerfile" --file Dockerfile
# Output: "⚠️  Docker AI (Gordon) unavailable - using fallback"
```

### Suggestions Don't Apply to My Stack

**Provide more context:**
```bash
# Include technology stack in prompt
docker ai "optimize dockerfile for python fastapi application with postgresql and redis dependencies"
```

### Build Fails After Applying Suggestions

**Rollback:**
```bash
# List backups
python scripts/apply_dockerfile_improvements.py Dockerfile --list-backups

# Rollback to previous version
python scripts/apply_dockerfile_improvements.py Dockerfile --rollback <backup-path>
```

**Validate before building:**
```bash
python scripts/apply_dockerfile_improvements.py Dockerfile --validate
```

## Quick Command Reference

```bash
# Optimize Dockerfile
python scripts/gordon_wrapper.py "optimize dockerfile" --file Dockerfile

# Debug container
python scripts/gordon_wrapper.py "why did container crash?" --container ID

# Generate Dockerfile
python scripts/gordon_wrapper.py "create dockerfile for <stack>"

# Apply improvements
python scripts/apply_dockerfile_improvements.py Dockerfile --file improved.Dockerfile

# Validate Dockerfile
python scripts/apply_dockerfile_improvements.py Dockerfile --validate

# Rollback changes
python scripts/apply_dockerfile_improvements.py Dockerfile --rollback <backup>

# Use template (fallback)
cp assets/dockerfile-templates/fastapi.Dockerfile ./Dockerfile
```

## Phase IV Compliance

✅ **Gordon First:** Always attempt to use Gordon before falling back
✅ **Fallback Ready:** Graceful degradation when Gordon unavailable
✅ **Validation:** All changes validated before deployment
✅ **Documentation:** ADRs for significant containerization decisions
✅ **Integration:** Designed for cloudops-engineer agent use
✅ **Production-Ready:** All templates and suggestions are production-tested
