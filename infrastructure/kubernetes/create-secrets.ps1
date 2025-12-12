# ========================================
# Create Kubernetes Secrets for Dapr Components (PowerShell)
# ========================================
# This script creates Kubernetes secrets from plain-text values.
# No need to manually base64 encode!
#
# Usage:
#   1. Edit the variables below with your actual credentials
#   2. Run: powershell -ExecutionPolicy Bypass -File create-secrets.ps1
#   3. Verify: kubectl get secrets
#
# ========================================

Write-Host "🔐 Creating Kubernetes Secrets for Todo App..." -ForegroundColor Cyan
Write-Host ""

# ========================================
# EDIT THESE VALUES WITH YOUR CREDENTIALS
# ========================================

# Redpanda Cloud
$REDPANDA_BROKERS = "your-cluster.cloud.redpanda.com:9092"
$REDPANDA_USERNAME = "todo-app-producer"
$REDPANDA_PASSWORD = "your-redpanda-password"

# DigitalOcean Managed Redis
$REDIS_HOST = "your-redis-host.db.ondigitalocean.com:25061"
$REDIS_PASSWORD = "your-redis-password"

# Application Secrets (optional - will use environment variables if set)
$OPENAI_API_KEY = if ($env:OPENAI_API_KEY) { $env:OPENAI_API_KEY } else { "your-openai-key" }
$BETTER_AUTH_SECRET = if ($env:BETTER_AUTH_SECRET) { $env:BETTER_AUTH_SECRET } else { "your-better-auth-secret" }

# ========================================
# Validation
# ========================================

if ($REDPANDA_BROKERS -eq "your-cluster.cloud.redpanda.com:9092") {
    Write-Host "❌ Error: Please edit the script and provide actual Redpanda credentials" -ForegroundColor Red
    Write-Host ""
    Write-Host "Edit this file: $PSCommandPath"
    Write-Host "Update the REDPANDA_* variables at the top"
    exit 1
}

if ($REDIS_HOST -eq "your-redis-host.db.ondigitalocean.com:25061") {
    Write-Host "❌ Error: Please edit the script and provide actual Redis credentials" -ForegroundColor Red
    Write-Host ""
    Write-Host "Edit this file: $PSCommandPath"
    Write-Host "Update the REDIS_* variables at the top"
    exit 1
}

# ========================================
# Create Secrets
# ========================================

Write-Host "1️⃣  Creating redpanda-credentials secret..." -ForegroundColor Yellow

kubectl create secret generic redpanda-credentials `
    --from-literal=brokers="$REDPANDA_BROKERS" `
    --from-literal=sasl-username="$REDPANDA_USERNAME" `
    --from-literal=sasl-password="$REDPANDA_PASSWORD" `
    --namespace=default `
    --dry-run=client -o yaml | kubectl apply -f -

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ redpanda-credentials created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create redpanda-credentials" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "2️⃣  Creating redis-credentials secret..." -ForegroundColor Yellow

kubectl create secret generic redis-credentials `
    --from-literal=redis-host="$REDIS_HOST" `
    --from-literal=redis-password="$REDIS_PASSWORD" `
    --namespace=default `
    --dry-run=client -o yaml | kubectl apply -f -

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ redis-credentials created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create redis-credentials" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "3️⃣  Creating app-secrets secret..." -ForegroundColor Yellow

kubectl create secret generic app-secrets `
    --from-literal=openai-api-key="$OPENAI_API_KEY" `
    --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" `
    --namespace=default `
    --dry-run=client -o yaml | kubectl apply -f -

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ app-secrets created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create app-secrets" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ========================================
# Verification
# ========================================

Write-Host "🔍 Verifying secrets..." -ForegroundColor Cyan
Write-Host ""

kubectl get secrets -n default | Select-String -Pattern "redpanda-credentials|redis-credentials|app-secrets"

Write-Host ""
Write-Host "✅ All secrets created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Apply Dapr components: kubectl apply -f infrastructure/dapr/components/*-prod.yaml"
Write-Host "  2. Restart backend pods to inject Dapr sidecar"
Write-Host ""
