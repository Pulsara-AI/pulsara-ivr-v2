#!/usr/bin/env python3
"""
Database initialization script for Pulsara IVR v2.

This script adds the missing columns to the database tables
to resolve SQLAlchemy errors with the current schema.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

def init_db():
    """Initialize database with required columns."""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    # First check if the Restaurant table exists
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT * FROM \"Restaurant\" LIMIT 1"))
            print("Restaurant table exists")
        except Exception as e:
            print(f"Error checking Restaurant table: {e}")
            print("Make sure the database and basic tables exist first")
            return
    
    # Now let's try to add the timezone column in a separate connection/transaction
    with engine.connect() as conn:
        try:
            # First check if timezone column exists
            try:
                conn.execute(text("SELECT timezone FROM \"Restaurant\" LIMIT 1"))
                print("✅ timezone column already exists")
            except Exception:
                # Commit the transaction before attempting to add the column
                conn.commit()
                
                # Add the missing timezone column in a fresh transaction
                conn.execute(text('ALTER TABLE "Restaurant" ADD COLUMN timezone VARCHAR DEFAULT \'America/Chicago\''))
                print("✅ Added timezone column to Restaurant table")
                
                # Commit the changes
                conn.commit()
                
            print("Database initialization complete!")
            
        except Exception as e:
            print(f"Error modifying tables: {e}")
            conn.rollback()
            return

if __name__ == "__main__":
    init_db() 