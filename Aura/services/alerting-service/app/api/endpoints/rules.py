"""Alert rules API endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from aura_common.utils.logging import get_logger

from app.db.session import get_db
from app.models.rule import AlertRule, RuleStatus
from app.schemas.rule import AlertRule as AlertRuleSchema
from app.schemas.rule import AlertRuleCreate, AlertRuleList, AlertRuleUpdate

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=AlertRuleList)
async def get_rules(
    user_id: int = Query(..., description="User ID"),
    status: Optional[RuleStatus] = Query(None, description="Filter by status"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, description="Maximum number of rules to return"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get alert rules for a user.
    
    Args:
        user_id: User ID
        status: Filter by status
        symbol: Filter by symbol
        limit: Maximum number of rules to return
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of alert rules
    """
    # Build the query
    query = db.query(AlertRule).filter(AlertRule.user_id == user_id)
    
    # Apply filters if provided
    if status:
        query = query.filter(AlertRule.status == status)
    if symbol:
        query = query.filter(AlertRule.symbol == symbol)
    
    # Get the total count
    total = query.count()
    
    # Apply pagination and ordering
    rules = query.order_by(AlertRule.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "rules": rules,
        "total": total,
    }


@router.post("", response_model=AlertRuleSchema, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_create: AlertRuleCreate,
    db: Session = Depends(get_db),
) -> AlertRule:
    """Create a new alert rule.
    
    Args:
        rule_create: Rule creation data
        db: Database session
        
    Returns:
        Created rule
    """
    # Create a new rule
    rule = AlertRule(**rule_create.dict())
    
    # Save the rule
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    logger.info(f"Created alert rule: {rule.name} for user {rule.user_id}")
    
    return rule


@router.get("/{rule_id}", response_model=AlertRuleSchema)
async def get_rule(
    rule_id: int = Path(..., description="Rule ID"),
    db: Session = Depends(get_db),
) -> AlertRule:
    """Get an alert rule by ID.
    
    Args:
        rule_id: Rule ID
        db: Database session
        
    Returns:
        Alert rule
        
    Raises:
        HTTPException: If the rule is not found
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found",
        )
    
    return rule


@router.patch("/{rule_id}", response_model=AlertRuleSchema)
async def update_rule(
    rule_update: AlertRuleUpdate,
    rule_id: int = Path(..., description="Rule ID"),
    db: Session = Depends(get_db),
) -> AlertRule:
    """Update an alert rule.
    
    Args:
        rule_update: Rule update data
        rule_id: Rule ID
        db: Database session
        
    Returns:
        Updated rule
        
    Raises:
        HTTPException: If the rule is not found
    """
    # Get the rule
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found",
        )
    
    # Update the rule
    for key, value in rule_update.dict(exclude_unset=True).items():
        setattr(rule, key, value)
    
    # Save changes
    db.commit()
    db.refresh(rule)
    
    logger.info(f"Updated alert rule: {rule.name} for user {rule.user_id}")
    
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int = Path(..., description="Rule ID"),
    db: Session = Depends(get_db),
) -> None:
    """Delete an alert rule (mark as deleted).
    
    Args:
        rule_id: Rule ID
        db: Database session
        
    Raises:
        HTTPException: If the rule is not found
    """
    # Get the rule
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found",
        )
    
    # Mark as deleted (soft delete)
    rule.status = RuleStatus.DELETED
    
    # Save changes
    db.commit()
    
    logger.info(f"Deleted alert rule: {rule.name} for user {rule.user_id}") 