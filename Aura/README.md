# Aura: AI-Powered Financial Trading Platform

Aura is a sophisticated microservices-based platform that leverages AI to process financial data, generate insights, and provide optimized trading strategies.

## Architecture

The platform follows a microservices architecture with the following components:

### Core Services

- **API Gateway Service**: Central entry point for all client applications, handling authentication and request routing.
- **Auth Service**: User authentication, registration, and profile management.
- **Data Ingestion Service**: Integration with market data providers and ingestion of financial data.
- **Data Processing Service**: Processing of raw market data into usable formats and technical indicators.
- **AI Modeling Service**: Machine learning models for price prediction and trend analysis.
- **Portfolio Optimization Service**: Asset allocation and portfolio construction algorithms.
- **Personalization Service**: User preference management and tailored experiences.
- **Brokerage Integration Service**: Connection to brokerage platforms for executing trades.
- **Alerting Service**: Rule-based alert generation and delivery based on market conditions.

### Infrastructure

- PostgreSQL: Relational database for user data, preferences, and transactions.
- InfluxDB: Time-series database for market data storage.
- Kafka: Message queue for asynchronous processing and service communication.
- Docker & Docker Compose: Container orchestration for local development.

## Key Features

- **Real-time Data Processing**: Process market data in real-time through a Kafka-based pipeline.
- **AI-Powered Predictions**: Utilize machine learning models to predict market movements.
- **Modern Portfolio Theory**: Implement portfolio optimization using PyPortfolioOpt.
- **Modular Architecture**: Independently scalable microservices.
- **Robust Security**: JWT-based authentication and role-based access control.
- **Brokerage Integration**: Connect to Alpaca Markets for paper trading and real trading.
- **Real-time Alerts**: WebSocket-based alerts for market conditions and trading opportunities.

## Safety Features

- **API Key Validation**: Services validate required API keys on startup to prevent runtime errors.
- **Simulated Trading**: Real trading is disabled by default and requires explicit enablement.
- **Comprehensive Logging**: Detailed logging for debugging and auditing.
- **Error Handling**: Robust error handling across all services.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Poetry (Python package manager)

### Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aura.git
   cd aura
   ```

2. Copy the example environment file:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file to add your API keys:
   - ALPACA_API_KEY and ALPACA_API_SECRET for brokerage integration
   - NEWS_API_KEY for news data (if used)
   - Other API keys as needed

4. Start the services:
   ```
   docker-compose up
   ```

5. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## Development

### Adding a New Service

1. Create a new directory in the `services` folder.
2. Use the existing service structure as a template.
3. Add the service to the `docker-compose.yml` file.

### Common Library

All services use the `aura_common` library for shared functionality:

- Configuration management
- Database connections
- Kafka clients
- Security utilities
- Logging

### Coding Standards

- Use Black for code formatting
- Write comprehensive docstrings
- Include type annotations
- Write unit tests for all services

## Deployment

For production deployment, consider the following:

- Use Kubernetes for container orchestration
- Implement proper secrets management (not environment variables)
- Set up monitoring and alerting
- Configure horizontal scaling for services

## Security Notes

- Store API keys in a secure vault in production (e.g., Kubernetes Secrets)
- Rotate JWT secrets regularly
- Monitor for unusual activity
- Set appropriate rate limits on public endpoints

## License

This project is licensed under the MIT License - see the LICENSE file for details. 