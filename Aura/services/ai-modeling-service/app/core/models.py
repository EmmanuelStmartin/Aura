"""ML models management for the AI modeling service."""

import os
import pickle
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import pmdarima as pm
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()

# Global model storage
models = {
    "market_movement": None,
    "sentiment": None,
}


async def initialize_models() -> None:
    """Initialize ML models."""
    logger.info("Initializing ML models")
    
    # Initialize market movement model
    await initialize_market_movement_model()
    
    # Initialize sentiment model
    await initialize_sentiment_model()


async def initialize_market_movement_model() -> None:
    """Initialize market movement prediction model."""
    logger.info("Initializing market movement model")
    
    # Use a simple model for the MVP
    if settings.ENABLE_ADVANCED_ML_MODELS:
        # For future implementation (post-MVP)
        logger.info("Advanced ML models enabled, but not implemented in MVP")
        # TODO: Implement advanced market movement model (e.g., transformer-based model)
        models["market_movement"] = SimpleARIMAModel()
    else:
        # Use a simple ARIMA model
        models["market_movement"] = SimpleARIMAModel()
    
    logger.info("Market movement model initialized")


async def initialize_sentiment_model() -> None:
    """Initialize sentiment analysis model."""
    logger.info("Initializing sentiment model")
    
    if settings.ENABLE_ADVANCED_ML_MODELS:
        # Use a pre-trained Hugging Face model
        try:
            # Load FinBERT or similar financial sentiment model
            model_name = "ProsusAI/finbert"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Create pipeline
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            models["sentiment"] = HuggingFaceSentimentModel(sentiment_pipeline)
            logger.info(f"Loaded advanced sentiment model: {model_name}")
        except Exception as e:
            logger.exception(f"Failed to load advanced sentiment model: {str(e)}")
            # Fallback to simple model
            models["sentiment"] = SimpleSentimentModel()
    else:
        # Use a simple sentiment model
        models["sentiment"] = SimpleSentimentModel()
    
    logger.info("Sentiment model initialized")


def get_model(model_type: str) -> Any:
    """Get ML model by type.
    
    Args:
        model_type: Model type
        
    Returns:
        ML model instance
    
    Raises:
        ValueError: If model type is unknown
    """
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}")
        
    return models[model_type]


class SimpleARIMAModel:
    """Simple ARIMA model for market movement prediction."""
    
    def __init__(self):
        """Initialize ARIMA model."""
        self.models = {}  # Cache for symbol-specific models
    
    async def predict(self, symbol: str, historical_data: pd.DataFrame, horizon: int = 5) -> Dict[str, Any]:
        """Predict market movement.
        
        Args:
            symbol: Stock symbol
            historical_data: Historical OHLCV data
            horizon: Prediction horizon in days
            
        Returns:
            Prediction results
        """
        try:
            # Ensure we have a clean time series
            if "close" not in historical_data.columns:
                raise ValueError("Historical data must contain 'close' column")
                
            close_prices = historical_data["close"].astype(float)
            
            # Use existing model or fit a new one
            if symbol in self.models:
                model = self.models[symbol]
            else:
                # Fit an ARIMA model
                model = pm.auto_arima(
                    close_prices,
                    seasonal=True,
                    m=5,  # Business week seasonality
                    suppress_warnings=True,
                    error_action="ignore",
                    stepwise=True
                )
                self.models[symbol] = model
                
            # Make predictions
            forecast, conf_int = model.predict(n_periods=horizon, return_conf_int=True)
            
            # Calculate confidence scores based on prediction intervals
            confidence_scores = 1.0 - (conf_int[:, 1] - conf_int[:, 0]) / (2 * close_prices.mean())
            confidence_scores = np.clip(confidence_scores, 0.1, 0.9)  # Limit extreme values
            
            # Determine direction
            last_price = close_prices.iloc[-1]
            directions = ["up" if price > last_price else "down" for price in forecast]
            
            return {
                "symbol": symbol,
                "forecast": forecast.tolist(),
                "conf_intervals": conf_int.tolist(),
                "confidence_scores": confidence_scores.tolist(),
                "directions": directions,
                "model_type": "ARIMA"
            }
        except Exception as e:
            logger.exception(f"Error in ARIMA prediction: {str(e)}")
            
            # Return a placeholder prediction
            placeholder_forecast = [historical_data["close"].iloc[-1]] * horizon
            placeholder_direction = ["neutral"] * horizon
            placeholder_confidence = [0.5] * horizon
            
            return {
                "symbol": symbol,
                "forecast": placeholder_forecast,
                "confidence_scores": placeholder_confidence,
                "directions": placeholder_direction,
                "model_type": "ARIMA (placeholder)"
            }


class SimpleSentimentModel:
    """Simple sentiment analysis model."""
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Predict sentiment.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        # Simple rule-based sentiment
        positive_words = ["growth", "profit", "increase", "positive", "up", "gain", "bull", "opportunity", "success"]
        negative_words = ["loss", "decline", "decrease", "negative", "down", "drop", "bear", "risk", "fail"]
        
        text_lower = text.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
            label = "neutral"
        else:
            score = (positive_count - negative_count) / total
            if score > 0.3:
                label = "positive"
            elif score < -0.3:
                label = "negative"
            else:
                label = "neutral"
                
        return {
            "label": label,
            "score": score,
            "confidence": 0.6,  # Fixed confidence for simple model
            "model_type": "rule-based"
        }


class HuggingFaceSentimentModel:
    """Hugging Face-based sentiment analysis model."""
    
    def __init__(self, pipeline):
        """Initialize Hugging Face sentiment model.
        
        Args:
            pipeline: Hugging Face pipeline
        """
        self.pipeline = pipeline
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Predict sentiment.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        try:
            # Use Hugging Face pipeline
            result = self.pipeline(text)[0]
            
            return {
                "label": result["label"].lower(),
                "score": result["score"],
                "confidence": result["score"],
                "model_type": "transformer"
            }
        except Exception as e:
            logger.exception(f"Error in Hugging Face sentiment prediction: {str(e)}")
            
            # Fallback to simple model
            simple_model = SimpleSentimentModel()
            return simple_model.predict(text) 