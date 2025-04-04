"""Market data models for Aura services."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Timeframe(str, Enum):
    """Timeframe enumeration."""
    
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class OHLCV(BaseModel):
    """OHLCV (Open, High, Low, Close, Volume) data model."""
    
    timestamp: datetime = Field(..., description="Bar timestamp")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: float = Field(..., description="Trading volume")
    
    class Config:
        """Pydantic model configuration."""
        
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketData(BaseModel):
    """Market data model."""
    
    symbol: str = Field(..., description="Asset symbol")
    timeframe: Timeframe = Field(..., description="Data timeframe")
    data: List[OHLCV] = Field(..., description="OHLCV data")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True


class News(BaseModel):
    """News article model."""
    
    title: str = Field(..., description="Article title")
    url: str = Field(..., description="Article URL")
    published_at: datetime = Field(..., description="Publication timestamp")
    source: str = Field(..., description="News source")
    summary: Optional[str] = Field(None, description="Article summary")
    content: Optional[str] = Field(None, description="Article content")
    related_symbols: List[str] = Field(default=[], description="Related asset symbols")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1.0 to 1.0)")
    
    class Config:
        """Pydantic model configuration."""
        
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TechnicalIndicator(BaseModel):
    """Technical indicator model."""
    
    symbol: str = Field(..., description="Asset symbol")
    indicator: str = Field(..., description="Indicator name")
    timeframe: Timeframe = Field(..., description="Data timeframe")
    timestamp: datetime = Field(..., description="Indicator timestamp")
    value: Union[float, Dict[str, float]] = Field(..., description="Indicator value")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 