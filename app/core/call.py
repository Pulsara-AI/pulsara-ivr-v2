"""
Call management module for Pulsara IVR v2.
"""

from typing import Dict, Optional, List
from datetime import datetime
from app.models.schemas import Call
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id
from app.utils.helpers import get_current_time

logger = get_logger(__name__)

# In-memory call cache
# This will be replaced with a database in the future
_calls = {}

# Active call tracking
_active_calls = {}

def get_call_by_id(call_id: str) -> Optional[Call]:
    """
    Get a call by ID.
    
    Args:
        call_id: The call ID
        
    Returns:
        The call or None if not found
    """
    return _calls.get(call_id)

def get_call_by_sid(call_sid: str) -> Optional[Call]:
    """
    Get a call by Twilio Call SID.
    
    Args:
        call_sid: The Twilio Call SID
        
    Returns:
        The call or None if not found
    """
    for call in _calls.values():
        if call.call_sid == call_sid:
            return call
    return None

def get_calls_by_restaurant(restaurant_id: str) -> List[Call]:
    """
    Get all calls for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A list of calls for the restaurant
    """
    return [call for call in _calls.values() if call.restaurant_id == restaurant_id]

def create_call(restaurant_id: str, call_sid: str, caller_number: str) -> Call:
    """
    Create a new call record.
    
    Args:
        restaurant_id: The restaurant ID
        call_sid: The Twilio Call SID
        caller_number: The caller's phone number
        
    Returns:
        The created call record
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise ValueError(f"Restaurant not found for ID: {restaurant_id}")
    
    # Create the call record
    call = Call(
        restaurant_id=restaurant_id,
        call_sid=call_sid,
        caller_number=caller_number,
        start_time=get_current_time()
    )
    
    # Generate an ID if not provided
    if not call.id:
        import uuid
        call.id = str(uuid.uuid4())
    
    # Store the call record
    _calls[call.id] = call
    logger.info(f"Created call record: {call.id} for restaurant: {restaurant.name}")
    
    # Track as active call
    _active_calls[call_sid] = call.id
    
    return call

def update_call(call_id: str, call_data: Dict) -> Optional[Call]:
    """
    Update an existing call record.
    
    Args:
        call_id: The ID of the call to update
        call_data: The updated call data
        
    Returns:
        The updated call record or None if not found
    """
    existing = get_call_by_id(call_id)
    if not existing:
        return None
    
    updated = Call(**{**existing.dict(), **call_data})
    _calls[call_id] = updated
    logger.info(f"Updated call record: {call_id}")
    return updated

def end_call(call_id: str, forwarded: bool = False, forwarded_to: str = None) -> Optional[Call]:
    """
    End a call and update its record.
    
    Args:
        call_id: The ID of the call to end
        forwarded: Whether the call was forwarded
        forwarded_to: Who the call was forwarded to
        
    Returns:
        The updated call record or None if not found
    """
    call = get_call_by_id(call_id)
    if not call:
        return None
    
    # Update call record
    now = get_current_time()
    call_data = {
        "end_time": now,
        "duration": int((now - call.start_time).total_seconds()),
        "forwarded": forwarded
    }
    
    if forwarded and forwarded_to:
        call_data["forwarded_to"] = forwarded_to
        call_data["forwarded_time"] = now
    
    updated_call = update_call(call_id, call_data)
    
    # Remove from active calls
    if call.call_sid in _active_calls:
        del _active_calls[call.call_sid]
    
    # Trigger email notification
    from app.services.email import send_call_summary_email
    send_call_summary_email(updated_call)
    
    return updated_call

def get_active_call_by_sid(call_sid: str) -> Optional[Call]:
    """
    Get an active call by Twilio Call SID.
    
    Args:
        call_sid: The Twilio Call SID
        
    Returns:
        The active call or None if not found
    """
    call_id = _active_calls.get(call_sid)
    if call_id:
        return get_call_by_id(call_id)
    return None

def get_call_statistics(restaurant_id: str, days: int = 30) -> Dict:
    """
    Get call statistics for a restaurant.
    
    Args:
        restaurant_id: The restaurant ID
        days: The number of days to include in the statistics
        
    Returns:
        A dictionary of call statistics
    """
    # Get all calls for the restaurant
    calls = get_calls_by_restaurant(restaurant_id)
    
    # Filter by date range
    from datetime import timedelta
    start_date = get_current_time() - timedelta(days=days)
    filtered_calls = [call for call in calls if call.start_time >= start_date]
    
    # Calculate statistics
    total_calls = len(filtered_calls)
    ai_handled = len([call for call in filtered_calls if not call.forwarded])
    forwarded = len([call for call in filtered_calls if call.forwarded])
    
    # Calculate average duration
    durations = [call.duration for call in filtered_calls if call.duration is not None]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Count sentiment labels
    sentiment_breakdown = {
        "positive": len([call for call in filtered_calls if call.sentiment_label == "positive"]),
        "neutral": len([call for call in filtered_calls if call.sentiment_label == "neutral"]),
        "negative": len([call for call in filtered_calls if call.sentiment_label == "negative"])
    }
    
    # Count call reasons
    reasons = {}
    for call in filtered_calls:
        if call.reason:
            reasons[call.reason] = reasons.get(call.reason, 0) + 1
    
    # Group calls by day
    calls_by_day = {}
    for call in filtered_calls:
        day = call.start_time.strftime("%Y-%m-%d")
        calls_by_day[day] = calls_by_day.get(day, 0) + 1
    
    return {
        "totalCalls": total_calls,
        "aiHandled": ai_handled,
        "forwarded": forwarded,
        "avgDuration": avg_duration,
        "sentimentBreakdown": sentiment_breakdown,
        "callReasons": reasons,
        "callsByDay": {
            "labels": list(calls_by_day.keys()),
            "data": list(calls_by_day.values())
        }
    }
