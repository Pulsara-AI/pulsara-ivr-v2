"""
Knowledge base management module for Pulsara IVR v2.
"""

from typing import Dict, Optional, List
from app.models.schemas import KnowledgeBase as KnowledgeBaseSchema
from app.models.database_models import Restaurant as RestaurantModel
from app.models.database_models import MenuItem as MenuItemModel
from app.models.database_models import TextLink as TextLinkModel
from app.db import get_db, SessionLocal
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id
import uuid

logger = get_logger(__name__)

def generate_menu_knowledge_base(restaurant_id: str) -> Optional[KnowledgeBaseSchema]:
    """
    Generate a menu knowledge base from the restaurant's menu items in the database.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A knowledge base object containing formatted menu content
    """
    if not restaurant_id:
        logger.warning("Tried to generate menu KB with empty restaurant ID")
        return None
    
    # Get the restaurant to ensure it exists
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {restaurant_id}")
        return None
    
    try:
        # Fetch menu items from the database
        db = SessionLocal()
        menu_items = db.query(MenuItemModel).filter(MenuItemModel.restaurantId == restaurant_id).all()
        db.close()
        
        if not menu_items:
            logger.warning(f"No menu items found for restaurant: {restaurant.name}")
            # Return an empty KB so the agent knows about an empty menu
            return KnowledgeBaseSchema(
                id=str(uuid.uuid4()),
                restaurant_id=restaurant_id,
                elevenlabs_kb_id=f"kb_{restaurant_id}_menu",
                name="Menu",
                type="menu",
                content="This restaurant does not have a menu configured yet."
            )
            
        # Group menu items by category
        menu_by_category = {}
        for item in menu_items:
            if item.category not in menu_by_category:
                menu_by_category[item.category] = []
            
            # Format price with 2 decimal places
            price_formatted = f"${item.price:.2f}"
            
            # Format description if it exists
            description = f": {item.description}" if item.description else ""
            
            # Add formatted menu item entry
            if item.isAvailable:
                menu_by_category[item.category].append(f"- {item.name}: {price_formatted}{description}")
            # Could optionally include unavailable items with a marker
        
        # Build the formatted menu content
        content = []
        for category, items in menu_by_category.items():
            content.append(f"{category}:")
            content.extend(items)
            content.append("")  # Add a blank line between categories
        
        # Create a knowledge base object
        kb = KnowledgeBaseSchema(
            id=str(uuid.uuid4()),
            restaurant_id=restaurant_id,
            elevenlabs_kb_id=f"kb_{restaurant_id}_menu",
            name="Menu",
            type="menu",
            content="\n".join(content)
        )
        
        return kb
    except Exception as e:
        logger.error(f"Error generating menu knowledge base for restaurant ID {restaurant_id}: {e}")
        if 'db' in locals():
            db.close()
        return None

def generate_info_knowledge_base(restaurant_id: str) -> Optional[KnowledgeBaseSchema]:
    """
    Generate an info knowledge base with restaurant details from the database.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A knowledge base object containing formatted restaurant info
    """
    if not restaurant_id:
        logger.warning("Tried to generate info KB with empty restaurant ID")
        return None
    
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {restaurant_id}")
        return None
    
    try:
        # Get restaurant settings for hours
        from app.core.settings import get_settings
        settings = get_settings(restaurant_id)
        
        # Get text links
        db = SessionLocal()
        text_links = db.query(TextLinkModel).filter(TextLinkModel.restaurantId == restaurant_id).all()
        db.close()
        
        # Build the info content
        content = [
            f"Restaurant Name: {restaurant.name}",
            f"Address: {restaurant.address}" if restaurant.address else "Address: Not specified",
            f"Phone: {restaurant.phone}" if restaurant.phone else "Phone: Not specified"
        ]
        
        # Add hours
        if settings:
            content.append(f"Business Hours: {settings.call_hours_start} - {settings.call_hours_end}, Monday to Sunday")
        
        content.append("")  # Add blank line
        
        # Add text links if available
        if text_links:
            content.append("Online Links:")
            for link in text_links:
                content.append(f"- {link.name}: {link.url}" + (f" ({link.message})" if link.message else ""))
        
        # Create a knowledge base object
        kb = KnowledgeBaseSchema(
            id=str(uuid.uuid4()),
            restaurant_id=restaurant_id,
            elevenlabs_kb_id=f"kb_{restaurant_id}_info",
            name="Restaurant Information",
            type="info",
            content="\n".join(content)
        )
        
        return kb
    except Exception as e:
        logger.error(f"Error generating info knowledge base for restaurant ID {restaurant_id}: {e}")
        if 'db' in locals():
            db.close()
        return None

