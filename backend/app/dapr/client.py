"""
Dapr client wrapper for pub/sub and state management.

Provides a simple interface for publishing events to Dapr pub/sub
and managing state through Dapr state store.
"""

import httpx
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DaprClient:
    """
    Dapr HTTP client for pub/sub and state management operations.

    This client communicates with the Dapr sidecar via HTTP to:
    - Publish events to pub/sub topics
    - Save and retrieve state from state stores
    - Invoke service-to-service calls

    Attributes:
        dapr_http_port: Port where Dapr sidecar listens (default: 3500)
        base_url: Base URL for Dapr HTTP API
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize Dapr client.

        Args:
            dapr_http_port: Port number for Dapr sidecar HTTP API (default: 3500)
        """
        self.dapr_http_port = dapr_http_port
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.client = httpx.Client(timeout=30.0)
        logger.info(f"Dapr client initialized with base URL: {self.base_url}")

    def publish_event(
        self,
        pubsub_name: str,
        topic_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to a Dapr pub/sub topic.

        Args:
            pubsub_name: Name of the pub/sub component (e.g., "kafka-pubsub")
            topic_name: Name of the topic to publish to (e.g., "task-events")
            data: Event data payload (will be JSON serialized)
            metadata: Optional metadata for the event

        Returns:
            bool: True if publish succeeded, False otherwise

        Example:
            >>> client = DaprClient()
            >>> client.publish_event(
            ...     pubsub_name="kafka-pubsub",
            ...     topic_name="task-events",
            ...     data={"event_type": "task_created", "task_id": 123}
            ... )
            True
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic_name}"

        headers = {
            "Content-Type": "application/json"
        }

        # Add metadata to headers if provided
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value

        try:
            # Add timestamp to data
            event_data = {
                **data,
                "timestamp": datetime.utcnow().isoformat()
            }

            response = self.client.post(
                url,
                json=event_data,
                headers=headers
            )

            if response.status_code == 204:
                logger.info(
                    f"Successfully published event to {pubsub_name}/{topic_name}: "
                    f"{json.dumps(event_data, default=str)}"
                )
                return True
            else:
                logger.error(
                    f"Failed to publish event to {pubsub_name}/{topic_name}. "
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error publishing event to {pubsub_name}/{topic_name}: {str(e)}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error publishing event to {pubsub_name}/{topic_name}: {str(e)}"
            )
            return False

    def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Save state to a Dapr state store.

        Args:
            store_name: Name of the state store component (e.g., "statestore")
            key: State key
            value: State value (will be JSON serialized)
            metadata: Optional metadata for the state

        Returns:
            bool: True if save succeeded, False otherwise

        Example:
            >>> client = DaprClient()
            >>> client.save_state(
            ...     store_name="statestore",
            ...     key="reminder_sent_123",
            ...     value={"sent_at": "2025-12-11T12:00:00Z"}
            ... )
            True
        """
        url = f"{self.base_url}/v1.0/state/{store_name}"

        state_data = [
            {
                "key": key,
                "value": value
            }
        ]

        if metadata:
            state_data[0]["metadata"] = metadata

        try:
            response = self.client.post(url, json=state_data)

            if response.status_code == 204:
                logger.info(f"Successfully saved state to {store_name}: key={key}")
                return True
            else:
                logger.error(
                    f"Failed to save state to {store_name}. "
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

        except httpx.HTTPError as e:
            logger.error(f"HTTP error saving state to {store_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving state to {store_name}: {str(e)}")
            return False

    def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """
        Retrieve state from a Dapr state store.

        Args:
            store_name: Name of the state store component
            key: State key

        Returns:
            State value if found, None otherwise

        Example:
            >>> client = DaprClient()
            >>> value = client.get_state(store_name="statestore", key="reminder_sent_123")
            >>> print(value)
            {"sent_at": "2025-12-11T12:00:00Z"}
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = self.client.get(url)

            if response.status_code == 200:
                if response.content:
                    return response.json()
                else:
                    logger.info(f"State key {key} not found in {store_name}")
                    return None
            else:
                logger.error(
                    f"Failed to get state from {store_name}. "
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting state from {store_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting state from {store_name}: {str(e)}")
            return None

    def delete_state(
        self,
        store_name: str,
        key: str
    ) -> bool:
        """
        Delete state from a Dapr state store.

        Args:
            store_name: Name of the state store component
            key: State key to delete

        Returns:
            bool: True if delete succeeded, False otherwise

        Example:
            >>> client = DaprClient()
            >>> client.delete_state(store_name="statestore", key="reminder_sent_123")
            True
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = self.client.delete(url)

            if response.status_code == 204:
                logger.info(f"Successfully deleted state from {store_name}: key={key}")
                return True
            else:
                logger.error(
                    f"Failed to delete state from {store_name}. "
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False

        except httpx.HTTPError as e:
            logger.error(f"HTTP error deleting state from {store_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting state from {store_name}: {str(e)}")
            return False

    def close(self):
        """Close the HTTP client connection."""
        self.client.close()
        logger.info("Dapr client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes client."""
        self.close()


# Singleton instance for app-wide use
dapr_client = DaprClient()
