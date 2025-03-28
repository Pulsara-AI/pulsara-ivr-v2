"""
Knowledge base management module for Pulsara IVR v2.
"""

from typing import Dict, Optional, List
from app.models.schemas import KnowledgeBase
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id

logger = get_logger(__name__)

# In-memory knowledge base cache
# This will be replaced with a database in the future
_knowledge_bases = {}

def get_knowledge_base_by_id(kb_id: str) -> Optional[KnowledgeBase]:
    """
    Get a knowledge base item by ID.
    
    Args:
        kb_id: The knowledge base item ID
        
    Returns:
        The knowledge base item or None if not found
    """
    return _knowledge_bases.get(kb_id)

def get_knowledge_bases_by_restaurant(restaurant_id: str) -> List[KnowledgeBase]:
    """
    Get all knowledge base items for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A list of knowledge base items for the restaurant
    """
    return [kb for kb in _knowledge_bases.values() if kb.restaurant_id == restaurant_id]

def get_knowledge_base_by_type(restaurant_id: str, kb_type: str) -> Optional[KnowledgeBase]:
    """
    Get a knowledge base item by type for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        kb_type: The knowledge base type
        
    Returns:
        The knowledge base item or None if not found
    """
    for kb in _knowledge_bases.values():
        if kb.restaurant_id == restaurant_id and kb.type == kb_type:
            return kb
    return None

def create_knowledge_base(restaurant_id: str, name: str, kb_type: str, content: str, elevenlabs_kb_id: str = None) -> KnowledgeBase:
    """
    Create a new knowledge base item.
    
    Args:
        restaurant_id: The restaurant ID
        name: The knowledge base item name
        kb_type: The knowledge base type
        content: The knowledge base content
        elevenlabs_kb_id: The ElevenLabs knowledge base ID (optional)
        
    Returns:
        The created knowledge base item
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise ValueError(f"Restaurant not found for ID: {restaurant_id}")
    
    # Create the knowledge base item
    kb = KnowledgeBase(
        restaurant_id=restaurant_id,
        name=name,
        type=kb_type,
        content=content,
        elevenlabs_kb_id=elevenlabs_kb_id or f"kb_{restaurant_id}_{kb_type}"
    )
    
    # Generate an ID if not provided
    if not kb.id:
        import uuid
        kb.id = str(uuid.uuid4())
    
    # Store the knowledge base item
    _knowledge_bases[kb.id] = kb
    logger.info(f"Created knowledge base item: {kb.name} (ID: {kb.id}) for restaurant: {restaurant.name}")
    
    # Sync with ElevenLabs if no ID was provided
    if not elevenlabs_kb_id:
        from app.services.elevenlabs import sync_knowledge_base
        sync_knowledge_base(kb)
    
    return kb

def update_knowledge_base(kb_id: str, kb_data: Dict) -> Optional[KnowledgeBase]:
    """
    Update an existing knowledge base item.
    
    Args:
        kb_id: The ID of the knowledge base item to update
        kb_data: The updated knowledge base data
        
    Returns:
        The updated knowledge base item or None if not found
    """
    existing = get_knowledge_base_by_id(kb_id)
    if not existing:
        return None
    
    updated = KnowledgeBase(**{**existing.dict(), **kb_data})
    _knowledge_bases[kb_id] = updated
    logger.info(f"Updated knowledge base item: {updated.name} (ID: {kb_id})")
    
    # Sync with ElevenLabs
    from app.services.elevenlabs import sync_knowledge_base
    sync_knowledge_base(updated)
    
    return updated

def delete_knowledge_base(kb_id: str) -> bool:
    """
    Delete a knowledge base item.
    
    Args:
        kb_id: The ID of the knowledge base item to delete
        
    Returns:
        True if the knowledge base item was deleted, False otherwise
    """
    if kb_id in _knowledge_bases:
        kb = _knowledge_bases[kb_id]
        
        # Delete from ElevenLabs
        from app.services.elevenlabs import delete_knowledge_base as delete_elevenlabs_kb
        delete_elevenlabs_kb(kb.elevenlabs_kb_id)
        
        # Delete from local cache
        del _knowledge_bases[kb_id]
        logger.info(f"Deleted knowledge base item: {kb.name} (ID: {kb_id})")
        return True
    return False

def initialize_default_knowledge_base():
    """
    Initialize default knowledge base items for the default restaurant.
    """
    from app.core.restaurant import default_restaurant
    
    # Check if menu knowledge base already exists
    menu_kb = get_knowledge_base_by_type(default_restaurant.id, "menu")
    if not menu_kb:
        # Create default menu knowledge base
        menu_content = """
        Appetizers:
        - Garlic Bread: $5.99
        - Mozzarella Sticks: $7.99
        - Chicken Wings: $9.99
        
        Main Courses:
        - Spaghetti Bolognese: $12.99
        - Margherita Pizza: $14.99
        - Chicken Parmesan: $16.99
        
        Desserts:
        - Tiramisu: $6.99
        - Cheesecake: $5.99
        - Ice Cream: $4.99
        """
        create_knowledge_base(
            restaurant_id=default_restaurant.id,
            name="Menu",
            kb_type="menu",
            content=menu_content
        )
        logger.info(f"Created default menu knowledge base for restaurant: {default_restaurant.name}")
    
    # Check if info knowledge base already exists
    info_kb = get_knowledge_base_by_type(default_restaurant.id, "info")
    if not info_kb:
        # Create default info knowledge base
        info_content = f"""
        Restaurant Name: {default_restaurant.name}
        Address: {default_restaurant.address}
        Phone: {default_restaurant.phone}
        Hours: 9 AM - 10 PM, Monday to Sunday
        Reservations: Recommended for parties of 6 or more
        Parking: Available in the lot behind the restaurant
        """
        create_knowledge_base(
            restaurant_id=default_restaurant.id,
            name="Restaurant Information",
            kb_type="info",
            content=info_content
        )
        logger.info(f"Created default info knowledge base for restaurant: {default_restaurant.name}")

# Initialize default knowledge base items
initialize_default_knowledge_base()
