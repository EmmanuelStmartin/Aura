"""Alerts API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from aura_common.utils.logging import get_logger

from app.db.session import get_db
from app.models.alert import Alert, AlertStatus
from app.schemas.alert import Alert as AlertSchema
from app.schemas.alert import AlertList, AlertUpdate

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=AlertList)
async def get_alerts(
    user_id: int = Query(..., description="User ID"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get alerts for a user.
    
    Args:
        user_id: User ID
        status: Filter by status
        symbol: Filter by symbol
        limit: Maximum number of alerts to return
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of alerts
    """
    # Build the query
    query = db.query(Alert).filter(Alert.user_id == user_id)
    
    # Apply filters if provided
    if status:
        query = query.filter(Alert.status == status)
    if symbol:
        query = query.filter(Alert.symbol == symbol)
    
    # Get the total count
    total = query.count()
    
    # Apply pagination and ordering
    alerts = query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "alerts": alerts,
        "total": total,
    }


@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(
    alert_id: int = Path(..., description="Alert ID"),
    db: Session = Depends(get_db),
) -> Alert:
    """Get an alert by ID.
    
    Args:
        alert_id: Alert ID
        db: Database session
        
    Returns:
        Alert
        
    Raises:
        HTTPException: If the alert is not found
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )
    
    return alert


@router.patch("/{alert_id}", response_model=AlertSchema)
async def update_alert(
    alert_update: AlertUpdate,
    alert_id: int = Path(..., description="Alert ID"),
    db: Session = Depends(get_db),
) -> Alert:
    """Update an alert.
    
    Args:
        alert_update: Alert update data
        alert_id: Alert ID
        db: Database session
        
    Returns:
        Updated alert
        
    Raises:
        HTTPException: If the alert is not found
    """
    # Get the alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )
    
    # Update the alert
    for key, value in alert_update.dict(exclude_unset=True).items():
        setattr(alert, key, value)
    
    # Save changes
    db.commit()
    db.refresh(alert)
    
    return alert


@router.patch("/{alert_id}/mark-as-read", response_model=AlertSchema)
async def mark_alert_as_read(
    alert_id: int = Path(..., description="Alert ID"),
    db: Session = Depends(get_db),
) -> Alert:
    """Mark an alert as read.
    
    Args:
        alert_id: Alert ID
        db: Database session
        
    Returns:
        Updated alert
        
    Raises:
        HTTPException: If the alert is not found
    """
    # Get the alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )
    
    # Mark as read
    alert.status = AlertStatus.READ
    
    # Save changes
    db.commit()
    db.refresh(alert)
    
    return alert 