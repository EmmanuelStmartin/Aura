"""SQLAlchemy base class for database models."""

from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for SQLAlchemy models."""
    
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name.
        
        Returns:
            Table name
        """
        return cls.__name__.lower() 