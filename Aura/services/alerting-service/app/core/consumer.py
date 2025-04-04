"""Kafka consumer for processing market data and generating alerts."""

import asyncio
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from aura_common.config import Settings, get_settings
from aura_common.kafka import KafkaConsumer
from aura_common.utils.logging import get_logger

from app.core.rule_engine import evaluate_rules, get_active_rules_for_data
from app.db.session import SessionLocal
from app.models.alert import Alert, AlertType
from app.models.rule import AlertRule

logger = get_logger(__name__)
settings = get_settings()

# Define the Kafka topics to subscribe to
TOPICS = [
    "processed_technical_indicators",
    "processed_news_sentiment"
]


async def process_message(topic: str, message: Dict[str, Any]) -> None:
    """Process a Kafka message and generate alerts if necessary.
    
    Args:
        topic: Kafka topic
        message: Message data
    """
    logger.debug(f"Processing message from topic {topic}: {message}")
    
    try:
        # Create a new database session
        db = SessionLocal()
        
        try:
            # Determine the alert type based on the topic
            alert_type = None
            if topic == "processed_technical_indicators":
                alert_type = AlertType.TECHNICAL_INDICATOR
            elif topic == "processed_news_sentiment":
                alert_type = AlertType.NEWS_SENTIMENT
            else:
                logger.warning(f"Unknown topic: {topic}")
                return
            
            # Get the symbol from the message
            symbol = message.get("symbol")
            if not symbol:
                logger.warning(f"Message missing symbol: {message}")
                return
            
            # Get active rules for this data
            rules = get_active_rules_for_data(db, alert_type=alert_type, symbol=symbol)
            
            # No rules to evaluate
            if not rules:
                logger.debug(f"No active rules for {symbol} with alert type {alert_type}")
                return
            
            # Evaluate the rules against the data
            triggered_alerts = evaluate_rules(rules, message)
            
            # Create and save alerts for triggered rules
            for alert in triggered_alerts:
                db.add(alert)
            
            # Commit the transaction if there are any alerts
            if triggered_alerts:
                db.commit()
                logger.info(f"Generated {len(triggered_alerts)} alerts for {symbol}")
                
                # Publish alerts to connected WebSocket clients
                for alert in triggered_alerts:
                    await publish_alert_to_websocket(alert)
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")


async def publish_alert_to_websocket(alert: Alert) -> None:
    """Publish an alert to connected WebSocket clients.
    
    Args:
        alert: Alert to publish
    """
    from app.core.websocket_manager import manager
    
    # Convert the alert to a JSON string
    alert_data = alert.as_dict()
    alert_json = json.dumps(alert_data)
    
    # Send the alert to the user's WebSocket connection
    await manager.send_personal_message(alert_json, str(alert.user_id))


async def start_kafka_consumer() -> None:
    """Start the Kafka consumer to process market data messages."""
    consumer = KafkaConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=f"{settings.KAFKA_CONSUMER_GROUP_ID}-alerting",
        topics=TOPICS,
    )
    
    logger.info(f"Starting Kafka consumer for topics: {TOPICS}")
    
    try:
        await consumer.start()
        
        async for topic, message in consumer:
            # Process the message asynchronously
            asyncio.create_task(process_message(topic, message))
    except Exception as e:
        logger.exception(f"Error in Kafka consumer: {str(e)}")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped") 