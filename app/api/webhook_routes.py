"""
Webhook API routes for Pulsara IVR v2.
"""

import json
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.logging import get_logger
from app.core.restaurant import get_restaurant_by_id
from app.core.call import get_call_by_sid, update_call
from app.services.twilio import send_hangup_message, forward_call
from app.api.call_routes import active_connections, active_conversations
from app.db import get_db

logger = get_logger(__name__)

router = APIRouter()

@router.post("/tools/end_call")
async def end_call_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for the end_call tool.
    
    This is called by ElevenLabs when the agent wants to end the call.
    """
    logger.info("★★★ WEBHOOK CALLED: end_call ★★★")
    
    # Parse the request body
    data = await request.json()
    logger.info(f"Received webhook data: {json.dumps(data)}")
    
    # Find the most recent active call
    if active_connections:
        # Just get the most recent connection
        connection_id = list(active_connections.keys())[-1]
        conn_info = active_connections[connection_id]
        stream_sid = conn_info.get("stream_sid")
        
        # Get conversation from our separate dictionary
        conversation = active_conversations.get(connection_id)
        
        # Mark this connection as ended by agent request
        if connection_id in active_connections:
            active_connections[connection_id]["agent_requested_end"] = True
            logger.info(f"[CONN:{connection_id}] Marked connection for termination via webhook")
        
        # Try to end both the Twilio call and ElevenLabs conversation
        twilio_success = False
        elevenlabs_success = False
        
        # First, try to end the Twilio call
        if stream_sid:
            # Send hangup command to Twilio
            twilio_success = await send_hangup_message(stream_sid, connection_id)
            if twilio_success:
                logger.info(f"[WEBHOOK] Twilio call termination successful via webhook")
            else:
                logger.warning(f"[WEBHOOK] Failed to terminate Twilio call via webhook")
        else:
            logger.warning(f"[WEBHOOK] No stream_sid found for connection {connection_id}")
        
        # Next, try to end the ElevenLabs conversation
        if conversation:
            try:
                logger.info(f"[WEBHOOK] Ending ElevenLabs conversation via webhook")
                # End the conversation session from the webhook
                conversation.end_session()
                elevenlabs_success = True
                logger.info(f"[WEBHOOK] ElevenLabs conversation ended successfully via webhook")
            except Exception as e:
                logger.error(f"[WEBHOOK] Error ending ElevenLabs conversation: {str(e)}")
        else:
            logger.warning(f"[WEBHOOK] No conversation object found for connection {connection_id}")
        
        # Return success as long as either Twilio call or ElevenLabs conversation was ended
        if twilio_success or elevenlabs_success:
            logger.info(f"[WEBHOOK] Call termination partially or fully successful")
            return {"status": "success", "message": "Call ended successfully"}
        
        # Still return success to the agent even if both attempts failed
        # This ensures the agent doesn't get confused
        return {"status": "success", "message": "Call end request received. Call will be terminated."}
    
    # If we got here, we couldn't find a call to end
    logger.warning("[WEBHOOK] Failed to find an active call to terminate")
    return {"status": "error", "message": "No active call found to terminate"}

@router.get("/tools/get_address")
async def get_address_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for the get_address tool.
    
    This is called by ElevenLabs when the agent wants to retrieve the restaurant address.
    Uses GET method for simplicity since no input data is needed.
    """
    logger.info("★★★ WEBHOOK CALLED: get_address (GET) ★★★")
    
    # Find the most recent active call
    if active_connections:
        # Just get the most recent connection
        connection_id = list(active_connections.keys())[-1]
        conn_info = active_connections[connection_id]
        call_sid = conn_info.get("call_sid")
        
        # Get the call from our database
        call = get_call_by_sid(call_sid)
        if call:
            # Get the restaurant
            restaurant = get_restaurant_by_id(call.restaurant_id)
            if restaurant and restaurant.address:
                logger.info(f"[WEBHOOK] Returning address: {restaurant.address}")
                return {"status": "success", "message": restaurant.address}
            else:
                logger.warning(f"[WEBHOOK] Restaurant found but address is missing")
                return {"status": "error", "message": "This restaurant has not set up their address information"}
    
    # If we couldn't find the restaurant or there's no active call, return an error
    logger.warning(f"[WEBHOOK] Could not determine restaurant for address request")
    return {"status": "error", "message": "Could not determine restaurant address"}

