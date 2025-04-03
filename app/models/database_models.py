"""
SQLAlchemy models mapping to the shared database tables.

These models mirror the structure of the tables defined in the main application's
Prisma schema (backend/prisma/schema.prisma).
"""

from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey, DateTime, Enum, Text, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db import Base

# --- Enum Definitions ---
# These should match the enums in the Prisma schema

class CallType(str, enum.Enum):
    AI_HANDLED = "AI_HANDLED"
    FORWARDED = "FORWARDED"

class SentimentType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

# --- Model Definitions ---

class Restaurant(Base):
    """SQLAlchemy model for the Restaurant table."""
    __tablename__ = "Restaurant"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    ownerId = Column(String, nullable=False)
    timezone = Column(String, default="America/Chicago")
    aiCallHandling = Column(Boolean, default=True)
    callHoursStart = Column(String, default="09:00")
    callHoursEnd = Column(String, default="17:00")
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    elevenlabsAgentId = Column(String)
    voiceId = Column(String)
    
    # Define relationships if needed for the IVR app's specific use cases
    # These are optional and can be added later if needed
    calls = relationship("Call", back_populates="restaurant")
    settings = relationship("Settings", back_populates="restaurant", uselist=False)
    menuItems = relationship("MenuItem", back_populates="restaurant")

class Call(Base):
    """SQLAlchemy model for the Call table."""
    __tablename__ = "Call"

    id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)
    duration = Column(String, nullable=False)
    type = Column(Enum(CallType), nullable=False)
    sentiment = Column(Enum(SentimentType), nullable=False)
    transcript = Column(Text, nullable=False)
    keyPoints = Column(ARRAY(String), nullable=False, default=[])
    actions = Column(ARRAY(String), nullable=False, default=[])
    restaurantId = Column(String, ForeignKey("Restaurant.id"), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    audioUrl = Column(String)
    callerNumber = Column(String)
    call_sid = Column(String)
    conversationId = Column(String)
    
    # Define the relationship to Restaurant
    restaurant = relationship("Restaurant", back_populates="calls")

class Settings(Base):
    """SQLAlchemy model for the Settings table."""
    __tablename__ = "Settings"

    id = Column(String, primary_key=True)
    postCallMessage = Column(String)
    cateringEnabled = Column(Boolean, default=False)
    restaurantId = Column(String, ForeignKey("Restaurant.id"), unique=True, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generalContext = Column(String)
    
    # Define the relationship to Restaurant
    restaurant = relationship("Restaurant", back_populates="settings")

class MenuItem(Base):
    """SQLAlchemy model for the MenuItem table."""
    __tablename__ = "MenuItem"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    isAvailable = Column(Boolean, default=True)
    restaurantId = Column(String, ForeignKey("Restaurant.id"), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define the relationship to Restaurant
    restaurant = relationship("Restaurant", back_populates="menuItems")

class TextLink(Base):
    """SQLAlchemy model for the TextLink table."""
    __tablename__ = "TextLink"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    message = Column(String)
    restaurantId = Column(String, ForeignKey("Restaurant.id"), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship is defined only if needed by IVR app
    # restaurant = relationship("Restaurant")

# Note: We're only defining models for tables that the IVR app needs to directly 
# access. Other tables from the Prisma schema can be added later if needed. 