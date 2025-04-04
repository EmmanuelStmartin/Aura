"""Status endpoints for portfolio optimization service."""

from fastapi import APIRouter, Depends, HTTPException, status

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import influxdb_client


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
        "service": "portfolio-optimization-service",
        "status": "operational",
        "version": "0.1.0",
    }


@router.get("/status/database")
async def check_database_status():
    """Check database status.
    
    Returns:
        Database status information
    """
    status_info = {
        "influxdb": "unavailable",
    }
    
    # Check InfluxDB connection
    try:
        health = influxdb_client.client.health()
        status_info["influxdb"] = "connected" if health.status == "pass" else "unhealthy"
    except Exception as e:
        logger.error(f"InfluxDB connection error: {str(e)}")
    
    return status_info 