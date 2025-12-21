#!/bin/bash
# Kafka Infrastructure Deployment Script
# Deploys Kafka cluster (Strimzi or Redpanda) to Kubernetes

set -e

# Configuration
KAFKA_PROVIDER="${KAFKA_PROVIDER:-strimzi}"  # strimzi or redpanda
NAMESPACE="${NAMESPACE:-kafka}"
KAFKA_CLUSTER_NAME="${KAFKA_CLUSTER_NAME:-my-cluster}"
STORAGE_TYPE="${STORAGE_TYPE:-ephemeral}"  # ephemeral or persistent

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster."
        exit 1
    fi

    log_info "Prerequisites satisfied"
}

# Create namespace
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"

    if kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warn "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace $NAMESPACE
        log_info "Namespace created"
    fi
}

# Deploy Strimzi
deploy_strimzi() {
    log_info "Deploying Strimzi Operator..."

    # Install Strimzi operator
    kubectl create -f assets/strimzi/strimzi-operator.yaml -n $NAMESPACE || log_warn "Strimzi operator may already exist"

    # Wait for operator to be ready
    log_info "Waiting for Strimzi operator to be ready..."
    kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n $NAMESPACE --timeout=300s

    # Deploy Kafka cluster
    log_info "Deploying Kafka cluster..."
    kubectl apply -f assets/strimzi/kafka-cluster-${STORAGE_TYPE}.yaml -n $NAMESPACE

    # Wait for Kafka cluster to be ready
    log_info "Waiting for Kafka cluster to be ready..."
    kubectl wait kafka/$KAFKA_CLUSTER_NAME --for=condition=Ready --timeout=600s -n $NAMESPACE

    log_info "Strimzi Kafka cluster deployed successfully"
}

# Deploy Redpanda
deploy_redpanda() {
    log_info "Deploying Redpanda Operator..."

    # Install Redpanda operator
    kubectl create -f assets/redpanda/redpanda-operator.yaml -n $NAMESPACE || log_warn "Redpanda operator may already exist"

    # Wait for operator to be ready
    log_info "Waiting for Redpanda operator to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda-operator -n $NAMESPACE --timeout=300s

    # Deploy Redpanda cluster
    log_info "Deploying Redpanda cluster..."
    kubectl apply -f assets/redpanda/redpanda-cluster-${STORAGE_TYPE}.yaml -n $NAMESPACE

    # Wait for Redpanda cluster to be ready
    log_info "Waiting for Redpanda cluster to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n $NAMESPACE --timeout=600s

    log_info "Redpanda cluster deployed successfully"
}

# Create topics
create_topics() {
    log_info "Creating Kafka topics..."

    if [ "$KAFKA_PROVIDER" = "strimzi" ]; then
        # Strimzi uses KafkaTopic CRs
        kubectl apply -f assets/strimzi/kafka-topics.yaml -n $NAMESPACE

        # Wait for topics to be ready
        for topic in task-events reminders task-updates; do
            log_info "Waiting for topic $topic to be ready..."
            kubectl wait kafkatopic/$topic --for=condition=Ready --timeout=120s -n $NAMESPACE || log_warn "Topic $topic may not be ready"
        done
    else
        # Redpanda uses native topic creation
        kubectl apply -f assets/redpanda/kafka-topics.yaml -n $NAMESPACE
    fi

    log_info "Kafka topics created successfully"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Run health check
    bash scripts/health_check.sh

    if [ $? -eq 0 ]; then
        log_info "Kafka infrastructure is healthy!"
    else
        log_error "Kafka infrastructure health check failed"
        exit 1
    fi
}

# Main deployment flow
main() {
    log_info "Starting Kafka infrastructure deployment..."
    log_info "Provider: $KAFKA_PROVIDER"
    log_info "Namespace: $NAMESPACE"
    log_info "Cluster: $KAFKA_CLUSTER_NAME"
    log_info "Storage: $STORAGE_TYPE"

    check_prerequisites
    create_namespace

    if [ "$KAFKA_PROVIDER" = "strimzi" ]; then
        deploy_strimzi
    elif [ "$KAFKA_PROVIDER" = "redpanda" ]; then
        deploy_redpanda
    else
        log_error "Invalid KAFKA_PROVIDER: $KAFKA_PROVIDER (must be 'strimzi' or 'redpanda')"
        exit 1
    fi

    create_topics
    verify_deployment

    log_info "Kafka infrastructure deployment complete!"
    log_info ""
    log_info "Bootstrap servers: $KAFKA_CLUSTER_NAME-kafka-bootstrap.$NAMESPACE.svc.cluster.local:9092"
    log_info "Topics created: task-events, reminders, task-updates"
}

# Run main function
main
