"""Admin endpoints for data processing service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import get_db
from app.models.processed_news import ProcessedNews
from app.models.processed_sec_filings import ProcessedSecFiling


router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/stats")
async def get_processing_stats(db: Session = Depends(get_db)):
    """Get data processing statistics.
    
    Args:
        db: Database session
        
    Returns:
        Processing statistics
    """
    try:
        # Get news count
        news_count = db.query(ProcessedNews).count()
        
        # Get SEC filings count
        filings_count = db.query(ProcessedSecFiling).count()
        
        # Get recent news count (last 24 hours)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_news_count = db.query(ProcessedNews).filter(
            ProcessedNews.created_at >= last_24h
        ).count()
        
        # Get recent filings count (last 24 hours)
        recent_filings_count = db.query(ProcessedSecFiling).filter(
            ProcessedSecFiling.created_at >= last_24h
        ).count()
        
        return {
            "total_processed_news": news_count,
            "total_processed_sec_filings": filings_count,
            "news_processed_last_24h": recent_news_count,
            "filings_processed_last_24h": recent_filings_count
        }
    except Exception as e:
        logger.exception(f"Error getting processing stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting processing statistics"
        )


@router.get("/news")
async def get_processed_news(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get processed news.
    
    Args:
        limit: Maximum number of news to return
        offset: Offset for pagination
        symbol: Filter by symbol
        db: Database session
        
    Returns:
        List of processed news
    """
    try:
        query = db.query(ProcessedNews)
        
        if symbol:
            query = query.join(ProcessedNews.symbols).filter(
                ProcessedNews.symbols.any(symbol=symbol)
            )
        
        total = query.count()
        news_list = query.order_by(ProcessedNews.published_at.desc()) \
            .offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "news": [
                {
                    "id": news.id,
                    "title": news.title,
                    "source": news.source,
                    "url": news.url,
                    "published_at": news.published_at.isoformat(),
                    "sentiment_score": news.sentiment_score,
                    "symbols": [symbol.symbol for symbol in news.symbols]
                }
                for news in news_list
            ]
        }
    except Exception as e:
        logger.exception(f"Error getting processed news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting processed news"
        )


@router.get("/sec-filings")
async def get_processed_sec_filings(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    symbol: Optional[str] = None,
    form_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get processed SEC filings.
    
    Args:
        limit: Maximum number of filings to return
        offset: Offset for pagination
        symbol: Filter by symbol
        form_type: Filter by form type
        db: Database session
        
    Returns:
        List of processed SEC filings
    """
    try:
        query = db.query(ProcessedSecFiling)
        
        if symbol:
            query = query.filter(ProcessedSecFiling.symbol == symbol)
            
        if form_type:
            query = query.filter(ProcessedSecFiling.form_type == form_type)
        
        total = query.count()
        filings_list = query.order_by(ProcessedSecFiling.filing_date.desc()) \
            .offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "filings": [
                {
                    "id": filing.id,
                    "symbol": filing.symbol,
                    "company_name": filing.company_name,
                    "form_type": filing.form_type,
                    "filing_date": filing.filing_date.isoformat(),
                    "filing_url": filing.filing_url
                }
                for filing in filings_list
            ]
        }
    except Exception as e:
        logger.exception(f"Error getting processed SEC filings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting processed SEC filings"
        ) 