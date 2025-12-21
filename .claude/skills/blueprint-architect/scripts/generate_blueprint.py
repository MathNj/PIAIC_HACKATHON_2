#!/usr/bin/env python3
"""
Blueprint Generator

Extracts reusable architectural patterns from the codebase and generates
Cloud-Native Blueprints.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlueprintGenerator:
    """
    Generates Cloud-Native Blueprints from existing project structure.

    Analyzes FastAPI + Next.js + Dapr + Kafka architecture and extracts
    reusable patterns as blueprints.
    """

    def __init__(self, project_root: str, output_dir: str = "blueprints"):
        """
        Initialize Blueprint Generator.

        Args:
            project_root: Root directory of the project to analyze
            output_dir: Directory to output generated blueprints
        """
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def analyze_project_structure(self) -> Dict[str, Any]:
        """
        Analyze project structure and identify components.

        Returns:
            Dict with project structure analysis
        """
        logger.info("Analyzing project structure...")

        structure = {
            "backend": {
                "exists": (self.project_root / "backend").exists(),
                "framework": "FastAPI",
                "language": "Python",
                "features": []
            },
            "frontend": {
                "exists": (self.project_root / "frontend").exists(),
                "framework": "Next.js",
                "language": "TypeScript",
                "features": []
            },
            "infrastructure": {
                "helm_charts": (self.project_root / "infrastructure" / "helm").exists(),
                "k8s_manifests": (self.project_root / "infrastructure" / "kubernetes").exists(),
                "dapr_components": (self.project_root / "infrastructure" / "dapr").exists(),
                "terraform": (self.project_root / "infrastructure" / "terraform").exists()
            },
            "deployment": {
                "minikube": [],
                "production": [],
                "cloud_provider": "kubernetes"
            },
            "event_driven": {
                "kafka": self._check_kafka_setup(),
                "dapr_pubsub": self._check_dapr_pubsub(),
                "dapr_jobs": self._check_dapr_jobs()
            }
        }

        # Detect backend features
        if structure["backend"]["exists"]:
            structure["backend"]["features"] = self._detect_backend_features()

        # Detect frontend features
        if structure["frontend"]["exists"]:
            structure["frontend"]["features"] = self._detect_frontend_features()

        return structure

    def _check_kafka_setup(self) -> bool:
        """Check if Kafka infrastructure exists."""
        dapr_path = self.project_root / "infrastructure" / "dapr" / "components"
        if not dapr_path.exists():
            return False

        for file in dapr_path.glob("*pubsub*.yaml"):
            content = file.read_text()
            if "kafka" in content.lower():
                return True
        return False

    def _check_dapr_pubsub(self) -> bool:
        """Check if Dapr pub/sub is configured."""
        dapr_path = self.project_root / "infrastructure" / "dapr" / "components"
        return dapr_path.exists() and any(dapr_path.glob("*pubsub*.yaml"))

    def _check_dapr_jobs(self) -> bool:
        """Check if Dapr Jobs API is configured."""
        # Check for job scheduler component or job-related code
        return False  # Placeholder

    def _detect_backend_features(self) -> List[str]:
        """Detect backend features."""
        features = []
        backend_path = self.project_root / "backend"

        # Check for specific features
        if (backend_path / "app" / "routers" / "auth.py").exists():
            features.append("Authentication (JWT)")

        if (backend_path / "app" / "models").exists():
            features.append("SQLModel ORM")

        if (backend_path / "mcp").exists():
            features.append("MCP Tools")

        if (backend_path / "agent_runner").exists():
            features.append("OpenAI Agents SDK")

        return features

    def _detect_frontend_features(self) -> List[str]:
        """Detect frontend features."""
        features = []
        frontend_path = self.project_root / "frontend"

        # Check for specific features
        if (frontend_path / "app" / "chat").exists():
            features.append("OpenAI ChatKit")

        if (frontend_path / "lib" / "i18n").exists():
            features.append("i18n (English/Urdu)")

        if (frontend_path / "components" / "VoiceButton.tsx").exists():
            features.append("Voice Input")

        return features

    def generate_blueprint(
        self,
        name: str,
        description: str,
        use_cases: List[str]
    ) -> str:
        """
        Generate a complete blueprint.

        Args:
            name: Blueprint name
            description: Blueprint description
            use_cases: List of use cases

        Returns:
            Path to generated blueprint directory
        """
        logger.info(f"Generating blueprint: {name}")

        # Analyze project
        structure = self.analyze_project_structure()

        # Create blueprint directory
        blueprint_dir = self.output_dir / name
        blueprint_dir.mkdir(exist_ok=True)

        # Copy infrastructure
        self._copy_infrastructure(blueprint_dir)

        # Generate spec templates
        self._generate_spec_templates(blueprint_dir)

        # Generate BLUEPRINT.md
        self._generate_blueprint_md(
            blueprint_dir,
            name,
            description,
            use_cases,
            structure
        )

        # Generate metadata
        self._generate_metadata(blueprint_dir, name, structure)

        logger.info(f"Blueprint generated at: {blueprint_dir}")
        return str(blueprint_dir)

    def _copy_infrastructure(self, blueprint_dir: Path):
        """Copy Helm charts and K8s manifests."""
        logger.info("Copying infrastructure files...")

        infra_src = self.project_root / "infrastructure"
        infra_dst = blueprint_dir / "infrastructure"
        infra_dst.mkdir(exist_ok=True)

        # Copy Helm charts
        if (infra_src / "helm").exists():
            shutil.copytree(
                infra_src / "helm",
                infra_dst / "helm",
                dirs_exist_ok=True
            )
            logger.info("Copied Helm charts")

        # Copy K8s manifests
        if (infra_src / "kubernetes").exists():
            shutil.copytree(
                infra_src / "kubernetes",
                infra_dst / "kubernetes",
                dirs_exist_ok=True
            )
            logger.info("Copied K8s manifests")

        # Copy Dapr components
        if (infra_src / "dapr").exists():
            shutil.copytree(
                infra_src / "dapr",
                infra_dst / "dapr",
                dirs_exist_ok=True
            )
            logger.info("Copied Dapr components")

    def _generate_spec_templates(self, blueprint_dir: Path):
        """Generate Spec-Kit templates."""
        logger.info("Generating Spec-Kit templates...")

        specs_dir = blueprint_dir / "specs"
        specs_dir.mkdir(exist_ok=True)

        # Create template spec
        template_spec = """# {Feature Name}

