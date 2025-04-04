"""Authentication API endpoints."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from aura_common.config import Settings, get_settings
from aura_common.models.user import Token, UserCreate, User as UserModel
from aura_common.utils.logging import get_logger

from app.api.models import LoginRequest, PasswordResetRequest, PasswordResetConfirm
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    oauth2_scheme,
)
from app.core.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    revoke_token,
)
from app.db.session import get_db

logger = get_logger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Dict[str, str]:
    """Log in a user.
    
    Args:
        request: FastAPI request
        login_data: Login credentials
        db: Database session
        settings: Settings instance
        
    Returns:
        Token information
        
    Raises:
        HTTPException: If login fails
    """
    user_agent = request.headers.get("User-Agent")
    client_ip = request.client.host if request.client else None
    
    try:
        token_data = authenticate_user(
            db=db,
            email=login_data.email,
            password=login_data.password,
            user_agent=user_agent,
            ip_address=client_ip
        )
        
        logger.info(
            f"User logged in: {login_data.email}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": token_data["user_id"],
                "ip_address": client_ip,
            }
        )
        
        return {
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
        }
    except HTTPException as e:
        logger.warning(
            f"Login failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "email": login_data.email,
                "ip_address": client_ip,
            }
        )
        raise


@router.post("/login/form", response_model=Token)
async def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Dict[str, str]:
    """Log in a user using a form.
    
    Args:
        request: FastAPI request
        form_data: Form data
        db: Database session
        settings: Settings instance
        
    Returns:
        Token information
        
    Raises:
        HTTPException: If login fails
    """
    user_agent = request.headers.get("User-Agent")
    client_ip = request.client.host if request.client else None
    
    try:
        token_data = authenticate_user(
            db=db,
            email=form_data.username,  # OAuth2 uses 'username' field
            password=form_data.password,
            user_agent=user_agent,
            ip_address=client_ip
        )
        
        logger.info(
            f"User logged in via form: {form_data.username}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": token_data["user_id"],
                "ip_address": client_ip,
            }
        )
        
        return {
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
        }
    except HTTPException as e:
        logger.warning(
            f"Form login failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "email": form_data.username,
                "ip_address": client_ip,
            }
        )
        raise


@router.post("/register", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Register a new user.
    
    Args:
        request: FastAPI request
        user_create: User creation data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user = create_user(db=db, user_create=user_create)
        
        logger.info(
            f"User registered: {user.email}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user.id,
                "ip_address": request.client.host if request.client else None,
            }
        )
        
        # We don't want to return the hashed password
        user.hashed_password = "REDACTED"
        return user
    except HTTPException as e:
        logger.warning(
            f"Registration failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "email": user_create.email,
                "ip_address": request.client.host if request.client else None,
            }
        )
        raise


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, bool]:
    """Log out a user.
    
    Args:
        request: FastAPI request
        token: JWT token
        db: Database session
        current_user: Current user
        
    Returns:
        Status of the logout operation
        
    Raises:
        HTTPException: If logout fails
    """
    try:
        revoke_token(db=db, token=token)
        
        logger.info(
            f"User logged out: {current_user.email}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": current_user.id,
                "ip_address": request.client.host if request.client else None,
            }
        )
        
        return {"success": True}
    except HTTPException as e:
        logger.warning(
            f"Logout failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": getattr(current_user, "id", None),
                "ip_address": request.client.host if request.client else None,
            }
        )
        raise


@router.post("/password-reset/request")
async def request_password_reset(
    request: Request,
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> Dict[str, bool]:
    """Request a password reset.
    
    Args:
        request: FastAPI request
        password_reset: Password reset request
        db: Database session
        
    Returns:
        Status of the request
        
    Note:
        This is a placeholder for now. In a real implementation, you would
        send an email with a reset token.
    """
    # Check if user exists
    user = get_user_by_email(db=db, email=password_reset.email)
    if user:
        # In a real implementation, you would generate a token and send an email
        # For now, we'll just log the request
        logger.info(
            f"Password reset requested: {password_reset.email}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user.id,
                "ip_address": request.client.host if request.client else None,
            }
        )
    else:
        # We don't want to leak information about whether an email exists or not
        logger.info(
            f"Password reset requested for non-existent user: {password_reset.email}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "ip_address": request.client.host if request.client else None,
            }
        )
    
    # Always return success to prevent email enumeration
    return {"success": True}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: Request,
    password_reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> Dict[str, bool]:
    """Confirm a password reset.
    
    Args:
        request: FastAPI request
        password_reset_confirm: Password reset confirmation
        db: Database session
        
    Returns:
        Status of the confirmation
        
    Note:
        This is a placeholder for now. In a real implementation, you would
        verify the token and update the password.
    """
    # In a real implementation, you would verify the token and update the password
    # For now, we'll just log the request
    logger.info(
        "Password reset confirmation requested",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "ip_address": request.client.host if request.client else None,
        }
    )
    
    # Always return success to prevent token enumeration
    return {"success": True}


@router.get("/me", response_model=UserModel)
async def get_current_user_info(
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    """Get information about the current user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current user information
    """
    # We don't want to return the hashed password
    current_user.hashed_password = "REDACTED"
    return current_user 