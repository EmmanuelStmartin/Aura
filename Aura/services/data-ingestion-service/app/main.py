"""Main application module for the data ingestion service."""

import logging
from typing import Any

from fastapi import FastAPI

from aura_common.config import get_settings
from aura_common.service_template import create_app
from aura_common.utils.logging import setup_logging, get_logger

from app.api.api import api_router
from app.core.kafka import message_publisher


logger = get_logger(__name__)
settings = get_settings()

# Create the FastAPI app
app = create_app(
    service_name="data-ingestion-service",
    settings=settings,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute actions on application startup."""
    logger.info("Data ingestion service starting up")
    
    # Validate required API keys
    try:
        # Alpaca API is required for market data
        settings.validate_alpaca_api_keys()
        logger.info("Alpaca API keys validated")
        
        # News API is required for news data (if used)
        if not settings.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY is not set. News data ingestion will not be available.")
    except ValueError as e:
        error_msg = f"API key validation failed: {str(e)}"
        logger.critical(error_msg)
        raise ValueError(error_msg)
    
    # Initialize Kafka producer
    await message_publisher.initialize()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute actions on application shutdown."""
    logger.info("Data ingestion service shutting down")
    
    # Close Kafka producer
    await message_publisher.close()


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