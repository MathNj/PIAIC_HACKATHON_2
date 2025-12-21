---
name: blueprint-architect
description: Extract and productize reusable cloud-native architectural patterns as blueprints. Use when: (1) Creating reusable architecture templates from existing projects, (2) Generating Cloud-Native Blueprints with FastAPI + Next.js + Dapr + Kafka stack, (3) Packaging Helm charts and K8s manifests for reuse, (4) Documenting architectural patterns with deployment guides, (5) Extracting Spec-Kit templates from codebase, (6) Productizing project architecture for other teams, or (7) Claiming bonus points for cloud-native blueprints. Analyzes project structure and generates complete blueprint packages with infrastructure, specs, and documentation.
---

# Blueprint Architect

Extract reusable cloud-native architectural patterns from existing projects and package them as deployable blueprints.

## Overview

This skill analyzes your project structure (FastAPI + Next.js + Dapr + Kafka) and generates Cloud-Native Blueprints - reusable architectural patterns that can be deployed to other projects or shared with teams.

**Key Features:**
- Project structure analysis
- Helm chart and K8s manifest packaging
- Spec-Kit template generation
- BLUEPRINT.md documentation with deployment guides
- Metadata extraction for components
- Event-driven architecture patterns
- Production-ready configurations

**Bonus Points:** Generates cloud-native blueprints for architectural productization.

## Quick Start

### Generate Blueprint from Todo App

```bash
# From project root
python scripts/generate_blueprint.py \
  --project-root . \
  --name "fastapi-nextjs-dapr-stack" \
  --description "Full-stack microservices with event-driven architecture" \
  --use-cases \
    "Task management applications" \
    "CRM systems" \
    "Project management tools"

# Output: blueprints/fastapi-nextjs-dapr-stack/
```

### What Gets Generated

```
blueprints/fastapi-nextjs-dapr-stack/
├── infrastructure/
│   ├── helm/                    # Copied Helm charts
│   ├── kubernetes/              # Copied K8s manifests
│   └── dapr/                    # Copied Dapr components
├── specs/
│   └── feature-template.md      # Spec-Kit template
├── BLUEPRINT.md                 # Complete deployment guide
└── blueprint.json               # Metadata
```

## Core Workflows

### Workflow 1: Analyze Project Structure

Analyze existing project to identify components:

```python
from scripts.generate_blueprint import BlueprintGenerator

generator = BlueprintGenerator(project_root=".")
structure = generator.analyze_project_structure()

print(f"Backend: {structure['backend']['framework']}")
print(f"Frontend: {structure['frontend']['framework']}")
print(f"Kafka: {structure['event_driven']['kafka']}")
print(f"Dapr: {structure['event_driven']['dapr_pubsub']}")
```

**Output:**
```json
{
  "backend": {
    "exists": true,
    "framework": "FastAPI",
    "language": "Python",
    "features": ["Authentication (JWT)", "SQLModel ORM", "MCP Tools"]
  },
  "frontend": {
    "exists": true,
    "framework": "Next.js",
    "language": "TypeScript",
    "features": ["OpenAI ChatKit", "i18n (English/Urdu)", "Voice Input"]
  },
  "infrastructure": {
    "helm_charts": true,
    "k8s_manifests": true,
    "dapr_components": true
  },
  "event_driven": {
    "kafka": true,
    "dapr_pubsub": true
  }
}
```

### Workflow 2: Generate Complete Blueprint

Extract all components into a reusable blueprint:

```bash
python scripts/generate_blueprint.py \
  --project-root . \
  --output-dir blueprints \
  --name "microservices-stack" \
  --description "Event-driven microservices with Dapr and Kafka" \
  --use-cases \
    "Real-time collaboration apps" \
    "Event-driven workflows" \
    "Multi-tenant SaaS platforms"
```

