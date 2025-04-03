"""
Settings management module for Pulsara IVR v2.
"""

from typing import Dict, Optional
from app.models.schemas import Settings as SettingsSchema
from app.models.database_models import Settings as SettingsModel
from app.models.database_models import Restaurant as RestaurantModel
from app.db import get_db, SessionLocal
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id
import uuid

logger = get_logger(__name__)

def get_settings(restaurant_id: str) -> Optional[SettingsSchema]:
    """
    Get settings for a restaurant from the database.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        The settings or None if not found
    """
    if not restaurant_id:
        logger.warning("Tried to get settings with empty restaurant ID")
        return None
        
    try:
        db = SessionLocal()
        
        # First check the dedicated Settings table
        settings_db = db.query(SettingsModel).filter(SettingsModel.restaurantId == restaurant_id).first()
        
        # If settings exist in the Settings table, use those
        if settings_db:
            settings = SettingsSchema(
                id=settings_db.id,
                restaurant_id=settings_db.restaurantId,
                call_hours_start=settings_db.callHoursStart if hasattr(settings_db, 'callHoursStart') else "09:00",
                call_hours_end=settings_db.callHoursEnd if hasattr(settings_db, 'callHoursEnd') else "17:00",
                ai_enabled=settings_db.aiEnabled if hasattr(settings_db, 'aiEnabled') else True,
                post_call_message=settings_db.postCallMessage,
                catering_enabled=settings_db.cateringEnabled,
                catering_min_notice=settings_db.cateringMinNotice if hasattr(settings_db, 'cateringMinNotice') else 24,
                catering_message=settings_db.cateringMessage if hasattr(settings_db, 'cateringMessage') else None
            )
            db.close()
            return settings
        
        # If no dedicated settings, get the relevant fields from the Restaurant table
        restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
        db.close()
        
        if not restaurant:
            logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return None
            
        # Create a settings object from restaurant fields
        settings = SettingsSchema(
            id=f"settings-{restaurant_id}",  # Generated ID
            restaurant_id=restaurant_id,
            # These fields are on the Restaurant model directly in Prisma schema
            call_hours_start=restaurant.callHoursStart if hasattr(restaurant, 'callHoursStart') else "09:00",
            call_hours_end=restaurant.callHoursEnd if hasattr(restaurant, 'callHoursEnd') else "17:00",
            ai_enabled=restaurant.aiCallHandling if hasattr(restaurant, 'aiCallHandling') else True,
            # These would be null/default as they're not on Restaurant
            post_call_message=None,
            catering_enabled=False,
            catering_min_notice=24,
            catering_message=None
        )
        
        return settings
    except Exception as e:
        logger.error(f"Error fetching settings for restaurant ID {restaurant_id}: {e}")
        if 'db' in locals():
            db.close()
        return None

# For backwards compatibility, provide access to default settings
def get_default_settings() -> Optional[SettingsSchema]:
    """
    Get default settings for the first available restaurant.
    This should only be used in fallback scenarios where a specific restaurant is not known.
    """
    logger.warning("get_default_settings() called - this is deprecated")
    
    try:
        # Get the first restaurant
        db = SessionLocal()
        restaurant = db.query(RestaurantModel).first()
        db.close()
        
        if not restaurant:
            logger.warning("No restaurants found to get default settings")
            return None
            
        # Use get_settings to get settings for this restaurant
        return get_settings(restaurant.id)
    except Exception as e:
        logger.error(f"Error getting default settings: {e}")
        return None

# Alias for backwards compatibility
default_settings = get_default_settings()
