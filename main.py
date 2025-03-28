"""
Main entry point for Pulsara IVR v2.
"""

import uvicorn
from app import create_app
from config.settings import SERVER

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Run the application using uvicorn
    uvicorn.run(
        "main:app",
        host=SERVER["host"],
        port=SERVER["port"],
        reload=True
    )
