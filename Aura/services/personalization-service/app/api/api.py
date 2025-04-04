"""API router for personalization service."""

from fastapi import APIRouter

from app.api.endpoints import profiles, interests, recommendations, status


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(profiles.router, prefix="/users", tags=["profiles"])
api_router.include_router(interests.router, prefix="/interests", tags=["interests"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(status.router, tags=["status"]) 