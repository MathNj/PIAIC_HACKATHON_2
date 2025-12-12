# Redpanda Cloud Setup with Dapr

## Summary
This document describes the successful integration of Dapr with Redpanda Cloud for Phase 5 event-driven architecture.

## Issue Encountered
Dapr kafka-pubsub component failed to connect to Redpanda Cloud with error:
```
kafka: client has run out of available brokers to talk to
init timeout for component kafka-pubsub (pubsub.kafka/v1)
```

## Root Cause
The `saslMechanism` metadata field was set to `"SCRAM-SHA-256"` instead of the correct Dapr value `"SHA-256"`.

## Solution
According to [Dapr's Kafka component documentation](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/), the `saslMechanism` field for SCRAM-SHA-256 authentication should use:

**Incorrect (causes connection failure):**
```yaml
- name: saslMechanism
  value: "SCRAM-SHA-256"
```

**Correct:**
```yaml
- name: saslMechanism
  value: "SHA-256"
```

Similarly, for SCRAM-SHA-512, use `"SHA-512"` not `"SCRAM-SHA-512"`.

## Configuration
See `infrastructure/dapr/components/kafka-pubsub-prod.yaml` for the complete working configuration.

### Key Settings
- **Bootstrap Server**: `d4thqjgeuu3l6h0sd130.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
- **Authentication**: SASL/SCRAM-SHA-256 via Kubernetes secrets
- **TLS**: Enabled (`enableTLS: "true"`)
- **Protocol Version**: Kafka 3.0.0 (Redpanda compatible)
- **Producer Features**: Idempotence enabled, gzip compression, 3 retries
- **Consumer Features**: Retry enabled, auto-offset-reset to earliest

## Verification Steps

### 1. Check Components Loaded
```bash
kubectl logs <backend-pod> -c daprd -n default | grep "Component loaded"
```
Expected:
```
Component loaded: kafka-pubsub (pubsub.kafka/v1)
Component loaded: statestore (state.redis/v1)
```

### 2. Test Event Publishing
```bash
kubectl exec <backend-pod> -c backend -n default -- python -c "
import http.client, json
conn = http.client.HTTPConnection('localhost', 3500)
headers = {'Content-Type': 'application/json'}
data = json.dumps({'test': 'event', 'message': 'Hello Redpanda'})
conn.request('POST', '/v1.0/publish/kafka-pubsub/task-events', data, headers)
response = conn.getresponse()
print(f'Status: {response.status}')
conn.close()
"
```
Expected: `Status: 204`

### 3. Test State Store
```bash
kubectl exec <backend-pod> -c backend -n default -- python -c "
import http.client, json
conn = http.client.HTTPConnection('localhost', 3500)
headers = {'Content-Type': 'application/json'}
data = json.dumps([{'key': 'test', 'value': 'Hello Valkey'}])
conn.request('POST', '/v1.0/state/statestore', data, headers)
response = conn.getresponse()
print(f'Save: {response.status}')
conn.close()
"
```
Expected: `Save: 204`

## Troubleshooting

### Network Connectivity Test
```bash
# DNS Resolution
kubectl exec <backend-pod> -c backend -n default -- python -c "
import socket
print(socket.gethostbyname('<redpanda-broker>'))
"

# TCP Connectivity
kubectl exec <backend-pod> -c backend -n default -- python -c "
import socket
s = socket.socket()
s.settimeout(5)
result = s.connect_ex(('<redpanda-broker>', 9092))
print('SUCCESS' if result == 0 else f'FAILED: {result}')
s.close()
"

# TLS Handshake
kubectl exec <backend-pod> -c backend -n default -- python -c "
import ssl, socket
context = ssl.create_default_context()
s = socket.socket()
s.settimeout(10)
tls_s = context.wrap_socket(s, server_hostname='<redpanda-broker>')
result = tls_s.connect_ex(('<redpanda-broker>', 9092))
print('TLS SUCCESS' if result == 0 else f'TLS FAILED: {result}')
tls_s.close()
"
```

### Check Dapr Logs for Errors
```bash
kubectl logs <backend-pod> -c daprd -n default --tail=100 | grep -i error
```

### Verify Secrets
```bash
kubectl get secret redpanda-credentials -n default -o jsonpath='{.data.brokers}' | base64 -d
kubectl get secret redpanda-credentials -n default -o jsonpath='{.data.sasl-username}' | base64 -d
```

## Resources
- [Dapr Kafka Component Docs](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Redpanda Cloud Authentication Guide](https://www.redpanda.com/guides/kafka-cloud-kafka-authentication)
- [Redpanda Kafka Compatibility](https://docs.redpanda.com/redpanda-cloud/develop/kafka-clients/)

## Status
✅ **Working** - Both Dapr components (kafka-pubsub and statestore) are operational and successfully integrated with cloud services.

Last Updated: 2025-12-12
