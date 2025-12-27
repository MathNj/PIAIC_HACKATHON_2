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
   - `smtp-server`: SMTP server address (default: smtp.gmail.com)
   - `smtp-port`: SMTP server port (default: 587)
   - `smtp-username`: Your Gmail address
   - `smtp-password`: Gmail app password (not your regular password)
   - `smtp-from-email`: Email address for sending notifications
   - `smtp-from-name`: Display name for email sender (e.g., "TODO App Notifications")
   - `email-notifications-enabled`: Enable/disable email notifications (true/false)

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
  --from-literal=openai-model="llama-3.3-70b-versatile" \
  --from-literal=smtp-server="smtp.gmail.com" \
  --from-literal=smtp-port="587" \
  --from-literal=smtp-username="your-gmail@gmail.com" \
  --from-literal=smtp-password="your-gmail-app-password" \
  --from-literal=smtp-from-email="your-gmail@gmail.com" \
  --from-literal=smtp-from-name="TODO App Notifications" \
  --from-literal=email-notifications-enabled="true"
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
| `smtp-server` | SMTP server address | `smtp.gmail.com` |
| `smtp-port` | SMTP server port | `587` |
| `smtp-username` | Gmail address for sending emails | `your-email@gmail.com` |
| `smtp-password` | Gmail app password | `xxxx xxxx xxxx xxxx` |
| `smtp-from-email` | Sender email address | `your-email@gmail.com` |
| `smtp-from-name` | Sender display name | `TODO App Notifications` |
| `email-notifications-enabled` | Enable/disable email notifications | `true` or `false` |

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

### Gmail SMTP (Email Notifications)
1. Go to your Google Account settings: https://myaccount.google.com
2. Navigate to Security → 2-Step Verification (enable if not already enabled)
3. Go to Security → App passwords
4. Select app: "Mail", select device: "Other (Custom name)"
5. Enter a name (e.g., "TODO App")
6. Click "Generate"
7. Copy the 16-character app password (format: `xxxx xxxx xxxx xxxx`)
8. Use your Gmail address as `smtp-username` and `smtp-from-email`
9. Use the app password as `smtp-password`

**Note**: Never use your actual Gmail password. Always use an app password for security.

To disable email notifications, set `email-notifications-enabled: "false"` in the secrets.

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
