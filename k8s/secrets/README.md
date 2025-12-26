# Kubernetes Secrets Configuration

This directory contains templates and documentation for configuring Kubernetes secrets for the Todo App.

## ⚠️ Security Warning

**NEVER commit actual secrets to git!** The `app-secrets.yaml` file is gitignored to prevent accidental commits of sensitive data.

## Setup Instructions

### Option 1: Using the Template File (Recommended for Local Development)

1. Copy the template file:
   ```bash
   cp app-secrets.yaml.template app-secrets.yaml
   ```

2. Edit `app-secrets.yaml` and replace the placeholder values with your actual credentials:
   - `database-url`: Your PostgreSQL connection string (e.g., Neon database URL)
   - `jwt-secret`: A secure random string (minimum 32 characters)
   - `openai-api-key`: Your Groq API key
   - `openai-base-url`: Groq API base URL (already set correctly)
   - `openai-model`: AI model name (already set correctly)

3. Apply the secrets to your Kubernetes cluster:
   ```bash
   kubectl apply -f app-secrets.yaml
   ```

4. Verify the secrets were created:
   ```bash
   kubectl get secrets app-secrets
   ```

### Option 2: Using kubectl create secret (Production)

Create secrets directly without storing them in files:

```bash
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://user:password@host:port/database?sslmode=require" \
  --from-literal=jwt-secret="your-jwt-secret-min-32-characters-long" \
  --from-literal=openai-api-key="gsk_your-groq-api-key-here" \
  --from-literal=openai-base-url="https://api.groq.com/openai/v1" \
  --from-literal=openai-model="llama-3.3-70b-versatile"
```

### Option 3: Using Helm Values (Cloud Deployment)

For production deployments, use Helm's `--set` flag or a separate values file:

```bash
helm install todo-app ./helm/todo-app \
  --set secrets.databaseUrl="your-database-url" \
  --set secrets.jwtSecret="your-jwt-secret" \
  --set secrets.openaiApiKey="your-groq-api-key" \
  --set secrets.openaiBaseUrl="https://api.groq.com/openai/v1" \
  --set secrets.openaiModel="llama-3.3-70b-versatile"
```

Or create a `values-production.yaml` file (and keep it gitignored):

```yaml
secrets:
  databaseUrl: "postgresql://..."
  jwtSecret: "..."
  openaiApiKey: "gsk_..."
  openaiBaseUrl: "https://api.groq.com/openai/v1"
  openaiModel: "llama-3.3-70b-versatile"
```

Then install with:
```bash
helm install todo-app ./helm/todo-app -f values-production.yaml
```

## Required Secrets

| Secret Key | Description | Example Value |
|------------|-------------|---------------|
| `database-url` | PostgreSQL connection string | `postgresql://user:pass@host:port/db?sslmode=require` |
| `jwt-secret` | JWT authentication secret (min 32 chars) | `your-secure-random-string-here` |
| `openai-api-key` | Groq API key for AI agent | `gsk_...` |
| `openai-base-url` | Groq API base URL | `https://api.groq.com/openai/v1` |
| `openai-model` | AI model name | `llama-3.3-70b-versatile` |

## Getting API Keys

### Database (Neon)
1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string from the dashboard
4. Ensure `?sslmode=require` is appended

### Groq API
1. Sign up at https://console.groq.com
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key (starts with `gsk_`)

## Updating Secrets

If you need to update secrets after they've been created:

```bash
# Delete old secret
kubectl delete secret app-secrets

# Apply new secret
kubectl apply -f app-secrets.yaml

# Or recreate using kubectl
kubectl create secret generic app-secrets --from-literal=...

# Restart pods to pick up new secrets
kubectl rollout restart deployment/todo-app-backend
```

## Verification

Check that secrets are properly injected into pods:

```bash
# List secrets
kubectl get secrets

# Verify secret has correct keys (values will be base64 encoded)
kubectl describe secret app-secrets

# Check environment variables in a pod
kubectl exec -it <pod-name> -- printenv | grep -E '(DATABASE_URL|OPENAI_API_KEY|OPENAI_BASE_URL)'
```

## Security Best Practices

1. **Never commit secrets to git** - The actual `app-secrets.yaml` file is gitignored
2. **Use strong JWT secrets** - Minimum 32 characters, random string
3. **Rotate secrets regularly** - Update API keys and JWT secrets periodically
4. **Use RBAC** - Limit who can view/edit secrets in Kubernetes
5. **Use sealed secrets for GitOps** - Consider tools like Sealed Secrets or External Secrets Operator for production

## Troubleshooting

### Secret not found error
```
Error: secrets "app-secrets" not found
```
**Solution**: Apply the secrets first: `kubectl apply -f app-secrets.yaml`

### Environment variable not set
```
OPENAI_API_KEY environment variable is required
```
**Solution**:
1. Verify secret exists: `kubectl get secret app-secrets`
2. Check pod environment: `kubectl exec <pod> -- printenv`
3. Restart deployment: `kubectl rollout restart deployment/todo-app-backend`

### Invalid API key
```
Error: 401 Unauthorized
```
**Solution**: Verify your Groq API key is correct and active at https://console.groq.com
