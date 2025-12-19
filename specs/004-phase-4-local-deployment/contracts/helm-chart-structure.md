# Contract: Helm Chart Structure

**Chart Name**: todo-stack
**Chart Version**: 1.0.0
**App Version**: 4.0.0 (Phase IV)
**Kubernetes API**: apps/v1, v1

## Directory Structure

```
infrastructure/helm/todo-stack/
├── Chart.yaml                      # Chart metadata
├── values.yaml                     # Default configuration values
├── values-local.yaml               # Local environment overrides
├── values-production.yaml          # Production environment overrides
├── templates/
│   ├── _helpers.tpl                # Template helpers and labels
│   ├── backend-deployment.yaml     # Backend Deployment manifest
│   ├── backend-service.yaml        # Backend Service manifest
│   ├── frontend-deployment.yaml    # Frontend Deployment manifest
│   ├── frontend-service.yaml       # Frontend Service manifest
│   ├── secrets.yaml                # Secrets manifest (reference only)
│   ├── configmap.yaml              # ConfigMap for non-sensitive config
│   ├── ingress.yaml                # Optional Ingress (disabled by default)
│   └── NOTES.txt                   # Post-install instructions
├── .helmignore                     # Files to ignore in packaging
└── README.md                       # Chart documentation
```

## Chart.yaml Specification

```yaml
apiVersion: v2
name: todo-stack
description: Todo Chatbot with AI Agent (Phase III) - Kubernetes Deployment
type: application
version: 1.0.0
appVersion: "4.0.0"
keywords:
  - todo
  - kubernetes
  - helm
  - ai
  - chatbot
  - minikube
  - fastapi
  - nextjs
maintainers:
  - name: Todo App Team
    email: team@example.com
sources:
  - https://github.com/your-org/todo-app
icon: https://example.com/todo-icon.png
```

## values.yaml (Default Values)

```yaml
# Global configuration
global:
  environment: local
  labels:
    app: todo
    managedBy: helm

# Backend configuration
backend:
  enabled: true
  replicaCount: 2

  image:
    repository: todo-backend
    tag: local
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000

  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1024Mi

  healthProbes:
    readiness:
      path: /health/ready
      port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
    liveness:
      path: /health/live
      port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3

  env:
    LOG_LEVEL: info
    WORKERS: "1"

# Frontend configuration
frontend:
  enabled: true
  replicaCount: 1

  image:
    repository: todo-frontend
    tag: local
    pullPolicy: IfNotPresent

  service:
    type: NodePort
    port: 3000
    targetPort: 3000
    nodePort: 30080  # Fixed for local development

  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

  healthProbes:
    readiness:
      path: /
      port: 3000
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
    liveness:
      path: /
      port: 3000
      initialDelaySeconds: 15
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3

  env:
    NEXT_PUBLIC_API_URL: http://backend-service:8000

# Secrets configuration
secrets:
  name: todo-secrets
  create: false  # Manually created via kubectl
  keys:
    - DATABASE_URL
    - OPENAI_API_KEY
    - BETTER_AUTH_SECRET

# ConfigMap configuration
configMap:
  name: todo-config
  data:
    APP_NAME: "Todo Chatbot"
    ENVIRONMENT: "{{ .Values.global.environment }}"

# Ingress configuration (optional)
ingress:
  enabled: false
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com
```

## values-local.yaml (Local Overrides)

```yaml
global:
  environment: local

backend:
  replicaCount: 2
  image:
    tag: local
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1024Mi

frontend:
  replicaCount: 1
  image:
    tag: local
  service:
    type: NodePort
    nodePort: 30080
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

ingress:
  enabled: false
```

## values-production.yaml (Production Overrides)

```yaml
global:
  environment: production

backend:
  replicaCount: 3
  image:
    repository: registry.digitalocean.com/todo/backend
    tag: v1.0.0
    pullPolicy: Always
  resources:
    requests:
      cpu: 1000m
      memory: 1024Mi
    limits:
      cpu: 2000m
      memory: 2048Mi

frontend:
  replicaCount: 2
  image:
    repository: registry.digitalocean.com/todo/frontend
    tag: v1.0.0
    pullPolicy: Always
  service:
    type: LoadBalancer
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1024Mi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.yourdomain.com
```

