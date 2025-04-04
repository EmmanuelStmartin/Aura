"""Alert schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from app.models.alert import AlertStatus, AlertSeverity, AlertType


class AlertBase(BaseModel):
    """Base alert schema."""
    
    user_id: int = Field(..., description="User ID")
    symbol: str = Field(..., description="Asset symbol")
    alert_type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(AlertSeverity.MEDIUM, description="Alert severity")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    rule_id: Optional[int] = Field(None, description="Rule ID that triggered the alert")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AlertCreate(AlertBase):
    """Alert creation schema."""
    
    pass


class AlertUpdate(BaseModel):
    """Alert update schema."""
    
    status: Optional[AlertStatus] = Field(None, description="Alert status")
    is_delivered: Optional[bool] = Field(None, description="Whether the alert has been delivered")


class Alert(AlertBase):
    """Alert schema."""
    
    id: int = Field(..., description="Alert ID")
    timestamp: datetime = Field(..., description="Alert timestamp")
    status: AlertStatus = Field(..., description="Alert status")
    is_delivered: bool = Field(..., description="Whether the alert has been delivered")
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True
        use_enum_values = True


class AlertList(BaseModel):
    """List of alerts."""
    
    alerts: List[Alert] = Field(..., description="List of alerts")
    total: int = Field(..., description="Total number of alerts") 