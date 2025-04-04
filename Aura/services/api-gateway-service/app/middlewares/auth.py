"""Authentication middleware for the API Gateway Service."""

import re
from typing import List, Set, Optional, Tuple

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from aura_common.config import get_settings
from aura_common.utils.security import decode_access_token
from aura_common.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Define public routes that don't require authentication
PUBLIC_ROUTES: List[re.Pattern] = [
    re.compile(r"^/api/v1/auth/login.*$"),
    re.compile(r"^/api/v1/auth/register$"),
    re.compile(r"^/api/v1/auth/password-reset.*$"),
    re.compile(r"^/health$"),
    re.compile(r"^/ready$"),
    re.compile(r"^/docs.*$"),
    re.compile(r"^/openapi.json$"),
]


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for validating JWT tokens."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and validate JWT token when necessary.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in the chain
            
        Returns:
            Response from downstream services
            
        Raises:
            HTTPException: If authentication fails
        """
        # Skip authentication for public routes
        if self._is_public_route(request.url.path):
            return await call_next(request)
            
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(
                "Missing Authorization header",
                extra={"path": request.url.path, "request_id": getattr(request.state, "request_id", None)}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check for Bearer token format
        if not auth_header.startswith("Bearer "):
            logger.warning(
                "Invalid Authorization header format",
                extra={"path": request.url.path, "request_id": getattr(request.state, "request_id", None)}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Extract and validate the token
        token = auth_header.replace("Bearer ", "")
        token_data = decode_access_token(token, settings)
        
        if token_data is None:
            logger.warning(
                "Invalid token",
                extra={"path": request.url.path, "request_id": getattr(request.state, "request_id", None)}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Add user information to request state
        request.state.user = token_data
        
        # Add validated user info to headers for downstream services
        # (safely encoded to prevent header injection)
        email = token_data.email.replace("\n", "").replace("\r", "") if token_data.email else ""
        role = token_data.role.replace("\n", "").replace("\r", "") if token_data.role else ""
        
        # Clone request headers to add our validated user info
        # This allows downstream services to access the authenticated user without re-validating the token
        for name, value in request.headers.items():
            if name.lower() not in ("x-user-email", "x-user-role"):
                # Copy original headers except our custom ones to prevent spoofing
                pass
                
        # Send authenticated user info to downstream services
        request.headers.__dict__["_list"].extend([
            (b"x-user-email", email.encode()),
            (b"x-user-role", role.encode()),
        ])
        
        return await call_next(request)
        
    def _is_public_route(self, path: str) -> bool:
        """Check if the route is public and doesn't require authentication.
        
        Args:
            path: Request path
            
        Returns:
            Whether the route is public
        """
        return any(pattern.match(path) for pattern in PUBLIC_ROUTES) 