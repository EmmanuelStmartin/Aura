"""Kafka consumer implementation for data processing service."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from aura_common.config import get_settings
from aura_common.kafka import KafkaConsumer
from aura_common.utils.logging import get_logger

from app.processors.market_data_processor import process_market_data
from app.processors.news_processor import process_news
from app.processors.sec_filing_processor import process_sec_filing


logger = get_logger(__name__)
settings = get_settings()

# Kafka consumer instances
consumers = []


async def process_message(topic: str, value: Dict[str, Any], key: Optional[str], headers: Optional[List[tuple]]) -> None:
    """Process Kafka message.
    
    Args:
        topic: Kafka topic
        value: Message value
        key: Message key
        headers: Message headers
    """
    logger.info(f"Processing message from topic: {topic}")
    
    try:
        if topic == "raw_market_data":
            await process_market_data(value)
        elif topic == "raw_news":
            await process_news(value)
        elif topic == "raw_sec_filings":
            await process_sec_filing(value)
        else:
            logger.warning(f"Unknown topic: {topic}")
    except Exception as e:
        logger.exception(f"Error processing message from topic {topic}: {str(e)}")


async def kafka_consumer_task(consumer: KafkaConsumer) -> None:
    """Kafka consumer task.
    
    Args:
        consumer: Kafka consumer instance
    """
    def callback(topic: str, value: Any, key: Optional[str], headers: Optional[List[tuple]]) -> None:
        """Callback function for Kafka consumer."""
        asyncio.create_task(process_message(topic, value, key, headers))
        
    consumer.consume(callback)


async def start_kafka_consumers() -> None:
    """Start Kafka consumers."""
    global consumers
    
    # Create consumer for market data
    market_data_consumer = KafkaConsumer(
        topics=["raw_market_data"],
        group_id=f"{settings.KAFKA_CONSUMER_GROUP_ID}-market-data",
        settings=settings
    )
    consumers.append(market_data_consumer)
    
    # Create consumer for news
    news_consumer = KafkaConsumer(
        topics=["raw_news"],
        group_id=f"{settings.KAFKA_CONSUMER_GROUP_ID}-news",
        settings=settings
    )
    consumers.append(news_consumer)
    
    # Create consumer for SEC filings
    sec_filings_consumer = KafkaConsumer(
        topics=["raw_sec_filings"],
        group_id=f"{settings.KAFKA_CONSUMER_GROUP_ID}-sec-filings",
        settings=settings
    )
    consumers.append(sec_filings_consumer)
    
    # Start consumer tasks
    tasks = [asyncio.create_task(kafka_consumer_task(consumer)) for consumer in consumers]
    await asyncio.gather(*tasks)


async def stop_kafka_consumers() -> None:
    """Stop Kafka consumers."""
    global consumers
    
    for consumer in consumers:
        consumer.close()
    
    consumers = [] 