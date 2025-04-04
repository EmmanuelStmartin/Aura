"""Validation utilities for Aura services."""

import re
from typing import Optional


def validate_symbol(symbol: str) -> bool:
    """Validate asset symbol format.
    
    Args:
        symbol: Asset symbol
        
    Returns:
        Whether the symbol is valid
    """
    # Basic validation for stock/ETF symbols
    # This is a simple example - in production, you'd have more sophisticated validation
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    return bool(re.match(pattern, symbol)) 