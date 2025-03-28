"""
Agent management module for Pulsara IVR v2.
"""

import json
from typing import Dict, Optional, List, Any
from app.models.schemas import Agent
from config.settings import AGENT
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id

logger = get_logger(__name__)

# In-memory agent cache
# This will be replaced with a database in the future
_agents = {}

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
        template["workplace"]["location"] = restaurant.address.split(",")[-2].strip()
    
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

def get_agent_by_id(agent_id: str) -> Optional[Agent]:
    """
    Get an agent by ID.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        The agent or None if not found
    """
    return _agents.get(agent_id)

def get_agent_by_restaurant(restaurant_id: str) -> Optional[Agent]:
    """
    Get an agent by restaurant ID.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The agent or None if not found
    """
    for agent in _agents.values():
        if agent.restaurant_id == restaurant_id:
            return agent
    return None

def create_agent(restaurant_id: str, name: str = None) -> Agent:
    """
    Create a new agent for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        name: The agent name (optional)
        
    Returns:
        The created agent
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise ValueError(f"Restaurant not found for ID: {restaurant_id}")
    
    # Generate a name if not provided
    if not name:
        name = f"Pulsara for {restaurant.name}"
    
    # Create the agent
    agent = Agent(
        restaurant_id=restaurant_id,
        elevenlabs_agent_id=AGENT["elevenlabs_agent_id"],
        name=name,
        voice_id=AGENT["voice_id"],
        system_prompt=get_system_prompt(restaurant_id),
        tools=get_agent_tools()
    )
    
    # Generate an ID if not provided
    if not agent.id:
        import uuid
        agent.id = str(uuid.uuid4())
    
    # Store the agent
    _agents[agent.id] = agent
    logger.info(f"Created agent: {agent.name} (ID: {agent.id}) for restaurant: {restaurant.name}")
    
    return agent

def update_agent(agent_id: str, agent_data: Dict) -> Optional[Agent]:
    """
    Update an existing agent.
    
    Args:
        agent_id: The ID of the agent to update
        agent_data: The updated agent data
        
    Returns:
        The updated agent or None if not found
    """
    existing = get_agent_by_id(agent_id)
    if not existing:
        return None
    
    updated = Agent(**{**existing.dict(), **agent_data})
    _agents[agent_id] = updated
    logger.info(f"Updated agent: {updated.name} (ID: {agent_id})")
    return updated

def delete_agent(agent_id: str) -> bool:
    """
    Delete an agent.
    
    Args:
        agent_id: The ID of the agent to delete
        
    Returns:
        True if the agent was deleted, False otherwise
    """
    if agent_id in _agents:
        agent = _agents[agent_id]
        del _agents[agent_id]
        logger.info(f"Deleted agent: {agent.name} (ID: {agent_id})")
        return True
    return False

def initialize_default_agent():
    """
    Initialize the default agent for the default restaurant.
    """
    from app.core.restaurant import default_restaurant
    
    # Check if an agent already exists for the default restaurant
    existing_agent = get_agent_by_restaurant(default_restaurant.id)
    if existing_agent:
        logger.info(f"Default agent already exists: {existing_agent.name}")
        return existing_agent
    
    # Create a new agent for the default restaurant
    return create_agent(default_restaurant.id)

# Initialize the default agent
default_agent = initialize_default_agent()
