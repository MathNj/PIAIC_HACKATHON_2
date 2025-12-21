# Dockerfile Optimization Strategies

Production-ready patterns for building efficient, secure, and performant Docker images.

## Table of Contents
- Multi-Stage Builds
- Layer Caching Optimization
- Image Size Reduction
- Security Hardening
- Build Performance
- Production Best Practices

## Multi-Stage Builds

### Basic Pattern

Reduce final image size by separating build and runtime dependencies:

```dockerfile
# Build stage
FROM python:3.13 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

**Benefits:**
- Build tools not included in final image
- Smaller final image (200MB → 50MB typical reduction)
- Faster deployments

### Advanced: Multiple Build Stages

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Test
FROM builder AS test
RUN npm test

# Stage 4: Production
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## Layer Caching Optimization

### Order Dependencies Before Code

**❌ Bad - Cache invalidated on every code change:**
```dockerfile
FROM python:3.13
WORKDIR /app
COPY . .  # Code changes invalidate everything below
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

**✅ Good - Dependencies cached separately:**
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .  # Only changes when deps change
RUN pip install -r requirements.txt
COPY . .  # Code changes don't affect pip install layer
CMD ["python", "app.py"]
```

### Combine RUN Commands Strategically

**❌ Bad - Many layers:**
```dockerfile
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y python3-dev
RUN apt-get clean
```

**✅ Good - Single layer:**
```dockerfile
RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*
```

### Use .dockerignore

```
# .dockerignore
.git
.gitignore
README.md
tests/
*.pyc
__pycache__
node_modules
.env
.vscode
*.log
```

**Impact:** Reduces context size, speeds up builds

## Image Size Reduction

### Choose Minimal Base Images

```dockerfile
# ❌ Large (900MB)
FROM python:3.13

# ✅ Better (150MB)
FROM python:3.13-slim

# ✅ Smallest (50MB) - but may lack system libs
FROM python:3.13-alpine
```

### Remove Build Dependencies After Use

```dockerfile
FROM python:3.13-slim

# Install, build, and cleanup in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install -r requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

### Use --no-cache-dir for pip

```dockerfile
# Saves ~20-50MB
RUN pip install --no-cache-dir -r requirements.txt
```

### Minimize Installed Packages

```dockerfile
# Install only what's needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \  # PostgreSQL client library
    && rm -rf /var/lib/apt/lists/*
```

## Security Hardening

### Run as Non-Root User

```dockerfile
# Create user
RUN useradd -m -u 1000 appuser

# Set ownership
COPY --chown=appuser:appuser . /app

# Switch user
USER appuser

# All subsequent commands run as appuser
CMD ["python", "app.py"]
```

### Scan for Vulnerabilities

```bash
# Use Docker Scout or Trivy
docker scout cves myimage:latest
trivy image myimage:latest
```

### Use Specific Image Tags

```dockerfile
# ❌ Bad - unpredictable, could break
FROM python:latest

# ✅ Good - reproducible builds
FROM python:3.13.0-slim
```

### Minimize Attack Surface

```dockerfile
# Remove package manager in final stage
FROM python:3.13-slim AS final
# ... build steps ...

# Optional: Remove pip if not needed at runtime
RUN pip uninstall -y pip setuptools
```

### Set Read-Only Filesystem

```dockerfile
# In docker run
docker run --read-only --tmpfs /tmp myimage

# Or in Kubernetes
securityContext:
  readOnlyRootFilesystem: true
```

## Build Performance

### BuildKit Features

Enable BuildKit for faster builds:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Or in dockerfile syntax
# syntax=docker/dockerfile:1.4
```

### Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1.4
FROM python:3.13

# Mount pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

### Parallel Builds

```dockerfile
# Build stages in parallel
FROM base AS stage1
RUN heavy-operation-1

FROM base AS stage2
RUN heavy-operation-2

FROM base AS final
COPY --from=stage1 /output1 .
COPY --from=stage2 /output2 .
```

### Reduce Context Size

```bash
# Check context size
docker build --no-cache -f Dockerfile . 2>&1 | grep "Sending build context"

# Use .dockerignore to exclude files
# Or build from subdirectory
docker build -f Dockerfile ./app
```

## Production Best Practices

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Metadata Labels

```dockerfile
LABEL org.opencontainers.image.title="My App"
LABEL org.opencontainers.image.description="FastAPI application"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="team@example.com"
```

### Signal Handling

```dockerfile
# Use exec form to properly handle signals
CMD ["python", "app.py"]  # ✅ Receives SIGTERM

# NOT shell form (creates shell wrapper)
CMD python app.py  # ❌ Shell receives SIGTERM, not Python
```

### Environment Variables

```dockerfile
# Set sensible defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Allow runtime override
docker run -e PYTHONUNBUFFERED=0 myimage
```

### Logging Configuration

```dockerfile
# Log to stdout/stderr for container logs
ENV PYTHONUNBUFFERED=1

# Application should log to stdout
CMD ["uvicorn", "app:app", "--log-config", "/app/logging.conf"]
```

## Complete Example: Optimized FastAPI Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.4

# ============================================================================
# Build Stage
# ============================================================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc

# Install Python dependencies with cache mount
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-warn-script-location -r requirements.txt

# ============================================================================
# Runtime Stage
# ============================================================================
FROM python:3.13-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application
COPY --chown=appuser:appuser . .

# Environment
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Metadata
LABEL org.opencontainers.image.title="FastAPI App"
LABEL org.opencontainers.image.version="1.0.0"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Results:**
- ✅ Image size: ~150MB (vs 900MB unoptimized)
- ✅ Build time: ~30s (vs 2m unoptimized)
- ✅ Security: Non-root user, minimal packages
- ✅ Production-ready: Health checks, proper signal handling
- ✅ Fast rebuilds: Layer caching optimized

## Measuring Improvements

### Image Size

```bash
# Before optimization
docker images myapp:before
# REPOSITORY   TAG      SIZE
# myapp        before   900MB

# After optimization
docker images myapp:after
# REPOSITORY   TAG      SIZE
# myapp        after    150MB

# Reduction: 83%
```

### Build Time

```bash
# Clear cache
docker builder prune -af

# Time build
time docker build -t myapp .

# With cache
time docker build -t myapp .
```

### Layers Analysis

```bash
# Analyze layers
docker history myapp:latest

# Use dive for interactive analysis
dive myapp:latest
```

## Quick Checklist

- [ ] Use multi-stage builds
- [ ] Copy dependencies before code
- [ ] Use slim/alpine base images
- [ ] Run as non-root user
- [ ] Add health checks
- [ ] Use .dockerignore
- [ ] Combine RUN commands where appropriate
- [ ] Use specific image tags (not latest)
- [ ] Remove package manager caches
- [ ] Enable BuildKit
- [ ] Use exec form for CMD/ENTRYPOINT
- [ ] Set appropriate LABELS
- [ ] Scan for vulnerabilities
