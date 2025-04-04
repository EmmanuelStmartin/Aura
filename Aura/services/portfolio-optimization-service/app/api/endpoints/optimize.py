"""Optimization endpoints for portfolio optimization service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.core.data import fetch_market_data, calculate_returns
from app.core.optimizer import optimize_maximum_sharpe, optimize_minimum_volatility
from app.schemas.optimization import (
    MaximizeSharpeRequest,
    MinimizeVolatilityRequest,
    ScenarioAnalysisRequest,
    OptimizationResponse,
    ScenarioAnalysisResponse,
    PortfolioPerformance
)


router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.post("/maximize-sharpe", response_model=OptimizationResponse)
async def maximize_sharpe(request: MaximizeSharpeRequest):
    """Optimize portfolio to maximize Sharpe ratio.
    
    Args:
        request: Maximizing Sharpe ratio request
        
    Returns:
        Optimization results
        
    Raises:
        HTTPException: If optimization fails
    """
    try:
        # Extract request parameters
        symbols = request.symbols
        risk_free_rate = request.risk_free_rate
        constraints = request.constraints
        
        # Set date range for historical data
        start_date = None
        end_date = None
        if request.date_range:
            start_date = request.date_range.start_date
            end_date = request.date_range.end_date
        
        # Fetch market data
        market_data = await fetch_market_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        # Check if we have data for all symbols
        missing_symbols = [symbol for symbol in symbols if symbol not in market_data]
        if missing_symbols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No market data found for symbols: {missing_symbols}"
            )
        
        # Calculate returns
        returns = await calculate_returns(market_data)
        
        if returns.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to calculate returns from market data"
            )
        
        # Optimize portfolio
        result = await optimize_maximum_sharpe(
            returns=returns,
            risk_free_rate=risk_free_rate,
            weight_bounds=(constraints.min_weight, constraints.max_weight)
        )
        
        # Check for optimization errors
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # Return optimization results
        return OptimizationResponse(
            weights=result["weights"],
            performance=PortfolioPerformance(**result["performance"])
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Error maximizing Sharpe ratio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error maximizing Sharpe ratio: {str(e)}"
        )


@router.post("/minimize-volatility", response_model=OptimizationResponse)
async def minimize_volatility(request: MinimizeVolatilityRequest):
    """Optimize portfolio to minimize volatility.
    
    Args:
        request: Minimizing volatility request
        
    Returns:
        Optimization results
        
    Raises:
        HTTPException: If optimization fails
    """
    try:
        # Extract request parameters
        symbols = request.symbols
        target_return = request.target_return
        risk_free_rate = request.risk_free_rate
        constraints = request.constraints
        
        # Set date range for historical data
        start_date = None
        end_date = None
        if request.date_range:
            start_date = request.date_range.start_date
            end_date = request.date_range.end_date
        
        # Fetch market data
        market_data = await fetch_market_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        # Check if we have data for all symbols
        missing_symbols = [symbol for symbol in symbols if symbol not in market_data]
        if missing_symbols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No market data found for symbols: {missing_symbols}"
            )
        
        # Calculate returns
        returns = await calculate_returns(market_data)
        
        if returns.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to calculate returns from market data"
            )
        
        # Optimize portfolio
        result = await optimize_minimum_volatility(
            returns=returns,
            target_return=target_return,
            risk_free_rate=risk_free_rate,
            weight_bounds=(constraints.min_weight, constraints.max_weight)
        )
        
        # Check for optimization errors
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # Return optimization results
        return OptimizationResponse(
            weights=result["weights"],
            performance=PortfolioPerformance(**result["performance"])
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Error minimizing volatility: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error minimizing volatility: {str(e)}"
        )


@router.post("/analyze/scenario", response_model=ScenarioAnalysisResponse)
async def analyze_scenario(request: ScenarioAnalysisRequest):
    """Analyze portfolio performance under different scenarios.
    
    Args:
        request: Scenario analysis request
        
    Returns:
        Scenario analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    # Placeholder for MVP - will be implemented post-MVP
    logger.info(f"Received scenario analysis request for symbols: {request.symbols}")
    
    # Create a placeholder response
    return ScenarioAnalysisResponse(
        base_performance=PortfolioPerformance(
            expected_annual_return=0.08,
            expected_volatility=0.15,
            sharpe_ratio=0.4
        ),
        scenarios={},
        message="Scenario analysis not implemented in MVP"
    ) 