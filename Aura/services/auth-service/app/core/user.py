"""User service with CRUD operations."""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aura_common.config import Settings, get_settings
from aura_common.models.user import UserCreate, UserUpdate, UserRole, UserStatus
from aura_common.utils.security import hash_password, verify_password, create_access_token

from app.api.models import UserProfileCreate, UserProfileUpdate
from app.models.user import User, UserProfile, AccessToken


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[str] = None,
    status: Optional[str] = None
) -> List[User]:
    """Get a list of users.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        role: Filter by role
        status: Filter by status
        
    Returns:
        List of users
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
        
    if status:
        query = query.filter(User.status == status)
        
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user_create: UserCreate) -> User:
    """Create a new user.
    
    Args:
        db: Database session
        user_create: User creation data
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user with this email already exists
    db_user = get_user_by_email(db, email=user_create.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Hash the password
    hashed_password = hash_password(user_create.password)
    
    # Create the user
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role=user_create.role,
        status=user_create.status,
        ai_trading_enabled=user_create.ai_trading_enabled
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )


def update_user(
    db: Session, 
    user_id: int, 
    user_update: UserUpdate
) -> User:
    """Update a user.
    
    Args:
        db: Database session
        user_id: User ID
        user_update: User update data
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    update_data = user_update.dict(exclude_unset=True)
    
    # If password is being updated, hash it
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Whether the user was deleted
        
    Raises:
        HTTPException: If user not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(
    db: Session, 
    email: str, 
    password: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Dict[str, str]:
    """Authenticate a user and generate a JWT token.
    
    Args:
        db: Database session
        email: User email
        password: User password
        user_agent: User agent
        ip_address: IP address
        
    Returns:
        Token information
        
    Raises:
        HTTPException: If authentication fails
    """
    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if db_user.status != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )
    
    settings = get_settings()
    
    # Create access token
    token_data = {
        "sub": db_user.email,
        "role": db_user.role,
    }
    
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data,
        settings=settings,
        expires_delta=expires_delta
    )
    
    # Create token in database
    expires_at = datetime.utcnow() + expires_delta
    db_token = AccessToken(
        user_id=db_user.id,
        token=access_token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    db.add(db_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user_id": db_user.id,
        "role": db_user.role
    }


def revoke_token(db: Session, token: str) -> bool:
    """Revoke a token.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        Whether the token was revoked
        
    Raises:
        HTTPException: If token not found
    """
    db_token = db.query(AccessToken).filter(AccessToken.token == token).first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )
    
    db_token.is_revoked = True
    db.commit()
    return True


def get_user_profile(db: Session, user_id: int) -> Optional[UserProfile]:
    """Get a user profile.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User profile if found, None otherwise
    """
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def create_user_profile(
    db: Session, 
    user_id: int, 
    profile_create: UserProfileCreate
) -> UserProfile:
    """Create a user profile.
    
    Args:
        db: Database session
        user_id: User ID
        profile_create: Profile creation data
        
    Returns:
        Created user profile
        
    Raises:
        HTTPException: If user not found or profile already exists
    """
    # Check if user exists
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if user already has a profile
    db_profile = get_user_profile(db, user_id)
    if db_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile already exists",
        )
    
    # Create profile
    profile_data = profile_create.dict()
    
    # Convert list fields to JSON strings
    if profile_data.get("preferred_sectors"):
        profile_data["preferred_sectors"] = json.dumps(profile_data["preferred_sectors"])
        
    if profile_data.get("excluded_sectors"):
        profile_data["excluded_sectors"] = json.dumps(profile_data["excluded_sectors"])
    
    db_profile = UserProfile(
        user_id=user_id,
        **profile_data
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_user_profile(
    db: Session, 
    user_id: int, 
    profile_update: UserProfileUpdate
) -> UserProfile:
    """Update a user profile.
    
    Args:
        db: Database session
        user_id: User ID
        profile_update: Profile update data
        
    Returns:
        Updated user profile
        
    Raises:
        HTTPException: If user or profile not found
    """
    # Check if user exists
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if profile exists
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # Convert list fields to JSON strings
    if update_data.get("preferred_sectors"):
        update_data["preferred_sectors"] = json.dumps(update_data["preferred_sectors"])
        
    if update_data.get("excluded_sectors"):
        update_data["excluded_sectors"] = json.dumps(update_data["excluded_sectors"])
    
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile 