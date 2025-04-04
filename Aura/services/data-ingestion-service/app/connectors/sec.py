"""SEC EDGAR connector for SEC filing data."""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from aura_common.config import get_settings
from aura_common.utils.logging import get_logger

from app.connectors.base import SECFilingConnector


logger = get_logger(__name__)


class SECEDGARConnector(SECFilingConnector):
    """SEC EDGAR connector for SEC filing data."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the SEC EDGAR connector.
        
        Args:
            api_key: Not used for SEC EDGAR
            user_agent: User agent string for SEC EDGAR API requests
            **kwargs: Additional parameters
        """
        super().__init__(api_key, **kwargs)
        
        # SEC EDGAR API requires a user agent identifying the app and contact email
        # Example: "Aura Financial App help@aura.ai"
        self.user_agent = user_agent or kwargs.get("user_agent") or "Aura Financial App"
        
        # Base URLs
        self.base_url = "https://www.sec.gov"
        self.edgar_url = f"{self.base_url}/edgar"
        self.archives_url = f"{self.edgar_url}/Archives"
        self.data_url = f"{self.edgar_url}/data"
        self.cik_lookup_url = f"{self.edgar_url}/browse-edgar"
        
        # Create HTTP client with appropriate headers
        self._client = None
        
    async def connect(self) -> None:
        """Connect to SEC EDGAR.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Create HTTP client with appropriate headers
            self._client = httpx.AsyncClient(
                headers={
                    "User-Agent": self.user_agent,
                    "Accept-Encoding": "gzip, deflate",
                    "Host": "www.sec.gov"
                },
                timeout=30.0
            )
            
            # Test connection with a simple query
            await self._client.get(self.base_url)
            logger.info("Connected to SEC EDGAR")
        except httpx.HTTPError as e:
            logger.error(f"Failed to connect to SEC EDGAR: {str(e)}")
            raise ConnectionError(f"Failed to connect to SEC EDGAR: {str(e)}")
        
    async def disconnect(self) -> None:
        """Disconnect from SEC EDGAR."""
        if self._client:
            await self._client.aclose()
        self._client = None
        logger.info("Disconnected from SEC EDGAR")
        
    async def _get_cik(self, symbol: str) -> str:
        """Get CIK number for a ticker symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            CIK number as a string
            
        Raises:
            ValueError: If CIK not found
            ConnectionError: If connection fails
        """
        try:
            # Try to get CIK from company ticker lookup
            response = await self._client.get(
                f"{self.base_url}/include/ticker.txt"
            )
            response.raise_for_status()
            
            # Parse the ticker-CIK mapping (format is TICKER[TAB]CIK)
            for line in response.text.strip().split("\n"):
                parts = line.strip().split("\t")
                if len(parts) == 2 and parts[0].upper() == symbol.upper():
                    # Format CIK with leading zeros to match SEC's format (10 digits)
                    return parts[1].zfill(10)
            
            # If not found in ticker lookup, try search API
            params = {
                "CIK": symbol,
                "owner": "exclude",
                "FindCo": "Search"
            }
            response = await self._client.get(self.cik_lookup_url, params=params)
            response.raise_for_status()
            
            # Parse the response HTML to extract CIK
            soup = BeautifulSoup(response.text, "lxml")
            
            # Look for the CIK number in the response
            cik_matches = re.findall(r"CIK=(\d+)", response.text)
            if cik_matches:
                return cik_matches[0].zfill(10)
            
            raise ValueError(f"CIK not found for symbol: {symbol}")
        except httpx.HTTPError as e:
            logger.error(f"Failed to get CIK for {symbol}: {str(e)}")
            raise ConnectionError(f"Failed to get CIK for {symbol}: {str(e)}")
        
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
        if self._client is None:
            await self.connect()
            
        try:
            # Get CIK for the symbol
            cik = await self._get_cik(symbol)
            
            # Set default dates if not provided
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=365 * 2)  # 2 years of data
                
            # Format dates for the API
            date_from = start_date.strftime("%Y-%m-%d")
            date_to = end_date.strftime("%Y-%m-%d")
            
            # Build query parameters
            params = {
                "action": "getcompany",
                "CIK": cik,
                "type": form_type or "",
                "dateb": date_to.replace("-", ""),
                "datea": date_from.replace("-", ""),
                "owner": "exclude",
                "count": str(limit),
                "output": "atom"
            }
            
            # Make the request
            response = await self._client.get(f"{self.edgar_url}/browse-edgar", params=params)
            response.raise_for_status()
            
            # Parse the XML response
            soup = BeautifulSoup(response.text, "lxml-xml")
            entries = soup.find_all("entry")
            
            results = []
            for entry in entries:
                # Extract filing details
                title = entry.find("title").text if entry.find("title") else ""
                
                # Extract form type from title (format: "10-K (Filer) - COMPANY NAME")
                entry_form_type = title.split(" ")[0] if title else ""
                
                # Extract filing date
                filing_date_str = entry.find("filing-date").text if entry.find("filing-date") else ""
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d") if filing_date_str else None
                
                # Extract filing URLs
                filing_href = None
                for link in entry.find_all("link"):
                    rel = link.get("rel", "")
                    if rel == "alternate":
                        filing_href = link.get("href", "")
                        break
                
                if not filing_href:
                    continue
                
                # Extract accession number from filing URL
                accession_match = re.search(r"accession_number=([^&]+)", filing_href)
                accession_number = accession_match.group(1) if accession_match else ""
                
                # Format filing URL
                filing_url = f"{self.edgar_url}/data/{cik}/{accession_number.replace('-', '')}/{accession_number}.txt"
                
                results.append({
                    "symbol": symbol,
                    "company_name": title.split(" - ")[-1] if " - " in title else "",
                    "form_type": entry_form_type,
                    "filing_date": filing_date.isoformat() if filing_date else "",
                    "accession_number": accession_number,
                    "filing_url": filing_url,
                    "html_url": filing_href,
                })
                
            return results
        except (httpx.HTTPError, ValueError) as e:
            if isinstance(e, ValueError):
                raise
            logger.error(f"Failed to get filings for {symbol}: {str(e)}")
            raise ConnectionError(f"Failed to get filings for {symbol}: {str(e)}")
        
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
        if self._client is None:
            await self.connect()
            
        try:
            # Make the request
            response = await self._client.get(filing_url)
            response.raise_for_status()
            
            # Return the content
            return response.text
        except httpx.HTTPError as e:
            if e.response and e.response.status_code == 404:
                raise ValueError(f"Filing not found: {filing_url}")
            logger.error(f"Failed to get filing content for {filing_url}: {str(e)}")
            raise ConnectionError(f"Failed to get filing content for {filing_url}: {str(e)}")
            
    async def extract_financial_data(self, symbol: str, form_type: str = "10-Q") -> Dict[str, Any]:
        """Extract financial data from the latest filing.
        
        Args:
            symbol: Asset symbol
            form_type: Type of form (e.g., "10-K", "10-Q")
            
        Returns:
            Financial data
            
        Raises:
            ValueError: If filing not found
            ConnectionError: If connection fails
        """
        if self._client is None:
            await self.connect()
            
        # This is a placeholder for the MVP
        # In a real implementation, we would parse XBRL data from the filing
        # to extract structured financial information
        
        # For now, just return some mock data
        return {
            "symbol": symbol,
            "form_type": form_type,
            "financial_data": {
                "revenue": 0.0,
                "net_income": 0.0,
                "eps": 0.0,
                "assets": 0.0,
                "liabilities": 0.0,
                "equity": 0.0
            },
            "is_mock_data": True,
            "note": "This is placeholder data. Real implementation would parse XBRL data from SEC filings."
        } 