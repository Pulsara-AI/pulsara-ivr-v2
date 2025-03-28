"""
Dashboard API integration service for Pulsara IVR v2.
"""

from typing import Dict, Any, Optional, List
from app.utils.logging import get_logger
from app.models.schemas import Restaurant, Agent, KnowledgeBase, Settings, Call
from app.utils.helpers import safe_json_dumps, safe_json_loads

logger = get_logger(__name__)

# API base URL
# In a real implementation, this would be loaded from environment variables
API_BASE_URL = "https://dashboard.pulsara.ai/api/v1"

# API key
# In a real implementation, this would be loaded from environment variables
API_KEY = "mock_api_key"

def make_api_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """
    Make an API request to the dashboard API.
    
    Args:
        method: The HTTP method (GET, POST, PUT, DELETE)
        endpoint: The API endpoint
        data: The request data (optional)
        
    Returns:
        The API response as a dictionary
    """
    # In a real implementation, this would use requests or httpx
    # For now, we'll just log the request and return a mock response
    logger.info(f"Making API request: {method} {endpoint}")
    
    if data:
        logger.info(f"Request data: {safe_json_dumps(data)}")
    
    # Mock successful response
    return {"success": True}

def get_restaurant(restaurant_id: str) -> Optional[Dict]:
    """
    Get a restaurant from the dashboard API.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The restaurant data as a dictionary or None if not found
    """
    endpoint = f"/restaurants/{restaurant_id}"
    
    # Mock response
    return {
        "id": restaurant_id,
        "name": "Pulsara Restaurant",
        "address": "1509 W Taylor St, Chicago, IL 60607",
        "phone": "224-651-4178",
        "timezone": "America/Chicago"
    }

def get_restaurant_by_phone(phone_number: str) -> Optional[Dict]:
    """
    Get a restaurant by phone number from the dashboard API.
    
    Args:
        phone_number: The restaurant phone number
        
    Returns:
        The restaurant data as a dictionary or None if not found
    """
    endpoint = f"/restaurants/lookup?phone={phone_number}"
    
    # Mock response
    return {
        "id": "default",
        "name": "Pulsara Restaurant",
        "address": "1509 W Taylor St, Chicago, IL 60607",
        "phone": phone_number,
        "timezone": "America/Chicago"
    }

def get_agent(restaurant_id: str) -> Optional[Dict]:
    """
    Get an agent for a restaurant from the dashboard API.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The agent data as a dictionary or None if not found
    """
    endpoint = f"/restaurants/{restaurant_id}/agent"
    
    # Mock response
    return {
        "id": "agent_123",
        "restaurant_id": restaurant_id,
        "elevenlabs_agent_id": "mock_elevenlabs_agent_id",
        "name": "Pulsara",
        "voice_id": "tnSpp4vdxKPjI9w0GnoV",
        "system_prompt": {},
        "tools": [
            {
                "name": "end_call",
                "enabled": True,
                "description": "Ends the current phone call completely."
            },
            {
                "name": "get_address",
                "enabled": True,
                "description": "Returns the restaurant's address."
            },
            {
                "name": "forward_call",
                "enabled": True,
                "description": "Forwards the call to the restaurant owner."
            }
        ]
    }

def get_knowledge_bases(restaurant_id: str) -> List[Dict]:
    """
    Get knowledge bases for a restaurant from the dashboard API.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A list of knowledge base data as dictionaries
    """
    endpoint = f"/restaurants/{restaurant_id}/knowledge-bases"
    
    # Mock response
    return [
        {
            "id": "kb_123",
            "restaurant_id": restaurant_id,
            "elevenlabs_kb_id": "mock_elevenlabs_kb_id_menu",
            "name": "Menu",
            "type": "menu",
            "content": "Menu content..."
        },
        {
            "id": "kb_124",
            "restaurant_id": restaurant_id,
            "elevenlabs_kb_id": "mock_elevenlabs_kb_id_info",
            "name": "Restaurant Information",
            "type": "info",
            "content": "Restaurant information content..."
        }
    ]

def get_settings(restaurant_id: str) -> Optional[Dict]:
    """
    Get settings for a restaurant from the dashboard API.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The settings data as a dictionary or None if not found
    """
    endpoint = f"/restaurants/{restaurant_id}/settings"
    
    # Mock response
    return {
        "id": "settings_123",
        "restaurant_id": restaurant_id,
        "call_hours_start": "09:00",
        "call_hours_end": "21:00",
        "ai_enabled": True,
        "post_call_message": None,
        "catering_enabled": False,
        "catering_min_notice": 24,
        "catering_message": None
    }

def log_call(call: Call) -> bool:
    """
    Log a call to the dashboard API.
    
    Args:
        call: The call to log
        
    Returns:
        True if the call was logged successfully, False otherwise
    """
    endpoint = f"/restaurants/{call.restaurant_id}/calls"
    
    # Convert call to dictionary
    call_data = call.dict()
    
    # Make API request
    response = make_api_request("POST", endpoint, call_data)
    
    return response.get("success", False)

def update_call(call: Call) -> bool:
    """
    Update a call in the dashboard API.
    
    Args:
        call: The call to update
        
    Returns:
        True if the call was updated successfully, False otherwise
    """
    endpoint = f"/restaurants/{call.restaurant_id}/calls/{call.id}"
    
    # Convert call to dictionary
    call_data = call.dict()
    
    # Make API request
    response = make_api_request("PUT", endpoint, call_data)
    
    return response.get("success", False)

def get_webhook_url(restaurant_id: str, event_type: str) -> Optional[str]:
    """
    Get a webhook URL for a restaurant and event type from the dashboard API.
    
    Args:
        restaurant_id: The restaurant ID
        event_type: The event type
        
    Returns:
        The webhook URL or None if not found
    """
    endpoint = f"/restaurants/{restaurant_id}/webhooks?event_type={event_type}"
    
    # Mock response
    return f"https://dashboard.pulsara.ai/api/v1/webhooks/{restaurant_id}/{event_type}"

def send_webhook_event(url: str, event_type: str, data: Dict) -> bool:
    """
    Send a webhook event to the dashboard API.
    
    Args:
        url: The webhook URL
        event_type: The event type
        data: The event data
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # In a real implementation, this would use requests or httpx
    # For now, we'll just log the event and return a mock response
    logger.info(f"Sending webhook event: {event_type} to {url}")
    logger.info(f"Event data: {safe_json_dumps(data)}")
    
    # Mock successful response
    return True
