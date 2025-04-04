"""Kafka consumer for Aura services."""

import json
from typing import Any, Callable, Dict, List, Optional, Union

from kafka import KafkaConsumer as KafkaConsumerClient
from kafka.errors import KafkaError

from aura_common.config import Settings, get_settings


class KafkaConsumer:
    """Kafka consumer for Aura services."""
    
    def __init__(
        self, 
        topics: List[str], 
        group_id: Optional[str] = None,
        auto_offset_reset: str = 'latest',
        settings: Optional[Settings] = None
    ) -> None:
        """Initialize Kafka consumer.
        
        Args:
            topics: List of Kafka topics to subscribe to
            group_id: Consumer group ID (default: from settings)
            auto_offset_reset: Auto offset reset strategy ('latest' or 'earliest')
            settings: Settings instance
        """
        if settings is None:
            settings = get_settings()
            
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.group_id = group_id or settings.KAFKA_CONSUMER_GROUP_ID
        self.topics = topics
        
        self.consumer = KafkaConsumerClient(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=auto_offset_reset,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
    
    def consume(self, callback: Callable[[str, Any, Optional[str], Optional[List[tuple]]], None]) -> None:
        """Consume messages from Kafka topics and process them with a callback.
        
        Args:
            callback: Callback function that takes topic, value, key, and headers
        """
        try:
            for message in self.consumer:
                callback(
                    message.topic,
                    message.value,
                    message.key,
                    message.headers
                )
        except KafkaError as e:
            # In production, you'd want to log this error
            raise
    
    def close(self) -> None:
        """Close the consumer connection."""
        self.consumer.close() 