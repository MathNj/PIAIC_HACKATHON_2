# Docker AI (Gordon) Command Reference

Comprehensive guide to using Docker AI (Gordon) for intelligent containerization.

## Table of Contents
- Getting Started with Gordon
- Common Prompts and Use Cases
- Output Parsing Patterns
- Best Practices
- Troubleshooting

## Getting Started with Gordon

### Installation

Docker AI (Gordon) is included with Docker Desktop. Ensure you have:
- Docker Desktop 4.26+ installed
- Docker AI feature enabled in settings

### Basic Usage

```bash
# Basic prompt
docker ai "how do I optimize this dockerfile?"

# With file context
docker ai "analyze this dockerfile" --file Dockerfile

# With container context
docker ai "why did this container crash?" --container abc123

# Help
docker ai --help
```

### Checking Availability

```bash
# Check if Gordon is available
docker ai --version

# Test Gordon
docker ai "hello"
```

## Common Prompts and Use Cases

### Dockerfile Optimization

**Reduce Image Size:**
```bash
docker ai "how can I reduce the size of this Docker image?" --file Dockerfile
docker ai "optimize this dockerfile for minimal image size"
docker ai "suggest multi-stage build for this dockerfile"
```

**Performance Improvements:**
```bash
docker ai "how can I make this dockerfile build faster?"
docker ai "optimize docker layer caching for this dockerfile"
docker ai "suggest build optimizations"
```

**Security Hardening:**
```bash
docker ai "identify security issues in this dockerfile"
docker ai "how can I make this image more secure?"
docker ai "suggest security best practices for this dockerfile"
```

### Container Debugging

**Crash Analysis:**
```bash
docker ai "why did my container crash?" --container abc123
docker ai "analyze container exit code" --container abc123
docker ai "debug container startup failure"
```

**Log Analysis:**
```bash
docker ai "analyze these container logs" --container abc123
docker ai "what does this error mean?" --container abc123
docker ai "troubleshoot application errors in container"
```

**Resource Issues:**
```bash
docker ai "why is my container using so much memory?"
docker ai "diagnose high CPU usage in container"
docker ai "container is running out of disk space, why?"
```

### Dockerfile Generation

**From Scratch:**
```bash
docker ai "generate a dockerfile for a fastapi application"
docker ai "create a dockerfile for nextjs with typescript"
docker ai "build a dockerfile for python cli tool"
```

**Language-Specific:**
```bash
docker ai "dockerfile for python 3.13 web app"
docker ai "dockerfile for node 20 application"
docker ai "dockerfile for go microservice"
```

**With Dependencies:**
```bash
docker ai "dockerfile for app with postgresql and redis dependencies"
docker ai "multi-container setup with docker compose"
```

### Image Analysis

**Vulnerability Scanning:**
```bash
docker ai "scan this image for vulnerabilities"
docker ai "identify security issues in image"
docker ai "check for outdated packages"
```

**Layer Analysis:**
```bash
docker ai "analyze docker image layers"
docker ai "which layers are taking up the most space?"
docker ai "optimize image layers"
```

### Networking and Connectivity

**Connection Issues:**
```bash
docker ai "container can't connect to database, why?"
docker ai "troubleshoot networking between containers"
docker ai "debug port binding issues"
```

**Network Configuration:**
```bash
docker ai "how do I configure custom network for containers?"
docker ai "setup service discovery between containers"
```

### Docker Compose

**Configuration:**
```bash
docker ai "generate docker-compose.yml for this project"
docker ai "optimize docker compose configuration"
docker ai "add healthchecks to docker compose"
```

**Troubleshooting:**
```bash
docker ai "why isn't docker compose starting services?"
docker ai "debug docker compose networking"
```

## Output Parsing Patterns

Gordon typically structures responses in these formats:

### Code Blocks

Dockerfile suggestions are provided in code blocks:

```
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```
```

### Numbered Recommendations

```
1. Use multi-stage builds to reduce final image size
2. Leverage build cache by copying requirements.txt before source code
3. Use .dockerignore to exclude unnecessary files
```

### Bullet Points

```
- Consider using alpine base image for smaller size
- Add healthcheck for production deployments
- Run as non-root user for security
```

### Action Phrases

```
You should use multi-stage builds to reduce the image size from 500MB to 150MB.
Consider adding a .dockerignore file to exclude node_modules.
Try using --no-cache-dir flag when installing pip packages.
```

## Best Practices

### Effective Prompts

**Be Specific:**
```bash
# ❌ Too vague
docker ai "fix my dockerfile"

