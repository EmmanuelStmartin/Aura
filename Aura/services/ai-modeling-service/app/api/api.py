"""API router for AI modeling service."""

from fastapi import APIRouter

from app.api.endpoints import predictions, training, status


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(status.router, tags=["status"]) 