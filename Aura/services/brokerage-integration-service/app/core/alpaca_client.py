"""Alpaca API client utilities."""

import asyncio
from typing import Any, Dict, List, Optional

import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import get_logger

logger = get_logger(__name__)


def get_alpaca_client(settings: Optional[Settings] = None) -> REST:
    """Get an Alpaca REST API client.
    
    Args:
        settings: Settings instance
        
    Returns:
        Alpaca REST client
    """
    if settings is None:
        settings = get_settings()
        
    # Create and return the Alpaca client
    return tradeapi.REST(
        key_id=settings.ALPACA_API_KEY,
        secret_key=settings.ALPACA_API_SECRET,
        base_url="https://paper-api.alpaca.markets" if not settings.ENABLE_REAL_TRADING else "https://api.alpaca.markets"
    )


async def validate_alpaca_credentials(settings: Optional[Settings] = None) -> None:
    """Validate Alpaca API credentials by making a test API call.
    
    Args:
        settings: Settings instance
        
    Raises:
        Exception: If the API call fails
    """
    if settings is None:
        settings = get_settings()
    
    # Create a client
    client = get_alpaca_client(settings)
    
    # Run the API call in a thread pool executor since Alpaca's API is synchronous
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, client.get_account)


async def get_positions(
    symbol: Optional[str] = None,
    settings: Optional[Settings] = None
) -> List[Dict[str, Any]]:
    """Get positions from Alpaca.
    
    Args:
        symbol: Optional symbol to filter by
        settings: Settings instance
        
    Returns:
        List of positions
        
    Raises:
        Exception: If the API call fails
    """
    if settings is None:
        settings = get_settings()
    
    # Create a client
    client = get_alpaca_client(settings)
    
    try:
        # Run the API call in a thread pool executor since Alpaca's API is synchronous
        loop = asyncio.get_event_loop()
        positions = await loop.run_in_executor(None, client.list_positions)
        
        # Filter by symbol if provided
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        
        # Convert to dict for easier serialization
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "market_value": float(p.market_value),
                "avg_entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": float(p.unrealized_plpc),
                "side": p.side,
            }
            for p in positions
        ]
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        raise


async def submit_order(
    symbol: str,
    qty: float,
    side: str,
    type: str,
    time_in_force: str,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    settings: Optional[Settings] = None
) -> Dict[str, Any]:
    """Submit an order to Alpaca.
    
    Args:
        symbol: Asset symbol
        qty: Quantity of shares
        side: Order side (buy/sell)
        type: Order type (market/limit/stop/stop_limit)
        time_in_force: Time in force (day/gtc/opg/cls/ioc/fok)
        limit_price: Limit price for limit or stop-limit orders
        stop_price: Stop price for stop or stop-limit orders
        settings: Settings instance
        
    Returns:
        Order information
        
    Raises:
        Exception: If the API call fails
    """
    if settings is None:
        settings = get_settings()
    
    # Create a client
    client = get_alpaca_client(settings)
    
    # Check if real trading is enabled
    if not settings.ENABLE_REAL_TRADING:
        logger.warning(
            "Real trading disabled, order not submitted",
            extra={
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": type,
                "time_in_force": time_in_force,
                "limit_price": limit_price,
                "stop_price": stop_price
            }
        )
        
        # Return a simulated order response
        return {
            "id": "simulated-order-id",
            "client_order_id": "simulated-client-order-id",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "status": "pending",
            "created_at": None,
            "submitted_at": None,
            "filled_at": None,
            "filled_qty": 0,
            "filled_avg_price": 0,
            "simulation": True,
        }
    
    try:
        # Run the API call in a thread pool executor since Alpaca's API is synchronous
        loop = asyncio.get_event_loop()
        order = await loop.run_in_executor(
            None,
            lambda: client.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price
            )
        )
        
        # Convert to dict for easier serialization
        return {
            "id": order.id,
            "client_order_id": order.client_order_id,
            "symbol": order.symbol,
            "qty": float(order.qty),
            "side": order.side,
            "type": order.type,
            "time_in_force": order.time_in_force,
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
            "simulation": False,
        }
    except Exception as e:
        logger.error(f"Error submitting order: {str(e)}")
        raise


async def get_order(
    order_id: str,
    settings: Optional[Settings] = None
) -> Dict[str, Any]:
    """Get order information from Alpaca.
    
    Args:
        order_id: Order ID
        settings: Settings instance
        
    Returns:
        Order information
        
    Raises:
        Exception: If the API call fails
    """
    if settings is None:
        settings = get_settings()
    
    # Check if this is a simulated order ID (for testing)
    if order_id.startswith("simulated-"):
        logger.warning(f"Getting simulated order: {order_id}")
        return {
            "id": order_id,
            "symbol": "SIMULATION",
            "qty": 0,
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "status": "pending",
            "created_at": None,
            "simulation": True,
        }
    
    # Create a client
    client = get_alpaca_client(settings)
    
    try:
        # Run the API call in a thread pool executor since Alpaca's API is synchronous
        loop = asyncio.get_event_loop()
        order = await loop.run_in_executor(None, lambda: client.get_order(order_id))
        
        # Convert to dict for easier serialization
        return {
            "id": order.id,
            "client_order_id": order.client_order_id,
            "symbol": order.symbol,
            "qty": float(order.qty),
            "side": order.side,
            "type": order.type,
            "time_in_force": order.time_in_force,
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
            "simulation": False,
        }
    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        raise 