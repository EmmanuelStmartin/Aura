"""API router for the Brokerage Integration Service."""

from fastapi import APIRouter

from app.api.endpoints import positions, orders

api_router = APIRouter()

api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"]) 