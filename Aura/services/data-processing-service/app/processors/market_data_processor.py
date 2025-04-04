"""Market data processor for raw market data."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import pandas_ta as ta
from influxdb_client import Point

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.database import influxdb_client


logger = get_logger(__name__)
settings = get_settings()


async def process_market_data(data: Dict[str, Any]) -> None:
    """Process raw market data.
    
    Args:
        data: Raw market data from Kafka
    """
    logger.info(f"Processing market data for symbol: {data.get('symbol')}")
    
    try:
        # Extract data
        symbol = data.get("symbol")
        interval = data.get("interval", "1d")
        bars = data.get("bars", [])
        
        if not symbol or not bars:
            logger.warning("Missing symbol or bars in market data")
            return
            
        # Convert to DataFrame for calculating indicators
        df = pd.DataFrame(bars)
        
        # Ensure timestamp column exists and convert to datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            logger.warning("Missing timestamp column in market data")
            return
            
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Write OHLCV data to InfluxDB
        await write_ohlcv_to_influxdb(symbol, interval, df)
        
        # Write technical indicators to InfluxDB
        await write_indicators_to_influxdb(symbol, interval, df)
        
        logger.info(f"Successfully processed market data for symbol: {symbol}")
    except Exception as e:
        logger.exception(f"Error processing market data: {str(e)}")


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for a DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added technical indicators
    """
    # Ensure proper column names
    required_cols = {"open", "high", "low", "close", "volume"}
    if not set(df.columns).issuperset(required_cols):
        logger.warning(f"DataFrame missing required columns: {required_cols - set(df.columns)}")
        # Try to rename columns if possible
        if "o" in df.columns: df = df.rename(columns={"o": "open"})
        if "h" in df.columns: df = df.rename(columns={"h": "high"})
        if "l" in df.columns: df = df.rename(columns={"l": "low"})
        if "c" in df.columns: df = df.rename(columns={"c": "close"})
        if "v" in df.columns: df = df.rename(columns={"v": "volume"})
    
    # Calculate Simple Moving Averages
    df["sma_20"] = ta.sma(df["close"], length=20)
    df["sma_50"] = ta.sma(df["close"], length=50)
    df["sma_200"] = ta.sma(df["close"], length=200)
    
    # Calculate Exponential Moving Averages
    df["ema_9"] = ta.ema(df["close"], length=9)
    df["ema_20"] = ta.ema(df["close"], length=20)
    
    # Calculate RSI
    df["rsi_14"] = ta.rsi(df["close"], length=14)
    
    # Calculate MACD
    macd = ta.macd(df["close"])
    df = pd.concat([df, macd], axis=1)
    
    # Calculate Bollinger Bands
    bbands = ta.bbands(df["close"])
    df = pd.concat([df, bbands], axis=1)
    
    return df


async def write_ohlcv_to_influxdb(symbol: str, interval: str, df: pd.DataFrame) -> None:
    """Write OHLCV data to InfluxDB.
    
    Args:
        symbol: Stock symbol
        interval: Time interval (e.g., '1d', '1h')
        df: DataFrame with OHLCV data
    """
    points = []
    
    for _, row in df.iterrows():
        point = Point("market_data_ohlcv") \
            .tag("symbol", symbol) \
            .tag("interval", interval) \
            .field("open", float(row["open"])) \
            .field("high", float(row["high"])) \
            .field("low", float(row["low"])) \
            .field("close", float(row["close"])) \
            .field("volume", float(row["volume"])) \
            .time(row["timestamp"])
            
        points.append(point)
    
    # Write points to InfluxDB
    influxdb_client.write_points(points)
    
    logger.info(f"Wrote {len(points)} OHLCV points to InfluxDB for {symbol}")


async def write_indicators_to_influxdb(symbol: str, interval: str, df: pd.DataFrame) -> None:
    """Write technical indicators to InfluxDB.
    
    Args:
        symbol: Stock symbol
        interval: Time interval (e.g., '1d', '1h')
        df: DataFrame with technical indicators
    """
    points = []
    
    # Indicators to write (exclude OHLCV data)
    indicator_columns = [col for col in df.columns if col not in ["open", "high", "low", "close", "volume", "timestamp"]]
    
    for _, row in df.iterrows():
        # Skip rows with missing indicator values (e.g., at the beginning of the series)
        if all(pd.isna(row[col]) for col in indicator_columns):
            continue
            
        point = Point("technical_indicators") \
            .tag("symbol", symbol) \
            .tag("interval", interval) \
            .time(row["timestamp"])
            
        # Add indicators as fields
        for col in indicator_columns:
            if not pd.isna(row[col]):
                point = point.field(col, float(row[col]))
                
        points.append(point)
    
    # Write points to InfluxDB
    influxdb_client.write_points(points)
    
    logger.info(f"Wrote {len(points)} technical indicator points to InfluxDB for {symbol}") 