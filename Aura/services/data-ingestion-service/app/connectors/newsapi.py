"""NewsAPI connector for news data."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import httpx
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.connectors.base import NewsConnector


logger = get_logger(__name__)


class NewsAPIConnector(NewsConnector):
    """NewsAPI connector for news data."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the NewsAPI connector.
        
        Args:
            api_key: NewsAPI API key
            **kwargs: Additional parameters
        """
        super().__init__(api_key, **kwargs)
        
        settings = get_settings()
        
        self.api_key = api_key or settings.NEWS_API_KEY
        
        if not self.api_key:
            logger.warning("NewsAPI API key not provided")
        
        self._client = None
        
    async def connect(self) -> None:
        """Connect to NewsAPI.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._client = NewsApiClient(api_key=self.api_key)
            
            # Test connection with a simple query
            self._client.get_sources()
            logger.info("Connected to NewsAPI")
        except NewsAPIException as e:
            logger.error(f"Failed to connect to NewsAPI: {str(e)}")
            raise ConnectionError(f"Failed to connect to NewsAPI: {str(e)}")
        
    async def disconnect(self) -> None:
        """Disconnect from NewsAPI."""
        self._client = None
        logger.info("Disconnected from NewsAPI")
        
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
        if self._client is None:
            await self.connect()
            
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            # NewsAPI free tier only allows up to 1 month of historical data
            start_date = end_date - timedelta(days=28)
            
        # Build query
        query_parts = []
        
        if keywords:
            keyword_query = " OR ".join(keywords)
            query_parts.append(f"({keyword_query})")
            
        if symbols:
            symbol_query = " OR ".join(symbols)
            query_parts.append(f"({symbol_query})")
            
        if not query_parts:
            # If no keywords or symbols provided, use a default finance-related query
            query_parts.append("(stock OR market OR finance OR investing)")
            
        query = " AND ".join(query_parts)
        
        try:
            # Get articles from NewsAPI
            response = self._client.get_everything(
                q=query,
                from_param=start_date.strftime("%Y-%m-%d"),
                to=end_date.strftime("%Y-%m-%d"),
                language="en",
                sort_by="relevancy",
                page_size=limit
            )
            
            articles = response.get("articles", [])
            
            # Convert to standard format
            results = []
            for article in articles:
                # Try to extract symbols from content
                related_symbols = []
                if symbols:
                    content = article.get("content", "") or ""
                    title = article.get("title", "") or ""
                    description = article.get("description", "") or ""
                    text = f"{title} {description} {content}".upper()
                    
                    for symbol in symbols:
                        if symbol.upper() in text:
                            related_symbols.append(symbol)
                
                results.append({
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "source": article.get("source", {}).get("name"),
                    "summary": article.get("description"),
                    "content": article.get("content"),
                    "related_symbols": related_symbols,
                    "sentiment_score": None,  # Sentiment analysis will be done by the processing service
                })
                
            return results
        except NewsAPIException as e:
            logger.error(f"Failed to get news: {str(e)}")
            raise ConnectionError(f"Failed to get news: {str(e)}")
            
    async def get_top_headlines(
        self,
        country: str = "us",
        category: str = "business",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top headlines.
        
        Args:
            country: Country code
            category: News category
            limit: Maximum number of articles to return
            
        Returns:
            List of news articles
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._client is None:
            await self.connect()
            
        try:
            # Get top headlines from NewsAPI
            response = self._client.get_top_headlines(
                country=country,
                category=category,
                page_size=limit
            )
            
            articles = response.get("articles", [])
            
            # Convert to standard format
            results = []
            for article in articles:
                results.append({
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "source": article.get("source", {}).get("name"),
                    "summary": article.get("description"),
                    "content": article.get("content"),
                    "related_symbols": [],  # Symbol extraction will be done by the processing service
                    "sentiment_score": None,  # Sentiment analysis will be done by the processing service
                })
                
            return results
        except NewsAPIException as e:
            logger.error(f"Failed to get top headlines: {str(e)}")
            raise ConnectionError(f"Failed to get top headlines: {str(e)}") 