# ✅ Specific
docker ai "optimize this dockerfile to reduce build time by caching pip dependencies"
```

**Provide Context:**
```bash
# ❌ No context
docker ai "why isn't this working?"

# ✅ With context
docker ai "fastapi container returns 502 error, logs show 'connection refused to port 5432'"
```

**Ask for Alternatives:**
```bash
docker ai "what are alternative approaches to reduce image size besides multi-stage builds?"
docker ai "compare alpine vs slim base images for python"
```

### Iterative Refinement

```bash
# Start broad
docker ai "optimize this dockerfile"

# Get specific suggestion, then refine
docker ai "how much size reduction from using alpine vs slim?"

# Apply and verify
docker ai "validate this optimized dockerfile"
```

### Combining with Standard Docker Commands

```bash
# Use Gordon for analysis
docker ai "analyze this dockerfile" --file Dockerfile > analysis.txt

# Apply manually
nano Dockerfile

# Build and test
docker build -t myapp .

# Ask Gordon to debug if issues
docker ai "build failed with error: ..."
```

## Troubleshooting

### Gordon Not Available

**Check Installation:**
```bash
docker --version  # Should be 4.26+
docker ai --version
```

**Enable Feature:**
- Open Docker Desktop Settings
- Navigate to Features
- Enable "Docker AI (Beta)"
- Restart Docker Desktop

**Fallback Strategy:**
```python
# Use gordon_wrapper.py from scripts/
python scripts/gordon_wrapper.py "optimize dockerfile"
# Automatically falls back to standard suggestions if Gordon unavailable
```

### Gordon Times Out

```bash
# Break complex prompts into smaller ones
# Instead of:
docker ai "optimize dockerfile, add security, reduce size, improve caching"

# Do:
docker ai "optimize dockerfile for size"
docker ai "add security best practices to dockerfile"
docker ai "improve build caching in dockerfile"
```

### Gordon Provides Generic Advice

**Add More Context:**
```bash
# Include file content
docker ai "optimize this dockerfile" --file Dockerfile

# Specify technology stack
docker ai "optimize dockerfile for python fastapi application with postgresql"

# Mention constraints
docker ai "optimize dockerfile but must keep size under 200MB"
```

### Suggestions Don't Apply

**Validate Before Applying:**
```bash
# Get suggestion from Gordon
docker ai "optimize dockerfile" --file Dockerfile > suggested.Dockerfile

# Review diff
diff Dockerfile suggested.Dockerfile

# Test build
docker build -t test -f suggested.Dockerfile .

# Apply if successful
mv suggested.Dockerfile Dockerfile
```

## Integration Patterns

### With CI/CD

```yaml
# GitHub Actions example
- name: Optimize Dockerfile with Gordon
  run: |
    docker ai "optimize this dockerfile for production" --file Dockerfile > optimized.Dockerfile
    if [ $? -eq 0 ]; then
      mv optimized.Dockerfile Dockerfile
      git add Dockerfile
      git commit -m "chore: apply Gordon optimizations"
    fi
```

### With Pre-Commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -q "Dockerfile"; then
    echo "Running Gordon analysis on Dockerfile..."
    docker ai "check for security issues in this dockerfile" --file Dockerfile
fi
```

### With Monitoring

```bash
# Automated container health checks
docker ai "analyze recent container crashes" --container $(docker ps -aq --filter status=exited | head -1)
```

## Advanced Usage

### JSON Output (if supported)

```bash
docker ai "analyze dockerfile" --file Dockerfile --format json > analysis.json
```

### Batch Processing

```bash
# Analyze multiple Dockerfiles
for dockerfile in $(find . -name "Dockerfile*"); do
    echo "Analyzing $dockerfile..."
    docker ai "optimize this dockerfile" --file "$dockerfile"
done
```

### Custom Scripts

```python
# Use gordon_wrapper.py for programmatic access
from scripts.gordon_wrapper import GordonWrapper

wrapper = GordonWrapper()
response = wrapper.execute_prompt(
    "optimize dockerfile",
    dockerfile_path="Dockerfile"
)

if response["success"]:
    for suggestion in response["suggestions"]:
        print(f"- {suggestion['content']}")
```

## Quick Reference

```bash
# Optimization
docker ai "reduce image size" --file Dockerfile

# Security
docker ai "security scan" --file Dockerfile

# Debugging
docker ai "container crashed" --container ID

# Generation
docker ai "create dockerfile for <stack>"

# Analysis
docker ai "explain this dockerfile" --file Dockerfile

# Validation
docker ai "check dockerfile best practices" --file Dockerfile
```
