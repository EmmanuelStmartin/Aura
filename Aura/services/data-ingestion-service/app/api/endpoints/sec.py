"""SEC filing endpoints for data ingestion service."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.connectors import get_sec_filing_connector
from app.core.kafka import message_publisher
from app.models.schema import DataSourceType, SECFilingRequest


logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


@router.post("/filings", status_code=status.HTTP_202_ACCEPTED)
async def fetch_sec_filings(
    request: SECFilingRequest,
    source: DataSourceType = Query(DataSourceType.SEC_EDGAR, description="Filing source"),
) -> Dict[str, Any]:
    """Fetch SEC filings and publish to Kafka.
    
    Args:
        request: SEC filing request
        source: Filing source
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If filing fetch fails
    """
    try:
        # Get the SEC filing connector
        connector = get_sec_filing_connector(source)
        await connector.connect()
        
        # Fetch filings
        filings = await connector.get_filings(
            symbol=request.symbol,
            form_type=request.form_type,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit,
        )
        
        # Get content for each filing if requested
        if request.include_content and filings:
            for i, filing in enumerate(filings):
                try:
                    content = await connector.get_filing_content(filing["filing_url"])
                    filings[i]["content"] = content
                except Exception as e:
                    logger.error(f"Failed to get content for filing: {str(e)}")
                    filings[i]["content_error"] = str(e)
        
        # Disconnect from filing source
        await connector.disconnect()
        
        if not filings:
            return {
                "status": "success",
                "message": "No filings found",
                "count": 0
            }
        
        # Publish to Kafka
        for filing in filings:
            content = filing.pop("content", None) if "content" in filing else None
            
            await message_publisher.publish_sec_filing(
                filing=filing,
                source=source,
                content=content,
                metadata={
                    "form_type": request.form_type,
                    "start_date": request.start_date.isoformat() if request.start_date else None,
                    "end_date": request.end_date.isoformat() if request.end_date else None,
                }
            )
        
        return {
            "status": "accepted",
            "message": "SEC filing fetch request accepted",
            "count": len(filings)
        }
    except ValueError as e:
        logger.error(f"SEC filing fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"SEC filing fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SEC filing fetch failed: {str(e)}",
        )


@router.get("/filings/{symbol}/latest", response_model=Dict[str, Any])
async def get_latest_filing(
    symbol: str,
    form_type: str = Query("10-Q", description="Filing form type"),
    source: DataSourceType = Query(DataSourceType.SEC_EDGAR, description="Filing source"),
) -> Dict[str, Any]:
    """Get the latest filing for a symbol.
    
    Args:
        symbol: Asset symbol
        form_type: Filing form type
        source: Filing source
        
    Returns:
        Filing data
        
    Raises:
        HTTPException: If filing not found or fetch fails
    """
    try:
        # Get the SEC filing connector
        connector = get_sec_filing_connector(source)
        await connector.connect()
        
        # Fetch the latest filing
        filings = await connector.get_filings(
            symbol=symbol,
            form_type=form_type,
            limit=1,
        )
        
        # Disconnect from filing source
        await connector.disconnect()
        
        if not filings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {form_type} filings found for {symbol}",
            )
        
        return filings[0]
    except ValueError as e:
        logger.error(f"Latest filing fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Latest filing fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Latest filing fetch failed: {str(e)}",
        )


@router.get("/financial-data/{symbol}", response_model=Dict[str, Any])
async def get_financial_data(
    symbol: str,
    form_type: str = Query("10-Q", description="Filing form type"),
    source: DataSourceType = Query(DataSourceType.SEC_EDGAR, description="Filing source"),
) -> Dict[str, Any]:
    """Get financial data from the latest filing for a symbol.
    
    Args:
        symbol: Asset symbol
        form_type: Filing form type
        source: Filing source
        
    Returns:
        Financial data
        
    Raises:
        HTTPException: If data not found or fetch fails
    """
    try:
        # Get the SEC filing connector
        connector = get_sec_filing_connector(source)
        await connector.connect()
        
        # Extract financial data
        # Note: This is SEC Edgar-specific, we're checking for the specific method
        if not hasattr(connector, "extract_financial_data"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The selected source ({source}) does not support financial data extraction",
            )
            
        financial_data = await connector.extract_financial_data(
            symbol=symbol,
            form_type=form_type,
        )
        
        # Disconnect from filing source
        await connector.disconnect()
        
        return financial_data
    except ValueError as e:
        logger.error(f"Financial data fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Financial data fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Financial data fetch failed: {str(e)}",
        ) 