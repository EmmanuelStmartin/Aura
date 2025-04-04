"""User profile model."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAEnum, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RiskTolerance(str, Enum):
    """Risk tolerance enum."""
    
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class TimeHorizon(str, Enum):
    """Time horizon enum."""
    
    SHORT_TERM = "short_term"  # < 1 year
    MEDIUM_TERM = "medium_term"  # 1-5 years
    LONG_TERM = "long_term"  # > 5 years


class InvestmentGoal(str, Enum):
    """Investment goal enum."""
    
    PRESERVATION = "preservation"
    INCOME = "income"
    GROWTH = "growth"
    SPECULATION = "speculation"


# Association table for many-to-many relationship between user profiles and interests
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_profile_id", Integer, ForeignKey("user_profiles.id"), primary_key=True),
    Column("interest_id", Integer, ForeignKey("interests.id"), primary_key=True),
)


class UserProfile(Base):
    """User profile model."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # User preferences
    risk_tolerance = Column(SQLAEnum(RiskTolerance), default=RiskTolerance.MODERATE)
    time_horizon = Column(SQLAEnum(TimeHorizon), default=TimeHorizon.MEDIUM_TERM)
    investment_goal = Column(SQLAEnum(InvestmentGoal), default=InvestmentGoal.GROWTH)
    
    # Additional profile information
    initial_investment = Column(Float, nullable=True)
    monthly_contribution = Column(Float, nullable=True)
    target_retirement_age = Column(Integer, nullable=True)
    tax_bracket = Column(Float, nullable=True)  # Percentage
    
    # Flags
    is_tax_aware = Column(Boolean, default=False)
    is_esg_focused = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interests = relationship(
        "Interest",
        secondary=user_interests,
        back_populates="users"
    )


class Interest(Base):
    """User interest model."""

    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)
    
    # Relationships
    users = relationship(
        "UserProfile",
        secondary=user_interests,
        back_populates="interests"
    ) 