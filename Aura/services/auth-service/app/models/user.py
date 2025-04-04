"""User database models for the auth service."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    role = Column(String(50), default="free", nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    ai_trading_enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    access_tokens = relationship("AccessToken", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """User profile database model for storing personalization settings."""
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_tolerance = Column(Integer, default=5, nullable=False)  # 1-10 scale
    investment_horizon = Column(String(50), default="medium_term", nullable=False)
    investment_goals = Column(String(255))
    esg_preferences = Column(Boolean, default=False, nullable=False)
    preferred_sectors = Column(Text)  # Stored as JSON string
    excluded_sectors = Column(Text)  # Stored as JSON string
    max_drawdown_tolerance = Column(Integer, default=20, nullable=False)  # Percentage
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="profiles")


class AccessToken(Base):
    """Access token database model for token tracking and revocation."""
    
    __tablename__ = "access_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="access_tokens") 