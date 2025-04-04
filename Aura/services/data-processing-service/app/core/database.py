"""Database connections for the data processing service."""

from typing import Generator

from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.database import PostgresClient, InfluxDBClient

from app.models.processed_news import Base as NewsBase
from app.models.processed_sec_filings import Base as SecFilingsBase


settings = get_settings()

# PostgreSQL client
postgres_client = PostgresClient(settings)

# InfluxDB client
influxdb_client = InfluxDBClient(settings)

# Create tables if they don't exist
def initialize_db() -> None:
    """Initialize database tables."""
    engine = postgres_client.engine
    NewsBase.metadata.create_all(bind=engine)
    SecFilingsBase.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session.
    
    Yields:
        Database session
    """
    db = postgres_client.get_session()
    try:
        yield db
    finally:
        db.close() 