## Overview

{Brief description of the feature}

## Requirements

### Functional Requirements

1. {Requirement 1}
2. {Requirement 2}
3. {Requirement 3}

### Non-Functional Requirements

- Performance: {Performance requirements}
- Security: {Security requirements}
- Scalability: {Scalability requirements}

## Architecture

### Backend (FastAPI)

- Endpoints: {List endpoints}
- Models: {List SQLModel models}
- Authentication: JWT with Better Auth

### Frontend (Next.js)

- Pages: {List pages}
- Components: {List components}
- State Management: React Query

### Event-Driven (Dapr + Kafka)

- Topics: {List Kafka topics}
- Publishers: {List publishers}
- Subscribers: {List subscribers}

## Database Schema

```sql
-- {Table definitions}
```

## API Endpoints

### {Endpoint Group}

**POST /{endpoint}**
- Description: {Description}
- Request: {Request schema}
- Response: {Response schema}

## Deployment

### Helm Chart Values

```yaml
# values.yaml
{Helm values}
```

### Kubernetes Resources

- Deployment
- Service
- Ingress
- ConfigMap
- Secret

## Testing

- Unit tests: {Test files}
- Integration tests: {Test files}
- E2E tests: {Test files}
"""

        (specs_dir / "feature-template.md").write_text(template_spec)
        logger.info("Created feature template")

    def _generate_blueprint_md(
        self,
        blueprint_dir: Path,
        name: str,
        description: str,
        use_cases: List[str],
        structure: Dict[str, Any]
    ):
        """Generate BLUEPRINT.md file."""
        logger.info("Generating BLUEPRINT.md...")

        content = f"""# {name}

