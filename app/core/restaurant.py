"""
Restaurant management module for Pulsara IVR v2.
"""

from typing import Dict, Optional, List
from app.models.schemas import Restaurant
from config.settings import RESTAURANT
from app.utils.logging import get_logger

logger = get_logger(__name__)

# In-memory restaurant cache
# This will be replaced with a database in the future
_restaurants = {}

def initialize_default_restaurant():
    """
    Initialize the default restaurant from settings.
    """
    default_restaurant = Restaurant(
        id="default",
        name=RESTAURANT["name"],
        address=RESTAURANT["address"],
        phone=RESTAURANT["phone"],
        timezone=RESTAURANT["timezone"].zone
    )
    _restaurants[default_restaurant.id] = default_restaurant
    logger.info(f"Initialized default restaurant: {default_restaurant.name}")
    return default_restaurant

def get_restaurant_by_id(restaurant_id: str) -> Optional[Restaurant]:
    """
    Get a restaurant by ID.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The restaurant or None if not found
    """
    return _restaurants.get(restaurant_id)

def get_restaurant_by_phone(phone: str) -> Optional[Restaurant]:
    """
    Get a restaurant by phone number.
    
    Args:
        phone: The restaurant phone number
        
    Returns:
        The restaurant or None if not found
    """
    for restaurant in _restaurants.values():
        if restaurant.phone == phone:
            return restaurant
    return None

def get_all_restaurants() -> List[Restaurant]:
    """
    Get all restaurants.
    
    Returns:
        A list of all restaurants
    """
    return list(_restaurants.values())

def create_restaurant(restaurant: Restaurant) -> Restaurant:
    """
    Create a new restaurant.
    
    Args:
        restaurant: The restaurant to create
        
    Returns:
        The created restaurant
    """
    if not restaurant.id:
        import uuid
        restaurant.id = str(uuid.uuid4())
    _restaurants[restaurant.id] = restaurant
    logger.info(f"Created restaurant: {restaurant.name} (ID: {restaurant.id})")
    return restaurant

def update_restaurant(restaurant_id: str, restaurant_data: Dict) -> Optional[Restaurant]:
    """
    Update an existing restaurant.
    
    Args:
        restaurant_id: The ID of the restaurant to update
        restaurant_data: The updated restaurant data
        
    Returns:
        The updated restaurant or None if not found
    """
    existing = get_restaurant_by_id(restaurant_id)
    if not existing:
        return None
    
    updated = Restaurant(**{**existing.dict(), **restaurant_data})
    _restaurants[restaurant_id] = updated
    logger.info(f"Updated restaurant: {updated.name} (ID: {restaurant_id})")
    return updated

def delete_restaurant(restaurant_id: str) -> bool:
    """
    Delete a restaurant.
    
    Args:
        restaurant_id: The ID of the restaurant to delete
        
    Returns:
        True if the restaurant was deleted, False otherwise
    """
    if restaurant_id in _restaurants:
        restaurant = _restaurants[restaurant_id]
        del _restaurants[restaurant_id]
        logger.info(f"Deleted restaurant: {restaurant.name} (ID: {restaurant_id})")
        return True
    return False

# Initialize the default restaurant
default_restaurant = initialize_default_restaurant()
