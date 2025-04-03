"""
Call management module for Pulsara IVR v2.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app.models.schemas import Call as CallSchema
from app.models.database_models import Call as CallModel
from app.models.database_models import Restaurant as RestaurantModel
from app.db import get_db, SessionLocal
from sqlalchemy import func, and_, desc
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id
from app.utils.helpers import get_current_time
import uuid

logger = get_logger(__name__)

# Active call tracking - this is kept in memory as it relates to the current server state
# We track call_sid to call_id mapping for active calls
_active_calls = {}

def get_call_by_id(call_id: str) -> Optional[CallSchema]:
    """
    Get a call by ID from the database.
    
    Args:
        call_id: The call ID
        
    Returns:
        The call or None if not found
    """
    if not call_id:
        logger.warning("Tried to get call with empty ID")
        return None
        
    try:
        db = SessionLocal()
        call_db = db.query(CallModel).filter(CallModel.id == call_id).first()
        db.close()
        
        if not call_db:
            logger.warning(f"Call not found with ID: {call_id}")
            return None
            
        # Convert database model to schema model
        call = CallSchema(
            id=call_db.id,
            restaurant_id=call_db.restaurantId,
            call_sid=call_db.call_sid or "",  # Use dedicated call_sid field
            stream_sid=call_db.conversationId,  # Stream SID can use conversationId temporarily
            caller_number=call_db.callerNumber or "",
            start_time=call_db.date,  # Using date field as start_time
            end_time=None,  # Not directly mapped from the schema
            duration=int(call_db.duration) if call_db.duration and call_db.duration.isdigit() else 0,
            handled_by="ai" if call_db.type == "AI_HANDLED" else "forwarded",
            forwarded=call_db.type == "FORWARDED",
            transcript=call_db.transcript or "",
            sentiment_label=call_db.sentiment.lower() if call_db.sentiment else None,
            audio_url=call_db.audioUrl
            # Additional fields could be added as needed
        )
        
        return call
    except Exception as e:
        logger.error(f"Error fetching call by ID {call_id}: {e}")
        if 'db' in locals():
            db.close()
        return None

def get_call_by_sid(call_sid: str) -> Optional[CallSchema]:
    """
    Get a call by Twilio Call SID from the database.
    
    Args:
        call_sid: The Twilio Call SID
        
    Returns:
        The call or None if not found
    """
    if not call_sid:
        logger.warning("Tried to get call with empty SID")
        return None
        
    try:
        db = SessionLocal()
        # Use the dedicated call_sid field
        call_db = db.query(CallModel).filter(CallModel.call_sid == call_sid).first()
        db.close()
        
        if not call_db:
            logger.warning(f"Call not found with SID: {call_sid}")
            return None
            
        # Convert database model to schema model (same conversion as in get_call_by_id)
        call = CallSchema(
            id=call_db.id,
            restaurant_id=call_db.restaurantId,
            call_sid=call_db.call_sid or "",
            stream_sid=call_db.conversationId,
            caller_number=call_db.callerNumber or "",
            start_time=call_db.date,
            end_time=None,
            duration=int(call_db.duration) if call_db.duration and call_db.duration.isdigit() else 0,
            handled_by="ai" if call_db.type == "AI_HANDLED" else "forwarded",
            forwarded=call_db.type == "FORWARDED",
            transcript=call_db.transcript or "",
            sentiment_label=call_db.sentiment.lower() if call_db.sentiment else None,
            audio_url=call_db.audioUrl
        )
        
        return call
    except Exception as e:
        logger.error(f"Error fetching call by SID {call_sid}: {e}")
        if 'db' in locals():
            db.close()
        return None

def get_calls_by_restaurant(restaurant_id: str) -> List[CallSchema]:
    """
    Get all calls for a restaurant from the database.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        A list of calls for the restaurant
    """
    if not restaurant_id:
        logger.warning("Tried to get calls with empty restaurant ID")
        return []
        
    try:
        db = SessionLocal()
        calls_db = db.query(CallModel).filter(CallModel.restaurantId == restaurant_id).order_by(desc(CallModel.date)).all()
        db.close()
        
        # Convert database models to schema models
        calls = []
        for call_db in calls_db:
            call = CallSchema(
                id=call_db.id,
                restaurant_id=call_db.restaurantId,
                call_sid=call_db.conversationId or "",
                stream_sid=call_db.conversationId,
                caller_number=call_db.callerNumber or "",
                start_time=call_db.date,
                end_time=None,
                duration=int(call_db.duration) if call_db.duration and call_db.duration.isdigit() else 0,
                handled_by="ai" if call_db.type == "AI_HANDLED" else "forwarded",
                forwarded=call_db.type == "FORWARDED",
                transcript=call_db.transcript or "",
                sentiment_label=call_db.sentiment.lower() if call_db.sentiment else None,
                audio_url=call_db.audioUrl
            )
            calls.append(call)
            
        return calls
    except Exception as e:
        logger.error(f"Error fetching calls for restaurant ID {restaurant_id}: {e}")
        if 'db' in locals():
            db.close()
        return []

def create_call(restaurant_id: str, call_sid: str, caller_number: str) -> CallSchema:
    """
    Create a new call record in the database.
    
    Args:
        restaurant_id: The restaurant ID
        call_sid: The Twilio Call SID
        caller_number: The caller's phone number
        
    Returns:
        The created call record
    """
    if not restaurant_id:
        logger.warning("Tried to create call with empty restaurant ID")
        raise ValueError("Restaurant ID is required to create a call")
        
    # Get the restaurant to ensure it exists
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {restaurant_id}")
        raise ValueError(f"Restaurant not found for ID: {restaurant_id}")
    
    try:
        # Create a unique ID for the call
        call_id = str(uuid.uuid4())
        
        # Create a new CallSchema for tracking during the active call
        call = CallSchema(
            id=call_id,
            restaurant_id=restaurant_id,
            call_sid=call_sid,
            caller_number=caller_number,
            start_time=get_current_time(),
            handled_by="ai",  # Default until forwarded
            forwarded=False
        )
        
        # Store the mapping for active call tracking
        _active_calls[call_sid] = call_id
        
        # Create a minimal call record in the database
        # The full record will be updated when the call ends
        db = SessionLocal()
        call_db = CallModel(
            id=call_id,
            restaurantId=restaurant_id,
            call_sid=call_sid,  # Use dedicated call_sid field
            conversationId=None,  # ElevenLabs conversation ID will be set later if needed
            callerNumber=caller_number,
            date=get_current_time(),
            duration="0",  # Will be updated later
            type="AI_HANDLED",  # Default type
            sentiment="NEUTRAL",  # Default sentiment
            transcript="",  # Will be updated later
            keyPoints=[],
            actions=[]
        )
        db.add(call_db)
        db.commit()
        db.close()
        
        logger.info(f"Created call record in database: {call_id} for restaurant: {restaurant.name}")
        return call
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise

def update_call(call_id: str, call_data: Dict) -> Optional[CallSchema]:
    """
    Update an existing call record in the database.
    
    Args:
        call_id: The ID of the call to update
        call_data: The updated call data
        
    Returns:
        The updated call record or None if not found
    """
    if not call_id:
        logger.warning("Tried to update call with empty ID")
        return None
        
    try:
        # Get the existing call first to ensure it exists
        existing_call = get_call_by_id(call_id)
        if not existing_call:
            logger.warning(f"Call not found with ID: {call_id}")
            return None
            
        # Update the CallSchema for return value
        updated_call_dict = existing_call.dict()
        updated_call_dict.update(call_data)
        updated_call = CallSchema(**updated_call_dict)
        
        # Update the database record
        db = SessionLocal()
        call_db = db.query(CallModel).filter(CallModel.id == call_id).first()
        
        if not call_db:
            logger.warning(f"Call not found in database with ID: {call_id}")
            db.close()
            return None
            
        # Map CallSchema fields to CallModel fields
        if 'duration' in call_data:
            call_db.duration = str(call_data['duration'])
            
        if 'transcript' in call_data:
            call_db.transcript = call_data['transcript']
            
        if 'audio_url' in call_data:
            call_db.audioUrl = call_data['audio_url']
            
        if 'sentiment_label' in call_data:
            # Convert to enum format (uppercase)
            sentiment = call_data['sentiment_label'].upper()
            if sentiment in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
                call_db.sentiment = sentiment
                
        if 'forwarded' in call_data:
            # Update the type field based on forwarded status
            call_db.type = "FORWARDED" if call_data['forwarded'] else "AI_HANDLED"
            
        if 'key_points' in call_data and isinstance(call_data['key_points'], list):
            call_db.keyPoints = call_data['key_points']
            
        if 'actions' in call_data and isinstance(call_data['actions'], list):
            call_db.actions = call_data['actions']
        
        # Commit changes to the database
        db.commit()
        db.close()
        
        logger.info(f"Updated call record: {call_id}")
        return updated_call
    except Exception as e:
        logger.error(f"Error updating call ID {call_id}: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return None

def end_call(call_id: str, forwarded: bool = False, forwarded_to: str = None) -> Optional[CallSchema]:
    """
    End a call and update its record in the database.
    
    Args:
        call_id: The ID of the call to end
        forwarded: Whether the call was forwarded
        forwarded_to: Who the call was forwarded to
        
    Returns:
        The updated call record or None if not found
    """
    if not call_id:
        logger.warning("Tried to end call with empty ID")
        return None
        
    try:
        # Get the existing call first to ensure it exists
        call = get_call_by_id(call_id)
        if not call:
            logger.warning(f"Call not found with ID: {call_id}")
            return None
            
        # Calculate call duration and prepare update data
        now = get_current_time()
        call_data = {
            'end_time': now,
            'duration': int((now - call.start_time).total_seconds()),
            'forwarded': forwarded
        }
        
        if forwarded and forwarded_to:
            call_data['forwarded_to'] = forwarded_to
            
        # Update the call record in the database
        updated_call = update_call(call_id, call_data)
        
        # Remove from active calls
        if call.call_sid in _active_calls:
            del _active_calls[call.call_sid]
            logger.info(f"Removed call with SID {call.call_sid} from active calls")
        
        # Trigger email notification
        try:
            from app.services.email import send_call_summary_email
            send_call_summary_email(updated_call)
        except Exception as email_error:
            logger.error(f"Error sending call summary email: {email_error}")
        
        return updated_call
    except Exception as e:
        logger.error(f"Error ending call ID {call_id}: {e}")
        return None

def get_active_call_by_sid(call_sid: str) -> Optional[CallSchema]:
    """
    Get an active call by Twilio Call SID.
    
    Args:
        call_sid: The Twilio Call SID
        
    Returns:
        The active call or None if not found
    """
    if not call_sid:
        logger.warning("Tried to get active call with empty SID")
        return None
        
    # Check if the call is in our active calls dictionary
    call_id = _active_calls.get(call_sid)
    if call_id:
        # Return the call record from the database
        return get_call_by_id(call_id)
    
    # If not in active calls, try to find it in the database directly
    # (This is a fallback - generally active calls should be in the dictionary)
    return get_call_by_sid(call_sid)

def get_call_statistics(restaurant_id: str, days: int = 30) -> Dict:
    """
    Get call statistics for a restaurant from the database.
    
    Args:
        restaurant_id: The restaurant ID
        days: The number of days to include in the statistics
        
    Returns:
        A dictionary of call statistics
    """
    if not restaurant_id:
        logger.warning("Tried to get call statistics with empty restaurant ID")
        return {
            "totalCalls": 0,
            "aiHandled": 0,
            "forwarded": 0,
            "avgDuration": 0,
            "sentimentBreakdown": {"positive": 0, "neutral": 0, "negative": 0},
            "callReasons": {},
            "callsByDay": {"labels": [], "data": []}
        }
        
    try:
        # Calculate the start date for filtering
        start_date = get_current_time() - timedelta(days=days)
        
        db = SessionLocal()
        
        # Get total call count
        total_calls = db.query(func.count(CallModel.id)).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date
        ).scalar() or 0
        
        # Get AI handled call count
        ai_handled = db.query(func.count(CallModel.id)).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date,
            CallModel.type == "AI_HANDLED"
        ).scalar() or 0
        
        # Get forwarded call count
        forwarded = db.query(func.count(CallModel.id)).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date,
            CallModel.type == "FORWARDED"
        ).scalar() or 0
        
        # Get average duration 
        # Note: duration is stored as a string in the database, so we need to convert
        durations = db.query(CallModel.duration).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date
        ).all()
        durations = [int(d[0]) for d in durations if d[0] and d[0].isdigit()]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Get sentiment breakdown
        positive = db.query(func.count(CallModel.id)).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date,
            CallModel.sentiment == "POSITIVE"
        ).scalar() or 0
        
        neutral = db.query(func.count(CallModel.id)).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date,
            CallModel.sentiment == "NEUTRAL"
        ).scalar() or 0
        
        negative = db.query(func.count(CallModel.id)).filter(
            CallModel.restaurantId == restaurant_id,
            CallModel.date >= start_date,
            CallModel.sentiment == "NEGATIVE"
        ).scalar() or 0
        
        # Get calls by day
        # This is more complex with SQLAlchemy and depends on the database type
        # Here's a simplified approach that might need adjustment based on the actual DB
        # For PostgreSQL:
        try:
            calls_by_day_query = db.query(
                func.date_trunc('day', CallModel.date).label('day'),
                func.count(CallModel.id).label('count')
            ).filter(
                CallModel.restaurantId == restaurant_id,
                CallModel.date >= start_date
            ).group_by('day').order_by('day').all()
            
            labels = [day.strftime("%Y-%m-%d") for day, _ in calls_by_day_query]
            data = [count for _, count in calls_by_day_query]
        except Exception as e:
            logger.warning(f"Error getting calls by day: {e}")
            # Fallback to empty data
            labels = []
            data = []
        
        db.close()
        
        # Build the result dictionary
        result = {
            "totalCalls": total_calls,
            "aiHandled": ai_handled,
            "forwarded": forwarded,
            "avgDuration": avg_duration,
            "sentimentBreakdown": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "callReasons": {},  # Placeholder - would need additional logic/fields to populate
            "callsByDay": {
                "labels": labels,
                "data": data
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"Error getting call statistics for restaurant ID {restaurant_id}: {e}")
        if 'db' in locals():
            db.close()
        return {
            "totalCalls": 0,
            "aiHandled": 0,
            "forwarded": 0,
            "avgDuration": 0,
            "sentimentBreakdown": {"positive": 0, "neutral": 0, "negative": 0},
            "callReasons": {},
            "callsByDay": {"labels": [], "data": []}
        }
