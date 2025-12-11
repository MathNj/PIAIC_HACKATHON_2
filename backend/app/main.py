"""
FastAPI application entry point.

Initializes the FastAPI app with:
- CORS middleware for frontend communication
- Database connection
- Health check endpoint
- API routers (to be added as features are implemented)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings, validate_settings
from app.database import init_db
from app.routers import tasks_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.priorities import router as priorities_router
from app.routers.tags import router as tags_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Startup:
        - Validate configuration
        - Initialize database connection
        - Initialize MCP server for Phase III AI Chat Agent

    Shutdown:
        - Clean up resources
    """
    # Startup
    print("Starting TODO API...")
    validate_settings()
    init_db()

    # Initialize MCP server (Phase III) - Disabled for Vercel deployment
    # from mcp.server import initialize_mcp_server
    # initialize_mcp_server()
    # print("MCP server initialized")

    print("Application started successfully")

    yield

    # Shutdown
    print("Shutting down TODO API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-user TODO application API with JWT authentication",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for frontend communication - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (localhost to internet)
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers (including Authorization)
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Application health status

    This endpoint is public and does not require authentication.
    Used by monitoring systems and load balancers.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "0.1.0"
    }


# Router registration
app.include_router(auth_router)  # Auth endpoints (no JWT required)
app.include_router(tasks_router)  # Task endpoints (JWT required)
app.include_router(priorities_router)  # Priority lookup (no JWT required)
app.include_router(tags_router)  # Tag management (no JWT required)
app.include_router(chat_router)  # Chat endpoints (JWT required) - Phase III
