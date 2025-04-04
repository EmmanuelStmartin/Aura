"""Market data endpoints for data ingestion service."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.connectors import get_data_connector
from app.core.kafka import message_publisher
from app.models.schema import (
    AssetSearchRequest,
    DataSourceType,
    DataType,
    MarketDataRequest,
    TimeInterval,
)


logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


@router.post("/fetch", status_code=status.HTTP_202_ACCEPTED)
async def fetch_market_data(
    request: MarketDataRequest,
) -> Dict[str, Any]:
    """Fetch market data for symbols and publish to Kafka.
    
    Args:
        request: Market data request
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If data fetch fails
    """
    try:
        # Get the data connector
        connector = get_data_connector(request.source)
        await connector.connect()
        
        # Fetch data for each symbol
        results = {}
        for symbol in request.symbols:
            try:
                df = await connector.get_price_data(
                    symbol=symbol,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    interval=request.interval,
                )
                
                if df.empty:
                    logger.warning(f"No data found for {symbol}")
                    results[symbol] = False
                    continue
                
                # Convert to records (list of dicts) for JSON serialization
                records = df.reset_index().to_dict(orient="records")
                
                # Publish to Kafka
                await message_publisher.publish_market_data(
                    symbol=symbol,
                    data=records,
                    source=request.source,
                    data_type=DataType.MARKET_DATA,
                    metadata={
                        "interval": request.interval,
                        "start_date": request.start_date.isoformat() if request.start_date else None,
                        "end_date": request.end_date.isoformat() if request.end_date else None,
                    }
                )
                
                results[symbol] = True
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
                results[symbol] = False
                
        # Disconnect from data source
        await connector.disconnect()
        
        # Return status for each symbol
        return {
            "status": "accepted",
            "message": "Market data fetch request accepted",
            "results": results
        }
    except Exception as e:
        logger.error(f"Market data fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market data fetch failed: {str(e)}",
        )


@router.post("/assets/search", response_model=List[Dict[str, Any]])
async def search_assets(
    request: AssetSearchRequest,
) -> List[Dict[str, Any]]:
    """Search for assets.
    
    Args:
        request: Asset search request
        
    Returns:
        List of asset information
        
    Raises:
        HTTPException: If search fails
    """
    try:
        # Get the data connector
        connector = get_data_connector(request.source)
        await connector.connect()
        
        # Search for assets
        results = await connector.search_assets(query=request.query)
        
        # Disconnect from data source
        await connector.disconnect()
        
        return results
    except Exception as e:
        logger.error(f"Asset search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Asset search failed: {str(e)}",
        )


@router.get("/assets/{symbol}", response_model=Dict[str, Any])
async def get_asset_info(
    symbol: str,
    source: DataSourceType = Query(DataSourceType.ALPACA),
) -> Dict[str, Any]:
    """Get information about an asset.
    
    Args:
        symbol: Asset symbol
        source: Data source
        
    Returns:
        Asset information
        
    Raises:
        HTTPException: If asset not found or fetch fails
    """
    try:
        # Get the data connector
        connector = get_data_connector(source)
        await connector.connect()
        
        # Get asset info
        result = await connector.get_asset_info(symbol=symbol)
        
        # Disconnect from data source
        await connector.disconnect()
        
        return result
    except ValueError as e:
        logger.error(f"Asset not found: {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset not found: {symbol}",
        )
    except Exception as e:
        logger.error(f"Asset info fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Asset info fetch failed: {str(e)}",
        ) 