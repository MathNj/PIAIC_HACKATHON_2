# Production-Optimized Python CLI Dockerfile
# Minimal image for CLI tools and scripts

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies to user location
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal CLI image
# ============================================================================
FROM python:3.13-slim

# Create non-root user
RUN useradd -m -u 1000 cliuser

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/cliuser/.local

# Copy application code
COPY --chown=cliuser:cliuser . .

# Update PATH
ENV PATH=/home/cliuser/.local/bin:$PATH

# Switch to non-root user
USER cliuser

# Set entry point to your CLI script
ENTRYPOINT ["python", "cli.py"]

# Default command (can be overridden)
CMD ["--help"]

# ============================================================================
# Build & Run Instructions
# ============================================================================
# Build:
#   docker build -t python-cli -f python-cli.Dockerfile .
#
# Run:
#   docker run python-cli <command> <args>
#
# Examples:
#   docker run python-cli --help
#   docker run python-cli process --input data.csv
#   docker run python-cli export --format json
#
# With volume mount (for file I/O):
#   docker run -v $(pwd)/data:/app/data python-cli process --input /app/data/input.csv
