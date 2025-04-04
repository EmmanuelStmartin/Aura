"""Brokerage schemas."""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class OrderSide(str, Enum):
    """Order side enumeration."""
    
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration."""
    
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderTimeInForce(str, Enum):
    """Order time in force enumeration."""
    
    DAY = "day"
    GTC = "gtc"  # Good Till Canceled
    OPG = "opg"  # Market on Open
    CLS = "cls"  # Market on Close
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill


class OrderStatus(str, Enum):
    """Order status enumeration."""
    
    PENDING_NEW = "pending_new"
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    DONE_FOR_DAY = "done_for_day"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING_CANCEL = "pending_cancel"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    PENDING = "pending"  # Used for simulated orders


class Position(BaseModel):
    """Position model."""
    
    symbol: str = Field(..., description="Asset symbol")
    qty: float = Field(..., description="Quantity of shares")
    market_value: float = Field(..., description="Current market value")
    avg_entry_price: float = Field(..., description="Average entry price")
    current_price: float = Field(..., description="Current price")
    unrealized_pl: float = Field(..., description="Unrealized profit/loss")
    unrealized_plpc: float = Field(..., description="Unrealized profit/loss percentage")
    side: str = Field(..., description="Position side (long/short)")


class OrderRequest(BaseModel):
    """Order request model."""
    
    symbol: str = Field(..., description="Asset symbol")
    qty: float = Field(..., description="Quantity of shares")
    side: OrderSide = Field(..., description="Order side")
    type: OrderType = Field(..., description="Order type")
    time_in_force: OrderTimeInForce = Field(..., description="Time in force")
    limit_price: Optional[float] = Field(None, description="Limit price for limit or stop-limit orders")
    stop_price: Optional[float] = Field(None, description="Stop price for stop or stop-limit orders")
    
    @validator("limit_price")
    def validate_limit_price(cls, v, values):
        """Validate limit price.
        
        Args:
            v: Limit price
            values: Other field values
            
        Returns:
            Validated limit price
            
        Raises:
            ValueError: If limit price is missing for limit order
        """
        if values.get("type") in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError("Limit price is required for limit or stop-limit orders")
        return v
    
    @validator("stop_price")
    def validate_stop_price(cls, v, values):
        """Validate stop price.
        
        Args:
            v: Stop price
            values: Other field values
            
        Returns:
            Validated stop price
            
        Raises:
            ValueError: If stop price is missing for stop order
        """
        if values.get("type") in [OrderType.STOP, OrderType.STOP_LIMIT] and v is None:
            raise ValueError("Stop price is required for stop or stop-limit orders")
        return v


class Order(BaseModel):
    """Order model."""
    
    id: str = Field(..., description="Order ID")
    client_order_id: Optional[str] = Field(None, description="Client order ID")
    symbol: str = Field(..., description="Asset symbol")
    qty: float = Field(..., description="Quantity of shares")
    side: str = Field(..., description="Order side")
    type: str = Field(..., description="Order type")
    time_in_force: str = Field(..., description="Time in force")
    limit_price: Optional[float] = Field(None, description="Limit price")
    stop_price: Optional[float] = Field(None, description="Stop price")
    status: str = Field(..., description="Order status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    submitted_at: Optional[str] = Field(None, description="Submission timestamp")
    filled_at: Optional[str] = Field(None, description="Fill timestamp")
    filled_qty: Optional[float] = Field(0, description="Filled quantity")
    filled_avg_price: Optional[float] = Field(0, description="Filled average price")
    simulation: Optional[bool] = Field(False, description="Whether this is a simulated order")


class PositionList(BaseModel):
    """List of positions."""
    
    positions: List[Position] = Field(..., description="List of positions") 