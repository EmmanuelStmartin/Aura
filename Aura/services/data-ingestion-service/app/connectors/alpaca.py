"""Alpaca connector for market data."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import alpaca_trade_api as tradeapi
import pandas as pd
from alpaca_trade_api.rest import REST, APIError

from aura_common.config import get_settings
from aura_common.models.asset import Asset, AssetClass, AssetType
from aura_common.utils.logging import get_logger

from app.connectors.base import DataConnector


logger = get_logger(__name__)


class AlpacaConnector(DataConnector):
    """Alpaca connector for market data."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the Alpaca connector.
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            base_url: Alpaca API base URL
            **kwargs: Additional parameters
        """
        super().__init__(api_key, **kwargs)
        
        settings = get_settings()
        
        self.api_key = api_key or settings.ALPACA_API_KEY
        self.api_secret = api_secret or settings.ALPACA_API_SECRET
        self.base_url = base_url or "https://paper-api.alpaca.markets"
        self.data_url = kwargs.get("data_url", "https://data.alpaca.markets")
        
        if not self.api_key or not self.api_secret:
            logger.warning("Alpaca API key or secret not provided")
        
        self._client = None
        
    async def connect(self) -> None:
        """Connect to Alpaca API.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._client = REST(
                key_id=self.api_key,
                secret_key=self.api_secret,
                base_url=self.base_url,
                data_url=self.data_url,
            )
            
            # Test connection
            account = self._client.get_account()
            logger.info(f"Connected to Alpaca API as {account.id}")
        except APIError as e:
            logger.error(f"Failed to connect to Alpaca API: {str(e)}")
            raise ConnectionError(f"Failed to connect to Alpaca API: {str(e)}")
        
    async def disconnect(self) -> None:
        """Disconnect from Alpaca API."""
        self._client = None
        logger.info("Disconnected from Alpaca API")
        
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
        if self._client is None:
            await self.connect()
            
        # Convert interval to Alpaca format
        timeframe_map = {
            "1m": "1Min",
            "5m": "5Min",
            "15m": "15Min",
            "30m": "30Min",
            "1h": "1Hour",
            "1d": "1Day",
        }
        
        timeframe = timeframe_map.get(interval)
        if timeframe is None:
            raise ValueError(f"Invalid interval: {interval}")
            
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            if interval in ["1m", "5m", "15m", "30m"]:
                # Limited history for minute-level data
                start_date = end_date - timedelta(days=7)
            elif interval == "1h":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=365)
                
        try:
            # Get bars from Alpaca
            bars = self._client.get_bars(
                symbol,
                timeframe,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                adjustment='raw'
            ).df
            
            if bars.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
                
            # Rename columns to standard format
            bars = bars.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            })
            
            return bars
        except APIError as e:
            logger.error(f"Failed to get price data for {symbol}: {str(e)}")
            raise ConnectionError(f"Failed to get price data for {symbol}: {str(e)}")
        
    async def search_assets(self, query: str) -> List[Dict[str, Any]]:
        """Search for assets matching a query.
        
        Args:
            query: Search query
            
        Returns:
            List of asset information
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._client is None:
            await self.connect()
            
        try:
            # Alpaca doesn't have a direct search endpoint, so we'll get all assets and filter
            assets = self._client.list_assets(status="active")
            
            # Filter assets by query (case-insensitive)
            query = query.lower()
            filtered_assets = [
                asset for asset in assets
                if query in asset.symbol.lower() or query in asset.name.lower()
            ]
            
            # Convert to standard format
            results = []
            for asset in filtered_assets[:20]:  # Limit to 20 results
                asset_class = AssetClass.EQUITY
                asset_type = AssetType.STOCK if asset.asset_class == "us_equity" else AssetType.ETF
                
                results.append({
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "exchange": asset.exchange,
                    "asset_class": asset_class.value,
                    "asset_type": asset_type.value,
                    "tradable": asset.tradable,
                })
                
            return results
        except APIError as e:
            logger.error(f"Failed to search assets: {str(e)}")
            raise ConnectionError(f"Failed to search assets: {str(e)}")
        
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
        if self._client is None:
            await self.connect()
            
        try:
            asset = self._client.get_asset(symbol)
            
            if not asset:
                raise ValueError(f"Asset not found: {symbol}")
                
            asset_class = AssetClass.EQUITY
            asset_type = AssetType.STOCK if asset.asset_class == "us_equity" else AssetType.ETF
            
            return {
                "symbol": asset.symbol,
                "name": asset.name,
                "exchange": asset.exchange,
                "asset_class": asset_class.value,
                "asset_type": asset_type.value,
                "tradable": asset.tradable,
                "fractionable": asset.fractionable,
                "marginable": asset.marginable,
                "shortable": asset.shortable,
            }
        except APIError as e:
            if "not found" in str(e).lower():
                raise ValueError(f"Asset not found: {symbol}")
            logger.error(f"Failed to get asset info for {symbol}: {str(e)}")
            raise ConnectionError(f"Failed to get asset info for {symbol}: {str(e)}")
            
    async def get_account_info(self) -> Dict[str, Any]:
        """Get information about the Alpaca account.
        
        Returns:
            Account information
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._client is None:
            await self.connect()
            
        try:
            account = self._client.get_account()
            
            return {
                "id": account.id,
                "status": account.status,
                "currency": account.currency,
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "buying_power": float(account.buying_power),
                "equity": float(account.equity),
                "last_equity": float(account.last_equity),
                "long_market_value": float(account.long_market_value),
                "short_market_value": float(account.short_market_value),
                "initial_margin": float(account.initial_margin),
                "maintenance_margin": float(account.maintenance_margin),
                "daytrade_count": int(account.daytrade_count),
                "trading_blocked": account.trading_blocked,
                "account_blocked": account.account_blocked,
            }
        except APIError as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise ConnectionError(f"Failed to get account info: {str(e)}") 