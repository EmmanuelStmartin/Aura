"""API router for the Alerting Service."""

from fastapi import APIRouter

from app.api.endpoints import alerts, rules, websocket

api_router = APIRouter()

api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(websocket.router, tags=["websocket"]) 