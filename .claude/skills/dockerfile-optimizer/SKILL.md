---
name: dockerfile-optimizer
description: Create production-optimized Dockerfiles with multi-stage builds, security hardening, and minimal image sizes. Use when: (1) Creating new Dockerfiles for applications, (2) Optimizing existing Docker images (reduce size, improve build time), (3) Implementing security best practices (non-root users, vulnerability scanning), (4) Setting up multi-stage builds for Python/Node.js/Go applications, (5) Configuring BuildKit features (cache mounts, secrets), (6) Adding health checks and metadata labels, or (7) Troubleshooting Docker build issues. This skill provides production-ready Dockerfile templates, optimization patterns, and security guidelines for FastAPI, Next.js, and general containerization needs.
---

# Dockerfile Optimizer

This skill provides production-ready Dockerfile templates and optimization patterns for creating secure, efficient container images.

## Quick Start Workflow

### Step 1: Review Best Practices Guide

Read the comprehensive best practices guide:
```bash
.claude/skills/dockerfile-optimizer/references/dockerfile-best-practices.md
```

This guide provides:
- Multi-stage build patterns
- Layer caching optimization
- Base image selection guidance
- Security best practices
- BuildKit advanced features
- Common mistakes and solutions
- Performance benchmarks

### Step 2: Choose Template

**For Python FastAPI backend**:
```bash
cp .claude/skills/dockerfile-optimizer/assets/examples/Dockerfile.fastapi ./backend/Dockerfile
```

**For Next.js frontend**:
```bash
cp .claude/skills/dockerfile-optimizer/assets/examples/Dockerfile.nextjs ./frontend/Dockerfile
```

### Step 3: Customize for Your Project

**FastAPI customization**:
1. Update application path if not `app.main:app`
2. Adjust worker count based on resources
3. Add environment-specific build args
4. Configure health check endpoint

**Next.js customization**:
1. Ensure `next.config.js` has `output: 'standalone'`
2. Update health check API route
3. Add environment variables
4. Configure port if not 3000

### Step 4: Build and Test

```bash
# Build with BuildKit enabled
export DOCKER_BUILDKIT=1
docker build -t my-app:latest .

# Test the image
docker run -p 8000:8000 my-app:latest

# Check image size
docker images my-app:latest

# Inspect layers
docker history my-app:latest
```

### Step 5: Optimize Further

**Lint Dockerfile**:
```bash
docker run --rm -i hadolint/hadolint < Dockerfile
```

**Scan for vulnerabilities**:
```bash
docker scout cves my-app:latest
# or
trivy image my-app:latest
```

**Analyze layers**:
```bash
dive my-app:latest
```

## Key Optimization Techniques

### 1. Multi-Stage Builds

**Benefits**:
- Separate build and runtime environments
- Reduce final image size by 60-80%
- Include only production dependencies

**Pattern**:
```dockerfile
# Stage 1: Build
FROM python:3.13-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "main.py"]
```

### 2. Layer Caching

**Order matters**: Least to most frequently changing

```dockerfile
# 1. Base image and system packages (rarely change)
FROM python:3.13-slim
RUN apt-get update && apt-get install -y gcc

# 2. Dependencies (change occasionally)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 3. Source code (changes frequently)
COPY . .
CMD ["python", "main.py"]
```

### 3. Minimal Base Images

**Size comparison**:
- `python:3.13` = ~1GB
- `python:3.13-slim` = ~150MB ✅ **Recommended**
- `python:3.13-alpine` = ~50MB (compatibility issues)
- `distroless/python3` = ~50MB (no shell, very secure)

### 4. Security Hardening

**Non-root user** (required):
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --chown=appuser:appuser . .
USER appuser
```

**Pin versions**:
```dockerfile
FROM python:3.13.1-slim  # Specific version
RUN pip install fastapi==0.95.2  # Pin dependencies
```

**No secrets in image**:
```dockerfile
# ❌ WRONG
ENV API_KEY=sk-abc123

# ✅ CORRECT: Pass at runtime
# docker run --env-file .env my-app
```

### 5. BuildKit Features

Enable BuildKit:
```bash
export DOCKER_BUILDKIT=1
```

**Cache mounts** (persistent pip cache):
```dockerfile
# syntax=docker/dockerfile:1.4

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

**Secret mounts** (build-time secrets):
```dockerfile
RUN --mount=type=secret,id=github_token \
    TOKEN=$(cat /run/secrets/github_token) && \
    git clone https://$TOKEN@github.com/private/repo.git
```

## Common Patterns

### Pattern 1: FastAPI with Database Migrations

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint handles migrations
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**entrypoint.sh**:
```bash
#!/bin/sh
alembic upgrade head
exec "$@"
```

### Pattern 2: Next.js with Standalone Output

Requires `next.config.js`:
```javascript
module.exports = {
  output: 'standalone'
}
```

Then use the Dockerfile.nextjs template.

### Pattern 3: Development vs Production

```dockerfile
FROM python:3.13-slim as development
WORKDIR /app
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--reload"]

FROM python:3.13-slim as production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app"]
```

**Build specific target**:
```bash
docker build --target development -t my-app:dev .
docker build --target production -t my-app:prod .
```

## Health Checks

```dockerfile
# HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Python health check (if curl not available)
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

## .dockerignore File

Create `.dockerignore` to exclude unnecessary files:

```
.git
.gitignore
.env
.venv
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
node_modules/
.DS_Store
README.md
*.md
tests/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info
```

## Production Checklist

Before deploying:

- [ ] Multi-stage build implemented
- [ ] All versions pinned (base image, dependencies)
- [ ] Minimal base image used (`-slim` variant)
- [ ] Running as non-root user
- [ ] `.dockerignore` file created
- [ ] No secrets in image
- [ ] Health check added
- [ ] Labels and metadata added
- [ ] Dockerfile linted with hadolint
- [ ] Vulnerabilities scanned
- [ ] Image size optimized (<200MB for Python, <180MB for Node.js)
- [ ] Build time optimized with layer caching

## Common Mistakes

### Mistake 1: Installing Dev Dependencies

```dockerfile
# ❌ WRONG
RUN pip install -r requirements.txt

# ✅ CORRECT
RUN pip install --no-cache-dir -r requirements.txt --no-dev
```

### Mistake 2: Using Latest Tag

```dockerfile
# ❌ WRONG
FROM python:latest

# ✅ CORRECT
FROM python:3.13.1-slim
```

### Mistake 3: Copying Everything First

```dockerfile
# ❌ WRONG: Breaks cache on any file change
COPY . .
RUN pip install -r requirements.txt

# ✅ CORRECT: Cache dependencies separately
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### Mistake 4: Running as Root

```dockerfile
# ❌ WRONG: Security vulnerability
# (no USER directive)

# ✅ CORRECT
RUN useradd -r appuser
USER appuser
```

## Expected Results

### Image Size Targets

| Application | Before Optimization | After Optimization | Reduction |
|-------------|---------------------|-------------------|-----------|
| Python FastAPI | ~1.2GB | ~150MB | 87% |
| Next.js | ~1.5GB | ~180MB | 88% |
| Go API | ~800MB | ~20MB | 97% |

### Build Time Targets

| Build Type | First Build | Rebuild (no changes) | Rebuild (code change) |
|------------|-------------|----------------------|----------------------|
| Without caching | 120s | 120s | 120s |
| With layer caching | 120s | 5s | 30s |
| With BuildKit mounts | 100s | 5s | 25s |

## Troubleshooting

**Issue**: Image size too large
**Solution**: Use multi-stage build, switch to `-slim` base image, add `.dockerignore`

**Issue**: Slow rebuilds
**Solution**: Order Dockerfile from least to most frequently changing, use BuildKit cache mounts

**Issue**: Permission errors
**Solution**: Use `--chown` flag in COPY, ensure files are owned by non-root user

**Issue**: Build fails on Alpine
**Solution**: Switch to `-slim` base image, Alpine has compatibility issues with some packages

## Reference Files

- **Best Practices Guide**: `references/dockerfile-best-practices.md` - Complete optimization guide
- **FastAPI Template**: `assets/examples/Dockerfile.fastapi` - Production-ready FastAPI Dockerfile
- **Next.js Template**: `assets/examples/Dockerfile.nextjs` - Production-ready Next.js Dockerfile

## Tools

- **hadolint**: Dockerfile linter
- **dive**: Interactive layer analysis
- **docker scout**: Vulnerability scanning
- **trivy**: Container security scanner
- **BuildKit**: Advanced build features

## Best Practices Summary

1. **Size**: Use multi-stage builds + `-slim` base images
2. **Security**: Non-root user + pin versions + scan vulnerabilities
3. **Speed**: Layer caching + BuildKit cache mounts
4. **Reliability**: Health checks + specific tags + .dockerignore
5. **Maintainability**: Comments + labels + documentation
