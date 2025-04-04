# API Gateway Service

The API Gateway Service serves as the main entry point for all client applications to interact with the Aura platform microservices. It handles authentication, request routing, and basic response transformation.

## Features

- **Authentication Middleware**: Validates JWT tokens from client requests and forwards authenticated user information to downstream services.
- **Service Routing**: Routes requests to the appropriate microservices based on URL path.
- **Error Handling**: Provides consistent error responses for downstream service failures.
- **WebSocket Support**: Proxies WebSocket connections for real-time alerts.

## API Routes

The API Gateway routes requests to the following services:

- `/auth/*` → Auth Service (authentication, registration)
- `/users/*` → Auth Service (user management)
- `/market-data/*` → Data Ingestion Service (assets, market data)
- `/predict/*` → AI Modeling Service (predictions)
- `/optimize/*` → Portfolio Optimization Service (portfolio construction)
- `/brokerage/*` → Brokerage Integration Service (positions, orders)
- `/alerts/*` → Alerting Service (user alerts)

## WebSocket Endpoints

- `/ws/alerts/{user_id}` - Real-time alerts for a specific user

## Environment Variables

This service uses the common configuration from `aura_common.config.Settings`. Key variables include:

- `JWT_SECRET_KEY` - Secret key for JWT token validation
- `*_SERVICE_URL` - URLs for each downstream service
- `PORT` - Port for the API Gateway (default: 8000)

## Development

### Setup

```bash
cd services/api-gateway-service
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

## Dependencies

- FastAPI - Web framework
- httpx - HTTP client for service communication
- python-jose - JWT token handling
- aura_common - Common utilities for Aura services 