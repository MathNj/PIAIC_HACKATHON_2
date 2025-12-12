#!/bin/bash

# ========================================
# Create Kubernetes Secrets for Dapr Components
# ========================================
# This script creates Kubernetes secrets from plain-text values.
# No need to manually base64 encode!
#
# Usage:
#   1. Edit the variables below with your actual credentials
#   2. Run: bash create-secrets.sh
#   3. Verify: kubectl get secrets
#
# ========================================

set -e  # Exit on error

echo "🔐 Creating Kubernetes Secrets for Todo App..."
echo ""

# ========================================
# EDIT THESE VALUES WITH YOUR CREDENTIALS
# ========================================

# Redpanda Cloud
REDPANDA_BROKERS="your-cluster.cloud.redpanda.com:9092"
REDPANDA_USERNAME="todo-app-producer"
REDPANDA_PASSWORD="your-redpanda-password"

# DigitalOcean Managed Redis
REDIS_HOST="your-redis-host.db.ondigitalocean.com:25061"
REDIS_PASSWORD="your-redis-password"

# Application Secrets (if needed)
OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-key}"
BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET:-your-better-auth-secret}"

# ========================================
# Validation
# ========================================

if [[ "$REDPANDA_BROKERS" == "your-cluster.cloud.redpanda.com:9092" ]]; then
  echo "❌ Error: Please edit the script and provide actual Redpanda credentials"
  echo ""
  echo "Edit this file: $0"
  echo "Update the REDPANDA_* variables at the top"
  exit 1
fi

if [[ "$REDIS_HOST" == "your-redis-host.db.ondigitalocean.com:25061" ]]; then
  echo "❌ Error: Please edit the script and provide actual Redis credentials"
  echo ""
  echo "Edit this file: $0"
  echo "Update the REDIS_* variables at the top"
  exit 1
fi

# ========================================
# Create Secrets
# ========================================

echo "1️⃣  Creating redpanda-credentials secret..."
kubectl create secret generic redpanda-credentials \
  --from-literal=brokers="$REDPANDA_BROKERS" \
  --from-literal=sasl-username="$REDPANDA_USERNAME" \
  --from-literal=sasl-password="$REDPANDA_PASSWORD" \
  --namespace=default \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ redpanda-credentials created"
echo ""

echo "2️⃣  Creating redis-credentials secret..."
kubectl create secret generic redis-credentials \
  --from-literal=redis-host="$REDIS_HOST" \
  --from-literal=redis-password="$REDIS_PASSWORD" \
  --namespace=default \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ redis-credentials created"
echo ""

echo "3️⃣  Creating app-secrets secret..."
kubectl create secret generic app-secrets \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --namespace=default \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ app-secrets created"
echo ""

# ========================================
# Verification
# ========================================

echo "🔍 Verifying secrets..."
echo ""

kubectl get secrets -n default | grep -E "redpanda-credentials|redis-credentials|app-secrets" || true

echo ""
echo "✅ All secrets created successfully!"
echo ""
echo "Next steps:"
echo "  1. Apply Dapr components: kubectl apply -f infrastructure/dapr/components/"
echo "  2. Restart backend pods to inject Dapr sidecar"
echo ""
