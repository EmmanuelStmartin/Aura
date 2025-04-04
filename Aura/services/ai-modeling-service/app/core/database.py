"""Database connections for the AI modeling service."""

from typing import Generator

from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.database import PostgresClient, InfluxDBClient


settings = get_settings()

# PostgreSQL client
postgres_client = PostgresClient(settings)

# InfluxDB client
influxdb_client = InfluxDBClient(settings)


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