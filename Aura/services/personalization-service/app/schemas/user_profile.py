"""Pydantic models for user profiles."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from app.models.user_profile import RiskTolerance, TimeHorizon, InvestmentGoal


class InterestBase(BaseModel):
    """Base interest model."""
    
    name: str = Field(..., description="Interest name")
    category: Optional[str] = Field(None, description="Interest category")


class InterestCreate(InterestBase):
    """Create interest model."""
    pass


class Interest(InterestBase):
    """Interest model."""
    
    id: int = Field(..., description="Interest ID")
    
    class Config:
        """Pydantic config."""
        
        from_attributes = True


class UserProfileBase(BaseModel):
    """Base user profile model."""
    
    risk_tolerance: RiskTolerance = Field(RiskTolerance.MODERATE, description="Risk tolerance")
    time_horizon: TimeHorizon = Field(TimeHorizon.MEDIUM_TERM, description="Time horizon")
    investment_goal: InvestmentGoal = Field(InvestmentGoal.GROWTH, description="Investment goal")
    initial_investment: Optional[float] = Field(None, description="Initial investment amount")
    monthly_contribution: Optional[float] = Field(None, description="Monthly contribution amount")
    target_retirement_age: Optional[int] = Field(None, description="Target retirement age")
    tax_bracket: Optional[float] = Field(None, description="Tax bracket percentage")
    is_tax_aware: bool = Field(False, description="Whether the user is tax-aware")
    is_esg_focused: bool = Field(False, description="Whether the user is ESG-focused")


class UserProfileCreate(UserProfileBase):
    """Create user profile model."""
    
    user_id: int = Field(..., description="User ID")
    interest_ids: Optional[List[int]] = Field(None, description="Interest IDs")


class UserProfileUpdate(UserProfileBase):
    """Update user profile model."""
    
    interest_ids: Optional[List[int]] = Field(None, description="Interest IDs")


class UserProfile(UserProfileBase):
    """User profile model."""
    
    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID")
    interests: List[Interest] = Field([], description="User interests")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    
    class Config:
        """Pydantic config."""
        
        from_attributes = True


class RecommendationRequest(BaseModel):
    """Recommendation request model."""
    
    user_id: int = Field(..., description="User ID")
    category: Optional[str] = Field(None, description="Recommendation category")
    limit: int = Field(10, description="Maximum number of recommendations", ge=1, le=50)


class Recommendation(BaseModel):
    """Recommendation model."""
    
    id: str = Field(..., description="Recommendation ID")
    type: str = Field(..., description="Recommendation type")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    score: float = Field(..., description="Recommendation score")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata") 