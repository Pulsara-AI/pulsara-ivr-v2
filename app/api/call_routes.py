"""
Call handling API routes for Pulsara IVR v2.
"""

import json
import uuid
import traceback
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, WebSocket, Depends, HTTPException
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect
# Remove SDK imports

from app.utils.logging import get_logger
from app.utils.helpers import generate_connection_id, get_current_time
from app.services.audio_interface import TwilioAudioInterface
from app.services.twilio import set_call_context, send_hangup_message
from app.services.elevenlabs import get_system_prompt_template, get_first_message_template, create_conversation
from app.core.restaurant import get_restaurant_by_id, get_restaurant_by_phone
from app.core.agent import get_agent_by_restaurant
from app.core.call import create_call, update_call, end_call, get_active_call_by_sid
from app.core.settings import get_settings
from config.environment import ELEVENLABS_API_KEY

logger = get_logger(__name__)

router = APIRouter()

# Dictionary to track active websocket connections
active_connections = {}

# Dictionary to store conversation objects separately (not JSON serializable)
active_conversations = {}

@router.post("/inbound_call")
async def handle_incoming_call(request: Request):
    """
    Handle an incoming call from Twilio.
    
    This endpoint is called by Twilio when a new call is received.
    It returns TwiML to instruct Twilio to connect to our WebSocket endpoint.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "Unknown")
    from_number = form_data.get("From", "Unknown")
    to_number = form_data.get("To", "Unknown")
    
    logger.info(f"Incoming call: CallSid={call_sid}, From={from_number}, To={to_number}")
    
    # Identify the restaurant based on the called number
    restaurant = get_restaurant_by_phone(to_number)
    if not restaurant:
        # Use default restaurant if no match found
        from app.core.restaurant import default_restaurant
        restaurant = default_restaurant
        logger.warning(f"No restaurant found for phone number {to_number}, using default")
    
    # Check if the restaurant is within operating hours
    settings = get_settings(restaurant.id)
    if settings:
        from datetime import datetime
        import pytz
        from app.utils.helpers import get_current_time
        
        # Get current time in restaurant's timezone
        tz = pytz.timezone(restaurant.timezone)
        now = get_current_time().astimezone(tz)
        
        # Parse operating hours
        from datetime import time
        start_hour, start_minute = map(int, settings.call_hours_start.split(':'))
        end_hour, end_minute = map(int, settings.call_hours_end.split(':'))
        
        start_time = time(start_hour, start_minute)
        end_time = time(end_hour, end_minute)
        current_time = now.time()
        
        # Check if current time is outside operating hours
        if current_time < start_time or current_time > end_time:
            # Return TwiML to play a message and hang up
            response = VoiceResponse()
            response.say(f"Thank you for calling {restaurant.name}. We are currently closed. Our hours are from {settings.call_hours_start} to {settings.call_hours_end}. Please call back during our operating hours.")
            response.hangup()
            return HTMLResponse(content=str(response), media_type="application/xml")
    
    # Create a call record
    call = create_call(
        restaurant_id=restaurant.id,
        call_sid=call_sid,
        caller_number=from_number
    )
    
    # Generate TwiML to connect to our WebSocket endpoint
    response = VoiceResponse()
    connect = Connect()
    
    # Create the Stream element with a Parameter for Call SID
    stream_url = f"wss://{request.url.hostname}/media-stream"
    stream = connect.stream(url=stream_url)
    
    # Add the CallSid as a parameter (this will be included in the start event)
    stream.parameter(name="callSid", value=call_sid)
    
    response.append(connect)
    
    return HTMLResponse(content=str(response), media_type="application/xml")

@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """
    Handle the WebSocket connection for a Twilio Media Stream.
    
    This endpoint is connected to by Twilio when a call is established.
    It handles the audio streaming between Twilio and ElevenLabs.
    """
    # Generate a unique connection ID
    connection_id = generate_connection_id()
    
    # Extract Call SID from query parameters
    call_sid = websocket.query_params.get("call_sid", "Unknown")
    
    # Track client info for debugging
    client_host = websocket.client.host if hasattr(websocket, 'client') and hasattr(websocket.client, 'host') else "Unknown"
    
    try:
        await websocket.accept()
        logger.info(f"[CONN:{connection_id}] WebSocket connection opened from {client_host}")
        
        # Register this connection
        active_connections[connection_id] = {
            "call_sid": call_sid,
            "stream_sid": None,
            "status": "connected",
            "timestamp": get_current_time().isoformat(),
            "client_host": client_host,
            "agent_requested_end": False,  # Track if agent used end_call
            "agent_requested_forward": False  # Track if agent used forward_call
        }
        logger.info(f"[CONN:{connection_id}] Active connections: {len(active_connections)}")
        
        # Initialize the audio interface
        audio_interface = TwilioAudioInterface(websocket, connection_id)
        
        # Set up a listener to update active_connections when stream_sid is received
        def on_stream_sid_received(stream_sid, call_sid):
            logger.info(f"[CONN:{connection_id}] Received stream_sid: {stream_sid}")
            if connection_id in active_connections:
                active_connections[connection_id]["stream_sid"] = stream_sid
                active_connections[connection_id]["call_sid"] = call_sid
                logger.info(f"[CONN:{connection_id}] Updated connection tracking with stream_sid")
        
        # Attach the listener to the audio interface
        audio_interface.on_stream_sid_received = on_stream_sid_received
        
        # Also register the stream_sid with server_tools for call termination
        def on_stream_sid_for_tools(stream_sid, call_sid):
            # Update our connection info with the stream_sid
            connection_info["stream_sid"] = stream_sid
            # Register the mapping in twilio service
            set_call_context(stream_sid, call_sid, connection_id)
        
        # Add a second listener that will update twilio service
        audio_interface.add_stream_sid_listener(on_stream_sid_for_tools)
        
        # No need to initialize ElevenLabs client - our service handles this
    except Exception as e:
        logger.error(f"[CONN:{connection_id}] Error during WebSocket accept: {e}")
        # Don't re-raise, so we can handle in the main try-except block
    
    try:
        # Get the active call
        active_call = get_active_call_by_sid(call_sid)
        if not active_call:
            logger.error(f"[CONN:{connection_id}] No active call found for call_sid: {call_sid}")
            return
        
        # Get the restaurant
        restaurant = get_restaurant_by_id(active_call.restaurant_id)
        if not restaurant:
            logger.error(f"[CONN:{connection_id}] No restaurant found for call: {active_call.id}")
            return
        
        # Get the agent
        agent = get_agent_by_restaurant(restaurant.id)
        if not agent:
            logger.error(f"[CONN:{connection_id}] No agent found for restaurant: {restaurant.id}")
            return
        
        # Initialize conversation connection information
        # This will be passed to server tools when they're invoked
        connection_info = {
            "connection_id": connection_id,
            "stream_sid": None,  # Will be updated when received 
            "call_sid": call_sid,
            "restaurant_id": restaurant.id
        }
        
        # Prepare the conversation configuration
        config = {
            "conversation_config_override": {
                "agent": {
                    "prompt": {
                        "prompt": json.dumps(agent.system_prompt),
                        "tools": agent.tools
                    },
                    "first_message": get_first_message_template().format(
                        time_of_day="morning" if 5 <= get_current_time().hour < 12 else "afternoon" if 12 <= get_current_time().hour < 18 else "evening",
                        restaurant_name=restaurant.name
                    ),
                    "language": "en"
                },
                "tts": {
                    "voice_id": agent.voice_id
                }
            }
        }
        
        # Create the conversation using our service
        conversation = create_conversation(
            agent_id=agent.elevenlabs_agent_id,
            audio_interface=audio_interface,
            on_agent_response=lambda text: print(f"TRANSCRIPT - Agent: {text}"),
            on_user_transcript=lambda text: print(f"TRANSCRIPT - User: {text}"),
            config=config
        )
        
        # Update stream_sid in connection_info when it becomes available
        def update_stream_sid_in_context(stream_sid, call_sid):
            logger.info(f"[CONN:{connection_id}] Updating connection_info with stream_sid")
            connection_info["stream_sid"] = stream_sid
            
        # Setup listener to keep connection_info up to date for our API endpoints
        audio_interface.add_stream_sid_listener(update_stream_sid_in_context)
        
        # Function to detect when the agent uses any tool
        def on_agent_tool_use(tool_name, tool_params):
            logger.info(f"[CONN:{connection_id}] ★★★ AGENT USED TOOL: {tool_name} ★★★")
            logger.info(f"[CONN:{connection_id}] Tool parameters: {json.dumps(tool_params) if tool_params else 'None'}")
            
            if tool_name == "end_call":
                logger.info(f"[CONN:{connection_id}] ★★★ AGENT USED END_CALL TOOL ★★★")
                # Mark this connection for termination
                if connection_id in active_connections:
                    active_connections[connection_id]["agent_requested_end"] = True
                    logger.info(f"[CONN:{connection_id}] Marked connection for termination")
            
            elif tool_name == "forward_call":
                logger.info(f"[CONN:{connection_id}] ★★★ AGENT USED FORWARD_CALL TOOL ★★★")
                # Mark that the agent requested call forwarding
                if connection_id in active_connections:
                    active_connections[connection_id]["agent_requested_forward"] = True
                    logger.info(f"[CONN:{connection_id}] Marked connection for forwarding")
                    
                    # Update the call record
                    if active_call:
                        update_call(active_call.id, {
                            "forwarded": True,
                            "forwarded_to": restaurant.phone,
                            "forwarded_time": get_current_time()
                        })
            
            elif tool_name == "get_address":
                logger.info(f"[CONN:{connection_id}] ★★★ AGENT USED GET_ADDRESS TOOL ★★★")
                # No special handling needed, just log it
        
        # Update connection status
        active_connections[connection_id]["status"] = "initializing_conversation"
        active_connections[connection_id]["agent_requested_end"] = False
        
        logger.info(f"[CONN:{connection_id}] Starting conversation session")
        # Register tool use callback to detect when agent uses tools
        conversation.on_tool_use = on_agent_tool_use
        
        # Start the conversation session asynchronously
        await conversation.start_session()
        
        # Update connection status
        active_connections[connection_id]["status"] = "active"
        active_connections[connection_id]["conversation_started"] = get_current_time().isoformat()
        
        # Store the conversation object in our separate dictionary (not in active_connections because it's not JSON serializable)
        active_conversations[connection_id] = conversation
        
        logger.info(f"[CONN:{connection_id}] Conversation started successfully")
        
        # Process incoming messages
        message_count = 0
        async for message in websocket.iter_text():
            message_count += 1
            if not message:
                continue
                
            try:
                # Only log messages periodically to reduce noise
                if message_count <= 5 or message_count % 100 == 0:
                    logger.debug(f"[CONN:{connection_id}] Received message #{message_count}")
                
                # Parse and handle the message
                message_data = json.loads(message)
                await audio_interface.handle_twilio_message(message_data)
                
                # Update last activity timestamp without logging
                active_connections[connection_id]["last_activity"] = get_current_time().isoformat()
            except json.JSONDecodeError:
                logger.warning(f"[CONN:{connection_id}] Received invalid JSON in message #{message_count}")
            except Exception as e:
                logger.error(f"[CONN:{connection_id}] Error processing message #{message_count}: {e}")
    
    except WebSocketDisconnect:
        logger.info(f"[CONN:{connection_id}] WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"[CONN:{connection_id}] Error in WebSocket handler: {e}")
        logger.error(f"[CONN:{connection_id}] Error details: {traceback.format_exc()}")
    finally:
        try:
            # Check if this connection is in a valid state for hangup
            should_attempt_hangup = False
            agent_requested_end = False
            agent_requested_forward = False
            
            if connection_id in active_connections:
                conn_info = active_connections[connection_id]
                status = conn_info.get("status", "unknown")
                
                # Check if agent explicitly requested call termination or forwarding
                agent_requested_end = conn_info.get("agent_requested_end", False)
                agent_requested_forward = conn_info.get("agent_requested_forward", False)
                
                # Update connection status
                active_connections[connection_id]["status"] = "closing"
                active_connections[connection_id]["close_time"] = get_current_time().isoformat()
                
                # Log connection state at close time
                logger.info(f"[CONN:{connection_id}] Closing connection, final state: {json.dumps(conn_info)}")
                
                # Skip hangup if call was forwarded
                if agent_requested_forward:
                    logger.info(f"[CONN:{connection_id}] Skipping hangup because call was forwarded to restaurant owner")
                    should_attempt_hangup = False
                # Only attempt hangup if we have a stream SID in our tracking and call was not forwarded
                elif conn_info.get("stream_sid") is not None:
                    should_attempt_hangup = True
                    if agent_requested_end:
                        logger.info(f"[CONN:{connection_id}] Will terminate call because agent used end_call tool")
                    else:
                        logger.info(f"[CONN:{connection_id}] Will terminate call due to conversation ending")
                else:
                    logger.info(f"[CONN:{connection_id}] Skipping hangup, no stream_sid in connection tracking")
            
            # Attempt hangup if appropriate
            if should_attempt_hangup:
                logger.info(f"[CONN:{connection_id}] Sending Twilio hangup message...")
                # Get the stream_sid from our tracking dictionary
                stream_sid = conn_info.get("stream_sid")
                # Pass the stream_sid to the hangup function
                hangup_success = await send_hangup_message(stream_sid, connection_id)
                if hangup_success:
                    logger.info(f"[CONN:{connection_id}] Twilio call terminated successfully")
                else:
                    logger.warning(f"[CONN:{connection_id}] Failed to terminate Twilio call")
            
            # Only try to end the ElevenLabs session if conversation was created
            if 'conversation' in locals() and conversation is not None:
                logger.info(f"[CONN:{connection_id}] Ending ElevenLabs session...")
                await conversation.end_session()
                conversation.wait_for_session_end()
                logger.info(f"[CONN:{connection_id}] Conversation session ended")
            else:
                logger.info(f"[CONN:{connection_id}] Call ended before conversation was fully established")
            
            # End the call in our database
            if 'active_call' in locals() and active_call is not None:
                end_call(
                    active_call.id,
                    forwarded=agent_requested_forward,
                    forwarded_to=restaurant.phone if agent_requested_forward else None
                )
            
            # Remove this connection from active connections and active conversations
            if connection_id in active_connections:
                del active_connections[connection_id]
                logger.info(f"[CONN:{connection_id}] Connection removed from tracking. Remaining connections: {len(active_connections)}")
            
            # Also clean up the conversation object
            if connection_id in active_conversations:
                del active_conversations[connection_id]
                logger.info(f"[CONN:{connection_id}] Conversation object removed from tracking")
                
            logger.info(f"[CONN:{connection_id}] Call cleanup completed")
        except Exception as e:
            logger.error(f"[CONN:{connection_id}] Error during call cleanup: {e}")
            logger.error(f"[CONN:{connection_id}] Error details: {traceback.format_exc()}")
