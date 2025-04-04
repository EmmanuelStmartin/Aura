"""Asset models for Aura services."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    """Asset class enumeration."""
    
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    OTHER = "other"


class AssetType(str, Enum):
    """Asset type enumeration."""
    
    STOCK = "stock"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    BOND = "bond"
    OPTION = "option"
    FUTURE = "future"
    FOREX = "forex"
    CRYPTO = "crypto"
    REIT = "reit"
    OTHER = "other"


class Asset(BaseModel):
    """Asset model."""
    
    symbol: str = Field(..., description="Asset symbol")
    name: str = Field(..., description="Asset name")
    asset_class: AssetClass = Field(..., description="Asset class")
    asset_type: AssetType = Field(..., description="Asset type")
    exchange: Optional[str] = Field(None, description="Exchange where the asset is traded")
    currency: str = Field("USD", description="Currency of the asset")
    country: Optional[str] = Field(None, description="Country of the asset")
    sector: Optional[str] = Field(None, description="Sector of the asset")
    industry: Optional[str] = Field(None, description="Industry of the asset")
    description: Optional[str] = Field(None, description="Asset description")
    is_tradable: bool = Field(True, description="Whether the asset is tradable")
    
    class Config:
        """Pydantic model configuration."""
        
        use_enum_values = True 