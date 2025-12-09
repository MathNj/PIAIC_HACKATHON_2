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

    # Initialize MCP server (Phase III)
    from mcp.server import initialize_mcp_server
    initialize_mcp_server()
    print("MCP server initialized")

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

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,  # Primary frontend URL from env
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Local development (alternate port)
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # All Vercel deployments (production & preview)
    allow_credentials=True,
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
app.include_router(chat_router)  # Chat endpoints (JWT required) - Phase III
