"""News processor for raw news data."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger
from aura_common.kafka import KafkaProducer

from app.core.database import get_db, postgres_client
from app.models.processed_news import ProcessedNews, Symbol


logger = get_logger(__name__)
settings = get_settings()

# Initialize VADER sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# Initialize Kafka producer for processed news
kafka_producer = KafkaProducer(settings)


async def process_news(data: Dict[str, Any]) -> None:
    """Process raw news data.
    
    Args:
        data: Raw news data from Kafka
    """
    logger.info(f"Processing news: {data.get('title')}")
    
    try:
        # Extract data
        title = data.get("title")
        summary = data.get("summary")
        source = data.get("source")
        url = data.get("url")
        published_at = data.get("published_at")
        symbols = data.get("symbols", [])
        
        if not title or not url:
            logger.warning("Missing title or URL in news data")
            return
            
        # Parse published_at if it's a string
        if isinstance(published_at, str):
            published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        elif published_at is None:
            published_at = datetime.utcnow()
        
        # Calculate sentiment score using VADER
        sentiment_score, sentiment_magnitude = analyze_sentiment(title, summary)
        
        # Store in PostgreSQL
        db = next(get_db())
        try:
            # Check if news already exists
            existing_news = db.query(ProcessedNews).filter(ProcessedNews.url == url).first()
            if existing_news:
                logger.info(f"News already exists: {url}")
                return
                
            # Create new processed news
            news = ProcessedNews(
                title=title,
                summary=summary,
                source=source,
                url=url,
                published_at=published_at,
                sentiment_score=sentiment_score,
                sentiment_magnitude=sentiment_magnitude
            )
            
            # Add symbols
            for symbol_str in symbols:
                symbol = db.query(Symbol).filter(Symbol.symbol == symbol_str).first()
                if not symbol:
                    symbol = Symbol(symbol=symbol_str)
                    db.add(symbol)
                news.symbols.append(symbol)
            
            db.add(news)
            db.commit()
            db.refresh(news)
            
            logger.info(f"Saved news to database with ID: {news.id}")
            
            # Publish processed news to Kafka
            await publish_processed_news(news.id, title, url, published_at, sentiment_score, symbols)
        except Exception as e:
            db.rollback()
            logger.exception(f"Error saving news to database: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Error processing news: {str(e)}")


def analyze_sentiment(title: str, summary: Optional[str] = None) -> tuple:
    """Analyze sentiment of news text using VADER.
    
    Args:
        title: News title
        summary: News summary
        
    Returns:
        Tuple of (sentiment_score, sentiment_magnitude)
    """
    # Combine title and summary for analysis
    text = title
    if summary:
        text = f"{title}. {summary}"
    
    # Get sentiment scores
    scores = sentiment_analyzer.polarity_scores(text)
    
    # Compound score is between -1 (negative) and 1 (positive)
    sentiment_score = scores["compound"]
    
    # Magnitude can be derived from the sum of absolute values of pos, neg, neu scores
    sentiment_magnitude = abs(scores["pos"]) + abs(scores["neg"]) + abs(scores["neu"])
    
    return sentiment_score, sentiment_magnitude


async def publish_processed_news(news_id: int, title: str, url: str, published_at: datetime, 
                               sentiment_score: float, symbols: List[str]) -> None:
    """Publish processed news to Kafka.
    
    Args:
        news_id: News ID
        title: News title
        url: News URL
        published_at: Published datetime
        sentiment_score: Sentiment score
        symbols: List of symbols
    """
    try:
        message = {
            "news_id": news_id,
            "title": title,
            "url": url,
            "published_at": published_at.isoformat(),
            "sentiment_score": sentiment_score,
            "symbols": symbols
        }
        
        kafka_producer.send(
            topic="processed_news_sentiment",
            value=message,
            key=f"news-{news_id}"
        )
        
        logger.info(f"Published processed news to Kafka: {news_id}")
    except Exception as e:
        logger.exception(f"Error publishing processed news to Kafka: {str(e)}") 