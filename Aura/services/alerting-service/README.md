# Alerting Service

The Alerting Service processes market data to generate and deliver alerts to users based on configurable rules. It provides both REST API endpoints for managing alerts and WebSocket connections for real-time alert delivery.

## Features

- **Rule Engine**: Evaluate market data against user-defined rules to trigger alerts
- **Kafka Consumer**: Process data from the data-processing-service in real-time
- **WebSocket Support**: Deliver alerts to connected clients in real-time
- **Alert Management**: REST API for managing alerts and rules
- **Database Storage**: Store alerts and rules in PostgreSQL for persistence

## API Endpoints

### Alerts

- `GET /alerts` - Get alerts for a user with filtering options
- `GET /alerts/{alert_id}` - Get a specific alert
- `PATCH /alerts/{alert_id}` - Update an alert
- `PATCH /alerts/{alert_id}/mark-as-read` - Mark an alert as read

### Rules

- `GET /rules` - Get alert rules for a user with filtering options
- `POST /rules` - Create a new alert rule
- `GET /rules/{rule_id}` - Get a specific rule
- `PATCH /rules/{rule_id}` - Update a rule
- `DELETE /rules/{rule_id}` - Delete a rule (soft delete)

### WebSocket

- `WebSocket /ws/alerts/{user_id}` - Real-time alerts for a specific user

## Rule Configuration

Alert rules are configurable with the following parameters:

- **Symbol**: Target asset symbol, or null for all assets
- **Alert Type**: Type of alert (technical indicator, news sentiment, etc.)
- **Indicator**: Data field to monitor (e.g., rsi.value, news.sentiment)
- **Operator**: Comparison operator (>, <, ==, !=, etc.)
- **Threshold**: Value to compare against
- **Cooldown**: Minimum time between repeated alerts

## Environment Variables

This service uses the common configuration from `aura_common.config.Settings`. Key variables include:

- `KAFKA_BOOTSTRAP_SERVERS` - Kafka connection string
- `POSTGRES_*` - PostgreSQL connection parameters
- `PORT` - Service port (default: 8006)

## Development

### Setup

```bash
cd services/alerting-service
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
- SQLAlchemy - Database ORM
- Kafka-Python - Kafka client
- WebSockets - Real-time communication
- aura_common - Common utilities for Aura services 