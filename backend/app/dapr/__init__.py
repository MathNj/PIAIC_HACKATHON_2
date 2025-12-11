"""
Dapr integration module.

Provides Dapr client for pub/sub and state management operations.
"""

from app.dapr.client import DaprClient

__all__ = ["DaprClient"]
