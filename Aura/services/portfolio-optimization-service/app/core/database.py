"""Database connections for the portfolio optimization service."""

from aura_common.config import get_settings
from aura_common.database import InfluxDBClient


settings = get_settings()

# InfluxDB client
influxdb_client = InfluxDBClient(settings) 