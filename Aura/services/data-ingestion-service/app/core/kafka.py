"""Kafka message publishing for data ingestion service."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from aura_common.config import get_settings
from aura_common.kafka import KafkaProducer
from aura_common.utils.logging import get_logger

from app.models.schema import DataType

logger = get_logger(__name__)
settings = get_settings()


class MessagePublisher:
    """Kafka message publisher for data ingestion service."""
    
    def __init__(self) -> None:
        """Initialize the message publisher."""
        self.producer = KafkaProducer(settings=settings)
        self.initialized = False
        
    async def initialize(self) -> None:
        """Initialize the Kafka producer."""
        if not self.initialized:
            # KafkaProducer doesn't have async init, so we're just setting a flag
            self.initialized = True
            
    async def close(self) -> None:
        """Close the Kafka producer."""
        if self.initialized:
            self.producer.close()
            self.initialized = False
    
    async def publish_market_data(
        self,
        symbol: str,
        data: Any,
        source: str,
        data_type: DataType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish market data to Kafka.
        
        Args:
            symbol: Asset symbol
            data: Market data
            source: Data source
            data_type: Type of data
            metadata: Additional metadata
        """
        # Ensure the producer is initialized
        await self.initialize()
        
        # Create a message
        message = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "data_type": data_type.value,
            "data": data,
            "metadata": metadata or {}
        }
        
        # Determine the topic based on data type
        topic = f"raw_{data_type.value.lower()}"
        
        # Send the message
        try:
            self.producer.send(topic=topic, value=message, key=symbol)
            logger.info(f"Published {data_type.value} data for {symbol} to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish {data_type.value} data for {symbol}: {str(e)}")
        
    async def publish_news(
        self,
        news_items: List[Dict[str, Any]],
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish news data to Kafka.
        
        Args:
            news_items: List of news items
            source: News source
            metadata: Additional metadata
        """
        # Ensure the producer is initialized
        await self.initialize()
        
        # Create a message for each news item
        for item in news_items:
            # Determine key (use first related symbol if available, otherwise None)
            related_symbols = item.get("related_symbols", [])
            key = related_symbols[0] if related_symbols else None
            
            # Add source and metadata to the item
            item["source"] = source
            item["metadata"] = metadata or {}
            item["ingestion_timestamp"] = datetime.now().isoformat()
            
            # Send the message
            try:
                self.producer.send(topic="raw_news", value=item, key=key)
                logger.info(f"Published news item: {item.get('title', '')[:50]}...")
            except Exception as e:
                logger.error(f"Failed to publish news item: {str(e)}")
                
    async def publish_sec_filing(
        self,
        filing: Dict[str, Any],
        source: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish SEC filing data to Kafka.
        
        Args:
            filing: Filing data
            source: Filing source
            content: Filing content
            metadata: Additional metadata
        """
        # Ensure the producer is initialized
        await self.initialize()
        
        # Add source and metadata to the filing
        filing["source"] = source
        filing["metadata"] = metadata or {}
        filing["ingestion_timestamp"] = datetime.now().isoformat()
        
        # Include content summary if provided
        if content:
            # Truncate content to avoid excessive message size
            filing["content_summary"] = content[:1000] + "..." if len(content) > 1000 else content
        
        # Send the message
        try:
            self.producer.send(topic="raw_sec_filings", value=filing, key=filing.get("symbol"))
            logger.info(f"Published SEC filing: {filing.get('form_type')} for {filing.get('symbol')}")
        except Exception as e:
            logger.error(f"Failed to publish SEC filing: {str(e)}")


# Singleton instance
message_publisher = MessagePublisher() 