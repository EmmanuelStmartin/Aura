"""Base service template for Aura microservices."""

import logging
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import setup_logging, get_logger


def create_app(
    service_name: str,
    settings: Optional[Settings] = None,
    docs_url: str = "/docs",
    openapi_url: str = "/openapi.json",
    include_middleware: bool = True,
    root_path: str = "",
) -> FastAPI:
    """Create a FastAPI application with common configuration.
    
    Args:
        service_name: Service name
        settings: Settings instance
        docs_url: Swagger docs URL
        openapi_url: OpenAPI schema URL
        include_middleware: Whether to include common middleware
        root_path: Root path for ASGI application
        
    Returns:
        FastAPI application
    """
    if settings is None:
        settings = get_settings()
        
    # Setup logging
    setup_logging(level=logging.DEBUG if settings.DEBUG else logging.INFO)
    logger = get_logger(service_name)
    
    # Create FastAPI app
    app = FastAPI(
        title=f"Aura {service_name.replace('-', ' ').title()}",
        description=f"API for Aura {service_name.replace('-', ' ').title()}",
        version="0.1.0",
        docs_url=docs_url,
        openapi_url=openapi_url,
        root_path=root_path,
    )
    
    # Add middleware if requested
    if include_middleware:
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, you'd want to restrict this
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", os.urandom(16).hex())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {str(exc)}", extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
        })
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": service_name}
    
    # Add readiness check endpoint
    @app.get("/ready")
    async def readiness_check():
        # In a real implementation, you might check database connections, etc.
        return {"status": "ready", "service": service_name}
    
    return app 