@router.post("/tools/forward_call")
async def forward_call_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for the forward_call tool.
    
    This is called by ElevenLabs when the agent wants to forward the call to the restaurant owner.
    """
    logger.info("★★★ WEBHOOK CALLED: forward_call ★★★")
    
    # Parse the request body
    data = await request.json()
    logger.info(f"Received webhook data: {json.dumps(data)}")
    
    # Find the most recent active call
    if active_connections:
        # Just get the most recent connection
        connection_id = list(active_connections.keys())[-1]
        logger.info(f"[WEBHOOK] Found active connection: {connection_id}")
        
        conn_info = active_connections[connection_id]
        logger.info(f"[WEBHOOK] Connection info: {json.dumps(conn_info)}")
        
        call_sid = conn_info.get("call_sid")
        logger.info(f"[WEBHOOK] Call SID for forwarding: {call_sid}")
        
        # Get conversation from our separate dictionary
        conversation = active_conversations.get(connection_id)
        logger.info(f"[WEBHOOK] Conversation object found: {conversation is not None}")
        
        if call_sid:
            # Get the call from our database
            call = get_call_by_sid(call_sid)
            if call:
                # Get the restaurant
                restaurant = get_restaurant_by_id(call.restaurant_id)
                if restaurant:
                    # Forward the call using Twilio's API
                    try:
                        # Mark this connection as forwarded by agent request
                        if connection_id in active_connections:
                            active_connections[connection_id]["agent_requested_forward"] = True
                            logger.info(f"[CONN:{connection_id}] Marked connection for forwarding via webhook")
                        
                        # Update the call record
                        from app.utils.helpers import get_current_time
                        update_call(call.id, {
                            "forwarded": True,
                            "forwarded_to": restaurant.phone,
                            "forwarded_time": get_current_time()
                        })
                        
                        # Check if restaurant has a phone number to forward to
                        if not restaurant.phone:
                            logger.error(f"[WEBHOOK] Restaurant {restaurant.name} does not have a phone number configured")
                            return {"status": "error", "message": "Restaurant doesn't have a phone number configured"}
                        
                        # Forward the call
                        success = forward_call(call_sid, restaurant.phone)
                        
                        if success:
                            logger.info(f"[WEBHOOK] Call {call_sid} forwarded to {restaurant.phone}")
                            
                            # End the ElevenLabs conversation since we're forwarding the call
                            if conversation:
                                try:
                                    logger.info(f"[WEBHOOK] Ending ElevenLabs conversation after forwarding call")
                                    conversation.end_session()
                                    logger.info(f"[WEBHOOK] ElevenLabs conversation ended successfully")
                                except Exception as e:
                                    logger.error(f"[WEBHOOK] Error ending ElevenLabs conversation: {str(e)}")
                            
                            return {"status": "success", "message": f"Call forwarded to restaurant owner at {restaurant.phone}"}
                        else:
                            logger.error(f"[WEBHOOK] Error forwarding call")
                            return {"status": "error", "message": "Error forwarding call"}
                    except Exception as e:
                        logger.error(f"[WEBHOOK] Error forwarding call: {str(e)}")
                        return {"status": "error", "message": f"Error forwarding call: {str(e)}"}
                else:
                    logger.warning(f"[WEBHOOK] Restaurant not found for call: {call.id}")
                    return {"status": "error", "message": "Restaurant not found"}
            else:
                logger.warning(f"[WEBHOOK] Call not found for SID: {call_sid}")
                return {"status": "error", "message": "Call not found"}
        else:
            logger.warning("[WEBHOOK] No call SID found for forwarding")
            return {"status": "error", "message": "No call SID found for forwarding"}
    
    # If we got here, we couldn't find a call to forward
    logger.warning("[WEBHOOK] Failed to find an active call to forward")
    return {"status": "error", "message": "No active call found to forward"}

@router.post("/elevenlabs/conversation_initiation")
async def elevenlabs_conversation_initiation(request: Request, db: Session = Depends(get_db)):
    """
    Webhook called by ElevenLabs when a conversation is initiated.
    
    This endpoint provides dynamic variables to the ElevenLabs agent.
    """
    # Get the current time
    from app.utils.helpers import get_formatted_time
    formatted_time = get_formatted_time()
    
    # Simple response with a single time string
    response_data = {
        "type": "conversation_initiation_client_data",
        "custom_llm_extra_body": {},
        "conversation_config_override": {},
        "dynamic_variables": {
            "current_time": formatted_time
        }
    }
    
    logger.info(f"Conversation initiation webhook called with time: {formatted_time}")
    return response_data

@router.post("/elevenlabs/{restaurant_id}/conversation_initiation")
async def restaurant_conversation_initiation(restaurant_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Restaurant-specific webhook called by ElevenLabs when a conversation is initiated.
    
    This endpoint provides restaurant-specific dynamic variables to the ElevenLabs agent.
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {restaurant_id}")
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Get the current time
    from app.utils.helpers import get_formatted_time
    formatted_time = get_formatted_time()
    
    # Get restaurant settings
    from app.core.settings import get_settings
    settings = get_settings(restaurant_id)
    
    # Create dynamic variables
    dynamic_variables = {
        "current_time": formatted_time,
        "restaurant_name": restaurant.name,
        "restaurant_address": restaurant.address
    }
    
    # Add operating hours if available
    if settings:
        dynamic_variables["operating_hours"] = f"{settings.call_hours_start} - {settings.call_hours_end}"
    
    # Response with restaurant-specific variables
    response_data = {
        "type": "conversation_initiation_client_data",
        "custom_llm_extra_body": {},
        "conversation_config_override": {},
        "dynamic_variables": dynamic_variables
    }
    
    logger.info(f"Restaurant-specific conversation initiation webhook called for {restaurant.name}")
    return response_data
