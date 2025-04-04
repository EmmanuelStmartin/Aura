"""Database session management."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aura_common.config import get_settings

settings = get_settings()

# Create the database engine
engine = create_engine(
    settings.get_postgres_dsn(),
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Get a database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 