"""Alert rule models."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, JSON, String, Text

from app.db.base_class import Base
from app.models.alert import AlertType, AlertSeverity


class RuleStatus(str, Enum):
    """Rule status enumeration."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"


class RuleConditionOperator(str, Enum):
    """Rule condition operator enumeration."""
    
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL_TO = "=="
    NOT_EQUAL = "!="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"


class AlertRule(Base):
    """Alert rule model."""
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(SQLAlchemyEnum(AlertType), nullable=False)
    severity = Column(SQLAlchemyEnum(AlertSeverity), default=AlertSeverity.MEDIUM, nullable=False)
    status = Column(SQLAlchemyEnum(RuleStatus), default=RuleStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Rule configuration
    symbol = Column(String(20), nullable=True)  # Can be null for rules that apply to all symbols
    indicator = Column(String(100), nullable=True)  # Technical indicator or data field to monitor
    operator = Column(SQLAlchemyEnum(RuleConditionOperator), nullable=False)
    threshold = Column(String(255), nullable=False)  # Can be numeric or string depending on rule
    lookback_period = Column(Integer, nullable=True)  # Period to look back in minutes
    cooldown_minutes = Column(Integer, default=60, nullable=False)  # Minimum time between alerts
    
    # Additional configuration
    additional_config = Column(JSON, nullable=True)
    
    def as_dict(self) -> dict:
        """Convert the rule to a dictionary.
        
        Returns:
            Dictionary representation of the rule
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "alert_type": self.alert_type.value if self.alert_type else None,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "symbol": self.symbol,
            "indicator": self.indicator,
            "operator": self.operator.value if self.operator else None,
            "threshold": self.threshold,
            "lookback_period": self.lookback_period,
            "cooldown_minutes": self.cooldown_minutes,
            "additional_config": self.additional_config,
        } 