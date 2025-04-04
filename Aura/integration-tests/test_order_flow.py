import os
import pytest
import requests
import json
from typing import Dict, Any

# Test configuration
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "http://localhost:8000")
TEST_USER = {
    "email": "test_user@example.com",
    "password": "TestPassword123!"
}

@pytest.fixture
def auth_token() -> str:
    """Get authentication token for test user."""
    # Login to get auth token
    response = requests.post(
        f"{API_GATEWAY_URL}/auth/login",
        json=TEST_USER
    )
    assert response.status_code == 200, "Failed to login"
    
    data = response.json()
    assert "access_token" in data, "No access token in response"
    return data["access_token"]

def test_place_market_order(auth_token: str):
    """Test market order placement flow through the API Gateway to Brokerage Integration Service."""
    # Create market order request
    order_request = {
        "symbol": "AAPL",
        "quantity": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    
    # Set authorization header
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Submit order
    response = requests.post(
        f"{API_GATEWAY_URL}/brokerage/orders",
        headers=headers,
        json=order_request
    )
    
    # Verify response
    assert response.status_code == 201, f"Failed to place order: {response.text}"
    
    order_data = response.json()
    assert "id" in order_data, "No order ID in response"
    assert order_data["symbol"] == order_request["symbol"]
    assert order_data["quantity"] == order_request["quantity"]
    assert order_data["side"] == order_request["side"]
    
    # Verify order status
    order_id = order_data["id"]
    response = requests.get(
        f"{API_GATEWAY_URL}/brokerage/orders/{order_id}",
        headers=headers
    )
    
    assert response.status_code == 200, f"Failed to get order status: {response.text}"
    
    status_data = response.json()
    assert status_data["id"] == order_id
    # In test environments, the order might be in "filled" status immediately
    assert status_data["status"] in ["filled", "new", "accepted", "pending_new"], f"Unexpected order status: {status_data['status']}"

def test_place_limit_order(auth_token: str):
    """Test limit order placement flow through the API Gateway to Brokerage Integration Service."""
    # Create limit order request
    order_request = {
        "symbol": "MSFT",
        "quantity": 1,
        "side": "buy",
        "type": "limit",
        "time_in_force": "day",
        "limit_price": 300.00  # Set an appropriate limit price
    }
    
    # Set authorization header
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Submit order
    response = requests.post(
        f"{API_GATEWAY_URL}/brokerage/orders",
        headers=headers,
        json=order_request
    )
    
    # Verify response
    assert response.status_code == 201, f"Failed to place order: {response.text}"
    
    order_data = response.json()
    assert "id" in order_data, "No order ID in response"
    assert order_data["symbol"] == order_request["symbol"]
    assert order_data["quantity"] == order_request["quantity"]
    assert order_data["side"] == order_request["side"]
    assert order_data["type"] == "limit"
    assert order_data["limit_price"] == order_request["limit_price"]
    
    # Verify order status
    order_id = order_data["id"]
    response = requests.get(
        f"{API_GATEWAY_URL}/brokerage/orders/{order_id}",
        headers=headers
    )
    
    assert response.status_code == 200, f"Failed to get order status: {response.text}"

def test_order_validation_errors(auth_token: str):
    """Test order validation error handling."""
    # Test case: Missing required field (quantity)
    invalid_order = {
        "symbol": "AAPL",
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_GATEWAY_URL}/brokerage/orders",
        headers=headers,
        json=invalid_order
    )
    
    assert response.status_code == 422, "Expected validation error for missing quantity"
    
    # Test case: Invalid symbol
    invalid_order = {
        "symbol": "INVALID_SYMBOL_123456",
        "quantity": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    
    response = requests.post(
        f"{API_GATEWAY_URL}/brokerage/orders",
        headers=headers,
        json=invalid_order
    )
    
    assert response.status_code in [400, 422], "Expected error for invalid symbol"

def test_unauthorized_order_access(auth_token: str):
    """Test unauthorized access to orders."""
    # Place an order first
    order_request = {
        "symbol": "AAPL",
        "quantity": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_GATEWAY_URL}/brokerage/orders",
        headers=headers,
        json=order_request
    )
    
    order_id = response.json()["id"]
    
    # Try to access without auth token
    response = requests.get(
        f"{API_GATEWAY_URL}/brokerage/orders/{order_id}"
    )
    
    assert response.status_code == 401, "Expected unauthorized error"

if __name__ == "__main__":
    # For manual test execution
    token = auth_token()
    test_place_market_order(token)
    test_place_limit_order(token)
    test_order_validation_errors(token)
    test_unauthorized_order_access(token) 