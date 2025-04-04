"""InfluxDB client for Aura services."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from aura_common.config import Settings, get_settings


class InfluxDBClient:
    """InfluxDB client for Aura services."""
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize InfluxDB client.
        
        Args:
            settings: Settings instance
        """
        if settings is None:
            settings = get_settings()
            
        self.url = settings.INFLUXDB_URL
        self.token = settings.INFLUXDB_TOKEN
        self.org = settings.INFLUXDB_ORG
        self.bucket = settings.INFLUXDB_BUCKET
        
        self.client = influxdb_client.InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )
        
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
    
    def write_point(self, measurement: str, tags: Dict[str, str], fields: Dict[str, Any], timestamp: Optional[datetime] = None) -> None:
        """Write a point to InfluxDB.
        
        Args:
            measurement: Measurement name
            tags: Tags as a dictionary
            fields: Fields as a dictionary
            timestamp: Timestamp (default: current time)
        """
        point = influxdb_client.Point(measurement)
        
        for key, value in tags.items():
            point = point.tag(key, value)
            
        for key, value in fields.items():
            point = point.field(key, value)
            
        if timestamp:
            point = point.time(timestamp)
            
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
    
    def write_points(self, points: List[influxdb_client.Point]) -> None:
        """Write multiple points to InfluxDB.
        
        Args:
            points: List of Point objects
        """
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Flux query.
        
        Args:
            query: Flux query string
            
        Returns:
            Query results as list of dictionaries
        """
        tables = self.query_api.query(query, org=self.org)
        
        results = []
        for table in tables:
            for record in table.records:
                results.append(record.values)
                
        return results
    
    def close(self) -> None:
        """Close the client connection."""
        self.client.close() 