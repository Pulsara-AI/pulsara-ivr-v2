"""
Twilio integration service for Pulsara IVR v2.
"""

from typing import Dict, Any, Optional
from app.utils.logging import get_logger
from config.environment import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Dial

logger = get_logger(__name__)

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Call mapping for active calls
call_mapping = {}

def generate_twiml_for_incoming_call(host: str) -> str:
    """
    Generate TwiML for an incoming call.
    
    Args:
        host: The host name for the WebSocket URL
        
    Returns:
        TwiML as a string
    """
    response = VoiceResponse()
    connect = Connect()
    
    # Create the Stream element
    stream_url = f"wss://{host}/media-stream"
    stream = connect.stream(url=stream_url)
    
    response.append(connect)
    
    return str(response)

def generate_twiml_for_forwarding(forward_number: str) -> str:
    """
    Generate TwiML for forwarding a call.
    
    Args:
        forward_number: The phone number to forward to
        
    Returns:
        TwiML as a string
    """
    response = VoiceResponse()
    response.say("Connecting you to the restaurant owner now. Please hold.")
    response.dial(forward_number)
    
    return str(response)

def forward_call(call_sid: str, forward_number: str) -> bool:
    """
    Forward an active call to another number.
    
    Args:
        call_sid: The Twilio Call SID
        forward_number: The phone number to forward to
        
    Returns:
        True if the call was forwarded successfully, False otherwise
    """
    try:
        # Generate TwiML for forwarding
        twiml = generate_twiml_for_forwarding(forward_number)
        
        # Update the in-progress call with the new TwiML
        twilio_client.calls(call_sid).update(twiml=twiml)
        
        logger.info(f"Call {call_sid} forwarded to {forward_number}")
        return True
    except Exception as e:
        logger.error(f"Error forwarding call: {str(e)}")
        return False

def end_call(call_sid: str) -> bool:
    """
    End an active call.
    
    Args:
        call_sid: The Twilio Call SID
        
    Returns:
        True if the call was ended successfully, False otherwise
    """
    try:
        # Use Twilio REST API to end the call
        call = twilio_client.calls(call_sid).update(status="completed")
        
        logger.info(f"Call {call_sid} ended with status: {call.status}")
        
        # Remove from call mapping
        if call_sid in call_mapping:
            del call_mapping[call_sid]
        
        return True
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")
        return False

def set_call_context(stream_sid: str, call_sid: str, connection_id: str = "unknown") -> None:
    """
    Store mapping from Stream SID to Call SID.
    
    Args:
        stream_sid: The Twilio Media Stream SID
        call_sid: The Twilio Call SID
        connection_id: The connection ID for logging
    """
    if not stream_sid:
        logger.warning(f"[CONN:{connection_id}] No Stream SID provided")
        return
        
    if not call_sid or call_sid == "Unknown":
        logger.warning(f"[CONN:{connection_id}] Invalid Call SID provided: {call_sid}")
        return
    
    # Store the mapping
    call_mapping[stream_sid] = call_sid
    
    logger.info(f"[CONN:{connection_id}] Added mapping: StreamSID={stream_sid} → CallSID={call_sid}")

async def send_hangup_message(stream_sid: str = None, connection_id: str = "unknown") -> bool:
    """
    End a Twilio call using the REST API.
    
    Args:
        stream_sid: The Stream SID of the call to end
        connection_id: The connection ID for logging
    
    Returns:
        True if the call was terminated successfully, False otherwise
    """
    try:
        call_sid = None
        logger.info(f"[CONN:{connection_id}] Hangup request received for StreamSID={stream_sid}")
        
        # If no specific Stream SID provided, use the last one (most recent call)
        if stream_sid is None and call_mapping:
            stream_sid = list(call_mapping.keys())[-1]
            logger.info(f"[CONN:{connection_id}] No StreamSID provided, using most recent: {stream_sid}")
        
        # Look up the Call SID in our mapping
        if stream_sid and stream_sid in call_mapping:
            call_sid = call_mapping[stream_sid]
            logger.info(f"[CONN:{connection_id}] Found matching CallSID: {call_sid}")
        else:
            logger.warning(f"[CONN:{connection_id}] Cannot find any Call SID to terminate")
            return False
        
        # End the call
        return end_call(call_sid)
        
    except Exception as e:
        logger.error(f"[CONN:{connection_id}] Error ending Twilio call: {str(e)}")
        return False

def get_call_details(call_sid: str) -> Optional[Dict[str, Any]]:
    """
    Get details for a call.
    
    Args:
        call_sid: The Twilio Call SID
        
    Returns:
        A dictionary of call details or None if the call was not found
    """
    try:
        call = twilio_client.calls(call_sid).fetch()
        
        return {
            "call_sid": call.sid,
            "from_number": call.from_,
            "to_number": call.to,
            "status": call.status,
            "direction": call.direction,
            "duration": call.duration,
            "start_time": call.start_time,
            "end_time": call.end_time,
            "price": call.price,
            "price_unit": call.price_unit
        }
    except Exception as e:
        logger.error(f"Error getting call details: {str(e)}")
        return None

def get_recent_calls(limit: int = 10) -> list:
    """
    Get recent calls.
    
    Args:
        limit: The maximum number of calls to return
        
    Returns:
        A list of recent calls
    """
    try:
        calls = twilio_client.calls.list(limit=limit)
        
        return [
            {
                "call_sid": call.sid,
                "from_number": call.from_,
                "to_number": call.to,
                "status": call.status,
                "direction": call.direction,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time
            }
            for call in calls
        ]
    except Exception as e:
        logger.error(f"Error getting recent calls: {str(e)}")
        return []