## Template Helpers (_helpers.tpl)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-stack.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-stack.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-stack.labels" -}}
helm.sh/chart: {{ include "todo-stack.chart" . }}
{{ include "todo-stack.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: {{ .Values.global.labels.app }}
environment: {{ .Values.global.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-stack.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-stack.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
AI Ops annotations
*/}}
{{- define "todo-stack.aiOpsAnnotations" -}}
ai-ops/enabled: "true"
ai-ops/tools: "kubectl-ai,kagent"
{{- end }}
```

## Deployment Templates

### Backend Deployment (backend-deployment.yaml)

Key requirements:
- 2 replicas (configurable via values)
- envFrom referencing todo-secrets
- Readiness and liveness probes
- Resource limits
- Security context (non-root user)
- Rolling update strategy
- Standard labels and AI ops annotations

### Frontend Deployment (frontend-deployment.yaml)

Key requirements:
- 1 replica (configurable via values)
- Environment variable for backend URL
- Readiness and liveness probes
- Resource limits
- Security context (non-root user)
- Rolling update strategy
- Standard labels and AI ops annotations

## Service Templates

### Backend Service (backend-service.yaml)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  labels:
    {{- include "todo-stack.labels" . | nindent 4 }}
    tier: backend
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: {{ .Values.backend.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "todo-stack.selectorLabels" . | nindent 4 }}
    tier: backend
```

### Frontend Service (frontend-service.yaml)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  labels:
    {{- include "todo-stack.labels" . | nindent 4 }}
    tier: frontend
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: {{ .Values.frontend.service.targetPort }}
      {{- if and (eq .Values.frontend.service.type "NodePort") .Values.frontend.service.nodePort }}
      nodePort: {{ .Values.frontend.service.nodePort }}
      {{- end }}
      protocol: TCP
      name: http
  selector:
    {{- include "todo-stack.selectorLabels" . | nindent 4 }}
    tier: frontend
```

## NOTES.txt (Post-Install Instructions)

```
Thank you for installing {{ .Chart.Name }}!

Your Todo Chatbot (Phase IV) has been deployed to Kubernetes.

Release Name: {{ .Release.Name }}
Namespace: {{ .Release.Namespace }}
Environment: {{ .Values.global.environment }}

To access the application:
{{- if eq .Values.frontend.service.type "NodePort" }}
  Frontend: http://localhost:{{ .Values.frontend.service.nodePort }}
{{- else if eq .Values.frontend.service.type "LoadBalancer" }}
  Frontend: Run 'kubectl get svc frontend-service' to get EXTERNAL-IP
{{- end }}

To check the deployment status:
  kubectl get pods -l app={{ .Values.global.labels.app }}
  kubectl get services -l app={{ .Values.global.labels.app }}

Backend Replicas: {{ .Values.backend.replicaCount }}
Frontend Replicas: {{ .Values.frontend.replicaCount }}

For troubleshooting:
  kubectl logs -l app={{ .Values.global.labels.app }},tier=backend -f
  kubectl logs -l app={{ .Values.global.labels.app }},tier=frontend -f

To upgrade the deployment:
  helm upgrade {{ .Release.Name }} . -f values-{{ .Values.global.environment }}.yaml

To uninstall:
  helm uninstall {{ .Release.Name }}
```

## Helm Commands

### Install
```bash
# Local environment
helm install todo-stack . -f values-local.yaml

# Production environment
helm install todo-stack . -f values-production.yaml

# Custom namespace
helm install todo-stack . -f values-local.yaml --namespace todo --create-namespace
```

### Upgrade
```bash
helm upgrade todo-stack . -f values-local.yaml

# With value overrides
helm upgrade todo-stack . -f values-local.yaml --set backend.replicaCount=3
```

### Uninstall
```bash
helm uninstall todo-stack
```

### Test
```bash
helm lint .
helm template . --debug
helm install todo-stack . --dry-run --debug -f values-local.yaml
```

## Validation Requirements

1. **Helm Lint**: Must pass without errors
2. **Template Render**: Must render valid YAML
3. **Labels**: All resources must have standard labels
4. **Annotations**: AI ops annotations on Deployments
5. **Health Probes**: Both readiness and liveness defined
6. **Resources**: Limits and requests specified
7. **Security**: Non-root users, no privileged containers
8. **Secrets**: Referenced, not embedded

## Success Criteria Mapping

- ✅ **FR-006**: Helm chart named `todo-stack` ✓
- ✅ **FR-007**: Environment configuration via values files ✓
- ✅ **FR-010**: Standardized labels (app, tier, environment) ✓
- ✅ **FR-012**: Secrets injection via envFrom ✓
- ✅ **FR-015**: Backend 2 replicas (configurable) ✓
- ✅ **FR-016**: Frontend 1 replica (configurable) ✓
- ✅ **FR-019**: Configuration externalized to values ✓
- ✅ **FR-022**: Default values with clear documentation ✓
- ✅ **SC-006**: Environment toggle via values files ✓
- ✅ **SC-014**: Configuration changes via Helm values ✓
