"""Kafka producer for Aura services."""

import json
from typing import Any, Dict, List, Optional, Union

from kafka import KafkaProducer as KafkaProducerClient
from kafka.errors import KafkaError

from aura_common.config import Settings, get_settings


class KafkaProducer:
    """Kafka producer for Aura services."""
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize Kafka producer.
        
        Args:
            settings: Settings instance
        """
        if settings is None:
            settings = get_settings()
            
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.producer = KafkaProducerClient(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1
        )
    
    def send(self, topic: str, value: Any, key: Optional[str] = None, headers: Optional[List[tuple]] = None) -> None:
        """Send a message to a Kafka topic.
        
        Args:
            topic: Kafka topic
            value: Message value
            key: Message key
            headers: Message headers
            
        Raises:
            KafkaError: If sending fails
        """
        try:
            future = self.producer.send(topic, value=value, key=key, headers=headers)
            # Wait for the message to be sent
            future.get(timeout=10)
        except KafkaError as e:
            # In production, you'd want to log this error
            raise
    
    def close(self) -> None:
        """Close the producer connection."""
        self.producer.close() 