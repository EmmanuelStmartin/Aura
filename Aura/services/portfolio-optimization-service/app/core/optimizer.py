"""Portfolio optimization functions."""

from typing import Dict, List, Optional, Any, Tuple

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions

from aura_common.utils.logging import get_logger


logger = get_logger(__name__)


async def optimize_maximum_sharpe(
    returns: pd.DataFrame, 
    risk_free_rate: float = 0.02,
    weight_bounds: Tuple[float, float] = (0, 1)
) -> Dict[str, Any]:
    """Optimize portfolio for maximum Sharpe ratio.
    
    Args:
        returns: DataFrame with daily returns for each symbol
        risk_free_rate: Risk-free rate (annualized)
        weight_bounds: Minimum and maximum weight for each asset
        
    Returns:
        Optimization results
    """
    try:
        if returns.empty:
            return {
                "error": "No returns data available"
            }
        
        # Calculate expected returns (simple mean of historical returns)
        mu = expected_returns.mean_historical_return(returns)
        
        # Calculate sample covariance
        S = risk_models.sample_cov(returns)
        
        # Create efficient frontier object
        ef = EfficientFrontier(mu, S, weight_bounds=weight_bounds)
        
        # Find maximum Sharpe ratio portfolio
        ef.max_sharpe(risk_free_rate=risk_free_rate)
        
        # Get clean weights (eliminating very small weights)
        weights = ef.clean_weights()
        
        # Get performance metrics
        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)
        
        # Extract metrics
        expected_return, expected_volatility, sharpe_ratio = performance
        
        # Format results
        result = {
            "weights": dict(weights),
            "performance": {
                "expected_annual_return": float(expected_return),
                "expected_volatility": float(expected_volatility),
                "sharpe_ratio": float(sharpe_ratio)
            }
        }
        
        return result
    except Exception as e:
        logger.exception(f"Error optimizing portfolio for maximum Sharpe ratio: {str(e)}")
        return {
            "error": f"Optimization failed: {str(e)}"
        }


async def optimize_minimum_volatility(
    returns: pd.DataFrame,
    target_return: Optional[float] = None,
    risk_free_rate: float = 0.02,
    weight_bounds: Tuple[float, float] = (0, 1)
) -> Dict[str, Any]:
    """Optimize portfolio for minimum volatility.
    
    Args:
        returns: DataFrame with daily returns for each symbol
        target_return: Target return (None for global minimum volatility)
        risk_free_rate: Risk-free rate (annualized)
        weight_bounds: Minimum and maximum weight for each asset
        
    Returns:
        Optimization results
    """
    try:
        if returns.empty:
            return {
                "error": "No returns data available"
            }
        
        # Calculate expected returns (simple mean of historical returns)
        mu = expected_returns.mean_historical_return(returns)
        
        # Calculate sample covariance
        S = risk_models.sample_cov(returns)
        
        # Create efficient frontier object
        ef = EfficientFrontier(mu, S, weight_bounds=weight_bounds)
        
        # Find minimum volatility portfolio, optionally with target return
        if target_return is not None:
            ef.efficient_risk(target_volatility=None, target_return=target_return)
        else:
            ef.min_volatility()
        
        # Get clean weights (eliminating very small weights)
        weights = ef.clean_weights()
        
        # Get performance metrics
        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)
        
        # Extract metrics
        expected_return, expected_volatility, sharpe_ratio = performance
        
        # Format results
        result = {
            "weights": dict(weights),
            "performance": {
                "expected_annual_return": float(expected_return),
                "expected_volatility": float(expected_volatility),
                "sharpe_ratio": float(sharpe_ratio)
            }
        }
        
        return result
    except Exception as e:
        logger.exception(f"Error optimizing portfolio for minimum volatility: {str(e)}")
        return {
            "error": f"Optimization failed: {str(e)}"
        } 