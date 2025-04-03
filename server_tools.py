"""
Server Tools for ElevenLabs ConversationalAI integration.

This module provides server-side tools that can be used by the ElevenLabs agent
to perform actions controlled by our server, such as ending a call or providing restaurant information.

These tools are registered with the ElevenLabs agent and can be invoked by the agent
during a conversation when appropriate.
"""

import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv
from twilio.rest import Client
from sqlalchemy.orm import Session

# For database access
from app.db import SessionLocal
from app.models.database_models import Restaurant as RestaurantModel
from app.core.restaurant import get_restaurant_by_id

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Twilio client
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Track active connections and call details
# This works with concurrent calls because each has a unique Stream SID
call_mapping = {}

# Counter for call statistics
call_stats = {
    "total_calls": 0,
    "successful_terminations": 0,
    "failed_terminations": 0
}

# Backup storage for latest Call SID (used when Stream SID mapping fails)
latest_call_sid = None

def store_call_sid_for_later(call_sid):
    """
    Store the Call SID as a backup in case the parameter method fails
    
    Args:
        call_sid: The Twilio Call SID to store
    """
    global latest_call_sid
    latest_call_sid = call_sid

def set_call_context(stream_sid, call_sid, connection_id="unknown"):
    """
    Store mapping from Stream SID to Call SID
    
    Args:
        stream_sid: The Twilio Media Stream SID (unique per call)
        call_sid: The Twilio Call SID
        connection_id: Optional connection ID for logging
    """
    global latest_call_sid, call_stats
    
    if not stream_sid:
        logger.warning(f"[CONN:{connection_id}] No Stream SID provided")
        return
        
    if not call_sid or call_sid == "Unknown":
        # Try to use the backup Call SID if available
        if latest_call_sid:
            call_sid = latest_call_sid
            logger.info(f"[CONN:{connection_id}] Using backup Call SID: {call_sid}")
        else:
            logger.warning(f"[CONN:{connection_id}] Invalid Call SID provided: {call_sid}")
            return
    
    # Store the mapping
    call_mapping[stream_sid] = call_sid
    call_stats["total_calls"] += 1
    
    # Log the mapping creation but not the full state (reduces noise)
    logger.info(f"[CONN:{connection_id}] Added mapping: StreamSID={stream_sid} → CallSID={call_sid}")

async def send_hangup_message(stream_sid=None, connection_id="unknown"):
    """
    End a Twilio call using the REST API
    
    Args:
        stream_sid: The Stream SID of the call to end. If None, uses the last active call.
        connection_id: Optional connection ID for logging
    
    Returns:
        bool: True if the call was terminated successfully, False otherwise
    """
    global latest_call_sid, call_stats
    
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
        # Try using the backup Call SID if we couldn't find one in the mapping
        elif latest_call_sid:
            call_sid = latest_call_sid
            logger.info(f"[CONN:{connection_id}] Using backup CallSID: {call_sid}")
        else:
            logger.warning(f"[CONN:{connection_id}] Cannot find any Call SID to terminate")
            call_stats["failed_terminations"] += 1
            return False
        
        # Use Twilio REST API to end the call
        logger.info(f"[CONN:{connection_id}] Ending call with CallSID={call_sid}")
        call = twilio_client.calls(call_sid).update(status="completed")
        logger.info(f"[CONN:{connection_id}] Twilio API response status: {call.status}")
        
        # Remove from active calls if we have a valid stream_sid
        if stream_sid and stream_sid in call_mapping:
            del call_mapping[stream_sid]
            logger.info(f"[CONN:{connection_id}] Removed mapping for StreamSID={stream_sid}")
        
        # Clear the backup call SID since we've used it
        latest_call_sid = None
        
        # Update stats
        call_stats["successful_terminations"] += 1
        logger.info(f"[CONN:{connection_id}] Call stats: {call_stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"[CONN:{connection_id}] Error ending Twilio call: {str(e)}")
        call_stats["failed_terminations"] += 1
        return False

# Server-side tool implementations
async def end_call(custom_state: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    End the current Twilio call.
    
    This is a server-side tool that allows the agent to end the call.
    When invoked by the LLM, this function will terminate the Twilio call.
    
    Args:
        custom_state: The custom state passed to the conversation (contains connection_info)
        params: Any additional parameters from ElevenLabs
        
    Returns:
        A response indicating success or failure
    """
    try:
        # Get connection information from custom state
        connection_info = custom_state.get("connection_info", {}) if custom_state else {}
        connection_id = connection_info.get("connection_id", "unknown")
        stream_sid = connection_info.get("stream_sid")
        
        # Make this very visible in the logs when agent explicitly uses the tool
        logger.info(f"[CONN:{connection_id}] ★★★ AGENT EXPLICITLY USED end_call SERVER TOOL ★★★")
        logger.info(f"[CONN:{connection_id}] Agent recognized end call request and is terminating the call")
        
        # Send the hangup message
        success = await send_hangup_message(stream_sid, connection_id)
        
        if success:
            logger.info(f"[CONN:{connection_id}] Agent-initiated call termination successful")
            return {"status": "success", "message": "Call ended successfully by agent"}
        else:
            logger.warning(f"[CONN:{connection_id}] Agent-initiated call termination FAILED")
            return {"status": "error", "message": "Failed to end call"}
            
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

async def get_address(custom_state: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get the restaurant address from the database.
    
    This server-side tool returns the restaurant's address when invoked by the agent.
    It uses the restaurant_id from the custom_state to fetch the address from the database.
    
    Args:
        custom_state: The custom state passed to the conversation (contains connection_info)
        params: Any additional parameters from ElevenLabs
        
    Returns:
        The restaurant address
    """
    try:
        # Get connection information from custom state
        connection_info = custom_state.get("connection_info", {}) if custom_state else {}
        connection_id = connection_info.get("connection_id", "unknown")
        restaurant_id = connection_info.get("restaurant_id")
        
        # Make this very visible in the logs when agent explicitly uses the tool
        logger.info(f"[CONN:{connection_id}] ★★★ AGENT USED get_address SERVER TOOL ★★★")
        logger.info(f"[CONN:{connection_id}] Tool calling is working! Agent successfully used a tool.")
        
        # Validate restaurant_id
        if not restaurant_id:
            logger.warning(f"[CONN:{connection_id}] No restaurant_id in connection_info")
            return {
                "status": "error",
                "message": "Restaurant information not available"
            }
        
        # Fetch restaurant address from database
        db = SessionLocal()
        try:
            restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
            if restaurant and restaurant.address:
                address = restaurant.address
                logger.info(f"[CONN:{connection_id}] Found address in database: {address}")
            else:
                logger.warning(f"[CONN:{connection_id}] Restaurant or address not found in database for ID: {restaurant_id}")
                return {
                    "status": "error",
                    "message": "This restaurant has not set up their address information"
                }
        finally:
            db.close()
        
        logger.info(f"[CONN:{connection_id}] Returning address: {address}")
        
        return {
            "status": "success",
            "message": address
        }
    except Exception as e:
        logger.error(f"Error getting address: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

# Dictionary of available tools to be used with ElevenLabs
server_tools = {
    "end_call": end_call,
    "get_address": get_address
}

def get_server_tools() -> Dict[str, Any]:
    """Returns all available server tools"""
    return server_tools
