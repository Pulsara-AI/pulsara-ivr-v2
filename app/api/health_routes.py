"""
Health check API routes for Pulsara IVR v2.
"""

from fastapi import APIRouter, Request
from app.utils.logging import get_logger
from app.api.call_routes import active_connections, active_conversations
from app.core.restaurant import get_all_restaurants
from app.core.agent import get_agent_by_restaurant
from app.core.call import get_call_statistics
from config.environment import ELEVENLABS_API_KEY, TWILIO_ACCOUNT_SID

logger = get_logger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns basic health information about the service.
    """
    # Check if we have API keys
    elevenlabs_api_key_set = bool(ELEVENLABS_API_KEY)
    twilio_account_sid_set = bool(TWILIO_ACCOUNT_SID)
    
    # Get active call count
    active_call_count = len(active_connections)
    
    # Get restaurant count
    restaurants = get_all_restaurants()
    restaurant_count = len(restaurants)
    
    # Check if each restaurant has an agent
    restaurants_with_agents = 0
    for restaurant in restaurants:
        agent = get_agent_by_restaurant(restaurant.id)
        if agent:
            restaurants_with_agents += 1
    
    return {
        "status": "ok",
        "version": "2.0.0",
        "elevenlabs_api_key_set": elevenlabs_api_key_set,
        "twilio_account_sid_set": twilio_account_sid_set,
        "active_calls": active_call_count,
        "restaurants": restaurant_count,
        "restaurants_with_agents": restaurants_with_agents
    }

@router.get("/status")
async def service_status():
    """
    Detailed service status endpoint.
    
    Returns detailed information about the service status.
    """
    # Get active connections
    active_call_count = len(active_connections)
    active_call_info = []
    
    for connection_id, conn_info in active_connections.items():
        call_sid = conn_info.get("call_sid", "Unknown")
        status = conn_info.get("status", "Unknown")
        timestamp = conn_info.get("timestamp", "Unknown")
        
        active_call_info.append({
            "connection_id": connection_id,
            "call_sid": call_sid,
            "status": status,
            "timestamp": timestamp
        })
    
    # Get restaurant information
    restaurants = get_all_restaurants()
    restaurant_info = []
    
    for restaurant in restaurants:
        agent = get_agent_by_restaurant(restaurant.id)
        
        # Get call statistics for the restaurant
        call_stats = get_call_statistics(restaurant.id, days=7)
        
        restaurant_info.append({
            "id": restaurant.id,
            "name": restaurant.name,
            "has_agent": agent is not None,
            "call_stats": {
                "total_calls": call_stats["totalCalls"],
                "ai_handled": call_stats["aiHandled"],
                "forwarded": call_stats["forwarded"]
            }
        })
    
    return {
        "status": "ok",
        "active_calls": {
            "count": active_call_count,
            "calls": active_call_info
        },
        "restaurants": restaurant_info
    }

@router.get("/metrics")
async def metrics():
    """
    Metrics endpoint.
    
    Returns metrics about the service for monitoring.
    """
    # Get all restaurants
    restaurants = get_all_restaurants()
    
    # Collect metrics for each restaurant
    restaurant_metrics = []
    total_calls = 0
    total_ai_handled = 0
    total_forwarded = 0
    
    for restaurant in restaurants:
        # Get call statistics for the restaurant
        call_stats = get_call_statistics(restaurant.id, days=30)
        
        # Update totals
        total_calls += call_stats["totalCalls"]
        total_ai_handled += call_stats["aiHandled"]
        total_forwarded += call_stats["forwarded"]
        
        restaurant_metrics.append({
            "id": restaurant.id,
            "name": restaurant.name,
            "total_calls": call_stats["totalCalls"],
            "ai_handled": call_stats["aiHandled"],
            "forwarded": call_stats["forwarded"],
            "avg_duration": call_stats["avgDuration"],
            "sentiment": call_stats["sentimentBreakdown"]
        })
    
    # Calculate overall metrics
    overall_metrics = {
        "total_calls": total_calls,
        "ai_handled": total_ai_handled,
        "forwarded": total_forwarded,
        "ai_handled_percentage": (total_ai_handled / total_calls * 100) if total_calls > 0 else 0,
        "forwarded_percentage": (total_forwarded / total_calls * 100) if total_calls > 0 else 0
    }
    
    return {
        "overall": overall_metrics,
        "restaurants": restaurant_metrics
    }
