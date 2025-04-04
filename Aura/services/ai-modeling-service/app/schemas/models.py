"""Pydantic models for AI modeling service."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    """Date range for fetching data."""
    
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")


class MarketMovementRequest(BaseModel):
    """Market movement prediction request."""
    
    symbol: str = Field(..., description="Stock symbol")
    interval: str = Field("1d", description="Time interval (e.g., '1d', '1h')")
    horizon: int = Field(5, description="Prediction horizon in days", ge=1, le=30)
    include_indicators: bool = Field(True, description="Whether to include technical indicators in the model input")
    date_range: Optional[DateRange] = Field(None, description="Date range for fetching historical data")


class MarketMovementPrediction(BaseModel):
    """Market movement prediction response."""
    
    symbol: str = Field(..., description="Stock symbol")
    forecast: List[float] = Field(..., description="Forecasted prices")
    confidence_scores: List[float] = Field(..., description="Confidence scores")
    directions: List[str] = Field(..., description="Forecasted directions (up, down, neutral)")
    model_type: str = Field(..., description="Model type used for prediction")


class SentimentRequest(BaseModel):
    """Sentiment analysis request."""
    
    text: Optional[str] = Field(None, description="Text to analyze")
    news_id: Optional[int] = Field(None, description="News article ID to analyze")


class SentimentPrediction(BaseModel):
    """Sentiment analysis response."""
    
    label: str = Field(..., description="Sentiment label (positive, negative, neutral)")
    score: float = Field(..., description="Sentiment score")
    confidence: float = Field(..., description="Confidence score")
    model_type: str = Field(..., description="Model type used for prediction")


class TrainingJobRequest(BaseModel):
    """Model training job request."""
    
    model_type: str = Field(..., description="Model type (market_movement, sentiment)")
    symbol: Optional[str] = Field(None, description="Stock symbol (for market_movement model)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Model parameters")
    date_range: Optional[DateRange] = Field(None, description="Date range for training data")


class TrainingJobResponse(BaseModel):
    """Model training job response."""
    
    job_id: str = Field(..., description="Training job ID")
    model_type: str = Field(..., description="Model type")
    status: str = Field(..., description="Job status (submitted, running, completed, failed)")
    message: str = Field(..., description="Status message") 