"""
Data models and schemas for Pulsara IVR v2.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class Restaurant(BaseModel):
    """Restaurant model for storing restaurant information."""
    id: Optional[str] = None
    name: str
    address: str
    phone: str
    timezone: str = "America/Chicago"
    
class Agent(BaseModel):
    """Agent model for storing agent configuration."""
    id: Optional[str] = None
    restaurant_id: str
    elevenlabs_agent_id: str
    name: str
    voice_id: str
    system_prompt: Dict[str, Any]
    tools: List[Dict[str, Any]]
    
class Call(BaseModel):
    """Call model for storing call information."""
    id: Optional[str] = None
    restaurant_id: str
    call_sid: str
    stream_sid: Optional[str] = None
    caller_number: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    handled_by: str = "ai"
    forwarded: bool = False
    forwarded_to: Optional[str] = None
    forwarded_time: Optional[datetime] = None
    transcript: Optional[str] = None
    sentiment_score: Optional[int] = None
    sentiment_label: Optional[str] = None
    summary: Optional[str] = None
    reason: Optional[str] = None
    audio_url: Optional[str] = None
    agent_responses: Optional[List[Dict[str, Any]]] = None
    
class KnowledgeBase(BaseModel):
    """Knowledge base model for storing restaurant-specific knowledge."""
    id: Optional[str] = None
    restaurant_id: str
    elevenlabs_kb_id: str
    name: str
    type: str
    content: str
    
class MenuItem(BaseModel):
    """Menu item model for storing menu items."""
    id: Optional[str] = None
    restaurant_id: str
    name: str
    description: Optional[str] = None
    price: float
    category: str
    is_available: bool = True
    order_position: int = 0
    
class Settings(BaseModel):
    """Settings model for storing restaurant settings."""
    id: Optional[str] = None
    restaurant_id: str
    call_hours_start: str = "09:00"
    call_hours_end: str = "21:00"
    ai_enabled: bool = True
    post_call_message: Optional[str] = None
    catering_enabled: bool = False
    catering_min_notice: Optional[int] = 24
    catering_message: Optional[str] = None
    
class WebhookRegistration(BaseModel):
    """Webhook registration model for IVR integration."""
    callback_url: str
    events: List[str]
    
class APIKey(BaseModel):
    """API key model for IVR integration."""
    name: str
    description: Optional[str] = None
    key: Optional[str] = None  # Only included when creating a new key
    
class CallRequest(BaseModel):
    """Call request model for IVR integration."""
    restaurant_id: str
    call_id: str
    timestamp: datetime
    caller_number: str
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    
class CallCompletion(BaseModel):
    """Call completion model for IVR integration."""
    duration: int
    forwarded_to: Optional[str] = None
    final_transcript: Optional[str] = None
    audio_url: Optional[str] = None
