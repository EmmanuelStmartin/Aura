"""Base connector interface for data sources."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd


class DataConnector(ABC):
    """Base class for all data connectors."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs) -> None:
        """Initialize the connector.
        
        Args:
            api_key: API key for the data provider
            **kwargs: Additional connector-specific parameters
        """
        self.api_key = api_key
        self.name = self.__class__.__name__
        self._client = None
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the data source.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the data source."""
        pass
    
    @abstractmethod
    async def get_price_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get price data for a symbol.
        
        Args:
            symbol: Asset symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (e.g., "1m", "5m", "1h", "1d")
            
        Returns:
            DataFrame with price data
            
        Raises:
            ValueError: If invalid parameters are provided
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def search_assets(self, query: str) -> List[Dict[str, Any]]:
        """Search for assets matching a query.
        
        Args:
            query: Search query
            
        Returns:
            List of asset information
            
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def get_asset_info(self, symbol: str) -> Dict[str, Any]:
        """Get information about an asset.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Asset information
            
        Raises:
            ValueError: If asset not found
            ConnectionError: If connection fails
        """
        pass


class NewsConnector(ABC):
    """Base class for news data connectors."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs) -> None:
        """Initialize the connector.
        
        Args:
            api_key: API key for the news provider
            **kwargs: Additional connector-specific parameters
        """
        self.api_key = api_key
        self.name = self.__class__.__name__
        self._client = None
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the news source.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the news source."""
        pass
    
    @abstractmethod
    async def get_news(
        self,
        keywords: Optional[List[str]] = None,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get news articles.
        
        Args:
            keywords: List of keywords to search for
            symbols: List of asset symbols
            start_date: Start date
            end_date: End date
            limit: Maximum number of articles to return
            
        Returns:
            List of news articles
            
        Raises:
            ValueError: If invalid parameters are provided
            ConnectionError: If connection fails
        """
        pass


class SECFilingConnector(ABC):
    """Base class for SEC filing connectors."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs) -> None:
        """Initialize the connector.
        
        Args:
            api_key: API key (if required)
            **kwargs: Additional connector-specific parameters
        """
        self.api_key = api_key
        self.name = self.__class__.__name__
        self._client = None
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the filing source.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the filing source."""
        pass
    
    @abstractmethod
    async def get_filings(
        self,
        symbol: str,
        form_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get SEC filings.
        
        Args:
            symbol: Asset symbol
            form_type: Type of form (e.g., "10-K", "10-Q")
            start_date: Start date
            end_date: End date
            limit: Maximum number of filings to return
            
        Returns:
            List of filings
            
        Raises:
            ValueError: If invalid parameters are provided
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def get_filing_content(self, filing_url: str) -> str:
        """Get the content of a filing.
        
        Args:
            filing_url: URL of the filing
            
        Returns:
            Filing content
            
        Raises:
            ValueError: If filing not found
            ConnectionError: If connection fails
        """
        pass 