"""Brokerage API gateway endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Request, Response

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import get_logger

from app.api.utils import proxy_request

logger = get_logger(__name__)
router = APIRouter()


@router.api_route(
    "/positions/{path:path}",
    methods=["GET"],
    include_in_schema=False,
)
async def positions_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the positions endpoints in brokerage integration service.
    
    Args:
        path: Path to forward to brokerage integration service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from brokerage integration service
    """
    # Construct the target URL
    target_url = f"{settings.BROKERAGE_INTEGRATION_SERVICE_URL}{settings.API_PREFIX}/positions/{path}"
    
    # Forward the request to the brokerage integration service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="brokerage service"
    )


@router.api_route(
    "/orders/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    include_in_schema=False,
)
async def orders_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the orders endpoints in brokerage integration service.
    
    Args:
        path: Path to forward to brokerage integration service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from brokerage integration service
    """
    # Construct the target URL
    target_url = f"{settings.BROKERAGE_INTEGRATION_SERVICE_URL}{settings.API_PREFIX}/orders/{path}"
    
    # Forward the request to the brokerage integration service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="brokerage service"
    )


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    include_in_schema=False,
)
async def brokerage_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the brokerage integration service.
    
    Args:
        path: Path to forward to brokerage integration service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from brokerage integration service
    """
    # Construct the target URL
    target_url = f"{settings.BROKERAGE_INTEGRATION_SERVICE_URL}{settings.API_PREFIX}/{path}"
    
    # Forward the request to the brokerage integration service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="brokerage service"
    ) 