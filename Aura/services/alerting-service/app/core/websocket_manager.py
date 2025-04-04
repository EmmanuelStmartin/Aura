"""WebSocket connection manager for the Alerting Service."""

from typing import Dict, List, Set

from fastapi import WebSocket
from aura_common.utils.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        """Initialize the connection manager."""
        # Map of user_id -> list of active connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Connect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Add the connection to the list of active connections for this user
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connection established for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Disconnect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        # Remove the connection from the list of active connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Remove the user from the active connections if there are no more connections
            if not self.active_connections[user_id]:
                self.active_connections.pop(user_id)
                
        logger.info(f"WebSocket connection closed for user {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str) -> None:
        """Send a message to a specific user.
        
        Args:
            message: Message to send
            user_id: User ID
        """
        if user_id in self.active_connections:
            disconnected_websockets = []
            
            # Send the message to all connections for this user
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")
                    disconnected_websockets.append(websocket)
            
            # Clean up any disconnected WebSockets
            for websocket in disconnected_websockets:
                self.disconnect(websocket, user_id)
    
    async def broadcast(self, message: str) -> None:
        """Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        disconnected_users = []
        
        # Send the message to all connections for all users
        for user_id, connections in self.active_connections.items():
            disconnected_websockets = []
            
            for websocket in connections:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message to user {user_id}: {str(e)}")
                    disconnected_websockets.append(websocket)
            
            # Clean up any disconnected WebSockets
            for websocket in disconnected_websockets:
                self.disconnect(websocket, user_id)
            
            # Mark the user for removal if there are no more connections
            if not self.active_connections.get(user_id, []):
                disconnected_users.append(user_id)
        
        # Clean up any disconnected users
        for user_id in disconnected_users:
            self.active_connections.pop(user_id, None)


# Create a global connection manager instance
manager = ConnectionManager() 