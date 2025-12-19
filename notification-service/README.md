# Notification Service

Event-driven microservice that consumes task lifecycle events from Redpanda Cloud via Dapr pub/sub.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────────┐      ┌────────────────────┐
│   Backend   │─────▶│  Dapr Sidecar│─────▶│  Redpanda Cloud  │─────▶│ Notification       │
│   Service   │      │  (kafka-pubsub)      │  (task-events)   │      │ Service + Dapr     │
└─────────────┘      └──────────────┘      └──────────────────┘      └────────────────────┘
   Publishes           Pub/Sub Component      Event Stream               Subscribes & Consumes
   Events              (SASL/TLS)             (3 partitions)             via Dapr
```

## Features

- **Event Subscription**: Automatically subscribes to `task-events` topic via Dapr
- **Event Types Supported**:
  - `task_created` - New task created
  - `task_updated` - Task modified
  - `task_deleted` - Task removed
  - `task_completed` - Task marked as complete
  - `task_uncompleted` - Task marked as incomplete
- **Graceful Error Handling**: Logs errors but doesn't fail (fire-and-forget pattern)
- **Health Checks**: Kubernetes-ready liveness/readiness probes
- **CloudEvents**: Handles Dapr CloudEvent format automatically

## Endpoints

### GET /health
Health check endpoint for Kubernetes probes.

**Response**:
```json
{
  "status": "healthy",
  "service": "notification-service",
  "timestamp": "2025-12-12T08:00:00.000000"
}
```

### GET /dapr/subscribe
Dapr subscription endpoint - tells Dapr which topics to subscribe to.

**Response**:
```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/task-events"
  }
]
```

### POST /task-events
Event handler endpoint - Dapr invokes this when events arrive.

**Request Body** (CloudEvent format from Dapr):
```json
{
  "id": "event-id",
  "source": "backend-service",
  "specversion": "1.0",
  "type": "com.dapr.event.sent",
  "data": {
    "event_type": "task_created",
    "task_id": 123,
    "user_id": "uuid",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority_id": 1,
    "due_date": "2025-12-15T00:00:00",
    "timestamp": "2025-12-12T08:00:00.000000"
  }
}
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Test health check
curl http://localhost:8001/health

# Test Dapr subscription
curl http://localhost:8001/dapr/subscribe
```

## Building Docker Image

```bash
# Build image
docker build -t registry.digitalocean.com/todo-chatbot-reg/notification-service:latest .

# Push to registry
doctl registry login
docker push registry.digitalocean.com/todo-chatbot-reg/notification-service:latest
```

## Deploying to DOKS

```bash
# Deploy with Dapr sidecar
kubectl apply -f infrastructure/kubernetes/notification-service-deployment.yaml

# Verify deployment
kubectl get pods -l tier=notification -n default

# Check logs
kubectl logs -l tier=notification -n default -c notification-service --tail=50

# Check Dapr sidecar logs
kubectl logs -l tier=notification -n default -c daprd --tail=50
```

## Environment Variables

None required - the service uses Dapr for all external communication.

## Dependencies

- **FastAPI**: Web framework for API endpoints
- **Uvicorn**: ASGI server
- **httpx**: HTTP client (for future integrations)
- **Pydantic**: Data validation

## Event Processing Flow

1. Backend creates/updates/deletes a task
2. Backend publishes event to Dapr sidecar
3. Dapr sidecar sends event to Redpanda Cloud
4. Dapr on notification-service receives event from Redpanda
5. Dapr invokes POST /task-events with CloudEvent
6. Notification service processes event and logs it
7. (Future) Send email, push notification, update metrics, etc.

## Current Implementation

**Production-Ready**:
- ✅ Event subscription via Dapr
- ✅ CloudEvent handling
- ✅ Event type routing
- ✅ Structured logging
- ✅ Health checks
- ✅ Error handling

**TODO (Future Enhancements)**:
- [ ] SendGrid email integration
- [ ] Push notification support
- [ ] Database persistence for notification history
- [ ] Retry logic with exponential backoff
- [ ] Dead letter queue for failed events
- [ ] Metrics and monitoring

## Logs

The service logs all events it receives:

```
2025-12-12 08:00:00 - __main__ - INFO - 🚀 Notification Service starting...
2025-12-12 08:00:00 - __main__ - INFO - 📡 Ready to consume events from kafka-pubsub/task-events
2025-12-12 08:01:00 - __main__ - INFO - 📨 Received event: task_created
2025-12-12 08:01:00 - __main__ - INFO - ✅ NEW TASK CREATED
2025-12-12 08:01:00 - __main__ - INFO -    Task ID: 123
2025-12-12 08:01:00 - __main__ - INFO -    User ID: uuid
2025-12-12 08:01:00 - __main__ - INFO -    Title: Buy groceries
```

## Troubleshooting

### Service not receiving events

1. Check Dapr sidecar is running: `kubectl get pods -l tier=notification`
2. Verify Dapr components loaded: `kubectl logs <pod> -c daprd | grep "Component loaded"`
3. Check Dapr subscription registered: `kubectl logs <pod> -c daprd | grep "subscribe"`
4. Verify backend is publishing events: `kubectl logs <backend-pod> -c daprd | grep "publish"`

### Events arriving but not processing

1. Check service logs: `kubectl logs <pod> -c notification-service`
2. Verify CloudEvent format: Look for "data" field in logs
3. Check event_type field matches expected values

## Architecture Benefits

- **Decoupled**: Backend doesn't know notification service exists
- **Resilient**: If notification service is down, backend continues working
- **Scalable**: Can add more replicas to handle high event volume
- **Extensible**: Easy to add more event types and handlers
- **Observable**: All events logged for debugging and auditing
