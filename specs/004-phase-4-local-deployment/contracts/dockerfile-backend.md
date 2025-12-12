# Contract: Backend Dockerfile

**Service**: Backend (FastAPI)
**Base Image**: python:3.13-slim
**Target Size**: <200MB (excluding base layers)
**Build Strategy**: Multi-stage (builder + runtime)

## Dockerfile Specification

### Stage 1: Builder
**Purpose**: Install dependencies using uv package manager

```dockerfile
FROM python:3.13-slim AS builder

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies in virtual environment using uv
RUN uv venv /app/.venv && \
    /app/.venv/bin/uv pip install --no-cache -r requirements.txt
```

### Stage 2: Runtime
**Purpose**: Copy only runtime dependencies and source code

```dockerfile
FROM python:3.13-slim AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY --chown=appuser:appuser ./src /app/src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import requests; requests.get('http://localhost:8000/health/live')"]

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## .dockerignore Specification

```
.git
.env
.env.*
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info/
tests/
docs/
.vscode/
.idea/
*.md
.gitignore
Dockerfile
.dockerignore
```

## Build Commands

### Local Development (Minikube)
```bash
# Connect to Minikube Docker daemon
eval $(minikube docker-env)

# Build image
docker build -t todo-backend:local -f Dockerfile .

# Verify image
docker images | grep todo-backend
docker inspect todo-backend:local | grep Size
```

### Production Build
```bash
docker build -t todo-backend:v1.0.0 -f Dockerfile .
docker tag todo-backend:v1.0.0 registry.example.com/todo-backend:v1.0.0
docker push registry.example.com/todo-backend:v1.0.0
```

## Environment Variables (Runtime)

**Injected via Kubernetes Secret**:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI agent
- `BETTER_AUTH_SECRET`: JWT secret for authentication

**Defaults**:
- `PORT`: 8000
- `LOG_LEVEL`: info
- `WORKERS`: 1 (Kubernetes handles scaling via replicas)

## Health Check Endpoints

**Readiness**: `GET /health/ready`
- Returns 200 if database connected
- Returns 503 if database unavailable

**Liveness**: `GET /health/live`
- Returns 200 if process running
- Returns 500 if process crashed

## Optimization Techniques

1. **Multi-stage build**: Separates build-time from runtime dependencies
2. **uv package manager**: 10-100x faster than pip for dependency installation
3. **Virtual environment**: Isolated dependency tree
4. **Layer caching**: Dependencies installed before source code copy
5. **.dockerignore**: Excludes unnecessary files from build context
6. **Non-root user**: Security best practice (UID 1000)
7. **Slim base image**: python:3.13-slim reduces size by ~500MB vs full image

## Expected Results

- **Build time** (cold): 2-3 minutes
- **Build time** (cached): <1 minute (dependencies cached)
- **Final image size**: ~150MB (excluding python:3.13-slim base ~120MB)
- **Layer count**: ~8-10 layers
- **Security scan**: No critical vulnerabilities (slim base regularly updated)
