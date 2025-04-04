"""Orders API endpoints."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import get_logger

from app.core.alpaca_client import submit_order, get_order
from app.schemas.brokerage import Order, OrderRequest

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_request: OrderRequest,
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Create a new order.
    
    Args:
        order_request: Order request model
        settings: Settings instance
        
    Returns:
        Order information
        
    Raises:
        HTTPException: If there's an error creating the order
    """
    try:
        # Submit the order
        order = await submit_order(
            symbol=order_request.symbol,
            qty=order_request.qty,
            side=order_request.side.value,
            type=order_request.type.value,
            time_in_force=order_request.time_in_force.value,
            limit_price=order_request.limit_price,
            stop_price=order_request.stop_price,
            settings=settings,
        )
        
        # Log whether this was a simulated order
        if order.get("simulation", False):
            logger.info(
                f"Created simulated order for {order_request.symbol}",
                extra={
                    "symbol": order_request.symbol,
                    "qty": order_request.qty,
                    "side": order_request.side.value,
                }
            )
        else:
            logger.info(
                f"Created order for {order_request.symbol}",
                extra={
                    "symbol": order_request.symbol,
                    "qty": order_request.qty,
                    "side": order_request.side.value,
                    "order_id": order.get("id"),
                }
            )
        
        return order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}",
        )


@router.get("/{order_id}", response_model=Order)
async def get_order_by_id(
    order_id: str = Path(..., description="Order ID"),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Get order information by ID.
    
    Args:
        order_id: Order ID
        settings: Settings instance
        
    Returns:
        Order information
        
    Raises:
        HTTPException: If the order is not found or there's an error
    """
    try:
        order = await get_order(order_id=order_id, settings=settings)
        return order
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting order: {str(e)}",
        ) 