"""Prediction endpoints for AI modeling service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.models import get_model
from app.core.data import (
    fetch_market_data, 
    fetch_technical_indicators, 
    fetch_news_by_id
)
from app.schemas.models import (
    MarketMovementRequest, 
    MarketMovementPrediction,
    SentimentRequest,
    SentimentPrediction
)


router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.post("/market-movement", response_model=MarketMovementPrediction)
async def predict_market_movement(request: MarketMovementRequest):
    """Predict market movement.
    
    Args:
        request: Market movement prediction request
        
    Returns:
        Market movement prediction
        
    Raises:
        HTTPException: If the prediction fails
    """
    try:
        # Get market movement model
        model = get_model("market_movement")
        if not model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Market movement model not available"
            )
        
        # Extract request parameters
        symbol = request.symbol
        interval = request.interval
        horizon = request.horizon
        include_indicators = request.include_indicators
        
        # Set date range
        if request.date_range:
            start_date = request.date_range.start_date
            end_date = request.date_range.end_date
        else:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)  # Use last year by default
        
        # Fetch historical market data
        market_data = await fetch_market_data(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            limit=500  # Get enough data for modeling
        )
        
        if market_data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No market data found for symbol: {symbol}"
            )
        
        # Fetch technical indicators if requested
        if include_indicators:
            indicators = await fetch_technical_indicators(
                symbol=symbol,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                limit=500
            )
            
            # Merge market data and indicators if indicators data exists
            if not indicators.empty:
                # Ensure both DataFrames have timestamp column
                if "timestamp" in market_data.columns and "timestamp" in indicators.columns:
                    # Merge on timestamp
                    market_data = market_data.merge(
                        indicators, 
                        on="timestamp", 
                        how="left", 
                        suffixes=("", "_indicator")
                    )
        
        # Make prediction
        prediction = await model.predict(symbol, market_data, horizon)
        
        return MarketMovementPrediction(
            symbol=prediction["symbol"],
            forecast=prediction["forecast"],
            confidence_scores=prediction["confidence_scores"],
            directions=prediction["directions"],
            model_type=prediction["model_type"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Error predicting market movement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting market movement: {str(e)}"
        )


@router.post("/sentiment", response_model=SentimentPrediction)
async def predict_sentiment(request: SentimentRequest):
    """Predict sentiment.
    
    Args:
        request: Sentiment analysis request
        
    Returns:
        Sentiment analysis prediction
        
    Raises:
        HTTPException: If the prediction fails
    """
    try:
        # Get sentiment model
        model = get_model("sentiment")
        if not model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sentiment model not available"
            )
        
        # Determine text to analyze
        text = request.text
        
        # If news_id is provided, fetch the news article
        if not text and request.news_id:
            news = await fetch_news_by_id(request.news_id)
            if not news:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"News article not found with ID: {request.news_id}"
                )
            
            # Combine title and summary
            text = news["title"]
            if news.get("summary"):
                text = f"{text}. {news['summary']}"
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either text or news_id must be provided"
            )
        
        # Make prediction
        prediction = model.predict(text)
        
        return SentimentPrediction(
            label=prediction["label"],
            score=prediction["score"],
            confidence=prediction["confidence"],
            model_type=prediction["model_type"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Error predicting sentiment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting sentiment: {str(e)}"
        ) 