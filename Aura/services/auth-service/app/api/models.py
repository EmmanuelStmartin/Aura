"""API models for the auth service."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

# We're reusing the models from the common library for consistency
from aura_common.models.user import UserCreate, UserUpdate, User, UserRole, UserStatus, Token


class UserProfileBase(BaseModel):
    """Base model for user profile."""
    
    risk_tolerance: int = Field(5, ge=1, le=10, description="Risk tolerance score (1-10)")
    investment_horizon: str = Field(
        "medium_term", 
        description="Investment time horizon",
        examples=["short_term", "medium_term", "long_term"]
    )
    investment_goals: Optional[str] = Field(None, description="Investment goals")
    esg_preferences: bool = Field(False, description="Whether to consider ESG factors")
    preferred_sectors: Optional[List[str]] = Field(None, description="Preferred sectors")
    excluded_sectors: Optional[List[str]] = Field(None, description="Excluded sectors")
    max_drawdown_tolerance: int = Field(20, ge=0, le=100, description="Maximum drawdown tolerance (%)")


class UserProfileCreate(UserProfileBase):
    """Model for creating a user profile."""
    
    pass


class UserProfileUpdate(BaseModel):
    """Model for updating a user profile."""
    
    risk_tolerance: Optional[int] = Field(None, ge=1, le=10, description="Risk tolerance score (1-10)")
    investment_horizon: Optional[str] = Field(
        None, 
        description="Investment time horizon",
        examples=["short_term", "medium_term", "long_term"]
    )
    investment_goals: Optional[str] = Field(None, description="Investment goals")
    esg_preferences: Optional[bool] = Field(None, description="Whether to consider ESG factors")
    preferred_sectors: Optional[List[str]] = Field(None, description="Preferred sectors")
    excluded_sectors: Optional[List[str]] = Field(None, description="Excluded sectors")
    max_drawdown_tolerance: Optional[int] = Field(None, ge=0, le=100, description="Maximum drawdown tolerance (%)")


class UserProfile(UserProfileBase):
    """User profile model."""
    
    id: int = Field(..., description="User profile ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True


class LoginRequest(BaseModel):
    """Login request model."""
    
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    
    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password")
    
    @validator("new_password")
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v 