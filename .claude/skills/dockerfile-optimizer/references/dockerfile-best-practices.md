# Dockerfile Optimization - Best Practices Guide

## Overview

This guide provides production-ready patterns for creating optimized, secure, and maintainable Docker images.

## Core Principles

1. **Minimize Image Size**: Smaller images = faster builds, faster deployments, less attack surface
2. **Maximize Layer Caching**: Order instructions from least to most frequently changing
3. **Security First**: Use minimal base images, scan for vulnerabilities, don't run as root
4. **Build Efficiency**: Use multi-stage builds, leverage BuildKit features
5. **Reproducibility**: Pin versions, use explicit tags, document dependencies

## Multi-Stage Build Pattern

### Python FastAPI Example

```dockerfile
# syntax=docker/dockerfile:1.4

#############################################
# Stage 1: Builder - Install dependencies
#############################################
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

#############################################
# Stage 2: Runtime - Minimal production image
#############################################
FROM python:3.13-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Make sure scripts are executable
RUN chmod +x /app/entrypoint.sh

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Size Reduction**: ~400MB → ~150MB with multi-stage build

### Next.js Frontend Example

```dockerfile
# syntax=docker/dockerfile:1.4

#############################################
# Stage 1: Dependencies
#############################################
FROM node:20-alpine AS deps

# Install dependencies only when needed
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on lockfile
COPY package.json package-lock.json* ./
RUN npm ci --only=production --ignore-scripts

#############################################
# Stage 2: Builder
#############################################
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build Next.js application
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

#############################################
# Stage 3: Runner - Production image
#############################################
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set permissions
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**Size Reduction**: ~1.2GB → ~180MB with multi-stage build

## Layer Caching Optimization

### Bad Example (Cache Busting)

```dockerfile
# ❌ WRONG: Copies everything first, breaks cache on any file change
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### Good Example (Optimal Caching)

```dockerfile
# ✅ CORRECT: Dependencies cached separately from source code
FROM python:3.13-slim
WORKDIR /app

# Install dependencies first (changes rarely)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code last (changes frequently)
COPY . .

CMD ["python", "main.py"]
```

**Build Time**: First build same, rebuilds 10x faster with caching

## Base Image Selection

### Comparison

| Base Image | Size | Use Case | Security |
|------------|------|----------|----------|
| `python:3.13` | ~1GB | Development | Many packages, more attack surface |
| `python:3.13-slim` | ~150MB | Production | Minimal, fewer vulnerabilities |
| `python:3.13-alpine` | ~50MB | Ultra-minimal | Very small, but compatibility issues |
| `distroless/python3` | ~50MB | Maximum security | No shell, minimal attack surface |

**Recommendation**: Use `-slim` for production (balance of size and compatibility)

## Security Best Practices

### 1. Don't Run as Root

```dockerfile
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser
```

### 2. Use Specific Versions

```dockerfile
# ❌ WRONG: Latest tag (unpredictable)
FROM python:latest

# ✅ CORRECT: Specific version
FROM python:3.13.1-slim
```

### 3. Scan for Vulnerabilities

```bash
# Use Docker Scout or Trivy
docker scout cves my-image:latest
trivy image my-image:latest
```

### 4. Use .dockerignore

```
# .dockerignore
.git
.gitignore
.env
.venv
__pycache__
*.pyc
node_modules
.DS_Store
README.md
*.md
tests/
.pytest_cache
```

### 5. Don't Store Secrets in Images

```dockerfile
# ❌ WRONG: Secrets in image
ENV API_KEY=sk-abc123...

# ✅ CORRECT: Secrets at runtime
# Pass via docker run --env-file or K8s secrets
```

## BuildKit Features

Enable BuildKit for advanced features:

```bash
export DOCKER_BUILDKIT=1
docker build -t my-app .
```

### 1. Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

# Cache pip packages across builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .
```

### 2. Secret Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

# Use secret at build time without storing it
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) && \
    git clone https://$GITHUB_TOKEN@github.com/private/repo.git

# Build with:
# docker build --secret id=github_token,src=./token.txt -t my-app .
```

### 3. SSH Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

# Use SSH keys at build time without storing them
RUN --mount=type=ssh \
    git clone git@github.com:private/repo.git

# Build with:
# docker build --ssh default -t my-app .
```

## Common Patterns

### Pattern 1: Python FastAPI with uv

```dockerfile
FROM python:3.13-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Install dependencies with uv (faster than pip)
COPY pyproject.toml .
RUN uv pip install --system -e .

# Copy source code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Pattern 2: Next.js with Standalone Output

```dockerfile
# In next.config.js:
# output: 'standalone'

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

CMD ["node", "server.js"]
```

### Pattern 3: Database Migrations

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint script handles migrations
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**entrypoint.sh**:
```bash
#!/bin/sh
set -e

# Run database migrations
alembic upgrade head

# Start application
exec "$@"
```

### Pattern 4: Monorepo (Multiple Services)

```dockerfile
# syntax=docker/dockerfile:1.4

ARG SERVICE_NAME

FROM python:3.13-slim AS base
WORKDIR /app

