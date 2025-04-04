"""Database connections for the personalization service."""

from typing import Generator

from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.database import PostgresClient

from app.models.user_profile import Base


settings = get_settings()

# PostgreSQL client
postgres_client = PostgresClient(settings)


def initialize_db() -> None:
    """Initialize database tables."""
    engine = postgres_client.engine
    Base.metadata.create_all(bind=engine)


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