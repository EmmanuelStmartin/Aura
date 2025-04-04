"""Alerts API gateway endpoints."""

import httpx
from typing import Any

from fastapi import APIRouter, Depends, Request, Response, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

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
async def alerts_proxy(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Proxy requests to the alerting service.
    
    Args:
        path: Path to forward to alerting service
        request: FastAPI request
        settings: Settings instance
        
    Returns:
        Response from alerting service
    """
    # Construct the target URL
    target_url = f"{settings.ALERTING_SERVICE_URL}{settings.API_PREFIX}/{path}"
    
    # Forward the request to the alerting service
    return await proxy_request(
        target_url=target_url,
        request=request,
        service_name="alerting service"
    )


@router.websocket("/ws/alerts/{user_id}")
async def alerts_websocket(
    websocket: WebSocket,
    user_id: str,
    settings: Settings = Depends(get_settings),
) -> None:
    """WebSocket endpoint for real-time alerts.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
        settings: Settings instance
    """
    target_url = f"{settings.ALERTING_SERVICE_URL}/ws/alerts/{user_id}"
    logger.info(f"Establishing WebSocket connection to: {target_url}")
    
    try:
        # Accept the connection from the client
        await websocket.accept()
        
        # Create a client to connect to the alerting service
        async with httpx.AsyncClient() as client:
            # Connect to the alerts WebSocket on the alerting service
            async with client.stream("GET", target_url) as response:
                # Check if we got a successful response
                if response.status_code != 101:  # 101 Switching Protocols (WebSocket)
                    logger.error(f"Failed to establish WebSocket connection: {response.status_code}")
                    if websocket.client_state != WebSocketState.DISCONNECTED:
                        await websocket.close(code=1011, reason="Server error")
                    return
                
                # Set up a task to forward messages from alerting service to client
                async for message in response.aiter_bytes():
                    if websocket.client_state == WebSocketState.DISCONNECTED:
                        break
                    await websocket.send_bytes(message)
    except WebSocketDisconnect as e:
        logger.info(f"WebSocket disconnected: {str(e)}", extra={"user_id": user_id})
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", extra={"user_id": user_id})
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=1011, reason="Server error") 