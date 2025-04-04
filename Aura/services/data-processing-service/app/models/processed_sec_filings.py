"""Processed SEC filings model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ProcessedSecFiling(Base):
    """Processed SEC filing model."""

    __tablename__ = "processed_sec_filings"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    company_name = Column(String, nullable=True)
    form_type = Column(String, nullable=False, index=True)
    filing_date = Column(DateTime, nullable=False)
    filing_url = Column(String, nullable=False, unique=True)
    cik = Column(String, nullable=True, index=True)
    accession_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Fields for future XBRL parsing (post-MVP)
    extracted_data = Column(Text, nullable=True)  # JSON data to be parsed post-MVP 