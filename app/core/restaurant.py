"""
Restaurant management module for Pulsara IVR v2.
"""

from typing import Dict, Optional, List
from app.models.schemas import Restaurant as RestaurantSchema
from app.models.database_models import Restaurant as RestaurantModel
from app.db import get_db, SessionLocal
from app.utils.logging import get_logger
import uuid

logger = get_logger(__name__)

def get_restaurant_by_id(restaurant_id: str) -> Optional[RestaurantSchema]:
    """
    Get a restaurant by ID from the database.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The restaurant or None if not found
    """
    if not restaurant_id:
        logger.warning("Tried to get restaurant with empty ID")
        return None
        
    try:
        db = SessionLocal()
        restaurant_db = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
        db.close()
        
        if not restaurant_db:
            logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return None
            
        # Convert database model to schema model for API responses
        restaurant = RestaurantSchema(
            id=restaurant_db.id,
            name=restaurant_db.name,
            address=restaurant_db.address or "",
            phone=restaurant_db.phone or "",
            timezone=restaurant_db.timezone if hasattr(restaurant_db, 'timezone') else "America/Chicago"
        )
        
        return restaurant
    except Exception as e:
        logger.error(f"Error fetching restaurant by ID {restaurant_id}: {e}")
        db.close()
        return None

def get_restaurant_by_phone(phone: str) -> Optional[RestaurantSchema]:
    """
    Get a restaurant by phone number from the database.
    
    Args:
        phone: The restaurant phone number
        
    Returns:
        The restaurant or None if not found
    """
    if not phone:
        logger.warning("Tried to get restaurant with empty phone number")
        return None
        
    try:
        db = SessionLocal()
        restaurant_db = db.query(RestaurantModel).filter(RestaurantModel.phone == phone).first()
        db.close()
        
        if not restaurant_db:
            logger.warning(f"Restaurant not found with phone number: {phone}")
            return None
            
        # Convert database model to schema model for API responses
        restaurant = RestaurantSchema(
            id=restaurant_db.id,
            name=restaurant_db.name,
            address=restaurant_db.address or "",
            phone=restaurant_db.phone or "",
            timezone=restaurant_db.timezone if hasattr(restaurant_db, 'timezone') else "America/Chicago"
        )
        
        return restaurant
    except Exception as e:
        logger.error(f"Error fetching restaurant by phone {phone}: {e}")
        db.close()
        return None

def get_all_restaurants() -> List[RestaurantSchema]:
    """
    Get all restaurants from the database.
    
    Returns:
        A list of all restaurants
    """
    try:
        db = SessionLocal()
        restaurants_db = db.query(RestaurantModel).all()
        db.close()
        
        # Convert database models to schema models for API responses
        restaurants = []
        for restaurant_db in restaurants_db:
            restaurant = RestaurantSchema(
                id=restaurant_db.id,
                name=restaurant_db.name,
                address=restaurant_db.address or "",
                phone=restaurant_db.phone or "",
                timezone=restaurant_db.timezone if hasattr(restaurant_db, 'timezone') else "America/Chicago"
            )
            restaurants.append(restaurant)
            
        return restaurants
    except Exception as e:
        logger.error(f"Error fetching all restaurants: {e}")
        db.close()
        return []

# Alias for backwards compatibility
# The default_restaurant concept is removed - calls should explicitly specify a restaurant
# This could be used to provide a "default" restaurant if absolutely necessary
def get_default_restaurant() -> Optional[RestaurantSchema]:
    """
    Get a default restaurant, if needed for backwards compatibility.
    In production, all calls should be tied to a specific restaurant.
    """
    logger.warning("get_default_restaurant() called - this is deprecated")
    
    try:
        db = SessionLocal()
        # Get the first restaurant in the database - highly non-deterministic!
        # In practice, you should ALWAYS specify a restaurant rather than using this fallback.
        restaurant_db = db.query(RestaurantModel).first()
        db.close()
        
        if not restaurant_db:
            logger.warning("No restaurants found in database to use as default!")
            return None
            
        # Convert database model to schema model for API responses
        restaurant = RestaurantSchema(
            id=restaurant_db.id,
            name=restaurant_db.name,
            address=restaurant_db.address or "",
            phone=restaurant_db.phone or "",
            timezone=restaurant_db.timezone if hasattr(restaurant_db, 'timezone') else "America/Chicago"
        )
        
        return restaurant
    except Exception as e:
        logger.error(f"Error fetching default restaurant: {e}")
        db.close()
        return None

# The default fallback value is now a function call
default_restaurant = get_default_restaurant()