**Generated Files:**
1. **infrastructure/** - All Helm charts, K8s manifests, Dapr components
2. **specs/feature-template.md** - Spec-Kit template for new features
3. **BLUEPRINT.md** - Complete documentation with:
   - Architecture overview
   - Technology stack
   - Deployment guide (step-by-step)
   - Configuration options
   - Customization guide
   - Troubleshooting
   - Production checklist
4. **blueprint.json** - Metadata for tooling integration

### Workflow 3: Deploy Blueprint to New Project

Deploy generated blueprint to another Kubernetes cluster:

```bash
# Navigate to blueprint
cd blueprints/microservices-stack/

# Step 1: Deploy Kafka
cd infrastructure/kafka
bash deploy_kafka.sh

# Step 2: Apply Dapr components
kubectl apply -f infrastructure/dapr/components/

# Step 3: Install with Helm
helm install my-app infrastructure/helm/todo-stack/ \
  --namespace default \
  --values infrastructure/helm/todo-stack/values-local.yaml

# Step 4: Verify
kubectl get pods
kubectl get svc
dapr components -k
```

### Workflow 4: Customize Blueprint for New Use Case

Adapt blueprint for specific requirements:

1. **Review BLUEPRINT.md** - Understand architecture and components

2. **Update Helm values** - Customize for your environment:
   ```yaml
   # infrastructure/helm/todo-stack/values.yaml
   backend:
     replicas: 3
     image: my-registry/backend:v1.0
     resources:
       requests:
         memory: 2Gi
         cpu: 1000m
   ```

3. **Add new features** using spec template:
   ```bash
   cp specs/feature-template.md specs/my-new-feature.md
   # Fill in feature requirements, API endpoints, schema
   ```

4. **Configure Dapr** for custom event-driven patterns:
   ```yaml
   # infrastructure/dapr/components/custom-pubsub.yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: custom-pubsub
   spec:
     type: pubsub.kafka
     metadata:
       - name: brokers
         value: "my-kafka:9092"
   ```

5. **Deploy customized blueprint**:
   ```bash
   helm upgrade --install my-app infrastructure/helm/todo-stack/ \
     --values my-custom-values.yaml
   ```

## Bundled Resources

### Scripts

**`scripts/generate_blueprint.py`**
- `BlueprintGenerator` class
- Project structure analysis
- Infrastructure copying (Helm, K8s, Dapr)
- Spec template generation
- BLUEPRINT.md generation
- Metadata extraction

### Assets

**`assets/templates/`** (created during generation):
- Feature spec template
- API spec template
- Database schema template

### References

**`references/blueprint-patterns.md`**
- Common architectural patterns
- Blueprint structure reference
- Deployment patterns
- Customization patterns
- Testing, monitoring, scaling patterns
- Security and CI/CD patterns

## Blueprint Components

### 1. Infrastructure Package

**Helm Charts:**
- Complete application deployment
- Backend + Frontend + Ingress
- ConfigMaps and Secrets
- Service definitions
- Production-ready resource limits

**Kubernetes Manifests:**
- Secret templates
- Service configurations
- Namespace definitions

**Dapr Components:**
- Kafka pub/sub configuration
- Redis state store
- Job scheduler (Dapr Jobs API)

### 2. Spec-Kit Templates

**Feature Template:**
- Overview and requirements
- Architecture (Backend, Frontend, Event-Driven)
- Database schema
- API endpoints
- Deployment configuration
- Testing strategy

**Customizable for:**
- New feature specifications
- API endpoint documentation
- Database schema design

### 3. BLUEPRINT.md

**Sections:**
- Architecture Overview
- Technology Stack
- Use Cases
- Directory Structure
- Deployment Guide (step-by-step)
- Configuration (env vars, Helm values)
- Customization Guide
- Event-Driven Patterns
- Scaling Strategies
- Monitoring and Security
- Troubleshooting
- Production Checklist

### 4. Metadata

**blueprint.json:**
```json
{
  "name": "fastapi-nextjs-dapr-stack",
  "version": "1.0.0",
  "generated_at": "2025-12-22T01:30:00",
  "structure": {...},
  "components": {
    "backend": true,
    "frontend": true,
    "kafka": true,
    "dapr": true,
    "helm": true
  }
}
```

## Architectural Patterns

### Pattern 1: Microservices Stack

**Components:**
- FastAPI backend with SQLModel
- Next.js frontend with App Router
- Kafka event bus
- Dapr for service mesh
- Redis for state
- Helm for deployment

**Use Cases:**
- Todo/Task management
- CRM systems
- Project management
- Collaboration platforms

### Pattern 2: Event-Driven Architecture

**Components:**
- Kafka cluster (Strimzi/Redpanda)
- Dapr pub/sub
- Event publishers/subscribers
- Dead letter queues

**Use Cases:**
- Real-time notifications
- Analytics pipelines
- Audit logging
- Workflow automation

### Pattern 3: AI-Powered Applications

**Components:**
- OpenAI Agents SDK
- MCP tools server
- Conversation persistence
- ChatKit frontend

**Use Cases:**
- AI assistants
- Chatbots
- Intelligent automation
- Knowledge management

## Customization

### Adding New Services

1. Update Helm chart with new deployment:
   ```yaml
   # infrastructure/helm/todo-stack/templates/new-service-deployment.yaml
   ```

2. Add service configuration:
   ```yaml
   # infrastructure/helm/todo-stack/templates/new-service-service.yaml
   ```

3. Configure in values.yaml:
   ```yaml
   newService:
     replicas: 2
     image: registry/new-service:latest
   ```

### Adding Event Topics

1. Update Kafka topics:
   ```yaml
   # infrastructure/kafka/topics.yaml
   apiVersion: kafka.strimzi.io/v1beta2
   kind: KafkaTopic
   metadata:
     name: new-topic
   spec:
     partitions: 3
     replicas: 1
   ```

2. Configure Dapr subscription:
   ```python
   @app.post("/dapr/subscribe")
   async def subscribe():
       return [{
           "pubsubname": "kafka-pubsub",
           "topic": "new-topic",
           "route": "/events/new"
       }]
   ```

### Configuring Authentication

1. Set JWT secrets in Helm values
2. Configure Better Auth in backend
3. Add auth provider in frontend
4. Protect routes with middleware

## Production Deployment

### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or DOKS)
- kubectl CLI configured
- Helm 3+ installed
- Dapr installed on cluster
- Domain name and TLS certificates

### Production Checklist

```bash
# 1. Deploy with persistent storage
STORAGE_TYPE=persistent bash infrastructure/kafka/deploy_kafka.sh

# 2. Configure secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=jwt-secret="..." \
  --from-literal=redis-password="..."

# 3. Deploy with production values
helm install app infrastructure/helm/todo-stack/ \
  --namespace production \
  --create-namespace \
  --values infrastructure/helm/todo-stack/values-production.yaml

# 4. Configure ingress with TLS
kubectl apply -f infrastructure/kubernetes/ingress-tls.yaml

# 5. Enable monitoring
kubectl apply -f infrastructure/monitoring/

# 6. Configure autoscaling
kubectl apply -f infrastructure/autoscaling/
```

## Monitoring

### Metrics Collection

**Prometheus:**
- Scrapes metrics from FastAPI
- Kafka JMX metrics
- Dapr metrics
- Custom application metrics

**Grafana:**
- Pre-built dashboards
- Alert configuration
- Visualization

### Logging

**Stack:**
- Fluent Bit (log collection)
- Elasticsearch (storage)
- Kibana (visualization)

## Troubleshooting

### Blueprint Generation Fails

**Symptoms:** Script errors during generation

**Checks:**
```bash
# Verify project structure
ls -la backend/ frontend/ infrastructure/

# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt
```

### Missing Components

**Symptoms:** Generated blueprint missing infrastructure files

**Cause:** Source project missing required directories

**Solution:** Ensure project has:
- `infrastructure/helm/`
- `infrastructure/kubernetes/`
- `infrastructure/dapr/`

### Deployment Issues

See BLUEPRINT.md troubleshooting section in generated blueprint.

## Best Practices

1. **Version Control** - Commit generated blueprints to Git
2. **Documentation** - Keep BLUEPRINT.md updated with customizations
3. **Testing** - Test blueprint deployment before sharing
4. **Secrets** - Never commit secrets in blueprints
5. **Customization** - Document all deviations from base blueprint

## Integration

### With Spec-Kit

Use generated spec templates for new features:

```bash
# Create feature spec from template
cp blueprints/{name}/specs/feature-template.md specs/features/my-feature.md
```

### With CI/CD

Automate blueprint deployment:

```yaml
# .github/workflows/deploy-blueprint.yml
name: Deploy Blueprint
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: |
          cd blueprints/my-blueprint
          helm upgrade --install app infrastructure/helm/todo-stack/
```

## Advanced Features

### Multi-Tenant Support

Configure namespace-based tenant isolation:

```bash
# Deploy for each tenant
for tenant in tenant1 tenant2 tenant3; do
  helm install ${tenant}-app infrastructure/helm/todo-stack/ \
    --namespace ${tenant} \
    --create-namespace \
    --set tenant.name=${tenant}
done
```

### Disaster Recovery

Backup blueprint configurations:

```bash
# Backup Helm releases
helm list --all-namespaces > backups/helm-releases.txt

# Backup K8s resources
kubectl get all -A -o yaml > backups/k8s-resources.yaml

# Backup Dapr components
kubectl get components -A -o yaml > backups/dapr-components.yaml
```

## Reference Documentation

For detailed patterns and examples:
- **Blueprint Patterns**: See `references/blueprint-patterns.md` for common architectural patterns, deployment strategies, and customization guides

## Bonus Points Compliance

✅ **Cloud-Native Blueprint Created** - Reusable architecture extracted
✅ **Infrastructure Packaged** - Helm charts and K8s manifests included
✅ **Deployment Guide** - Complete BLUEPRINT.md with step-by-step instructions
✅ **Spec Templates** - Spec-Kit templates for feature development
✅ **Production Ready** - Configurations for development and production
✅ **Documented** - Comprehensive architecture and deployment documentation
✅ **Shareable** - Blueprint can be deployed to other projects
