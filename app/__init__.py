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
        
        # Log database connection status
        from app.db import check_database_connection
        db_status = check_database_connection()
        if db_status["connected"]:
            logger.info(f"Successfully connected to database: {db_status['message']}")
        else:
            logger.error(f"Failed to connect to database: {db_status['message']}")
            logger.warning("Application will start but calls requiring database access may fail")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down Pulsara IVR v2")
    
    return app
