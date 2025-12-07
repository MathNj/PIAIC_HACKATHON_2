"""
Vercel serverless function entry point for FastAPI backend.

This adapts the FastAPI application to work with Vercel's serverless infrastructure.
Note: SQLite database will be in-memory on Vercel. For production, use Neon PostgreSQL.
"""

from app.main import app

# Vercel requires the app to be exposed as 'app' or 'handler'
# The app instance is imported from app.main which initializes the FastAPI app
app = app
