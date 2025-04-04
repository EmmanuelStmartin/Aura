"""API router for the data ingestion service."""

from fastapi import APIRouter

from app.api.endpoints import market_data, news, sec

api_router = APIRouter()

api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(sec.router, prefix="/sec", tags=["sec-filings"]) 