"""API router for the API Gateway Service."""

from fastapi import APIRouter

from app.api.endpoints import (
    auth, 
    users, 
    market_data, 
    predictions, 
    portfolio, 
    orders, 
    alerts
)

api_router = APIRouter()

# Auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Market data routes
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])

# Prediction routes
api_router.include_router(predictions.router, prefix="/predict", tags=["predictions"])

# Portfolio optimization routes
api_router.include_router(portfolio.router, prefix="/optimize", tags=["portfolio"])

# Orders and positions routes (brokerage)
api_router.include_router(orders.router, prefix="/brokerage", tags=["brokerage"])

# Alerts routes
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"]) 