"""Positions API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import get_logger

from app.core.alpaca_client import get_positions
from app.schemas.brokerage import Position, PositionList

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=PositionList)
async def get_all_positions(
    settings: Settings = Depends(get_settings),
) -> PositionList:
    """Get all positions.
    
    Args:
        settings: Settings instance
        
    Returns:
        List of positions
        
    Raises:
        HTTPException: If there's an error getting positions
    """
    try:
        positions = await get_positions(settings=settings)
        return PositionList(positions=positions)
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting positions: {str(e)}",
        )


@router.get("/{symbol}", response_model=Position)
async def get_position_by_symbol(
    symbol: str,
    settings: Settings = Depends(get_settings),
) -> Position:
    """Get position for a specific symbol.
    
    Args:
        symbol: Asset symbol
        settings: Settings instance
        
    Returns:
        Position information
        
    Raises:
        HTTPException: If the position is not found or there's an error
    """
    try:
        positions = await get_positions(symbol=symbol, settings=settings)
        
        if not positions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Position not found for symbol: {symbol}",
            )
            
        return positions[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting position for symbol {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting position: {str(e)}",
        ) 