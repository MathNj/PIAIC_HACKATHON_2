#!/bin/bash
# Minikube Deployment Script for Todo Chatbot
# Bash script to automate Kubernetes deployment

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================"
echo -e "Todo Chatbot - Minikube Deployment"
echo -e "========================================${NC}"
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/8] Checking Docker...${NC}"
if docker version >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Minikube is installed
echo -e "\n${YELLOW}[2/8] Checking Minikube...${NC}"
if command -v minikube >/dev/null 2>&1; then
    MINIKUBE_VERSION=$(minikube version | head -n 1)
    echo -e "${GREEN}✓ Minikube is installed: $MINIKUBE_VERSION${NC}"
else
    echo -e "${RED}✗ Minikube is not installed. Please install from https://minikube.sigs.k8s.io/docs/start/${NC}"
    exit 1
fi

# Start Minikube if not running
echo -e "\n${YELLOW}[3/8] Starting Minikube...${NC}"
if minikube status | grep -q "Running"; then
    echo -e "${GREEN}✓ Minikube is already running${NC}"
else
    echo -e "${CYAN}Starting Minikube with Docker driver (4 CPUs, 4GB RAM)...${NC}"
    minikube start --driver=docker --cpus=4 --memory=4096
    echo -e "${GREEN}✓ Minikube started successfully${NC}"
fi

# Configure Docker environment
echo -e "\n${YELLOW}[4/8] Configuring Docker environment...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker environment configured to use Minikube's Docker daemon${NC}"

# Build Docker images
echo -e "\n${YELLOW}[5/8] Building Docker images...${NC}"

echo -e "${CYAN}  Building backend image...${NC}"
cd backend
docker build -t todo-backend:local . -q
echo -e "${GREEN}  ✓ Backend image built: todo-backend:local${NC}"

echo -e "${CYAN}  Building frontend image...${NC}"
cd ../frontend
docker build -t todo-frontend:local . -q
echo -e "${GREEN}  ✓ Frontend image built: todo-frontend:local${NC}"

cd ..

# Check if secrets exist
echo -e "\n${YELLOW}[6/8] Checking Kubernetes secrets...${NC}"
if kubectl get secret todo-secrets >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Secrets already exist: todo-secrets${NC}"
else
    echo -e "${YELLOW}  Secrets not found. Please create them manually:${NC}"
    echo -e "${CYAN}  kubectl create secret generic todo-secrets \\${NC}"
    echo -e "${CYAN}    --from-literal=DATABASE_URL='your-database-url' \\${NC}"
    echo -e "${CYAN}    --from-literal=GEMINI_API_KEY='your-api-key' \\${NC}"
    echo -e "${CYAN}    --from-literal=BETTER_AUTH_SECRET='your-secret'${NC}"
    echo ""
    read -p "Do you want to create secrets now? (y/n): " CREATE_SECRET
    if [ "$CREATE_SECRET" = "y" ]; then
        read -p "Enter DATABASE_URL: " DB_URL
        read -p "Enter GEMINI_API_KEY: " API_KEY
        read -p "Enter BETTER_AUTH_SECRET: " AUTH_SECRET

        kubectl create secret generic todo-secrets \
            --from-literal=DATABASE_URL="$DB_URL" \
            --from-literal=GEMINI_API_KEY="$API_KEY" \
            --from-literal=BETTER_AUTH_SECRET="$AUTH_SECRET"

        echo -e "${GREEN}  ✓ Secrets created successfully${NC}"
    else
        echo -e "${RED}  ✗ Deployment cancelled. Please create secrets manually and run again.${NC}"
        exit 1
    fi
fi

# Deploy with Helm
echo -e "\n${YELLOW}[7/8] Deploying with Helm...${NC}"
cd infrastructure/helm

if helm list | grep -q "todo-app"; then
    echo -e "${CYAN}  Helm release 'todo-app' already exists. Upgrading...${NC}"
    helm upgrade todo-app ./todo-chart
else
    echo -e "${CYAN}  Installing Helm release 'todo-app'...${NC}"
    helm install todo-app ./todo-chart
fi

echo -e "${GREEN}  ✓ Helm deployment successful${NC}"
cd ../..

# Wait for pods to be ready
echo -e "\n${YELLOW}[8/8] Waiting for pods to be ready...${NC}"
echo -e "${CYAN}  This may take 1-2 minutes...${NC}"

MAX_WAIT=120
WAITED=0
INTERVAL=5

while [ $WAITED -lt $MAX_WAIT ]; do
    PODS=$(kubectl get pods -l app.kubernetes.io/name=todo-chart -o jsonpath='{.items[*].status.phase}')
    if [ -n "$PODS" ] && ! echo "$PODS" | grep -qv "Running"; then
        echo -e "${GREEN}  ✓ All pods are running${NC}"
        break
    fi

    sleep $INTERVAL
    WAITED=$((WAITED + INTERVAL))
    echo -e "${CYAN}  Waiting... ($WAITED/$MAX_WAIT seconds)${NC}"
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${YELLOW}  ⚠ Timeout waiting for pods. Check status with: kubectl get pods${NC}"
fi

# Display deployment status
echo -e "\n${CYAN}========================================"
echo -e "Deployment Status"
echo -e "========================================${NC}"

echo -e "\n${YELLOW}Pods:${NC}"
kubectl get pods

echo -e "\n${YELLOW}Services:${NC}"
kubectl get services

# Get frontend URL
echo -e "\n${CYAN}========================================"
echo -e "Access Your Application"
echo -e "========================================${NC}"

MINIKUBE_IP=$(minikube ip)
echo -e "\n${GREEN}Frontend URL: http://localhost:30080${NC}"
echo -e "${GREEN}Or: http://$MINIKUBE_IP:30080${NC}"

echo -e "\n${GREEN}Backend Service (ClusterIP): backend-service:8000${NC}"
echo -e "${CYAN}To access backend locally:${NC}"
echo -e "${CYAN}  kubectl port-forward service/backend-service 8000:8000${NC}"
echo -e "${CYAN}  Then visit: http://localhost:8000/health${NC}"

echo -e "\n${CYAN}========================================"
echo -e "Useful Commands"
echo -e "========================================${NC}"
echo -e "${YELLOW}View logs:${NC}"
echo -e "${CYAN}  kubectl logs -l app=todo-backend -f${NC}"
echo -e "${CYAN}  kubectl logs -l app=todo-frontend -f${NC}"
echo -e "\n${YELLOW}Open dashboard:${NC}"
echo -e "${CYAN}  minikube dashboard${NC}"
echo -e "\n${YELLOW}Restart deployment:${NC}"
echo -e "${CYAN}  kubectl rollout restart deployment todo-backend${NC}"
echo -e "${CYAN}  kubectl rollout restart deployment todo-frontend${NC}"
echo -e "\n${YELLOW}Uninstall:${NC}"
echo -e "${CYAN}  helm uninstall todo-app${NC}"
echo ""

echo -e "${GREEN}✓ Deployment complete!${NC}"
