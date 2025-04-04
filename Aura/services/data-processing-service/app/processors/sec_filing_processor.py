"""SEC filing processor for raw SEC filings data."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger
from aura_common.kafka import KafkaProducer

from app.core.database import get_db, postgres_client
from app.models.processed_sec_filings import ProcessedSecFiling


logger = get_logger(__name__)
settings = get_settings()

# Initialize Kafka producer for processed SEC filings
kafka_producer = KafkaProducer(settings)


async def process_sec_filing(data: Dict[str, Any]) -> None:
    """Process raw SEC filing data.
    
    Args:
        data: Raw SEC filing data from Kafka
    """
    logger.info(f"Processing SEC filing: {data.get('form_type')} for {data.get('symbol')}")
    
    try:
        # Extract data
        symbol = data.get("symbol")
        company_name = data.get("company_name")
        form_type = data.get("form_type")
        filing_date = data.get("filing_date")
        filing_url = data.get("filing_url")
        cik = data.get("cik")
        accession_number = data.get("accession_number")
        
        if not symbol or not form_type or not filing_url:
            logger.warning("Missing symbol, form_type, or filing_url in SEC filing data")
            return
            
        # Parse filing_date if it's a string
        if isinstance(filing_date, str):
            filing_date = datetime.fromisoformat(filing_date.replace("Z", "+00:00"))
        elif filing_date is None:
            filing_date = datetime.utcnow()
        
        # Placeholder for XBRL parsing (post-MVP)
        extracted_data = json.dumps({
            "status": "Placeholder for future XBRL parsing implementation",
            "filing_type": form_type,
            "filing_date": filing_date.isoformat()
        })
        
        # Store in PostgreSQL
        db = next(get_db())
        try:
            # Check if filing already exists
            existing_filing = db.query(ProcessedSecFiling).filter(
                ProcessedSecFiling.filing_url == filing_url
            ).first()
            
            if existing_filing:
                logger.info(f"SEC filing already exists: {filing_url}")
                return
                
            # Create new processed SEC filing
            filing = ProcessedSecFiling(
                symbol=symbol,
                company_name=company_name,
                form_type=form_type,
                filing_date=filing_date,
                filing_url=filing_url,
                cik=cik,
                accession_number=accession_number,
                extracted_data=extracted_data
            )
            
            db.add(filing)
            db.commit()
            db.refresh(filing)
            
            logger.info(f"Saved SEC filing to database with ID: {filing.id}")
            
            # Publish processed SEC filing to Kafka
            await publish_processed_sec_filing(filing.id, symbol, form_type, filing_date, filing_url)
        except Exception as e:
            db.rollback()
            logger.exception(f"Error saving SEC filing to database: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Error processing SEC filing: {str(e)}")


async def publish_processed_sec_filing(filing_id: int, symbol: str, form_type: str, 
                                     filing_date: datetime, filing_url: str) -> None:
    """Publish processed SEC filing to Kafka.
    
    Args:
        filing_id: Filing ID
        symbol: Stock symbol
        form_type: SEC form type
        filing_date: Filing date
        filing_url: Filing URL
    """
    try:
        message = {
            "filing_id": filing_id,
            "symbol": symbol,
            "form_type": form_type,
            "filing_date": filing_date.isoformat(),
            "filing_url": filing_url
        }
        
        kafka_producer.send(
            topic="processed_sec_filings",
            value=message,
            key=f"filing-{filing_id}"
        )
        
        logger.info(f"Published processed SEC filing to Kafka: {filing_id}")
    except Exception as e:
        logger.exception(f"Error publishing processed SEC filing to Kafka: {str(e)}") 