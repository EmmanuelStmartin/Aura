"""Main application module for the API Gateway Service."""

import logging
from typing import Any

from fastapi import FastAPI

from aura_common.config import get_settings
from aura_common.service_template import create_app
from aura_common.utils.logging import setup_logging, get_logger

from app.api.api import api_router
from app.middlewares.auth import AuthMiddleware

logger = get_logger(__name__)
settings = get_settings()

# Create the FastAPI app
app = create_app(
    service_name="api-gateway-service",
    settings=settings,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute actions on application startup."""
    logger.info("API Gateway service starting up")
    
    # Validate connection to dependent services
    # This is a placeholder - in a real implementation you would
    # ping each service to ensure it's available


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute actions on application shutdown."""
    logger.info("API Gateway service shutting down")


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