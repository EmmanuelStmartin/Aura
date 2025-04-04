"""News endpoints for data ingestion service."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.connectors import get_news_connector
from app.core.kafka import message_publisher
from app.models.schema import DataSourceType, NewsRequest


logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


@router.post("/fetch", status_code=status.HTTP_202_ACCEPTED)
async def fetch_news(
    request: NewsRequest,
) -> Dict[str, Any]:
    """Fetch news articles and publish to Kafka.
    
    Args:
        request: News request
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If news fetch fails
    """
    try:
        # Get the news connector
        connector = get_news_connector(request.source)
        await connector.connect()
        
        # Fetch news
        news_items = await connector.get_news(
            keywords=request.keywords,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit,
        )
        
        # Disconnect from news source
        await connector.disconnect()
        
        if not news_items:
            return {
                "status": "success",
                "message": "No news articles found",
                "count": 0
            }
        
        # Publish to Kafka
        await message_publisher.publish_news(
            news_items=news_items,
            source=request.source,
            metadata={
                "keywords": request.keywords,
                "symbols": request.symbols,
                "start_date": request.start_date.isoformat() if request.start_date else None,
                "end_date": request.end_date.isoformat() if request.end_date else None,
            }
        )
        
        return {
            "status": "accepted",
            "message": "News fetch request accepted",
            "count": len(news_items)
        }
    except Exception as e:
        logger.error(f"News fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"News fetch failed: {str(e)}",
        )


@router.get("/headlines", status_code=status.HTTP_202_ACCEPTED)
async def fetch_top_headlines(
    country: str = Query("us", description="Country code"),
    category: str = Query("business", description="News category"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of headlines to return"),
    source: DataSourceType = Query(DataSourceType.NEWSAPI, description="News source"),
) -> Dict[str, Any]:
    """Fetch top headlines and publish to Kafka.
    
    Args:
        country: Country code
        category: News category
        limit: Maximum number of headlines to return
        source: News source
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If headlines fetch fails
    """
    try:
        # Get the news connector
        connector = get_news_connector(source)
        await connector.connect()
        
        # Fetch top headlines
        # Note: This is NewsAPI-specific, we're checking for the specific class
        if not hasattr(connector, "get_top_headlines"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The selected source ({source}) does not support top headlines",
            )
            
        news_items = await connector.get_top_headlines(
            country=country,
            category=category,
            limit=limit,
        )
        
        # Disconnect from news source
        await connector.disconnect()
        
        if not news_items:
            return {
                "status": "success",
                "message": "No headlines found",
                "count": 0
            }
        
        # Publish to Kafka
        await message_publisher.publish_news(
            news_items=news_items,
            source=source,
            metadata={
                "country": country,
                "category": category,
                "type": "top_headlines",
            }
        )
        
        return {
            "status": "accepted",
            "message": "Headlines fetch request accepted",
            "count": len(news_items)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Headlines fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Headlines fetch failed: {str(e)}",
        ) 