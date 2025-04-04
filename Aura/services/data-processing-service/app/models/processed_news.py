"""Processed news model."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association table for many-to-many relationship between news and symbols
news_symbol_association = Table(
    "news_symbol_association",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("processed_news.id"), primary_key=True),
    Column("symbol", String, primary_key=True),
)


class ProcessedNews(Base):
    """Processed news model."""

    __tablename__ = "processed_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float, nullable=False)
    sentiment_magnitude = Column(Float, nullable=True)
    symbols = relationship(
        "Symbol",
        secondary=news_symbol_association,
        backref="news",
    )


class Symbol(Base):
    """Symbol model for news association."""

    __tablename__ = "symbols"

    symbol = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) 