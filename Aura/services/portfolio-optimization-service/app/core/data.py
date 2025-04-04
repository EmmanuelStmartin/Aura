"""Data access functions for portfolio optimization service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import influxdb_client


logger = get_logger(__name__)
settings = get_settings()


async def fetch_market_data(
    symbols: List[str], 
    interval: str = "1d", 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    limit: int = 252  # Default to ~1 year of trading days
) -> Dict[str, pd.DataFrame]:
    """Fetch market data for multiple symbols from InfluxDB.
    
    Args:
        symbols: List of stock symbols
        interval: Time interval (e.g., '1d', '1h')
        start_date: Start date
        end_date: End date
        limit: Maximum number of data points
        
    Returns:
        Dictionary mapping symbols to DataFrames with market data
    """
    result = {}
    
    try:
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=365)  # Default to last year
            
        # Convert to RFC3339 format for Flux
        start_date_str = start_date.isoformat() + "Z"
        end_date_str = end_date.isoformat() + "Z"
        
        # Create a comma-separated list of symbols
        symbols_str = '", "'.join(symbols)
        
        # Build Flux query for OHLCV data
        query = f"""
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: {start_date_str}, stop: {end_date_str})
            |> filter(fn: (r) => r._measurement == "market_data_ohlcv")
            |> filter(fn: (r) => contains(value: r.symbol, set: ["{symbols_str}"]))
            |> filter(fn: (r) => r.interval == "{interval}")
            |> pivot(rowKey: ["_time", "symbol"], columnKey: ["_field"], valueColumn: "_value")
            |> sort(columns: ["_time"], desc: false)
            |> limit(n: {limit})
        """
        
        # Execute the query
        query_result = influxdb_client.query(query)
        
        if not query_result:
            logger.warning(f"No market data found for symbols: {symbols}")
            return result
            
        # Convert to DataFrame
        df = pd.DataFrame(query_result)
        
        # Rename columns
        if "_time" in df.columns:
            df = df.rename(columns={"_time": "timestamp"})
        
        # Group data by symbol
        for symbol in symbols:
            symbol_data = df[df["symbol"] == symbol].copy()
            if not symbol_data.empty:
                # Set index to timestamp for easier calculations
                symbol_data = symbol_data.set_index("timestamp")
                result[symbol] = symbol_data
            else:
                logger.warning(f"No data found for symbol: {symbol}")
            
        return result
    except Exception as e:
        logger.exception(f"Error fetching market data: {str(e)}")
        return result


async def calculate_returns(market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculate daily returns from market data.
    
    Args:
        market_data: Dictionary mapping symbols to market data DataFrames
        
    Returns:
        DataFrame with daily returns for each symbol
    """
    returns_dict = {}
    
    try:
        # Calculate returns for each symbol
        for symbol, df in market_data.items():
            if not df.empty and "close" in df.columns:
                # Calculate daily returns
                returns = df["close"].pct_change().dropna()
                returns_dict[symbol] = returns
        
        # Combine returns into a single DataFrame
        if returns_dict:
            returns_df = pd.DataFrame(returns_dict)
            
            # Fill missing values with 0
            returns_df = returns_df.fillna(0)
            
            return returns_df
        else:
            return pd.DataFrame()
    except Exception as e:
        logger.exception(f"Error calculating returns: {str(e)}")
        return pd.DataFrame() 