"""User API endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session

from aura_common.config import Settings, get_settings
from aura_common.models.user import User as UserModel, UserUpdate
from aura_common.utils.logging import get_logger

from app.api.models import (
    UserProfileCreate, 
    UserProfileUpdate, 
    UserProfile as UserProfileModel
)
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
)
from app.core.user import (
    get_user_by_id,
    get_users,
    update_user,
    delete_user,
    get_user_profile,
    create_user_profile,
    update_user_profile,
)
from app.db.session import get_db

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=List[UserModel])
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_admin_user),
) -> List[UserModel]:
    """List users.
    
    Args:
        request: FastAPI request
        skip: Number of records to skip
        limit: Maximum number of records to return
        role: Filter by role
        status: Filter by status
        db: Database session
        current_user: Current admin user
        
    Returns:
        List of users
    """
    users = get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        status=status
    )
    
    # We don't want to return hashed passwords
    for user in users:
        user.hashed_password = "REDACTED"
    
    return users


@router.get("/{user_id}", response_model=UserModel)
async def get_user(
    request: Request,
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> UserModel:
    """Get a user by ID.
    
    Args:
        request: FastAPI request
        user_id: User ID
        db: Database session
        current_user: Current user
        
    Returns:
        User
        
    Raises:
        HTTPException: If user not found
    """
    # Regular users can only access their own user
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    db_user = get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # We don't want to return the hashed password
    db_user.hashed_password = "REDACTED"
    return db_user


@router.put("/{user_id}", response_model=UserModel)
async def update_user_by_id(
    request: Request,
    user_id: int = Path(..., gt=0),
    user_update: UserUpdate = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> UserModel:
    """Update a user.
    
    Args:
        request: FastAPI request
        user_id: User ID
        user_update: User update data
        db: Database session
        current_user: Current user
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found
    """
    # Regular users can only update their own user
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Regular users cannot change their role
    if current_user.role != "admin" and user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to change role",
        )
    
    try:
        updated_user = update_user(db=db, user_id=user_id, user_update=user_update)
        
        logger.info(
            f"User updated: {updated_user.email}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": updated_user.id,
                "updated_by": current_user.id,
            }
        )
        
        # We don't want to return the hashed password
        updated_user.hashed_password = "REDACTED"
        return updated_user
    except HTTPException as e:
        logger.warning(
            f"User update failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "updated_by": current_user.id,
            }
        )
        raise


@router.delete("/{user_id}")
async def delete_user_by_id(
    request: Request,
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_admin_user),
) -> Dict[str, bool]:
    """Delete a user.
    
    Args:
        request: FastAPI request
        user_id: User ID
        db: Database session
        current_user: Current admin user
        
    Returns:
        Status of the delete operation
        
    Raises:
        HTTPException: If user not found
    """
    try:
        delete_user(db=db, user_id=user_id)
        
        logger.info(
            f"User deleted: {user_id}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "deleted_by": current_user.id,
            }
        )
        
        return {"success": True}
    except HTTPException as e:
        logger.warning(
            f"User deletion failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "deleted_by": current_user.id,
            }
        )
        raise


@router.get("/{user_id}/profile", response_model=UserProfileModel)
async def get_user_profile_by_id(
    request: Request,
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> UserProfileModel:
    """Get a user profile.
    
    Args:
        request: FastAPI request
        user_id: User ID
        db: Database session
        current_user: Current user
        
    Returns:
        User profile
        
    Raises:
        HTTPException: If user not found or profile not found
    """
    # Regular users can only access their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if user exists
    db_user = get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get profile
    db_profile = get_user_profile(db=db, user_id=user_id)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    
    return db_profile


@router.post("/{user_id}/profile", response_model=UserProfileModel, status_code=status.HTTP_201_CREATED)
async def create_user_profile_by_id(
    request: Request,
    user_id: int = Path(..., gt=0),
    profile_create: UserProfileCreate = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> UserProfileModel:
    """Create a user profile.
    
    Args:
        request: FastAPI request
        user_id: User ID
        profile_create: Profile creation data
        db: Database session
        current_user: Current user
        
    Returns:
        Created user profile
        
    Raises:
        HTTPException: If user not found or profile already exists
    """
    # Regular users can only create their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        db_profile = create_user_profile(
            db=db,
            user_id=user_id,
            profile_create=profile_create
        )
        
        logger.info(
            f"User profile created: {user_id}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "created_by": current_user.id,
            }
        )
        
        return db_profile
    except HTTPException as e:
        logger.warning(
            f"User profile creation failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "created_by": current_user.id,
            }
        )
        raise


@router.put("/{user_id}/profile", response_model=UserProfileModel)
async def update_user_profile_by_id(
    request: Request,
    user_id: int = Path(..., gt=0),
    profile_update: UserProfileUpdate = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> UserProfileModel:
    """Update a user profile.
    
    Args:
        request: FastAPI request
        user_id: User ID
        profile_update: Profile update data
        db: Database session
        current_user: Current user
        
    Returns:
        Updated user profile
        
    Raises:
        HTTPException: If user or profile not found
    """
    # Regular users can only update their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    try:
        db_profile = update_user_profile(
            db=db,
            user_id=user_id,
            profile_update=profile_update
        )
        
        logger.info(
            f"User profile updated: {user_id}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "updated_by": current_user.id,
            }
        )
        
        return db_profile
    except HTTPException as e:
        logger.warning(
            f"User profile update failed: {str(e)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "updated_by": current_user.id,
            }
        )
        raise 