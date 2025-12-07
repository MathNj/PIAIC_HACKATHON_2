"""
API route handlers.

FastAPI routers for different endpoint groups.
"""

from app.routers.tasks import router as tasks_router

__all__ = ["tasks_router"]
