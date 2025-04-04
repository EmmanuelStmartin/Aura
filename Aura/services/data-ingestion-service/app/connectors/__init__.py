"""Connectors package for data ingestion service."""

from typing import Dict, Optional, Type, Union

from app.connectors.base import DataConnector, NewsConnector, SECFilingConnector
from app.connectors.alpaca import AlpacaConnector
from app.connectors.newsapi import NewsAPIConnector
from app.connectors.sec import SECEDGARConnector


# Connector registry
DATA_CONNECTORS: Dict[str, Type[DataConnector]] = {
    "alpaca": AlpacaConnector,
}

NEWS_CONNECTORS: Dict[str, Type[NewsConnector]] = {
    "newsapi": NewsAPIConnector,
}

SEC_FILING_CONNECTORS: Dict[str, Type[SECFilingConnector]] = {
    "sec_edgar": SECEDGARConnector,
}


def get_data_connector(name: str, **kwargs) -> DataConnector:
    """Get a data connector by name.
    
    Args:
        name: Connector name
        **kwargs: Additional parameters for the connector
        
    Returns:
        Data connector instance
        
    Raises:
        ValueError: If connector not found
    """
    connector_cls = DATA_CONNECTORS.get(name.lower())
    if not connector_cls:
        raise ValueError(f"Data connector not found: {name}")
    return connector_cls(**kwargs)


def get_news_connector(name: str, **kwargs) -> NewsConnector:
    """Get a news connector by name.
    
    Args:
        name: Connector name
        **kwargs: Additional parameters for the connector
        
    Returns:
        News connector instance
        
    Raises:
        ValueError: If connector not found
    """
    connector_cls = NEWS_CONNECTORS.get(name.lower())
    if not connector_cls:
        raise ValueError(f"News connector not found: {name}")
    return connector_cls(**kwargs)


def get_sec_filing_connector(name: str, **kwargs) -> SECFilingConnector:
    """Get a SEC filing connector by name.
    
    Args:
        name: Connector name
        **kwargs: Additional parameters for the connector
        
    Returns:
        SEC filing connector instance
        
    Raises:
        ValueError: If connector not found
    """
    connector_cls = SEC_FILING_CONNECTORS.get(name.lower())
    if not connector_cls:
        raise ValueError(f"SEC filing connector not found: {name}")
    return connector_cls(**kwargs) 