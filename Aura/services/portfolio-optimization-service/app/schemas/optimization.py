"""Pydantic models for portfolio optimization service."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field, root_validator, validator


class DateRange(BaseModel):
    """Date range for fetching market data."""
    
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")


class OptimizationConstraints(BaseModel):
    """Constraints for portfolio optimization."""
    
    min_weight: float = Field(0.0, description="Minimum weight for each asset", ge=0.0, le=1.0)
    max_weight: float = Field(1.0, description="Maximum weight for each asset", ge=0.0, le=1.0)
    
    @validator("max_weight")
    def max_weight_must_be_greater_than_min(cls, v, values):
        """Validate that max_weight is greater than min_weight."""
        if "min_weight" in values and v < values["min_weight"]:
            raise ValueError("max_weight must be greater than or equal to min_weight")
        return v


class PortfolioPerformance(BaseModel):
    """Portfolio performance metrics."""
    
    expected_annual_return: float = Field(..., description="Expected annual return")
    expected_volatility: float = Field(..., description="Expected annual volatility (standard deviation)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")


class MaximizeSharpeRequest(BaseModel):
    """Request for maximizing Sharpe ratio."""
    
    symbols: List[str] = Field(..., description="List of asset symbols", min_items=2)
    risk_free_rate: float = Field(0.02, description="Risk-free rate (annualized)")
    date_range: Optional[DateRange] = Field(None, description="Date range for historical data")
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints, description="Optimization constraints")


class MinimizeVolatilityRequest(BaseModel):
    """Request for minimizing volatility."""
    
    symbols: List[str] = Field(..., description="List of asset symbols", min_items=2)
    target_return: Optional[float] = Field(None, description="Target annual return (None for global minimum volatility)")
    risk_free_rate: float = Field(0.02, description="Risk-free rate (annualized)")
    date_range: Optional[DateRange] = Field(None, description="Date range for historical data")
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints, description="Optimization constraints")


class ScenarioAnalysisRequest(BaseModel):
    """Request for scenario analysis."""
    
    symbols: List[str] = Field(..., description="List of asset symbols", min_items=2)
    weights: Dict[str, float] = Field(..., description="Portfolio weights")
    scenarios: Dict[str, Dict[str, float]] = Field(..., description="Scenarios to analyze (name: {symbol: return_change})")
    date_range: Optional[DateRange] = Field(None, description="Date range for historical data")
    
    @validator("weights")
    def weights_must_sum_to_one(cls, v):
        """Validate that weights sum to approximately 1."""
        total = sum(v.values())
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"Weights must sum to approximately 1.0, got {total}")
        return v


class OptimizationResponse(BaseModel):
    """Response for portfolio optimization."""
    
    weights: Dict[str, float] = Field(..., description="Optimized portfolio weights")
    performance: PortfolioPerformance = Field(..., description="Portfolio performance metrics")


class ScenarioAnalysisResponse(BaseModel):
    """Response for scenario analysis."""
    
    base_performance: PortfolioPerformance = Field(..., description="Base portfolio performance")
    scenarios: Dict[str, PortfolioPerformance] = Field(..., description="Performance under different scenarios")
    message: str = Field("Scenario analysis not implemented in MVP", description="Status message") 