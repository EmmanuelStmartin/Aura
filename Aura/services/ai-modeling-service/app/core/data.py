"""Data access functions for AI modeling service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd
from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import influxdb_client, get_db


logger = get_logger(__name__)
settings = get_settings()


async def fetch_market_data(
    symbol: str, 
    interval: str = "1d", 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> pd.DataFrame:
    """Fetch market data from InfluxDB.
    
    Args:
        symbol: Stock symbol
        interval: Time interval (e.g., '1d', '1h')
        start_date: Start date
        end_date: End date
        limit: Maximum number of data points
        
    Returns:
        DataFrame with market data
    """
    try:
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=365)  # Default to last year
            
        # Convert to RFC3339 format for Flux
        start_date_str = start_date.isoformat() + "Z"
        end_date_str = end_date.isoformat() + "Z"
        
        # Build Flux query for OHLCV data
        query = f"""
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: {start_date_str}, stop: {end_date_str})
            |> filter(fn: (r) => r._measurement == "market_data_ohlcv")
            |> filter(fn: (r) => r.symbol == "{symbol}")
            |> filter(fn: (r) => r.interval == "{interval}")
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
            |> sort(columns: ["_time"], desc: false)
            |> limit(n: {limit})
        """
        
        # Execute the query
        result = influxdb_client.query(query)
        
        if not result:
            logger.warning(f"No market data found for {symbol}")
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(result)
        
        # Rename columns
        if "_time" in df.columns:
            df = df.rename(columns={"_time": "timestamp"})
            
        return df
    except Exception as e:
        logger.exception(f"Error fetching market data: {str(e)}")
        return pd.DataFrame()


async def fetch_technical_indicators(
    symbol: str, 
    interval: str = "1d", 
    indicators: Optional[List[str]] = None,
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> pd.DataFrame:
    """Fetch technical indicators from InfluxDB.
    
    Args:
        symbol: Stock symbol
        interval: Time interval (e.g., '1d', '1h')
        indicators: List of indicators to fetch (None for all)
        start_date: Start date
        end_date: End date
        limit: Maximum number of data points
        
    Returns:
        DataFrame with technical indicators
    """
    try:
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=365)  # Default to last year
            
        # Convert to RFC3339 format for Flux
        start_date_str = start_date.isoformat() + "Z"
        end_date_str = end_date.isoformat() + "Z"
        
        # Build indicator filter if provided
        indicator_filter = ""
        if indicators:
            indicator_list = '", "'.join(indicators)
            indicator_filter = f'|> filter(fn: (r) => contains(value: r._field, set: ["{indicator_list}"]))'
        
        # Build Flux query for technical indicators
        query = f"""
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: {start_date_str}, stop: {end_date_str})
            |> filter(fn: (r) => r._measurement == "technical_indicators")
            |> filter(fn: (r) => r.symbol == "{symbol}")
            |> filter(fn: (r) => r.interval == "{interval}")
            {indicator_filter}
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
            |> sort(columns: ["_time"], desc: false)
            |> limit(n: {limit})
        """
        
        # Execute the query
        result = influxdb_client.query(query)
        
        if not result:
            logger.warning(f"No technical indicators found for {symbol}")
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(result)
        
        # Rename columns
        if "_time" in df.columns:
            df = df.rename(columns={"_time": "timestamp"})
            
        return df
    except Exception as e:
        logger.exception(f"Error fetching technical indicators: {str(e)}")
        return pd.DataFrame()


async def fetch_news_by_id(news_id: int) -> Optional[Dict[str, Any]]:
    """Fetch news by ID from PostgreSQL.
    
    Args:
        news_id: News ID
        
    Returns:
        News data or None if not found
    """
    db = next(get_db())
    try:
        # Execute raw SQL query to get news data
        result = db.execute("""
            SELECT pn.id, pn.title, pn.summary, pn.source, pn.url, 
                   pn.published_at, pn.sentiment_score, pn.sentiment_magnitude,
                   string_agg(s.symbol, ',') as symbols
            FROM processed_news pn
            LEFT JOIN news_symbol_association nsa ON pn.id = nsa.news_id
            LEFT JOIN symbols s ON nsa.symbol = s.symbol
            WHERE pn.id = :news_id
            GROUP BY pn.id
        """, {"news_id": news_id}).fetchone()
        
        if not result:
            return None
            
        # Convert to dictionary
        news = dict(result._mapping)
        
        # Convert symbols to list
        if news.get("symbols"):
            news["symbols"] = news["symbols"].split(",")
        else:
            news["symbols"] = []
            
        # Convert datetime to string
        if news.get("published_at"):
            news["published_at"] = news["published_at"].isoformat()
            
        return news
    except Exception as e:
        logger.exception(f"Error fetching news by ID: {str(e)}")
        return None
    finally:
        db.close()


async def fetch_news_by_symbol(
    symbol: str, 
    limit: int = 10, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Fetch news by symbol from PostgreSQL.
    
    Args:
        symbol: Stock symbol
        limit: Maximum number of news items
        offset: Offset for pagination
        
    Returns:
        List of news data
    """
    db = next(get_db())
    try:
        # Execute raw SQL query to get news data
        result = db.execute("""
            SELECT pn.id, pn.title, pn.summary, pn.source, pn.url, 
                   pn.published_at, pn.sentiment_score, pn.sentiment_magnitude
            FROM processed_news pn
            JOIN news_symbol_association nsa ON pn.id = nsa.news_id
            WHERE nsa.symbol = :symbol
            ORDER BY pn.published_at DESC
            LIMIT :limit OFFSET :offset
        """, {"symbol": symbol, "limit": limit, "offset": offset}).fetchall()
        
        # Convert to list of dictionaries
        news_list = []
        for row in result:
            news = dict(row._mapping)
            
            # Convert datetime to string
            if news.get("published_at"):
                news["published_at"] = news["published_at"].isoformat()
                
            news_list.append(news)
            
        return news_list
    except Exception as e:
        logger.exception(f"Error fetching news by symbol: {str(e)}")
        return []
    finally:
        db.close() 