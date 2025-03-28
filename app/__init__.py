"""
Pulsara IVR v2 application.
"""

from fastapi import FastAPI
from app.api import api_router
from app.utils.logging import setup_logging
from config.settings import API_PREFIX

# Set up logging
logger = setup_logging()

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        The configured FastAPI application
    """
    # Create the FastAPI application
    app = FastAPI(
        title="Pulsara IVR v2",
        description="Pulsara IVR v2 API",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Include the API router
    app.include_router(api_router, prefix=API_PREFIX)
    
    # Initialize the application
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting Pulsara IVR v2")
        
        # Initialize the restaurant service
        from app.core.restaurant import initialize_default_restaurant
        default_restaurant = initialize_default_restaurant()
        logger.info(f"Initialized default restaurant: {default_restaurant.name}")
        
        # Initialize the agent service
        from app.core.agent import initialize_default_agent
        default_agent = initialize_default_agent()
        logger.info(f"Initialized default agent: {default_agent.name}")
        
        # Initialize the settings service
        from app.core.settings import initialize_default_settings
        default_settings = initialize_default_settings()
        logger.info(f"Initialized default settings for restaurant: {default_restaurant.name}")
        
        # Initialize the knowledge base service
        from app.core.knowledge_base import initialize_default_knowledge_base
        initialize_default_knowledge_base()
        logger.info(f"Initialized default knowledge base for restaurant: {default_restaurant.name}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down Pulsara IVR v2")
    
    return app
