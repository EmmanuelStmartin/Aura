"""Database session for the auth service."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aura_common.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.get_postgres_dsn(),
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"application_name": "aura-auth-service"},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 