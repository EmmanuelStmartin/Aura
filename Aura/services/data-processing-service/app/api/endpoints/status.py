"""Status endpoints for data processing service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import get_db, postgres_client, influxdb_client


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
        "service": "data-processing-service",
        "status": "operational",
        "version": "0.1.0",
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