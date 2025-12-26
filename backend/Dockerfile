# Stage 1: Builder - Install dependencies using uv package manager
FROM python:3.13-slim AS builder

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies in virtual environment using uv
RUN uv venv /app/.venv && \
    uv pip install --no-cache -r requirements.txt

# Stage 2: Runtime - Copy only runtime dependencies and source code
FROM python:3.13-slim AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./agent_runner /app/agent_runner
COPY --chown=appuser:appuser ./app_mcp /app/app_mcp
COPY --chown=appuser:appuser ./alembic /app/alembic
COPY --chown=appuser:appuser ./alembic.ini /app/alembic.ini

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
