"""Market data API gateway endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Request, Response

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import get_logger

from app.api.utils import proxy_request

logger = get_logger(__name__)
router = APIRouter()


@router.api_route(
    "/assets/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    include_in_schema=False,
)
async def assets_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the assets endpoints in data ingestion service.
    
    Args:
        path: Path to forward to data ingestion service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from data ingestion service
    """
    # Construct the target URL
    target_url = f"{settings.DATA_INGESTION_SERVICE_URL}{settings.API_PREFIX}/assets/{path}"
    
    # Forward the request to the data ingestion service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="market data service"
    )


@router.api_route(
    "/historical/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    include_in_schema=False,
)
async def historical_data_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the historical data endpoints in data ingestion service.
    
    Args:
        path: Path to forward to data ingestion service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from data ingestion service
    """
    # Construct the target URL
    target_url = f"{settings.DATA_INGESTION_SERVICE_URL}{settings.API_PREFIX}/historical/{path}"
    
    # Forward the request to the data ingestion service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="market data service"
    )


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    include_in_schema=False,
)
async def market_data_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the data ingestion service.
    
    Args:
        path: Path to forward to data ingestion service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from data ingestion service
    """
    # Construct the target URL
    target_url = f"{settings.DATA_INGESTION_SERVICE_URL}{settings.API_PREFIX}/{path}"
    
    # Forward the request to the data ingestion service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="market data service"
    ) 