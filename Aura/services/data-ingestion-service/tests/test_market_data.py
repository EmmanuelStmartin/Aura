"""Tests for market data endpoints."""

import json
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schema import DataSourceType, DataType


client = TestClient(app)


@pytest.fixture
def mock_data_connector():
    """Fixture for mocking the data connector."""
    with patch("app.api.endpoints.market_data.get_data_connector") as mock:
        connector = AsyncMock()
        mock.return_value = connector
        
        # Mock the get_price_data method
        test_df = pd.DataFrame({
            "Open": [100.0, 101.0, 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [95.0, 96.0, 97.0],
            "Close": [103.0, 104.0, 105.0],
            "Volume": [1000, 2000, 3000]
        }, index=pd.date_range(start=datetime.now() - timedelta(days=2), periods=3, freq='D'))
        
        connector.get_price_data.return_value = test_df
        
        # Mock the search_assets method
        connector.search_assets.return_value = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "asset_class": "equity",
                "asset_type": "stock",
                "tradable": True
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "exchange": "NASDAQ",
                "asset_class": "equity",
                "asset_type": "stock",
                "tradable": True
            }
        ]
        
        # Mock the get_asset_info method
        connector.get_asset_info.return_value = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "asset_class": "equity",
            "asset_type": "stock",
            "tradable": True,
            "fractionable": True,
            "marginable": True,
            "shortable": True
        }
        
        yield connector


@pytest.fixture
def mock_message_publisher():
    """Fixture for mocking the message publisher."""
    with patch("app.api.endpoints.market_data.message_publisher") as mock:
        mock.publish_market_data = AsyncMock()
        yield mock


def test_fetch_market_data(mock_data_connector, mock_message_publisher):
    """Test the fetch market data endpoint."""
    response = client.post(
        "/api/v1/market-data/fetch",
        json={
            "symbols": ["AAPL", "MSFT"],
            "interval": "1d",
            "source": "alpaca"
        }
    )
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["results"]["AAPL"] is True
    assert data["results"]["MSFT"] is True
    
    # Verify the connector was called correctly
    mock_data_connector.connect.assert_called()
    assert mock_data_connector.get_price_data.call_count == 2
    mock_data_connector.disconnect.assert_called()
    
    # Verify the message publisher was called correctly
    assert mock_message_publisher.publish_market_data.call_count == 2


def test_search_assets(mock_data_connector):
    """Test the search assets endpoint."""
    response = client.post(
        "/api/v1/market-data/assets/search",
        json={
            "query": "apple",
            "source": "alpaca"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"
    assert data[1]["symbol"] == "MSFT"
    
    # Verify the connector was called correctly
    mock_data_connector.connect.assert_called()
    mock_data_connector.search_assets.assert_called_once_with(query="apple")
    mock_data_connector.disconnect.assert_called()


def test_get_asset_info(mock_data_connector):
    """Test the get asset info endpoint."""
    response = client.get("/api/v1/market-data/assets/AAPL?source=alpaca")
    
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["name"] == "Apple Inc."
    
    # Verify the connector was called correctly
    mock_data_connector.connect.assert_called()
    mock_data_connector.get_asset_info.assert_called_once_with(symbol="AAPL")
    mock_data_connector.disconnect.assert_called()


def test_get_asset_info_not_found(mock_data_connector):
    """Test the get asset info endpoint with an asset that doesn't exist."""
    # Mock the get_asset_info method to raise ValueError
    mock_data_connector.get_asset_info.side_effect = ValueError("Asset not found")
    
    response = client.get("/api/v1/market-data/assets/INVALID?source=alpaca")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    
    # Verify the connector was called correctly
    mock_data_connector.connect.assert_called()
    mock_data_connector.get_asset_info.assert_called_once_with(symbol="INVALID")
    mock_data_connector.disconnect.assert_called() 