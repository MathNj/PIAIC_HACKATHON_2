"""
Vercel serverless entrypoint for FastAPI.
"""

from app.main import app

# Export for Vercel (ASGI application)
# Note: Only export 'app', not 'handler' for FastAPI/ASGI apps
