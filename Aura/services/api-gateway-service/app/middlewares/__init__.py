"""Middlewares for the API Gateway Service."""

from app.middlewares.auth import AuthMiddleware

__all__ = ["AuthMiddleware"] 