"""PostgreSQL database client for Aura services."""

from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from aura_common.config import Settings, get_settings


@lru_cache()
def get_postgres_engine(settings: Optional[Settings] = None) -> Engine:
    """Get SQLAlchemy engine instance.
    
    Args:
        settings: Settings instance
        
    Returns:
        SQLAlchemy engine
    """
    if settings is None:
        settings = get_settings()
        
    return create_engine(
        settings.get_postgres_dsn(),
        pool_pre_ping=True,
        pool_recycle=3600,
    )


class PostgresClient:
    """PostgreSQL client for Aura services."""
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize PostgreSQL client.
        
        Args:
            settings: Settings instance
        """
        if settings is None:
            settings = get_settings()
            
        self.engine = get_postgres_engine(settings)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session.
        
        Returns:
            Database session
        """
        return self.SessionLocal()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a raw SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query results as list of dictionaries
            
        Raises:
            SQLAlchemyError: If query execution fails
        """
        if params is None:
            params = {}
            
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params)
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            # In production, you'd want to log this error
            raise 