"""User models for Aura services."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enumeration."""
    
    ADMIN = "admin"
    PREMIUM = "premium"
    FREE = "free"


class UserStatus(str, Enum):
    """User status enumeration."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class UserBase(BaseModel):
    """Base user model."""
    
    email: EmailStr = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    role: UserRole = Field(default=UserRole.FREE, description="User role")
    status: UserStatus = Field(default=UserStatus.PENDING, description="User status")
    ai_trading_enabled: bool = Field(default=False, description="Whether AI trading is enabled for the user")


class UserCreate(UserBase):
    """User creation model."""
    
    password: str = Field(..., description="User password")


class UserUpdate(BaseModel):
    """User update model."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    role: Optional[UserRole] = Field(None, description="User role")
    status: Optional[UserStatus] = Field(None, description="User status")
    ai_trading_enabled: Optional[bool] = Field(None, description="Whether AI trading is enabled for the user")
    password: Optional[str] = Field(None, description="User password")


class User(UserBase):
    """User model."""
    
    id: int = Field(..., description="User ID")
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True
        use_enum_values = True


class UserInDB(User):
    """User model in database."""
    
    hashed_password: str = Field(..., description="Hashed user password")
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True
        use_enum_values = True


class Token(BaseModel):
    """Token model."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token data model."""
    
    email: Optional[str] = Field(None, description="User email address")
    role: Optional[UserRole] = Field(None, description="User role")
    exp: Optional[int] = Field(None, description="Token expiration timestamp") 