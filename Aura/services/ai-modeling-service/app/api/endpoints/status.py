"""Status endpoints for AI modeling service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import get_db, influxdb_client
from app.core.models import models


router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/status")
async def check_service_status():
    """Check service status.
    
    Returns:
        Service status information
    """
    return {
        "service": "ai-modeling-service",
        "status": "operational",
        "version": "0.1.0",
    }


@router.get("/status/models")
async def check_models_status():
    """Check loaded models status.
    
    Returns:
        Models status information
    """
    models_status = {}
    
    for model_name, model_instance in models.items():
        if model_instance:
            models_status[model_name] = {
                "status": "loaded",
                "type": model_instance.__class__.__name__
            }
        else:
            models_status[model_name] = {
                "status": "not_loaded"
            }
    
    return {
        "models": models_status,
        "advanced_models_enabled": settings.ENABLE_ADVANCED_ML_MODELS
    }


@router.get("/status/databases")
async def check_database_status(db: Session = Depends(get_db)):
    """Check database status.
    
    Args:
        db: Database session
        
    Returns:
        Database status information
    """
    status_info = {
        "postgres": "unavailable",
        "influxdb": "unavailable",
    }
    
    # Check PostgreSQL connection
    try:
        db.execute("SELECT 1")
        status_info["postgres"] = "connected"
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {str(e)}")
    
    # Check InfluxDB connection
    try:
        health = influxdb_client.client.health()
        status_info["influxdb"] = "connected" if health.status == "pass" else "unhealthy"
    except Exception as e:
        logger.error(f"InfluxDB connection error: {str(e)}")
    
    return status_info 