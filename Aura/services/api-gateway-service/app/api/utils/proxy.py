"""Proxy utility functions for the API Gateway Service."""

import httpx
from typing import Any, Dict, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from aura_common.config import Settings
from aura_common.utils.logging import get_logger

logger = get_logger(__name__)


async def proxy_request(
    target_url: str,
    request: Request,
    timeout: float = 30.0,
    service_name: str = "downstream service"
) -> Response:
    """Proxy a request to a downstream service.
    
    Args:
        target_url: URL to forward the request to
        request: FastAPI request
        timeout: Request timeout in seconds
        service_name: Name of the service (for logging)
        
    Returns:
        Response from the downstream service
    """
    logger.debug(f"Forwarding request to: {target_url}")
    
    # Get the request body
    body = await request.body()
    
    # Forward headers, except host which would cause issues
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    
    # Add our request ID to the outgoing request
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        headers["X-Request-ID"] = request_id
    
    # Forward authenticated user info if available
    if hasattr(request.state, "user"):
        headers["X-User-Email"] = getattr(request.state.user, "email", "")
        headers["X-User-Role"] = getattr(request.state.user, "role", "")
    
    try:
        async with httpx.AsyncClient() as client:
            # Forward the request to the downstream service
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=timeout,
            )
            
            # Return the response from the downstream service
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
    except httpx.RequestError as exc:
        logger.error(
            f"Error forwarding request to {service_name}: {str(exc)}",
            extra={"target_url": target_url, "request_id": request_id}
        )
        # Return a gateway error response
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": f"Error communicating with {service_name}"},
        )
    except httpx.TimeoutException as exc:
        logger.error(
            f"Timeout forwarding request to {service_name}: {str(exc)}",
            extra={"target_url": target_url, "request_id": request_id}
        )
        # Return a timeout error response
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": f"{service_name.capitalize()} timed out"},
        ) 