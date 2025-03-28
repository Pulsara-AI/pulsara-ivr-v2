import asyncio
import base64
import json
import logging
from fastapi import WebSocket
from elevenlabs.conversational_ai.conversation import AudioInterface
from starlette.websockets import WebSocketDisconnect, WebSocketState
from server_tools import set_call_context

# Set up logging
logger = logging.getLogger(__name__)

class TwilioAudioInterface(AudioInterface):
    def __init__(self, websocket: WebSocket, connection_id=None):
        self.websocket = websocket
        self.input_callback = None
        self.stream_sid = None
        self.call_sid = websocket.query_params.get("call_sid", "Unknown")
        self.connection_id = connection_id or "unknown"
        self.message_counter = 0
        self.loop = asyncio.get_event_loop()
        self.stream_sid_listeners = []  # List of additional listeners
        self.was_interrupted = False  # Flag to track if playback was interrupted
        self.post_interruption_audio_sent = False  # Track if we've sent audio after interruption
        logger.info(f"[CONN:{self.connection_id}] TwilioAudioInterface initialized with CallSID={self.call_sid}")
        
    def add_stream_sid_listener(self, listener_callback):
        """
        Add an additional listener for stream_sid events.
        This allows multiple components to be notified when a stream_sid is received.
        
        Args:
            listener_callback: A function that takes (stream_sid, call_sid) as arguments
        """
        self.stream_sid_listeners.append(listener_callback)
        logger.info(f"[CONN:{self.connection_id}] Added stream_sid listener, total listeners: {len(self.stream_sid_listeners)}")

    def start(self, input_callback):
        self.input_callback = input_callback
        logger.info(f"[CONN:{self.connection_id}] Audio interface started")

    def stop(self):
        self.input_callback = None
        self.stream_sid = None

    def output(self, audio: bytes):
        """
        This method should return quickly and not block the calling thread.
        It sends audio to Twilio, with special handling for post-interruption audio.
        """
        # If this is first audio after an interruption, log it
        if self.was_interrupted and not self.post_interruption_audio_sent:
            logger.info(f"[CONN:{self.connection_id}] ★★★ SENDING FIRST AUDIO AFTER INTERRUPTION ★★★")
            self.post_interruption_audio_sent = True
            # Add a small delay to ensure the previous clear command was processed
            async def send_with_delay():
                await asyncio.sleep(0.1)  # 100ms delay
                await self.send_audio_to_twilio(audio)
            asyncio.run_coroutine_threadsafe(send_with_delay(), self.loop)
        else:
            # Normal audio sending
            asyncio.run_coroutine_threadsafe(self.send_audio_to_twilio(audio), self.loop)
        
    def interrupt(self):
        """
        Handle user interruption by clearing the audio queue and sending a clear message to Twilio.
        Called by ElevenLabs when a user interrupts the agent while it's speaking.
        """
        logger.info(f"[CONN:{self.connection_id}] ★★★ INTERRUPTION DETECTED ★★★")
        
        # Set the interrupted flag
        self.was_interrupted = True
        
        # Send clear message to Twilio to stop current playback
        asyncio.run_coroutine_threadsafe(self.send_clear_message_to_twilio(), self.loop)
        
        logger.info(f"[CONN:{self.connection_id}] Audio cleared due to interruption")

    async def send_audio_to_twilio(self, audio: bytes):
        if self.stream_sid:
            audio_payload = base64.b64encode(audio).decode("utf-8")
            audio_delta = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {"payload": audio_payload},
            }
            try:
                if self.websocket.application_state == WebSocketState.CONNECTED:
                    await self.websocket.send_text(json.dumps(audio_delta))
            except (WebSocketDisconnect, RuntimeError):
                pass

    async def send_clear_message_to_twilio(self):
        if self.stream_sid:
            clear_message = {"event": "clear", "streamSid": self.stream_sid}
            try:
                if self.websocket.application_state == WebSocketState.CONNECTED:
                    await self.websocket.send_text(json.dumps(clear_message))
            except (WebSocketDisconnect, RuntimeError):
                pass

    async def handle_twilio_message(self, data):
        try:
            self.message_counter += 1
            event_type = data.get("event")
            
            if event_type == "start":
                # Log the full start event for debugging
                logger.info(f"[CONN:{self.connection_id}] START event received: {json.dumps(data)}")
                self.stream_sid = data["start"]["streamSid"]
                
                # Update the connection_id with stream SID for better tracking
                short_stream_sid = self.stream_sid[-8:] if self.stream_sid else "unknown"
                self.connection_id = f"{self.connection_id}:{short_stream_sid}"
                
                # Extract the Call SID from various possible locations in the start event
                # 1. Try customParameters first
                parameters = data.get("start", {}).get("customParameters", {})
                logger.info(f"[CONN:{self.connection_id}] Custom parameters: {parameters}")
                
                # 2. Look in different parameter locations (Twilio's format can vary)
                call_sid_found = False
                if "callSid" in parameters:
                    self.call_sid = parameters["callSid"]
                    call_sid_found = True
                    logger.info(f"[CONN:{self.connection_id}] Found callSid in customParameters")
                elif "CallSid" in parameters:
                    self.call_sid = parameters["CallSid"]
                    call_sid_found = True
                    logger.info(f"[CONN:{self.connection_id}] Found CallSid in customParameters")
                else:
                    # 3. Try other possible locations in the start event
                    all_params = data.get("start", {})
                    for key in ["callSid", "CallSid", "callsid", "call_sid"]:
                        if key in all_params:
                            self.call_sid = all_params[key]
                            call_sid_found = True
                            logger.info(f"[CONN:{self.connection_id}] Found {key} in start event")
                            break
                
                if not call_sid_found:
                    logger.warning(f"[CONN:{self.connection_id}] Could not find Call SID in any field")
                    
                # Log the results
                logger.info(f"[CONN:{self.connection_id}] Call SID: {self.call_sid}, Stream SID: {self.stream_sid}")
                
                # Create a mapping between Stream SID and Call SID
                set_call_context(self.stream_sid, self.call_sid, self.connection_id)
                
                # Notify primary listener about the updated stream SID
                if hasattr(self, 'on_stream_sid_received') and callable(self.on_stream_sid_received):
                    logger.info(f"[CONN:{self.connection_id}] Notifying primary listener about stream_sid={self.stream_sid}")
                    self.on_stream_sid_received(self.stream_sid, self.call_sid)
                
                # Notify any additional listeners
                if self.stream_sid_listeners:
                    logger.info(f"[CONN:{self.connection_id}] Notifying {len(self.stream_sid_listeners)} additional listeners")
                    for listener in self.stream_sid_listeners:
                        try:
                            listener(self.stream_sid, self.call_sid)
                        except Exception as e:
                            logger.error(f"[CONN:{self.connection_id}] Error in stream_sid listener: {e}")
                
            elif event_type == "media" and self.input_callback:
                # Process the audio data without any logging at all - this prevents log flooding
                audio_data = base64.b64decode(data["media"]["payload"])
                self.input_callback(audio_data)
                
            elif event_type == "mark" and data.get("mark", {}).get("name") == "interruption":
                # Handle the interruption mark event
                logger.info(f"[CONN:{self.connection_id}] ★★★ INTERRUPTION MARK RECEIVED ★★★")
                # Call the interrupt method to clear audio and send clear message to Twilio
                self.interrupt()
                
            elif event_type == "stop":
                logger.info(f"[CONN:{self.connection_id}] STOP event received")
            
            elif event_type == "agent_response_correction":
                # Handle the agent_response_correction event
                correction_event = data.get("agent_response_correction_event", {})
                original = correction_event.get("original_agent_response", "")
                corrected = correction_event.get("corrected_agent_response", "")
                
                logger.info(f"[CONN:{self.connection_id}] ★★★ AGENT RESPONSE CORRECTED DUE TO INTERRUPTION ★★★")
                logger.info(f"[CONN:{self.connection_id}] Original: {original[:50]}{'...' if len(original) > 50 else ''}")
                logger.info(f"[CONN:{self.connection_id}] Corrected: {corrected}")
                
                # Ensure interrupted flag is set and reset the post_interruption_audio_sent flag
                # This ensures the next audio chunk will be sent with a delay
                self.was_interrupted = True
                self.post_interruption_audio_sent = False
                logger.info(f"[CONN:{self.connection_id}] Reset post_interruption flags to handle corrected response")
                
            elif event_type != "media":  # Skip logging any media events completely
                # Log other non-media event types
                logger.info(f"[CONN:{self.connection_id}] Event: {event_type}")
                
        except Exception as e:
            logger.error(f"[CONN:{self.connection_id}] Error handling Twilio message: {e}")
            # Don't re-raise, so we can keep processing messages