{description}

## Architecture Overview

This blueprint implements a modern cloud-native microservices architecture with:

- **Backend**: FastAPI (Python) with SQLModel ORM
- **Frontend**: Next.js 16+ (TypeScript) with App Router
- **Event Bus**: Kafka (Strimzi/Redpanda) with Dapr pub/sub
- **Orchestration**: Kubernetes with Helm charts
- **State Management**: Dapr state store (Redis)
- **Job Scheduling**: Dapr Jobs API

## Technology Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Authentication**: Better Auth (JWT)
- **Features**: {', '.join(structure['backend']['features'])}

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Features**: {', '.join(structure['frontend']['features'])}

### Infrastructure
- **Container Orchestration**: Kubernetes
- **Package Manager**: Helm
- **Service Mesh**: Dapr
- **Event Streaming**: Kafka
- **State Store**: Redis

## Use Cases

{chr(10).join(f"- {uc}" for uc in use_cases)}

## Directory Structure

```
{name}/
├── infrastructure/
│   ├── helm/                 # Helm charts
│   │   └── todo-stack/       # Main application chart
│   ├── kubernetes/           # K8s manifests
│   │   ├── secrets.yaml
│   │   └── services.yaml
│   └── dapr/                 # Dapr components
│       └── components/
│           ├── kafka-pubsub.yaml
│           ├── statestore.yaml
│           └── job-scheduler.yaml
├── specs/                    # Spec-Kit templates
│   └── feature-template.md
└── BLUEPRINT.md              # This file
```

## Deployment Guide

### Prerequisites

- Kubernetes cluster (Minikube or cloud provider)
- kubectl CLI installed
- Helm 3+ installed
- Dapr CLI installed

### Step 1: Deploy Kafka Infrastructure

```bash
# Using kafka-infra-provisioner skill
cd infrastructure/kafka
bash deploy_kafka.sh
```

### Step 2: Deploy Dapr Components

```bash
# Apply Dapr components
kubectl apply -f infrastructure/dapr/components/
```

### Step 3: Deploy Application with Helm

```bash
# Install Helm chart
helm install my-app infrastructure/helm/todo-stack/ \\
  --namespace default \\
  --create-namespace \\
  --values infrastructure/helm/todo-stack/values-local.yaml
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# Check Dapr components
dapr components -k
```

## Configuration

### Environment Variables

**Backend:**
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret for JWT signing
- `REDIS_HOST`: Redis host for state store
- `KAFKA_BROKERS`: Kafka bootstrap servers

**Frontend:**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `BETTER_AUTH_SECRET`: Authentication secret

### Helm Values

Edit `infrastructure/helm/todo-stack/values.yaml` to configure:

- Replica counts
- Resource limits
- Ingress rules
- ConfigMaps
- Secrets

## Customization

### Adding New Features

1. Create feature spec in `specs/`
2. Implement backend endpoints in `backend/app/routers/`
3. Add database models in `backend/app/models/`
4. Create frontend pages in `frontend/app/`
5. Configure Dapr pub/sub if needed
6. Update Helm chart values

### Event-Driven Patterns

This blueprint uses Dapr pub/sub for event-driven communication:

**Publish Event:**
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="task-events",
        data=json.dumps({{"event": "task.created", "task_id": 123}})
    )
```

**Subscribe to Events:**
```python
@app.post("/dapr/subscribe")
async def dapr_subscribe():
    return [{{
        "pubsubname": "kafka-pubsub",
        "topic": "task-events",
        "route": "/events/task"
    }}]

