# Minikube Deployment Script for Todo Chatbot
# PowerShell script to automate Kubernetes deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Todo Chatbot - Minikube Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/8] Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Minikube is installed
Write-Host "`n[2/8] Checking Minikube..." -ForegroundColor Yellow
try {
    $minikubeVersion = minikube version
    Write-Host "✓ Minikube is installed: $($minikubeVersion -split "`n" | Select-Object -First 1)" -ForegroundColor Green
} catch {
    Write-Host "✗ Minikube is not installed. Please install from https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Red
    exit 1
}

# Start Minikube if not running
Write-Host "`n[3/8] Starting Minikube..." -ForegroundColor Yellow
$minikubeStatus = minikube status 2>&1
if ($minikubeStatus -match "Running") {
    Write-Host "✓ Minikube is already running" -ForegroundColor Green
} else {
    Write-Host "Starting Minikube with Docker driver (4 CPUs, 4GB RAM)..." -ForegroundColor Cyan
    minikube start --driver=docker --cpus=4 --memory=4096
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Minikube started successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to start Minikube" -ForegroundColor Red
        exit 1
    }
}

# Configure Docker environment
Write-Host "`n[4/8] Configuring Docker environment..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
Write-Host "✓ Docker environment configured to use Minikube's Docker daemon" -ForegroundColor Green

# Build Docker images
Write-Host "`n[5/8] Building Docker images..." -ForegroundColor Yellow

Write-Host "  Building backend image..." -ForegroundColor Cyan
Set-Location backend
docker build -t todo-backend:local . -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Backend image built: todo-backend:local" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to build backend image" -ForegroundColor Red
    exit 1
}

Write-Host "  Building frontend image..." -ForegroundColor Cyan
Set-Location ../frontend
docker build -t todo-frontend:local . -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Frontend image built: todo-frontend:local" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to build frontend image" -ForegroundColor Red
    exit 1
}

Set-Location ..

# Check if secrets exist
Write-Host "`n[6/8] Checking Kubernetes secrets..." -ForegroundColor Yellow
$secretExists = kubectl get secret todo-secrets 2>&1
if ($secretExists -match "NotFound") {
    Write-Host "  Secrets not found. Please create them manually:" -ForegroundColor Yellow
    Write-Host "  kubectl create secret generic todo-secrets \" -ForegroundColor Cyan
    Write-Host "    --from-literal=DATABASE_URL='your-database-url' \" -ForegroundColor Cyan
    Write-Host "    --from-literal=GEMINI_API_KEY='your-api-key' \" -ForegroundColor Cyan
    Write-Host "    --from-literal=BETTER_AUTH_SECRET='your-secret'" -ForegroundColor Cyan
    Write-Host ""
    $createSecret = Read-Host "Do you want to create secrets now? (y/n)"
    if ($createSecret -eq 'y') {
        $dbUrl = Read-Host "Enter DATABASE_URL"
        $apiKey = Read-Host "Enter GEMINI_API_KEY"
        $authSecret = Read-Host "Enter BETTER_AUTH_SECRET"

        kubectl create secret generic todo-secrets `
            --from-literal=DATABASE_URL="$dbUrl" `
            --from-literal=GEMINI_API_KEY="$apiKey" `
            --from-literal=BETTER_AUTH_SECRET="$authSecret"

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Secrets created successfully" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Failed to create secrets" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ✗ Deployment cancelled. Please create secrets manually and run again." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✓ Secrets already exist: todo-secrets" -ForegroundColor Green
}

# Deploy with Helm
Write-Host "`n[7/8] Deploying with Helm..." -ForegroundColor Yellow
Set-Location infrastructure/helm

$helmRelease = helm list | Select-String "todo-app"
if ($helmRelease) {
    Write-Host "  Helm release 'todo-app' already exists. Upgrading..." -ForegroundColor Cyan
    helm upgrade todo-app ./todo-chart
} else {
    Write-Host "  Installing Helm release 'todo-app'..." -ForegroundColor Cyan
    helm install todo-app ./todo-chart
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Helm deployment successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ Helm deployment failed" -ForegroundColor Red
    exit 1
}

Set-Location ../..

# Wait for pods to be ready
Write-Host "`n[8/8] Waiting for pods to be ready..." -ForegroundColor Yellow
Write-Host "  This may take 1-2 minutes..." -ForegroundColor Cyan

$maxWait = 120  # 2 minutes
$waited = 0
$interval = 5

while ($waited -lt $maxWait) {
    $pods = kubectl get pods -l app.kubernetes.io/name=todo-chart -o jsonpath='{.items[*].status.phase}'
    $allRunning = ($pods -split ' ' | Where-Object { $_ -ne 'Running' }).Count -eq 0

    if ($allRunning -and $pods) {
        Write-Host "  ✓ All pods are running" -ForegroundColor Green
        break
    }

    Start-Sleep -Seconds $interval
    $waited += $interval
    Write-Host "  Waiting... ($waited/$maxWait seconds)" -ForegroundColor Cyan
}

if ($waited -ge $maxWait) {
    Write-Host "  ⚠ Timeout waiting for pods. Check status with: kubectl get pods" -ForegroundColor Yellow
}

# Display deployment status
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nPods:" -ForegroundColor Yellow
kubectl get pods

Write-Host "`nServices:" -ForegroundColor Yellow
kubectl get services

# Get frontend URL
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Access Your Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$minikubeIp = minikube ip
Write-Host "`nFrontend URL: http://localhost:30080" -ForegroundColor Green
Write-Host "Or: http://$minikubeIp:30080" -ForegroundColor Green

Write-Host "`nBackend Service (ClusterIP): backend-service:8000" -ForegroundColor Green
Write-Host "To access backend locally:" -ForegroundColor Cyan
Write-Host "  kubectl port-forward service/backend-service 8000:8000" -ForegroundColor Cyan
Write-Host "  Then visit: http://localhost:8000/health" -ForegroundColor Cyan

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Useful Commands" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  kubectl logs -l app=todo-backend -f" -ForegroundColor Cyan
Write-Host "  kubectl logs -l app=todo-frontend -f" -ForegroundColor Cyan
Write-Host "`nOpen dashboard:" -ForegroundColor Yellow
Write-Host "  minikube dashboard" -ForegroundColor Cyan
Write-Host "`nRestart deployment:" -ForegroundColor Yellow
Write-Host "  kubectl rollout restart deployment todo-backend" -ForegroundColor Cyan
Write-Host "  kubectl rollout restart deployment todo-frontend" -ForegroundColor Cyan
Write-Host "`nUninstall:" -ForegroundColor Yellow
Write-Host "  helm uninstall todo-app" -ForegroundColor Cyan
Write-Host ""

Write-Host "✓ Deployment complete!" -ForegroundColor Green
