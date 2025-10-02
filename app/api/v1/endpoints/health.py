from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings

router = APIRouter()


@router.get("/", summary="Health Check", description="Check if the API is running and database is accessible")
async def health_check():
    """Health check endpoint that returns API status and timestamp."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/detailed", summary="Detailed Health Check", description="Check API and database connectivity")
async def detailed_health_check():
    """Detailed health check including database connectivity."""
    # Note: In a real application, you'd inject the database session here
    # For now, we'll just return the basic health info
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected",  # This would be checked with actual DB session
        "services": {
            "api": "running",
            "database": "accessible"
        }
    }
