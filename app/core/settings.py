"""
Settings management module for Pulsara IVR v2.
"""

from typing import Dict, Optional
from app.models.schemas import Settings
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id

logger = get_logger(__name__)

# In-memory settings cache
# This will be replaced with a database in the future
_settings = {}

def get_settings(restaurant_id: str) -> Optional[Settings]:
    """
    Get settings for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The settings or None if not found
    """
    return _settings.get(restaurant_id)

def create_settings(restaurant_id: str, settings_data: Dict = None) -> Settings:
    """
    Create settings for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        settings_data: The settings data (optional)
        
    Returns:
        The created settings
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise ValueError(f"Restaurant not found for ID: {restaurant_id}")
    
    # Create the settings
    settings = Settings(
        restaurant_id=restaurant_id,
        **(settings_data or {})
    )
    
    # Generate an ID if not provided
    if not settings.id:
        import uuid
        settings.id = str(uuid.uuid4())
    
    # Store the settings
    _settings[restaurant_id] = settings
    logger.info(f"Created settings for restaurant: {restaurant.name} (ID: {restaurant_id})")
    
    return settings

def update_settings(restaurant_id: str, settings_data: Dict) -> Optional[Settings]:
    """
    Update settings for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        settings_data: The updated settings data
        
    Returns:
        The updated settings or None if not found
    """
    existing = get_settings(restaurant_id)
    if not existing:
        return None
    
    updated = Settings(**{**existing.dict(), **settings_data})
    _settings[restaurant_id] = updated
    logger.info(f"Updated settings for restaurant ID: {restaurant_id}")
    return updated

def delete_settings(restaurant_id: str) -> bool:
    """
    Delete settings for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        True if the settings were deleted, False otherwise
    """
    if restaurant_id in _settings:
        del _settings[restaurant_id]
        logger.info(f"Deleted settings for restaurant ID: {restaurant_id}")
        return True
    return False

def initialize_default_settings():
    """
    Initialize default settings for the default restaurant.
    """
    from app.core.restaurant import default_restaurant
    
    # Check if settings already exist for the default restaurant
    existing_settings = get_settings(default_restaurant.id)
    if existing_settings:
        logger.info(f"Default settings already exist for restaurant: {default_restaurant.name}")
        return existing_settings
    
    # Create default settings for the default restaurant
    return create_settings(default_restaurant.id)

# Initialize default settings
default_settings = initialize_default_settings()
