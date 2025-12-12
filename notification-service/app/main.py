"""
Notification Service - Event Consumer

This microservice consumes task events from Dapr pub/sub (Redpanda Cloud)
and processes notifications for task lifecycle events.

Architecture:
- Subscribes to 'task-events' topic via Dapr pub/sub
- Receives events: task_created, task_updated, task_deleted, task_completed
- Logs events to console (production: send emails, push notifications, etc.)
- Demonstrates event-driven architecture with Dapr
"""

from fastapi import FastAPI, Request, status
from datetime import datetime
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Notification Service",
    description="Event consumer for task lifecycle notifications",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which pub/sub topics this service wants to subscribe to.
    Dapr will automatically call the specified route when events arrive.

    Returns:
        List of subscription configurations for Dapr
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/task-events"
        }
    ]

    logger.info(f"Dapr subscription request - returning {len(subscriptions)} subscriptions")
    return subscriptions


@app.post("/task-events")
async def handle_task_events(request: Request):
    """
    Handle incoming task events from Dapr pub/sub.

    Event Types:
    - task_created: New task was created
    - task_updated: Task was modified
    - task_deleted: Task was removed
    - task_completed: Task was marked as complete
    - task_uncompleted: Task was marked as incomplete

    Args:
        request: FastAPI request containing the Dapr CloudEvent

    Returns:
        Success response with status 200
    """
    try:
        # Parse the CloudEvent from Dapr
        event = await request.json()

        # Dapr wraps the message in CloudEvents format
        # The actual event data is in the 'data' field
        event_data = event.get("data", {})
        event_type = event_data.get("event_type", "unknown")

        # Log the full event for debugging
        logger.info(f"📨 Received event: {event_type}")
        logger.debug(f"Full event data: {json.dumps(event_data, indent=2, default=str)}")

        # Route to appropriate handler based on event type
        if event_type == "task_created":
            await handle_task_created(event_data)
        elif event_type == "task_updated":
            await handle_task_updated(event_data)
        elif event_type == "task_deleted":
            await handle_task_deleted(event_data)
        elif event_type == "task_completed":
            await handle_task_completed(event_data)
        elif event_type == "task_uncompleted":
            await handle_task_uncompleted(event_data)
        else:
            logger.warning(f"⚠️ Unknown event type: {event_type}")

        # Return success to Dapr
        return {"status": "success"}

    except Exception as e:
        logger.error(f"❌ Error processing task event: {str(e)}", exc_info=True)
        # Return success anyway to avoid message redelivery
        # In production, you might want to send to dead letter queue
        return {"status": "error", "message": str(e)}


async def handle_task_created(event_data: Dict[str, Any]):
    """Handle task_created events."""
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    title = event_data.get("title")
    priority_id = event_data.get("priority_id")
    due_date = event_data.get("due_date")

    logger.info(f"✅ NEW TASK CREATED")
    logger.info(f"   Task ID: {task_id}")
    logger.info(f"   User ID: {user_id}")
    logger.info(f"   Title: {title}")
    logger.info(f"   Priority: {priority_id}")
    logger.info(f"   Due Date: {due_date}")

    # TODO: Send email notification
    # TODO: Send push notification
    # TODO: Create calendar entry if due date is set


async def handle_task_updated(event_data: Dict[str, Any]):
    """Handle task_updated events."""
    task_id = event_data.get("task_id")
    title = event_data.get("title")
    updated_fields = event_data.get("updated_fields", [])

    logger.info(f"📝 TASK UPDATED")
    logger.info(f"   Task ID: {task_id}")
    logger.info(f"   Title: {title}")
    logger.info(f"   Updated Fields: {', '.join(updated_fields)}")

    # TODO: Send update notification if important fields changed


async def handle_task_deleted(event_data: Dict[str, Any]):
    """Handle task_deleted events."""
    task_id = event_data.get("task_id")
    title = event_data.get("title")
    user_id = event_data.get("user_id")

    logger.info(f"🗑️ TASK DELETED")
    logger.info(f"   Task ID: {task_id}")
    logger.info(f"   Title: {title}")
    logger.info(f"   User ID: {user_id}")

    # TODO: Send deletion confirmation
    # TODO: Remove from calendar if it was scheduled


async def handle_task_completed(event_data: Dict[str, Any]):
    """Handle task_completed events."""
    task_id = event_data.get("task_id")
    title = event_data.get("title")
    user_id = event_data.get("user_id")
    completed_at = event_data.get("completed_at")

    logger.info(f"🎉 TASK COMPLETED")
    logger.info(f"   Task ID: {task_id}")
    logger.info(f"   Title: {title}")
    logger.info(f"   User ID: {user_id}")
    logger.info(f"   Completed At: {completed_at}")

    # TODO: Send congratulations notification
    # TODO: Update productivity metrics
    # TODO: Trigger streak/achievement logic


async def handle_task_uncompleted(event_data: Dict[str, Any]):
    """Handle task_uncompleted events."""
    task_id = event_data.get("task_id")
    title = event_data.get("title")

    logger.info(f"↩️ TASK MARKED INCOMPLETE")
    logger.info(f"   Task ID: {task_id}")
    logger.info(f"   Title: {title}")


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("🚀 Notification Service starting...")
    logger.info("📡 Ready to consume events from kafka-pubsub/task-events")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information."""
    logger.info("🛑 Notification Service shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
