"""Settings module for Aura services."""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings class for Aura services."""

    # API configurations
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # PostgreSQL configurations
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "aura"
    POSTGRES_PASSWORD: str = "aura_password"
    POSTGRES_DB: str = "aura"

    # InfluxDB configurations
    INFLUXDB_URL: str = "http://influxdb:8086"
    INFLUXDB_TOKEN: str = "aura_token"
    INFLUXDB_ORG: str = "aura"
    INFLUXDB_BUCKET: str = "aura_timeseries"

    # Neo4j configurations
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"

    # Kafka configurations
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_CONSUMER_GROUP_ID: str = "aura-consumer"

    # JWT configurations
    JWT_SECRET_KEY: str = "your_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Feature flags
    ENABLE_ADVANCED_ML_MODELS: bool = False
    ENABLE_REAL_TRADING: bool = False

    # API keys
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_API_SECRET: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    IEX_CLOUD_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None

    # Service URLs
    DATA_INGESTION_SERVICE_URL: str = "http://data-ingestion-service:8001"
    DATA_PROCESSING_SERVICE_URL: str = "http://data-processing-service:8002"
    AI_MODELING_SERVICE_URL: str = "http://ai-modeling-service:8003"
    PORTFOLIO_OPTIMIZATION_SERVICE_URL: str = "http://portfolio-optimization-service:8004"
    PERSONALIZATION_SERVICE_URL: str = "http://personalization-service:8005"
    ALERTING_SERVICE_URL: str = "http://alerting-service:8006"
    API_GATEWAY_SERVICE_URL: str = "http://api-gateway-service:8000"
    AUTH_SERVICE_URL: str = "http://auth-service:8007"
    BROKERAGE_INTEGRATION_SERVICE_URL: str = "http://brokerage-integration-service:8008"

    @field_validator("KAFKA_BOOTSTRAP_SERVERS")
    @classmethod
    def validate_kafka_bootstrap_servers(cls, v: str) -> str:
        """Validate Kafka bootstrap servers.
        
        Args:
            v: Kafka bootstrap servers string
            
        Returns:
            Validated Kafka bootstrap servers string
        """
        if not v:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS cannot be empty")
        return v

    def get_postgres_dsn(self) -> str:
        """Get PostgreSQL connection string.
        
        Returns:
            PostgreSQL connection string
        """
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def validate_alpaca_api_keys(self) -> None:
        """Validate that Alpaca API keys are set.
        
        Raises:
            ValueError: If Alpaca API keys are missing
        """
        if not self.ALPACA_API_KEY or not self.ALPACA_API_SECRET:
            raise ValueError(
                "Missing Alpaca API credentials. ALPACA_API_KEY and ALPACA_API_SECRET must be set."
            )

    def validate_news_api_key(self) -> None:
        """Validate that News API key is set.
        
        Raises:
            ValueError: If News API key is missing
        """
        if not self.NEWS_API_KEY:
            raise ValueError("Missing NEWS_API_KEY. This key is required for news data ingestion.")

    def validate_iex_cloud_api_key(self) -> None:
        """Validate that IEX Cloud API key is set.
        
        Raises:
            ValueError: If IEX Cloud API key is missing
        """
        if not self.IEX_CLOUD_API_KEY:
            raise ValueError("Missing IEX_CLOUD_API_KEY. This key is required for market data.")

    def validate_polygon_api_key(self) -> None:
        """Validate that Polygon API key is set.
        
        Raises:
            ValueError: If Polygon API key is missing
        """
        if not self.POLYGON_API_KEY:
            raise ValueError("Missing POLYGON_API_KEY. This key is required for market data.")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton.
    
    Returns:
        Settings instance
    """
    return Settings() 