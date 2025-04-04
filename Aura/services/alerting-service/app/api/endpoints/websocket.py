"""WebSocket endpoints for real-time alerts."""

from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, Query
from starlette.websockets import WebSocketState

from aura_common.utils.logging import get_logger

from app.core.websocket_manager import manager

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws/alerts/{user_id}")
async def alerts_websocket(
    websocket: WebSocket,
    user_id: str,
) -> None:
    """WebSocket endpoint for real-time alerts.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
    """
    # Accept the connection
    try:
        await manager.connect(websocket, user_id)
        logger.info(f"WebSocket connection established for user {user_id}")
        
        try:
            # Wait for messages (client -> server)
            # This keeps the connection open
            while True:
                # We're not doing anything with messages from the client for now
                # Just keeping the connection alive
                message = await websocket.receive_text()
                logger.debug(f"Received message from user {user_id}: {message}")
        except WebSocketDisconnect:
            # Handle client disconnect
            manager.disconnect(websocket, user_id)
            logger.info(f"WebSocket connection closed for user {user_id}")
    except Exception as e:
        # Handle connection errors
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        manager.disconnect(websocket, user_id) 