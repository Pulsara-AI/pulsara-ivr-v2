"""
Database connection setup for SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logging import get_logger

# --- Environment Variable Loading ---
# Load from .env file in the IVR-Databased directory
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
DATABASE_URL = os.getenv("DATABASE_URL")
# ----------------------------------

logger = get_logger(__name__)

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set or not found in .env!")
    # Try loading from parent directory .env as fallback
    parent_dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
    if os.path.exists(parent_dotenv_path):
        load_dotenv(dotenv_path=parent_dotenv_path)
        DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set!")
    else:
        logger.info(f"Loaded DATABASE_URL from fallback path: {parent_dotenv_path}")
else:
    logger.info(f"Loaded DATABASE_URL from primary path: {dotenv_path}")

# Create the SQLAlchemy engine
try:
    # Example: postgresql+psycopg2://user:password@host:port/database
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)  # Set echo=True for debugging SQL
    logger.info("SQLAlchemy engine created successfully.")
except ImportError as e:
    logger.error(f"Database driver error (e.g., psycopg2 not installed?): {e}")
    raise
except Exception as e:
    logger.error(f"Error creating SQLAlchemy engine: {e}")
    raise

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("SQLAlchemy SessionLocal created.")

# Base class for declarative class definitions
Base = declarative_base()
logger.info("SQLAlchemy Base created.")

def get_db():
    """
    Dependency function to get a database session for FastAPI routes.
    Ensures the session is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error during request: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Example usage (for direct testing)
if __name__ == "__main__":
    logger.info("Testing database connection...")
    try:
        connection = engine.connect()
        logger.info("Database connection successful!")
        connection.close()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

def check_database_connection():
    """
    Tests the database connection and returns a status object.
    
    Returns:
        Dict with connection status and message
    """
    try:
        # Attempt to connect to the database
        connection = engine.connect()
        
        # Execute a simple query to further validate the connection
        result = connection.execute("SELECT 1").scalar()
        connection.close()
        
        # Check that the query returned the expected result
        if result == 1:
            return {
                "connected": True,
                "message": "Successfully connected to database and executed test query"
            }
        else:
            return {
                "connected": False,
                "message": f"Connected to database but test query returned unexpected result: {result}"
            }
    except ImportError as e:
        return {
            "connected": False,
            "message": f"Database driver error (missing dependency?): {e}"
        }
    except SQLAlchemyError as e:
        return {
            "connected": False,
            "message": f"Database connection error: {e}"
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Unexpected error: {e}"
        } 