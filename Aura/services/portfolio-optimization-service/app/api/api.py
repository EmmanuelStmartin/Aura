"""API router for portfolio optimization service."""

from fastapi import APIRouter

from app.api.endpoints import optimize, status


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(optimize.router, prefix="/optimize", tags=["optimize"])
api_router.include_router(status.router, tags=["status"]) 