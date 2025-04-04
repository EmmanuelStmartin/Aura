"""Main application module for the Brokerage Integration Service."""

import logging
from typing import Any

from fastapi import FastAPI

from aura_common.config import get_settings
from aura_common.service_template import create_app
from aura_common.utils.logging import setup_logging, get_logger

from app.api.api import api_router
from app.core.alpaca_client import validate_alpaca_credentials

logger = get_logger(__name__)
settings = get_settings()

# Create the FastAPI app
app = create_app(
    service_name="brokerage-integration-service",
    settings=settings,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute actions on application startup."""
    logger.info("Brokerage Integration service starting up")
    
    # Validate Alpaca API credentials
    if not settings.ALPACA_API_KEY or not settings.ALPACA_API_SECRET:
        error_msg = "Missing Alpaca API credentials. ALPACA_API_KEY and ALPACA_API_SECRET must be set."
        logger.critical(error_msg)
        raise ValueError(error_msg)
    
    # Validate that the API credentials work
    try:
        # Check if the credentials work by making a test API call
        await validate_alpaca_credentials(settings)
        logger.info("Alpaca API credentials validated successfully")
    except Exception as e:
        error_msg = f"Failed to validate Alpaca API credentials: {str(e)}"
        logger.critical(error_msg)
        raise ValueError(error_msg)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute actions on application shutdown."""
    logger.info("Brokerage Integration service shutting down")


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