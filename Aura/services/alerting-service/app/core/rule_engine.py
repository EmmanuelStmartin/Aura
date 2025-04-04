"""Rule engine for evaluating alert rules against incoming data."""

import operator
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from aura_common.utils.logging import get_logger

from app.models.alert import Alert, AlertStatus, AlertType
from app.models.rule import AlertRule, RuleStatus, RuleConditionOperator
from app.db.session import SessionLocal

logger = get_logger(__name__)

# Mapping of rule condition operators to Python operator functions
OPERATOR_MAP = {
    RuleConditionOperator.GREATER_THAN: operator.gt,
    RuleConditionOperator.LESS_THAN: operator.lt,
    RuleConditionOperator.EQUAL_TO: operator.eq,
    RuleConditionOperator.NOT_EQUAL: operator.ne,
    RuleConditionOperator.GREATER_EQUAL: operator.ge,
    RuleConditionOperator.LESS_EQUAL: operator.le,
    RuleConditionOperator.CONTAINS: lambda a, b: b in a,  # Contains is special case
}


def get_active_rules_for_data(
    db: Session,
    alert_type: AlertType,
    symbol: str,
) -> List[AlertRule]:
    """Get active rules for the given data.
    
    Args:
        db: Database session
        alert_type: Alert type
        symbol: Asset symbol
        
    Returns:
        List of active rules
    """
    # Query for rules that match the alert type and are active
    query = db.query(AlertRule).filter(
        AlertRule.alert_type == alert_type,
        AlertRule.status == RuleStatus.ACTIVE,
        # Symbol matches either the specific symbol or is null (applies to all symbols)
        or_(
            AlertRule.symbol == symbol,
            AlertRule.symbol.is_(None)
        )
    )
    
    return query.all()


def evaluate_rules(
    rules: List[AlertRule],
    data: Dict[str, Any],
) -> List[Alert]:
    """Evaluate rules against the incoming data.
    
    Args:
        rules: List of rules to evaluate
        data: Incoming data to evaluate
        
    Returns:
        List of alerts triggered by the rules
    """
    triggered_alerts = []
    
    for rule in rules:
        try:
            # Skip rules that don't have a valid indicator
            if not rule.indicator:
                logger.warning(f"Rule {rule.id} missing indicator")
                continue
                
            # Get the data value for the indicator
            value = get_value_from_data(data, rule.indicator)
            if value is None:
                logger.debug(f"No value found for indicator {rule.indicator} in data")
                continue
                
            # Convert the threshold to the appropriate type
            threshold = convert_threshold(rule.threshold, value)
            
            # Get the operator function
            op_func = OPERATOR_MAP.get(rule.operator)
            if not op_func:
                logger.warning(f"Unknown operator: {rule.operator}")
                continue
                
            # Check if the rule is triggered
            is_triggered = op_func(value, threshold)
            
            if is_triggered:
                # Check cooldown period
                last_alert = get_last_alert_for_rule(db=SessionLocal(), rule_id=rule.id)
                if last_alert:
                    cooldown = datetime.utcnow() - last_alert.timestamp
                    if cooldown.total_seconds() < rule.cooldown_minutes * 60:
                        logger.debug(f"Rule {rule.id} in cooldown period")
                        continue
                
                logger.info(f"Rule {rule.id} triggered: {value} {rule.operator} {threshold}")
                
                # Create an alert
                alert = Alert(
                    user_id=rule.user_id,
                    symbol=data.get("symbol", rule.symbol),
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    status=AlertStatus.NEW,
                    title=f"Alert: {rule.name}",
                    message=generate_alert_message(rule, value, threshold),
                    rule_id=rule.id,
                    metadata={
                        "rule_id": rule.id,
                        "indicator": rule.indicator,
                        "value": value,
                        "threshold": threshold,
                        "operator": rule.operator.value,
                        "data": data
                    },
                    is_delivered=False,
                )
                
                triggered_alerts.append(alert)
        except Exception as e:
            logger.exception(f"Error evaluating rule {rule.id}: {str(e)}")
    
    return triggered_alerts


def get_value_from_data(data: Dict[str, Any], indicator: str) -> Any:
    """Extract a value from the data using the indicator path.
    
    Args:
        data: Data to extract from
        indicator: Indicator path (e.g., "rsi.value" or "news.sentiment")
        
    Returns:
        Extracted value or None if not found
    """
    current = data
    parts = indicator.split(".")
    
    try:
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    except (KeyError, TypeError):
        return None


def convert_threshold(threshold: str, value: Any) -> Any:
    """Convert the threshold string to the appropriate type.
    
    Args:
        threshold: Threshold string
        value: Value to compare against (used to determine type)
        
    Returns:
        Converted threshold value
    """
    if isinstance(value, (int, float)):
        try:
            return float(threshold)
        except ValueError:
            return threshold
    elif isinstance(value, bool):
        return threshold.lower() == "true"
    else:
        return threshold


def generate_alert_message(rule: AlertRule, value: Any, threshold: Any) -> str:
    """Generate a message for the alert.
    
    Args:
        rule: Alert rule
        value: Actual value
        threshold: Threshold value
        
    Returns:
        Alert message
    """
    symbol = rule.symbol or "your assets"
    indicator_name = rule.indicator.replace(".", " ").title()
    
    if rule.operator == RuleConditionOperator.GREATER_THAN:
        return f"{symbol}: {indicator_name} is {value}, which is greater than the threshold of {threshold}."
    elif rule.operator == RuleConditionOperator.LESS_THAN:
        return f"{symbol}: {indicator_name} is {value}, which is less than the threshold of {threshold}."
    elif rule.operator == RuleConditionOperator.EQUAL_TO:
        return f"{symbol}: {indicator_name} is equal to {threshold}."
    elif rule.operator == RuleConditionOperator.NOT_EQUAL:
        return f"{symbol}: {indicator_name} is {value}, which is not equal to {threshold}."
    elif rule.operator == RuleConditionOperator.GREATER_EQUAL:
        return f"{symbol}: {indicator_name} is {value}, which is greater than or equal to the threshold of {threshold}."
    elif rule.operator == RuleConditionOperator.LESS_EQUAL:
        return f"{symbol}: {indicator_name} is {value}, which is less than or equal to the threshold of {threshold}."
    elif rule.operator == RuleConditionOperator.CONTAINS:
        return f"{symbol}: {indicator_name} contains {threshold}."
    else:
        return f"{symbol}: {indicator_name} triggered an alert. Current value: {value}, Threshold: {threshold}."


def get_last_alert_for_rule(db: Session, rule_id: int) -> Optional[Alert]:
    """Get the last alert for a rule.
    
    Args:
        db: Database session
        rule_id: Rule ID
        
    Returns:
        Last alert or None if no alert exists
    """
    return db.query(Alert).filter(
        Alert.rule_id == rule_id
    ).order_by(Alert.timestamp.desc()).first() 