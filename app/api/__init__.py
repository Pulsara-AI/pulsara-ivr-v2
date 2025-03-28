"""
API routes for Pulsara IVR v2.
"""

from fastapi import APIRouter
from app.api.call_routes import router as call_router
from app.api.webhook_routes import router as webhook_router
from app.api.health_routes import router as health_router

# Create the main API router
api_router = APIRouter()

# Include the call routes
api_router.include_router(
    call_router,
    prefix="/calls",
    tags=["calls"]
)

# Include the webhook routes
api_router.include_router(
    webhook_router,
    prefix="/webhooks",
    tags=["webhooks"]
)

# Include the health routes
api_router.include_router(
    health_router,
    prefix="/health",
    tags=["health"]
)
