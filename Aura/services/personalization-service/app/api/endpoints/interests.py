"""Interest endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from aura_common.utils.logging import get_logger

from app.core.database import get_db
from app.models.user_profile import Interest as InterestModel
from app.schemas.user_profile import Interest, InterestCreate


router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[Interest])
async def get_interests(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, description="Maximum number of interests to return", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    db: Session = Depends(get_db)
):
    """Get interests.
    
    Args:
        category: Filter by category
        limit: Maximum number of interests to return
        offset: Offset for pagination
        db: Database session
        
    Returns:
        List of interests
    """
    query = db.query(InterestModel)
    
    if category:
        query = query.filter(InterestModel.category == category)
    
    total = query.count()
    interests = query.offset(offset).limit(limit).all()
    
    return interests


@router.post("/", response_model=Interest, status_code=status.HTTP_201_CREATED)
async def create_interest(
    interest_create: InterestCreate,
    db: Session = Depends(get_db)
):
    """Create interest.
    
    Args:
        interest_create: Interest creation data
        db: Database session
        
    Returns:
        Created interest
        
    Raises:
        HTTPException: If interest already exists
    """
    # Check if interest already exists
    existing_interest = db.query(InterestModel).filter(InterestModel.name == interest_create.name).first()
    
    if existing_interest:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Interest already exists with name: {interest_create.name}"
        )
    
    # Create new interest
    interest = InterestModel(**interest_create.dict())
    
    try:
        db.add(interest)
        db.commit()
        db.refresh(interest)
        return interest
    except Exception as e:
        db.rollback()
        logger.exception(f"Error creating interest: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interest: {str(e)}"
        )


@router.get("/{interest_id}", response_model=Interest)
async def get_interest(
    interest_id: int = Path(..., description="Interest ID"),
    db: Session = Depends(get_db)
):
    """Get interest by ID.
    
    Args:
        interest_id: Interest ID
        db: Database session
        
    Returns:
        Interest
        
    Raises:
        HTTPException: If interest not found
    """
    interest = db.query(InterestModel).filter(InterestModel.id == interest_id).first()
    
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interest not found with ID: {interest_id}"
        )
    
    return interest 