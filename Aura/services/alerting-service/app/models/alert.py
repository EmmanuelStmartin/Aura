"""Alert models."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer, JSON, String, Text

from app.db.base_class import Base


class AlertStatus(str, Enum):
    """Alert status enumeration."""
    
    NEW = "new"
    READ = "read"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert type enumeration."""
    
    PRICE_CHANGE = "price_change"
    TECHNICAL_INDICATOR = "technical_indicator"
    NEWS_SENTIMENT = "news_sentiment"
    PRICE_TARGET = "price_target"
    CUSTOM = "custom"


class Alert(Base):
    """Alert model."""
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    alert_type = Column(SQLAlchemyEnum(AlertType), nullable=False)
    severity = Column(SQLAlchemyEnum(AlertSeverity), default=AlertSeverity.MEDIUM, nullable=False)
    status = Column(SQLAlchemyEnum(AlertStatus), default=AlertStatus.NEW, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    rule_id = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    is_delivered = Column(Boolean, default=False, nullable=False)
    
    def as_dict(self) -> dict:
        """Convert the alert to a dictionary.
        
        Returns:
            Dictionary representation of the alert
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "symbol": self.symbol,
            "alert_type": self.alert_type.value if self.alert_type else None,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value if self.status else None,
            "title": self.title,
            "message": self.message,
            "rule_id": self.rule_id,
            "metadata": self.metadata,
            "is_delivered": self.is_delivered,
        } 