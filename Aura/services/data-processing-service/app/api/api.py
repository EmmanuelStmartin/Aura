"""API router for data processing service."""

from fastapi import APIRouter

from app.api.endpoints import status, admin


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(status.router, tags=["status"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"]) 