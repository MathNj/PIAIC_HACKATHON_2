---
name: "k8s-deployer"
description: "Generates deployment configurations for the Todo App: Vercel deployment, Docker containers, Kubernetes manifests, and Dapr components. Use for Phase IV/V deployment tasks."
version: "2.0.0"
---

# Deployment & DevOps Skill

## When to Use
- User asks to "deploy to Vercel" or "containerize this"
- User says "Create Docker configuration" or "Generate K8s manifests"
- User requests "Dapr setup" or "Configure for production"
- Phase IV/V deployment and infrastructure work

## Context
This skill handles deployment following the project structure:
- **Primary Deployment**: Vercel (both frontend and backend)
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes (DigitalOcean/Minikube) with Dapr sidecars
- **Event-Driven**: Dapr Pub/Sub with Kafka/Redpanda (Phase V)
- **Database**: Neon PostgreSQL for production

## Workflow
1. **Identify Target**: Determine deployment platform (Vercel, K8s, Docker)
2. **Environment Variables**: Configure secrets and environment-specific settings
3. **Containerization**: Create Dockerfiles with multi-stage builds
4. **Orchestration**: Generate K8s manifests or Helm charts
5. **Dapr Configuration**: Add sidecar annotations and component specs
6. **CI/CD**: Set up deployment pipelines (Vercel auto-deployment, GitHub Actions)
7. **Testing**: Verify deployment in target environment

## Output Formats

### 1. Vercel Deployment (Primary)

#### Frontend Deployment
```json
// vercel.json (frontend)
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@backend-url"
  },
  "regions": ["iad1"]
}
```

#### Backend Deployment
```json
// vercel.json (backend)
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ],
  "env": {
    "DATABASE_URL": "@database-url",
    "BETTER_AUTH_SECRET": "@auth-secret",
    "FRONTEND_URL": "@frontend-url"
  }
}
```

#### Deployment Commands
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel --prod

# Deploy backend
cd backend
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add DATABASE_URL production
vercel env add BETTER_AUTH_SECRET production
```

### 2. Docker Configuration

#### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build with environment variables
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

#### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.13-slim AS base

WORKDIR /app

# Install dependencies
FROM base AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production image
FROM python:3.13-slim AS runner
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app ./app
COPY alembic.ini .
COPY alembic ./alembic

# Create non-root user
RUN useradd -m -u 1001 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/todoapp
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - FRONTEND_URL=http://localhost:3000
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=todoapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Kubernetes Deployment (Phase IV)

#### Backend Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        # Dapr sidecar annotations (Phase V)
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: your-registry/todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: auth-secret
        - name: FRONTEND_URL
          value: "https://your-frontend-url.vercel.app"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Frontend Deployment
```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/todo-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://todo-backend"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
spec:
  selector:
    app: todo-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

#### Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:pass@neon-host/db?sslmode=require"
  auth-secret: "your-secret-at-least-32-characters-long"
```

### 4. Dapr Configuration (Phase V)

#### Pub/Sub Component
```yaml
# dapr/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda:9092"
  - name: authType
    value: "none"
  - name: consumerGroup
    value: "todo-app"
```

#### State Store Component
```yaml
# dapr/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: todo-secrets
      key: database-url
```

#### Subscription
```yaml
# dapr/subscription.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events
spec:
  topic: task-events
  route: /api/events/tasks
  pubsubname: pubsub
scopes:
- todo-backend
```

### 5. Helm Chart (Advanced)

```yaml
# helm/todo-app/Chart.yaml
apiVersion: v2
name: todo-app
description: Full-stack TODO application with Dapr
version: 1.0.0
appVersion: "1.0.0"

# helm/todo-app/values.yaml
backend:
  image:
    repository: your-registry/todo-backend
    tag: latest
  replicas: 2
  dapr:
    enabled: true
    appId: todo-backend

frontend:
  image:
    repository: your-registry/todo-frontend
    tag: latest
  replicas: 2

database:
  url: "postgresql://user:pass@neon-host/db"

secrets:
  authSecret: "your-secret-here"
```

## Deployment Steps

### Vercel Deployment (Recommended for Phase II)
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy backend
cd backend
vercel --prod

# 3. Deploy frontend
cd frontend
vercel --prod

# 4. Configure environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add DATABASE_URL production
vercel env add BETTER_AUTH_SECRET production

# 5. Redeploy to apply env vars
vercel --prod --force
```

### Docker Local Development
```bash
# Build and run with docker-compose
docker-compose up --build

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```

### Kubernetes Deployment
```bash
# 1. Build and push images
docker build -t your-registry/todo-backend:latest ./backend
docker build -t your-registry/todo-frontend:latest ./frontend
docker push your-registry/todo-backend:latest
docker push your-registry/todo-frontend:latest

# 2. Apply secrets
kubectl apply -f k8s/secrets.yaml

# 3. Deploy backend and frontend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# 4. (Phase V) Deploy Dapr components
kubectl apply -f dapr/pubsub.yaml
kubectl apply -f dapr/statestore.yaml
kubectl apply -f dapr/subscription.yaml

# 5. Verify deployment
kubectl get pods
kubectl get services
kubectl logs -l app=todo-backend
```

## Post-Deployment Checklist
- [ ] Environment variables configured
- [ ] Database connection working
- [ ] Health checks passing
- [ ] CORS configured correctly
- [ ] HTTPS/SSL enabled
- [ ] Secrets secured (not hardcoded)
- [ ] Logging and monitoring enabled
- [ ] Auto-scaling configured (K8s)
- [ ] Backup strategy in place
- [ ] CI/CD pipeline set up

## Example
**Input**: "Deploy the app to Vercel for production"

**Output**:
- `vercel.json` for both frontend and backend
- Environment variable configuration commands
- Deployment commands with Vercel CLI
- Database migration instructions for Neon PostgreSQL
- CORS configuration for production URLs

## Quality Checklist
Before finalizing:
- [ ] All secrets use environment variables (never hardcoded)
- [ ] Health check endpoints configured
- [ ] Resource limits set (K8s)
- [ ] Multi-stage Docker builds for smaller images
- [ ] Non-root user for containers
- [ ] HTTPS enforced in production
- [ ] Database connection pooling configured
- [ ] Logging to stdout/stderr for container logs
- [ ] Graceful shutdown handlers
- [ ] Monitoring and alerting set up
