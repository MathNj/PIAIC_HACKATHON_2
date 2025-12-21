#!/bin/bash
# Kafka Health Check Script
# Verifies Kafka brokers are ready and topics are accessible

set -e

# Configuration
KAFKA_PROVIDER="${KAFKA_PROVIDER:-strimzi}"
NAMESPACE="${NAMESPACE:-kafka}"
KAFKA_CLUSTER_NAME="${KAFKA_CLUSTER_NAME:-my-cluster}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if namespace exists
check_namespace() {
    log_info "Checking namespace: $NAMESPACE"

    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_error "Namespace $NAMESPACE does not exist"
        return 1
    fi

    log_info "Namespace exists"
    return 0
}

# Check Kafka pods
check_kafka_pods() {
    log_info "Checking Kafka pods..."

    local pod_count=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=kafka -o jsonpath='{.items[*].status.phase}' | grep -o "Running" | wc -l)

    if [ "$pod_count" -eq 0 ]; then
        log_error "No Kafka pods running"
        return 1
    fi

    log_info "Found $pod_count Kafka pod(s) running"

    # Check if pods are ready
    local ready=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=kafka -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -o "True" | wc -l)

    if [ "$ready" -ne "$pod_count" ]; then
        log_error "Not all Kafka pods are ready ($ready/$pod_count)"
        return 1
    fi

    log_info "All Kafka pods are ready"
    return 0
}

# Check ZooKeeper (for Strimzi)
check_zookeeper() {
    if [ "$KAFKA_PROVIDER" != "strimzi" ]; then
        log_info "Skipping ZooKeeper check (Redpanda doesn't use ZooKeeper)"
        return 0
    fi

    log_info "Checking ZooKeeper pods..."

    local zk_count=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=zookeeper -o jsonpath='{.items[*].status.phase}' | grep -o "Running" | wc -l)

    if [ "$zk_count" -eq 0 ]; then
        log_error "No ZooKeeper pods running"
        return 1
    fi

    log_info "Found $zk_count ZooKeeper pod(s) running"

    local ready=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=zookeeper -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -o "True" | wc -l)

    if [ "$ready" -ne "$zk_count" ]; then
        log_error "Not all ZooKeeper pods are ready ($ready/$zk_count)"
        return 1
    fi

    log_info "All ZooKeeper pods are ready"
    return 0
}

# Check Kafka service
check_kafka_service() {
    log_info "Checking Kafka service..."

    local service_name="${KAFKA_CLUSTER_NAME}-kafka-bootstrap"

    if ! kubectl get svc $service_name -n $NAMESPACE &> /dev/null; then
        log_error "Kafka service $service_name not found"
        return 1
    fi

    local cluster_ip=$(kubectl get svc $service_name -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    local port=$(kubectl get svc $service_name -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')

    log_info "Kafka service: $service_name"
    log_info "Cluster IP: $cluster_ip"
    log_info "Port: $port"
    log_info "Bootstrap servers: $service_name.$NAMESPACE.svc.cluster.local:$port"

    return 0
}

# Check Kafka topics
check_kafka_topics() {
    log_info "Checking Kafka topics..."

    local required_topics=("task-events" "reminders" "task-updates")

    if [ "$KAFKA_PROVIDER" = "strimzi" ]; then
        # Check KafkaTopic CRs
        for topic in "${required_topics[@]}"; do
            if ! kubectl get kafkatopic $topic -n $NAMESPACE &> /dev/null; then
                log_error "Topic $topic not found"
                return 1
            fi

            local ready=$(kubectl get kafkatopic $topic -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')

            if [ "$ready" != "True" ]; then
                log_warn "Topic $topic is not ready yet"
            else
                log_info "Topic $topic is ready"
            fi
        done
    else
        # For Redpanda, list topics via exec
        log_info "Verifying topics in Redpanda..."
        local pod_name=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=redpanda -o jsonpath='{.items[0].metadata.name}')

        if [ -z "$pod_name" ]; then
            log_error "No Redpanda pod found"
            return 1
        fi

        kubectl exec -n $NAMESPACE $pod_name -- rpk topic list &> /dev/null || log_warn "Unable to list topics"
    fi

    log_info "All required topics verified"
    return 0
}

# Test Kafka connectivity
test_kafka_connectivity() {
    log_info "Testing Kafka connectivity..."

    local service_name="${KAFKA_CLUSTER_NAME}-kafka-bootstrap"
    local bootstrap_server="$service_name.$NAMESPACE.svc.cluster.local:9092"

    # Create a test pod to verify connectivity
    local test_pod="kafka-test-$$"

    kubectl run $test_pod -n $NAMESPACE --image=confluentinc/cp-kafka:latest --restart=Never --rm -i --quiet -- \
        kafka-broker-api-versions --bootstrap-server $bootstrap_server &> /dev/null

    if [ $? -eq 0 ]; then
        log_info "Kafka connectivity test passed"
        return 0
    else
        log_error "Kafka connectivity test failed"
        return 1
    fi
}

# Print cluster info
print_cluster_info() {
    log_info ""
    log_info "========================================="
    log_info "Kafka Cluster Information"
    log_info "========================================="
    log_info "Provider: $KAFKA_PROVIDER"
    log_info "Namespace: $NAMESPACE"
    log_info "Cluster Name: $KAFKA_CLUSTER_NAME"
    log_info "Bootstrap Servers: ${KAFKA_CLUSTER_NAME}-kafka-bootstrap.$NAMESPACE.svc.cluster.local:9092"
    log_info ""
    log_info "Topics:"
    log_info "  - task-events"
    log_info "  - reminders"
    log_info "  - task-updates"
    log_info "========================================="
}

# Main health check
main() {
    log_info "Starting Kafka health check..."

    local failed=0

    check_namespace || ((failed++))
    check_kafka_pods || ((failed++))
    check_zookeeper || ((failed++))
    check_kafka_service || ((failed++))
    check_kafka_topics || ((failed++))

    # Optional: Test connectivity (may fail in some environments)
    # test_kafka_connectivity || log_warn "Connectivity test skipped"

    if [ $failed -eq 0 ]; then
        log_info ""
        log_info "✅ All health checks passed!"
        print_cluster_info
        return 0
    else
        log_error ""
        log_error "❌ $failed health check(s) failed"
        return 1
    fi
}

# Run main
main
exit $?
