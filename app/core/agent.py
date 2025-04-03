"""
Agent management module for Pulsara IVR v2.
"""

import json
from typing import Dict, Optional, List, Any
from app.models.schemas import Agent as AgentSchema
from app.models.database_models import Restaurant as RestaurantModel
from app.db import get_db, SessionLocal
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id
import uuid

logger = get_logger(__name__)

def get_system_prompt(restaurant_id: str) -> Dict[str, Any]:
    """
    Get the system prompt for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The system prompt as a dictionary
    """
    from app.services.elevenlabs import get_system_prompt_template
    
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {restaurant_id}")
        return {}
    
    # Get the system prompt template
    template = get_system_prompt_template()
    
    # Replace placeholders with restaurant-specific values
    if "workplace" in template:
        template["workplace"]["restaurantName"] = restaurant.name
        if restaurant.address:
            city_state = restaurant.address.split(",")[-2].strip() if len(restaurant.address.split(",")) > 1 else ""
            template["workplace"]["location"] = city_state
    
    # Get restaurant settings
    from app.core.settings import get_settings
    settings = get_settings(restaurant_id)
    
    # Update operational context if settings exist
    if settings and "operationalContext" in template:
        template["operationalContext"]["workingHours"] = f"{settings.call_hours_start} - {settings.call_hours_end}"
    
    return template

def get_agent_tools() -> List[Dict[str, Any]]:
    """
    Get the default agent tools.
    
    Returns:
        A list of tool configurations
    """
    return [
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

def get_agent_by_restaurant(restaurant_id: str) -> Optional[AgentSchema]:
    """
    Get an agent configuration by restaurant ID.
    
    This function fetches the restaurant from the database and uses its
    elevenlabsAgentId and voiceId to construct an Agent object.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The agent configuration or None if not found
    """
    if not restaurant_id:
        logger.warning("Tried to get agent with empty restaurant ID")
        return None
        
    try:
        db = SessionLocal()
        restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
        db.close()
        
        if not restaurant:
            logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return None
            
        # Check if the restaurant has the necessary agent configuration
        if not restaurant.elevenlabsAgentId:
            logger.warning(f"Restaurant {restaurant.name} (ID: {restaurant_id}) does not have an ElevenLabs Agent ID configured")
            return None
            
        # Construct an agent configuration from the restaurant's fields
        agent_id = str(uuid.uuid4())  # Generate a local ID for this agent config
        
        # In SQLAlchemy, systemPrompt might be a string or might not exist
        system_prompt = {}
        if hasattr(restaurant, 'systemPrompt') and restaurant.systemPrompt:
            try:
                # Try to parse as JSON if it's stored as a string
                if isinstance(restaurant.systemPrompt, str):
                    system_prompt = json.loads(restaurant.systemPrompt)
                else:
                    system_prompt = restaurant.systemPrompt
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, generate a system prompt
                system_prompt = get_system_prompt(restaurant_id)
        else:
            # Generate a system prompt if none exists
            system_prompt = get_system_prompt(restaurant_id)
            
        agent = AgentSchema(
            id=agent_id,
            restaurant_id=restaurant_id,
            elevenlabs_agent_id=restaurant.elevenlabsAgentId,
            name=f"Pulsara for {restaurant.name}",
            voice_id=restaurant.voiceId or "EXAVITQu4vr4xnSDxMaL",  # Default voice ID if not set
            system_prompt=system_prompt,
            tools=get_agent_tools()
        )
        
        return agent
    except Exception as e:
        logger.error(f"Error fetching agent for restaurant ID {restaurant_id}: {e}")
        db.close()
        return None
        
def get_agent_by_id(agent_id: str) -> Optional[AgentSchema]:
    """
    This function is only included for API compatibility.
    In the shared DB architecture, agents aren't stored separately but
    derived from restaurant records.
    
    Args:
        agent_id: The agent ID (which would be the restaurant ID in this case)
        
    Returns:
        Always returns None as we don't store separate agents
    """
    logger.warning(f"get_agent_by_id() called with {agent_id} - not supported in shared DB architecture")
    return None

# For backwards compatibility, provide a way to get a default agent
def get_default_agent() -> Optional[AgentSchema]:
    """
    Get a default agent from the first available restaurant.
    This should only be used in fallback scenarios where a specific restaurant is not known.
    """
    logger.warning("get_default_agent() called - this is deprecated")
    
    try:
        # Get the first restaurant
        db = SessionLocal()
        restaurant = db.query(RestaurantModel).first()
        db.close()
        
        if not restaurant:
            logger.warning("No restaurants found to construct a default agent")
            return None
            
        # Use get_agent_by_restaurant to construct the agent
        return get_agent_by_restaurant(restaurant.id)
    except Exception as e:
        logger.error(f"Error getting default agent: {e}")
        return None

# Alias for backwards compatibility
default_agent = get_default_agent()
