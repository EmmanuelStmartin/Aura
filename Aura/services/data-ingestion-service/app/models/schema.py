"""Schema models for data ingestion service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class DataType(str, Enum):
    """Data type enumeration."""
    
    MARKET_DATA = "MARKET_DATA"
    TECHNICAL_INDICATOR = "TECHNICAL_INDICATOR"
    FUNDAMENTAL = "FUNDAMENTAL"
    NEWS = "NEWS"
    SEC_FILING = "SEC_FILING"
    ALTERNATIVE = "ALTERNATIVE"


class DataSourceType(str, Enum):
    """Data source type enumeration."""
    
    ALPACA = "alpaca"
    POLYGON = "polygon"
    YAHOO_FINANCE = "yahoo_finance"
    IEX_CLOUD = "iex_cloud"
    NEWSAPI = "newsapi"
    SEC_EDGAR = "sec_edgar"
    FINVIZ = "finviz"


class TimeInterval(str, Enum):
    """Time interval enumeration for market data."""
    
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class MarketDataRequest(BaseModel):
    """Market data request model for API."""
    
    symbols: List[str] = Field(..., min_items=1, max_items=50, description="List of asset symbols")
    start_date: Optional[datetime] = Field(None, description="Start date for data retrieval")
    end_date: Optional[datetime] = Field(None, description="End date for data retrieval")
    interval: TimeInterval = Field(TimeInterval.ONE_DAY, description="Time interval for data")
    source: Optional[DataSourceType] = Field(DataSourceType.ALPACA, description="Data source")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True


class NewsRequest(BaseModel):
    """News data request model for API."""
    
    keywords: Optional[List[str]] = Field(None, description="List of keywords to search for")
    symbols: Optional[List[str]] = Field(None, description="List of asset symbols")
    start_date: Optional[datetime] = Field(None, description="Start date for news retrieval")
    end_date: Optional[datetime] = Field(None, description="End date for news retrieval")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of news items to return")
    source: Optional[DataSourceType] = Field(DataSourceType.NEWSAPI, description="News source")
    
    @validator("symbols", "keywords")
    def validate_search_params(cls, v, values):
        """Validate that at least one of symbols or keywords is provided."""
        if not v and not values.get("symbols") and not values.get("keywords"):
            raise ValueError("At least one symbol or keyword must be provided")
        return v
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True


class SECFilingRequest(BaseModel):
    """SEC filing request model for API."""
    
    symbol: str = Field(..., description="Asset symbol")
    form_type: Optional[str] = Field(None, description="Filing form type (e.g., '10-K', '10-Q')")
    start_date: Optional[datetime] = Field(None, description="Start date for filing retrieval")
    end_date: Optional[datetime] = Field(None, description="End date for filing retrieval")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of filings to return")
    include_content: bool = Field(False, description="Whether to include filing content")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True


class AssetSearchRequest(BaseModel):
    """Asset search request model for API."""
    
    query: str = Field(..., min_length=1, description="Search query")
    source: Optional[DataSourceType] = Field(DataSourceType.ALPACA, description="Data source")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True


class DataIngestionTask(BaseModel):
    """Data ingestion task model for scheduled jobs."""
    
    task_id: str = Field(..., description="Task ID")
    task_type: str = Field(..., description="Task type")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    schedule: Optional[str] = Field(None, description="Cron schedule expression")
    enabled: bool = Field(True, description="Whether the task is enabled")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True 