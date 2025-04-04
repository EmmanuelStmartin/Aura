"""Authentication API gateway endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Response

from aura_common.config import Settings, get_settings
from aura_common.utils.logging import get_logger

from app.api.utils import proxy_request

logger = get_logger(__name__)
router = APIRouter()


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    include_in_schema=False,
)
async def auth_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the auth service.
    
    Args:
        path: Path to forward to auth service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from auth service
    """
    # Construct the target URL
    target_url = f"{settings.AUTH_SERVICE_URL}{settings.API_PREFIX}/auth/{path}"
    
    # Forward the request to the auth service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="authentication service"
    ) 