def get_knowledge_base_by_type(restaurant_id: str, kb_type: str) -> Optional[KnowledgeBaseSchema]:
    """
    Get a knowledge base by type for a restaurant. Generated dynamically.
    
    Args:
        restaurant_id: The restaurant ID
        kb_type: The knowledge base type
        
    Returns:
        The knowledge base object or None if not found
    """
    if not restaurant_id:
        logger.warning("Tried to get KB with empty restaurant ID")
        return None
    
    # Based on the requested type, generate the appropriate knowledge base
    if kb_type == "menu":
        return generate_menu_knowledge_base(restaurant_id)
    elif kb_type == "info":
        return generate_info_knowledge_base(restaurant_id)
    else:
        logger.warning(f"Unsupported knowledge base type: {kb_type}")
        return None

def get_knowledge_bases_by_restaurant(restaurant_id: str) -> List[KnowledgeBaseSchema]:
    """
    Get all knowledge bases for a restaurant. Generated dynamically.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A list of knowledge base items for the restaurant
    """
    result = []
    
    # Generate menu knowledge base
    menu_kb = generate_menu_knowledge_base(restaurant_id)
    if menu_kb:
        result.append(menu_kb)
    
    # Generate info knowledge base
    info_kb = generate_info_knowledge_base(restaurant_id)
    if info_kb:
        result.append(info_kb)
    
    return result

def sync_knowledge_base(kb: KnowledgeBaseSchema) -> bool:
    """
    Sync a knowledge base with ElevenLabs.
    
    Args:
        kb: The knowledge base to sync
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import here to avoid circular imports
        from app.services.elevenlabs import sync_knowledge_base_with_elevenlabs
        
        # Actually sync with ElevenLabs
        success = sync_knowledge_base_with_elevenlabs(kb)
        if success:
            logger.info(f"Successfully synced knowledge base: {kb.name} for restaurant ID: {kb.restaurant_id}")
        else:
            logger.warning(f"Failed to sync knowledge base: {kb.name} for restaurant ID: {kb.restaurant_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error syncing knowledge base with ElevenLabs: {e}")
        return False

def get_knowledge_base_by_id(kb_id: str) -> Optional[KnowledgeBaseSchema]:
    """
    This function is included for API compatibility.
    In our architecture, knowledge bases are generated on the fly rather than stored.
    
    Args:
        kb_id: The knowledge base ID
        
    Returns:
        Always returns None as we don't store knowledge bases
    """
    logger.warning(f"get_knowledge_base_by_id() called with {kb_id} - not supported as KBs are generated dynamically")
    return None

def initialize_default_knowledge_base():
    """
    Initialize default knowledge bases for the first available restaurant.
    This is now a no-op as we generate knowledge bases on demand.
    """
    logger.warning("initialize_default_knowledge_base() called - this is now a no-op as KBs are generated on demand")
    
    try:
        # Get the first restaurant
        db = SessionLocal()
        restaurant = db.query(RestaurantModel).first()
        db.close()
        
        if not restaurant:
            logger.warning("No restaurants found to initialize KBs")
            return None
            
        # Generate and sync the knowledge bases
        menu_kb = generate_menu_knowledge_base(restaurant.id)
        if menu_kb:
            sync_knowledge_base(menu_kb)
            
        info_kb = generate_info_knowledge_base(restaurant.id)
        if info_kb:
            sync_knowledge_base(info_kb)
            
        logger.info(f"Initialized knowledge bases for restaurant: {restaurant.name}")
        
    except Exception as e:
        logger.error(f"Error initializing default knowledge bases: {e}")
        return None
