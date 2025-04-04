# Data Ingestion Service

The Data Ingestion Service is responsible for connecting to various data sources, retrieving data, and publishing it to Kafka topics for further processing in the Aura platform.

## Features

- **Market Data**: Fetch OHLCV (Open, High, Low, Close, Volume) data for stocks and ETFs
- **News**: Fetch financial news articles and headlines
- **SEC Filings**: Fetch SEC filings (10-K, 10-Q, etc.) and extract financial data
- **Asset Information**: Search for assets and retrieve detailed information
- **Kafka Integration**: Publish all fetched data to Kafka topics for consumption by other services

## Connectors

The service currently supports the following data connectors:

- **Alpaca**: For market data and asset information
- **NewsAPI**: For news articles and headlines
- **SEC EDGAR**: For SEC filings

## API Endpoints

### Market Data

- `POST /api/v1/market-data/fetch`: Fetch market data for a list of symbols
- `POST /api/v1/market-data/assets/search`: Search for assets
- `GET /api/v1/market-data/assets/{symbol}`: Get information about a specific asset

### News

- `POST /api/v1/news/fetch`: Fetch news articles based on keywords or symbols
- `GET /api/v1/news/headlines`: Fetch top headlines

### SEC Filings

- `POST /api/v1/sec/filings`: Fetch SEC filings for a symbol
- `GET /api/v1/sec/filings/{symbol}/latest`: Get the latest filing for a symbol
- `GET /api/v1/sec/financial-data/{symbol}`: Extract financial data from filings

## Local Development

### Prerequisites

- Python 3.10+
- Kafka

### Setup

1. Install dependencies:

```bash
pip install poetry
poetry install
```

2. Set up environment variables:

```bash
cp ../../.env.example .env
# Edit .env with your configuration, including API keys for data providers
```

3. Run the service:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

4. Access the API documentation:

```
http://localhost:8001/docs
```

## Docker

```bash
docker build -t aura/data-ingestion-service .
docker run -p 8001:8001 --env-file .env aura/data-ingestion-service
```

## Testing

```bash
poetry run pytest
```

## Kafka Topics

The service publishes to the following Kafka topics:

- `raw_market_data`: Market data (OHLCV)
- `raw_news`: News articles
- `raw_sec_filings`: SEC filings

## Adding New Data Sources

To add a new data source:

1. Create a new connector class in the `app/connectors` directory
2. Implement the required interface methods
3. Register the connector in `app/connectors/__init__.py`
4. Update the API endpoints to use the new connector 