"""
Vercel serverless entrypoint for FastAPI.
"""

from app.main import app as fastapi_app

# Expose the FastAPI app for Vercel
app = fastapi_app
handler = fastapi_app
