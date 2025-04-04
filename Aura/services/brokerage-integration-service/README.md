# Brokerage Integration Service

The Brokerage Integration Service provides an abstraction layer for interacting with brokerage platforms. It currently integrates with Alpaca Markets for executing trades and retrieving account information.

## Features

- **Position Management**: Retrieve current positions and their market values.
- **Order Management**: Submit and track trading orders.
- **Simulation Mode**: Support for simulated trading when `ENABLE_REAL_TRADING` is set to `false`.
- **API Key Validation**: Validates API keys on startup to ensure the service can connect to the brokerage.

## API Endpoints

### Positions

- `GET /positions` - Get all positions in the portfolio
- `GET /positions/{symbol}` - Get position information for a specific symbol

### Orders

- `POST /orders` - Create a new order
- `GET /orders/{order_id}` - Get information about a specific order

## Environment Variables

This service uses the common configuration from `aura_common.config.Settings`. Key variables include:

- `ALPACA_API_KEY` - API key for Alpaca Markets (required)
- `ALPACA_API_SECRET` - API secret for Alpaca Markets (required)
- `ENABLE_REAL_TRADING` - Boolean flag to enable or disable real trading (default: false)

## Development

### Setup

```bash
cd services/brokerage-integration-service
poetry install
```

### Running

```bash
poetry run uvicorn app.main:app --reload
```

### Testing

```bash
poetry run pytest
```

## Safety Features

For safety, this service will:

1. Validate API keys on startup and fail if they're invalid
2. Only execute real trades when `ENABLE_REAL_TRADING` is explicitly set to `true`
3. When real trading is disabled, orders are logged but not actually executed
4. Provide detailed error messages and proper error handling

## Dependencies

- FastAPI - Web framework
- alpaca-trade-api - Python client for Alpaca Markets API
- aura_common - Common utilities for Aura services 