@app.post("/events/task")
async def handle_task_event(event: dict):
    # Process event
    pass
```

## Scaling

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Kafka Topic Partitioning

Adjust partitions in `infrastructure/kafka/topics.yaml` based on throughput requirements.

## Monitoring

### Metrics

- **Prometheus**: Collects metrics from FastAPI, Kafka, Dapr
- **Grafana**: Visualizes metrics and dashboards

### Logging

- **Fluent Bit**: Collects logs from all pods
- **Elasticsearch**: Stores logs
- **Kibana**: Log visualization

## Security

- **Network Policies**: Restrict pod-to-pod communication
- **Secrets Management**: Use Kubernetes secrets or external vault
- **TLS/mTLS**: Enable for all inter-service communication
- **RBAC**: Configure role-based access control

## Cost Optimization

- Use ephemeral storage for development (Minikube)
- Use persistent storage for production
- Configure resource requests/limits appropriately
- Enable autoscaling to handle variable load
- Use spot instances for non-critical workloads

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Dapr Components Not Loading

```bash
# Check Dapr components
dapr components -k

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

### Kafka Connection Issues

```bash
# Verify Kafka is running
kubectl get pods -n kafka

# Test connectivity
kubectl run kafka-test --image=confluentinc/cp-kafka:latest --rm -i -- \\
  kafka-broker-api-versions --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

## Production Checklist

- [ ] Configure persistent storage for databases
- [ ] Set up monitoring and alerting
- [ ] Configure backup and disaster recovery
- [ ] Enable TLS for all services
- [ ] Configure network policies
- [ ] Set resource limits appropriately
- [ ] Configure autoscaling
- [ ] Set up CI/CD pipeline
- [ ] Configure secrets management
- [ ] Enable logging and log retention

## License

{name} Blueprint - Cloud-Native Microservices Architecture

Generated on: {datetime.now().strftime("%Y-%m-%d")}

## Support

For issues or questions about this blueprint:
1. Check the troubleshooting section
2. Review the deployment guide
3. Consult the spec templates
4. Check Helm chart values

## Credits

Generated by blueprint-architect skill from the Todo App project.
"""

        (blueprint_dir / "BLUEPRINT.md").write_text(content)
        logger.info("Created BLUEPRINT.md")

    def _generate_metadata(
        self,
        blueprint_dir: Path,
        name: str,
        structure: Dict[str, Any]
    ):
        """Generate blueprint metadata JSON."""
        metadata = {
            "name": name,
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "structure": structure,
            "components": {
                "backend": structure["backend"]["exists"],
                "frontend": structure["frontend"]["exists"],
                "kafka": structure["event_driven"]["kafka"],
                "dapr": structure["infrastructure"]["dapr_components"],
                "helm": structure["infrastructure"]["helm_charts"]
            }
        }

        metadata_file = blueprint_dir / "blueprint.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        logger.info("Created blueprint.json")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Cloud-Native Blueprints")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory to analyze"
    )
    parser.add_argument(
        "--output-dir",
        default="blueprints",
        help="Output directory for blueprints"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Blueprint name"
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Blueprint description"
    )
    parser.add_argument(
        "--use-cases",
        nargs="+",
        required=True,
        help="Use cases for this blueprint"
    )

    args = parser.parse_args()

    generator = BlueprintGenerator(args.project_root, args.output_dir)
    blueprint_path = generator.generate_blueprint(
        name=args.name,
        description=args.description,
        use_cases=args.use_cases
    )

    print(f"\n✅ Blueprint generated successfully!")
    print(f"📁 Location: {blueprint_path}")
    print(f"\nNext steps:")
    print(f"1. Review BLUEPRINT.md in the blueprint directory")
    print(f"2. Customize Helm values if needed")
    print(f"3. Deploy using the deployment guide")


if __name__ == "__main__":
    main()
