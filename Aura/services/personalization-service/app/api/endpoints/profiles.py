"""User profile endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from aura_common.utils.logging import get_logger

from app.core.database import get_db
from app.models.user_profile import UserProfile as UserProfileModel, Interest as InterestModel
from app.schemas.user_profile import UserProfile, UserProfileCreate, UserProfileUpdate


router = APIRouter()
logger = get_logger(__name__)


@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: int = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get user profile.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User profile
        
    Raises:
        HTTPException: If user profile not found
    """
    # Query user profile
    profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User profile not found for user ID: {user_id}"
        )
    
    return profile


@router.put("/{user_id}/profile", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    user_id: int = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Update user profile.
    
    Args:
        profile_update: Profile update data
        user_id: User ID
        db: Database session
        
    Returns:
        Updated user profile
        
    Raises:
        HTTPException: If user profile not found
    """
    # Query user profile
    profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User profile not found for user ID: {user_id}"
        )
    
    # Update profile fields
    profile_data = profile_update.dict(exclude_unset=True, exclude={"interest_ids"})
    for key, value in profile_data.items():
        setattr(profile, key, value)
    
    # Update interests if provided
    if profile_update.interest_ids is not None:
        # Clear existing interests
        profile.interests = []
        
        # Add new interests
        if profile_update.interest_ids:
            interests = db.query(InterestModel).filter(
                InterestModel.id.in_(profile_update.interest_ids)
            ).all()
            
            profile.interests = interests
    
    try:
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        db.rollback()
        logger.exception(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )


@router.post("/{user_id}/profile", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    profile_create: UserProfileCreate,
    user_id: int = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Create user profile.
    
    Args:
        profile_create: Profile creation data
        user_id: User ID
        db: Database session
        
    Returns:
        Created user profile
        
    Raises:
        HTTPException: If user profile already exists
    """
    # Check if profile already exists
    existing_profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User profile already exists for user ID: {user_id}"
        )
    
    # Ensure user_id in path matches user_id in request body
    if profile_create.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID in path must match user ID in request body"
        )
    
    # Create new profile
    profile = UserProfileModel(**profile_create.dict(exclude={"interest_ids"}))
    
    # Add interests if provided
    if profile_create.interest_ids:
        interests = db.query(InterestModel).filter(
            InterestModel.id.in_(profile_create.interest_ids)
        ).all()
        
        profile.interests = interests
    
    try:
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        db.rollback()
        logger.exception(f"Error creating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user profile: {str(e)}"
        ) 