# Install shared dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the service we're building
COPY services/${SERVICE_NAME} ./service

CMD ["python", "service/main.py"]

# Build specific services:
# docker build --build-arg SERVICE_NAME=api -t api-service .
# docker build --build-arg SERVICE_NAME=worker -t worker-service .
```

## Image Size Optimization

### Techniques

1. **Multi-stage builds**: Separate build and runtime environments
2. **Minimal base images**: Use `-slim` or `-alpine` variants
3. **Clean up in same layer**: Remove temp files in same RUN command
4. **Use .dockerignore**: Exclude unnecessary files from context
5. **Compress layers**: Combine related RUN commands with &&

### Example: Cleaning Up in Same Layer

```dockerfile
# ❌ WRONG: Creates two layers, cache stays in image
RUN apt-get update && apt-get install -y build-essential
RUN rm -rf /var/lib/apt/lists/*

# ✅ CORRECT: Cleanup in same layer
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*
```

## Environment Variables

### Build-time vs Runtime

```dockerfile
# Build-time arguments (not in final image)
ARG BUILD_VERSION=1.0.0

# Runtime environment variables (in final image)
ENV APP_VERSION=${BUILD_VERSION}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Pass at build time:
# docker build --build-arg BUILD_VERSION=2.0.0 -t my-app .
```

## Health Checks

```dockerfile
# Simple HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# For services without curl
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

## Labels and Metadata

```dockerfile
LABEL maintainer="team@example.com"
LABEL version="1.0.0"
LABEL description="FastAPI Todo App"
LABEL org.opencontainers.image.source="https://github.com/org/repo"
LABEL org.opencontainers.image.licenses="MIT"
```

## Testing Dockerfiles

### Dockerfile Linter

```bash
# Install hadolint
brew install hadolint  # macOS
# or
docker run --rm -i hadolint/hadolint < Dockerfile

# Common issues it catches:
# - Pin versions
# - Use WORKDIR instead of cd
# - Use COPY instead of ADD
# - Avoid apt-get upgrade
```

### Image Analysis

```bash
# Analyze layers
docker history my-app:latest

# Show layer sizes
docker image inspect my-app:latest

# Use dive for interactive layer analysis
dive my-app:latest
```

## Production Checklist

- [ ] Use multi-stage builds
- [ ] Pin all versions (base image, dependencies)
- [ ] Use minimal base image (`-slim` or `distroless`)
- [ ] Run as non-root user
- [ ] Add .dockerignore file
- [ ] No secrets in image
- [ ] Add health checks
- [ ] Add labels and metadata
- [ ] Test with hadolint
- [ ] Scan for vulnerabilities
- [ ] Document build process
- [ ] Optimize layer caching

## Common Mistakes

### Mistake 1: Running apt-get upgrade

```dockerfile
# ❌ WRONG: Makes builds unpredictable
RUN apt-get update && apt-get upgrade -y

# ✅ CORRECT: Update base image instead
FROM python:3.13-slim  # Already updated
```

### Mistake 2: Using ADD instead of COPY

```dockerfile
# ❌ WRONG: ADD has hidden features (auto-extract, URL download)
ADD package.json .

# ✅ CORRECT: COPY is explicit
COPY package.json .
```

### Mistake 3: Installing dev dependencies in production

```dockerfile
# ❌ WRONG: Installs dev dependencies
RUN pip install -r requirements.txt

# ✅ CORRECT: Only production dependencies
RUN pip install --no-cache-dir -r requirements.txt --no-dev
```

## Performance Benchmarks

### Image Size Comparison (Python FastAPI App)

| Build Strategy | Image Size | Build Time | Security Score |
|----------------|------------|------------|----------------|
| Single-stage (python:3.13) | 1.2GB | 2min | Low |
| Multi-stage (python:3.13-slim) | 180MB | 2.5min | Medium |
| Multi-stage + Alpine | 80MB | 3min | High |
| Distroless | 75MB | 2.5min | Very High |

**Recommendation**: Multi-stage with `-slim` (best balance)

### Build Time Optimization

| Technique | First Build | Rebuild (no changes) | Rebuild (code change) |
|-----------|-------------|----------------------|----------------------|
| No optimization | 120s | 120s | 120s |
| Layer caching | 120s | 5s | 30s |
| BuildKit cache mounts | 100s | 5s | 25s |

## Advanced Patterns

### Pattern: Development vs Production

```dockerfile
# Development
FROM python:3.13-slim as development
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]

# Production
FROM python:3.13-slim as production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

# Build for development:
# docker build --target development -t my-app:dev .
# Build for production:
# docker build --target production -t my-app:prod .
```

### Pattern: Dynamic Versioning

```dockerfile
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown

LABEL git.commit=${GIT_COMMIT}
LABEL build.date=${BUILD_DATE}

# Build with:
# docker build \
#   --build-arg GIT_COMMIT=$(git rev-parse HEAD) \
#   --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
#   -t my-app:latest .
```

## Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [hadolint Linter](https://github.com/hadolint/hadolint)
- [dive Tool](https://github.com/wagoodman/dive)
- [Docker Scout](https://docs.docker.com/scout/)
