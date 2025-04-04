"""Main application module for the auth service."""

import logging
from typing import Any

from fastapi import FastAPI

from aura_common.config import get_settings
from aura_common.service_template import create_app
from aura_common.utils.logging import setup_logging, get_logger

from app.api.api import api_router
from app.db.base_class import Base
from app.db.session import engine

logger = get_logger(__name__)
settings = get_settings()

# Create the FastAPI app
app = create_app(
    service_name="auth-service",
    settings=settings,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Create database tables
# In production, you would use migrations (e.g., Alembic)
Base.metadata.create_all(bind=engine)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute actions on application startup."""
    logger.info("Auth service starting up")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute actions on application shutdown."""
    logger.info("Auth service shutting down")


if __name__ == "__main__":
    import uvicorn
    
    # Setup logging
    setup_logging(level=logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
    ) 