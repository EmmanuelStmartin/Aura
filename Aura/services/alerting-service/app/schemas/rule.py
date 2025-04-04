"""Alert rule schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from app.models.alert import AlertType, AlertSeverity
from app.models.rule import RuleStatus, RuleConditionOperator


class AlertRuleBase(BaseModel):
    """Base alert rule schema."""
    
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    alert_type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(AlertSeverity.MEDIUM, description="Alert severity")
    
    # Rule configuration
    symbol: Optional[str] = Field(None, description="Asset symbol (null for all symbols)")
    indicator: Optional[str] = Field(None, description="Technical indicator or data field")
    operator: RuleConditionOperator = Field(..., description="Condition operator")
    threshold: str = Field(..., description="Threshold value")
    lookback_period: Optional[int] = Field(None, description="Lookback period in minutes")
    cooldown_minutes: int = Field(60, description="Minimum time between alerts in minutes")
    
    # Additional configuration
    additional_config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


class AlertRuleCreate(AlertRuleBase):
    """Alert rule creation schema."""
    
    pass


class AlertRuleUpdate(BaseModel):
    """Alert rule update schema."""
    
    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    alert_type: Optional[AlertType] = Field(None, description="Alert type")
    severity: Optional[AlertSeverity] = Field(None, description="Alert severity")
    status: Optional[RuleStatus] = Field(None, description="Rule status")
    
    # Rule configuration
    symbol: Optional[str] = Field(None, description="Asset symbol")
    indicator: Optional[str] = Field(None, description="Technical indicator or data field")
    operator: Optional[RuleConditionOperator] = Field(None, description="Condition operator")
    threshold: Optional[str] = Field(None, description="Threshold value")
    lookback_period: Optional[int] = Field(None, description="Lookback period in minutes")
    cooldown_minutes: Optional[int] = Field(None, description="Minimum time between alerts in minutes")
    
    # Additional configuration
    additional_config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


class AlertRule(AlertRuleBase):
    """Alert rule schema."""
    
    id: int = Field(..., description="Rule ID")
    status: RuleStatus = Field(..., description="Rule status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True
        use_enum_values = True


class AlertRuleList(BaseModel):
    """List of alert rules."""
    
    rules: List[AlertRule] = Field(..., description="List of alert rules")
    total: int = Field(..., description="Total number of rules") 