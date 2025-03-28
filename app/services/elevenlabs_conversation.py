"""
ElevenLabs conversation handler for WebSocket communication.
"""

import json
import asyncio
import base64
import uuid
import time
from typing import Dict, Any, Optional, List, Callable, Union
import websockets
from websockets.exceptions import ConnectionClosed

from app.utils.logging import get_logger
from config.environment import ELEVENLABS_API_KEY

logger = get_logger(__name__)

class ElevenLabsConversation:
    """
    Handler for WebSocket-based conversations with ElevenLabs.
    
    This class replaces the ElevenLabs SDK's Conversation class with a direct
    WebSocket implementation for better stability and control.
    """
    
    WEBSOCKET_URL = "wss://api.elevenlabs.io/v1/convai/stream"
    
    def __init__(
        self,
        agent_id: str,
        api_key: str = None,
        audio_interface: Any = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the ElevenLabs conversation handler.
        
        Args:
            agent_id: The ElevenLabs agent ID
            api_key: The ElevenLabs API key (defaults to environment variable)
            audio_interface: The audio interface for sending/receiving audio
            config: Additional configuration for the conversation
        """
        self.agent_id = agent_id
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.audio_interface = audio_interface
        self.config = config or {}
        
        # Generate a unique conversation ID
        self.conversation_id = str(uuid.uuid4())
        
        # WebSocket connection
        self.websocket = None
        self.is_connected = False
        self.is_session_active = False
        
        # Callbacks
        self.on_tool_use = None
        self.on_agent_response = None
        self.on_user_transcript = None
        
        # Task for receiving messages
        self.receive_task = None
        
        # Audio buffer for incoming audio from the agent
        self.audio_buffer = bytearray()
        
        logger.info(f"Initialized conversation handler for agent {agent_id}")
    
    async def start_session(self):
        """
        Start a conversation session with the agent.
        
        This establishes a WebSocket connection and starts the message handling loop.
        """
        if self.is_session_active:
            logger.warning("Session is already active")
            return
        
        try:
            # Prepare connection parameters
            params = {
                "xi-api-key": self.api_key,
                "agent_id": self.agent_id
            }
            
            # Add any additional parameters from config
            if "conversation_id" in self.config:
                params["conversation_id"] = self.config["conversation_id"]
            
            # Build the URL with query parameters
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.WEBSOCKET_URL}?{query_string}"
            
            logger.info(f"Connecting to WebSocket at {self.WEBSOCKET_URL} for agent {self.agent_id}")
            
            # Connect to the WebSocket
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            
            # Start the message receiving task
            self.receive_task = asyncio.create_task(self._receive_messages())
            
            # Mark the session as active
            self.is_session_active = True
            
            logger.info(f"Session started for agent {self.agent_id}")
            
            # Start the audio interface if provided
            if self.audio_interface:
                self.audio_interface.start(self._handle_input_audio)
                logger.info("Audio interface started")
        
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            await self.end_session()
            raise
    
    async def end_session(self):
        """
        End the conversation session.
        
        This closes the WebSocket connection and cleans up resources.
        """
        logger.info(f"Ending session for agent {self.agent_id}")
        
        # Mark the session as inactive
        self.is_session_active = False
        
        # Cancel the receive task if it's running
        if self.receive_task and not self.receive_task.done():
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass
        
        # Close the WebSocket connection
        if self.websocket and self.is_connected:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {str(e)}")
            finally:
                self.is_connected = False
                self.websocket = None
        
        # Stop the audio interface if provided
        if self.audio_interface:
            self.audio_interface.stop()
            logger.info("Audio interface stopped")
        
        logger.info(f"Session ended for agent {self.agent_id}")
    
    def wait_for_session_end(self):
        """
        Wait for the session to end.
        
        This is a synchronous method that blocks until the session is ended.
        """
        # This is a placeholder for compatibility with the SDK
        # In a real implementation, this would wait for the session to end
        logger.info(f"Waiting for session to end for agent {self.agent_id}")
        
        # If the session is still active, end it
        if self.is_session_active:
            asyncio.create_task(self.end_session())
    
    def _handle_input_audio(self, audio_data: bytes):
        """
        Handle audio input from the audio interface.
        
        This method is called by the audio interface when new audio data is available.
        It sends the audio data to the agent via the WebSocket.
        
        Args:
            audio_data: The audio data as bytes
        """
        if not self.is_session_active or not self.is_connected:
            return
        
        # Send the audio data to the agent
        asyncio.create_task(self._send_audio(audio_data))
    
    async def _send_audio(self, audio_data: bytes):
        """
        Send audio data to the agent via the WebSocket.
        
        Args:
            audio_data: The audio data as bytes
        """
        if not self.is_session_active or not self.is_connected:
            return
        
        try:
            # Encode the audio data as base64
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            
            # Create the message
            message = {
                "type": "audio",
                "data": audio_base64
            }
            
            # Send the message
            await self.websocket.send(json.dumps(message))
        
        except Exception as e:
            logger.error(f"Error sending audio: {str(e)}")
    
    async def _receive_messages(self):
        """
        Receive and process messages from the WebSocket.
        
        This method runs in a separate task and handles incoming messages from the agent.
        """
        if not self.is_connected:
            logger.error("Cannot receive messages: WebSocket not connected")
            return
        
        try:
            async for message in self.websocket:
                try:
                    # Parse the message
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    # Handle different message types
                    if message_type == "agent_response":
                        # Agent text response
                        text = data.get("data", {}).get("text", "")
                        if self.on_agent_response and text:
                            self.on_agent_response(text)
                    
                    elif message_type == "audio":
                        # Agent audio response
                        audio_base64 = data.get("data", "")
                        if audio_base64:
                            # Decode the audio data
                            audio_data = base64.b64decode(audio_base64)
                            
                            # Send the audio to the audio interface
                            if self.audio_interface:
                                self.audio_interface.output(audio_data)
                    
                    elif message_type == "user_transcript":
                        # User transcript
                        text = data.get("data", {}).get("text", "")
                        if self.on_user_transcript and text:
                            self.on_user_transcript(text)
                    
                    elif message_type == "client_tool_call":
                        # Tool call from the agent
                        tool_data = data.get("data", {})
                        tool_name = tool_data.get("name", "")
                        tool_params = tool_data.get("parameters", {})
                        
                        logger.info(f"Tool call: {tool_name} with params: {json.dumps(tool_params)}")
                        
                        if self.on_tool_use and tool_name:
                            self.on_tool_use(tool_name, tool_params)
                    
                    elif message_type == "error":
                        # Error message
                        error_message = data.get("data", {}).get("message", "Unknown error")
                        logger.error(f"Error from ElevenLabs: {error_message}")
                    
                    else:
                        # Other message types
                        logger.debug(f"Received message of type {message_type}: {message}")
                
                except json.JSONDecodeError:
                    logger.error(f"Error decoding message: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
        
        except ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in receive task: {str(e)}")
        finally:
            # Mark the connection as closed
            self.is_connected = False
            
            # End the session if it's still active
            if self.is_session_active:
                asyncio.create_task(self.end_session())
    
    async def send_interruption(self):
        """
        Send an interruption signal to the agent.
        
        This tells the agent to stop speaking and listen to the user.
        """
        if not self.is_session_active or not self.is_connected:
            return
        
        try:
            # Create the interruption message
            message = {
                "type": "interruption"
            }
            
            # Send the message
            await self.websocket.send(json.dumps(message))
            logger.info("Sent interruption signal")
        
        except Exception as e:
            logger.error(f"Error sending interruption: {str(e)}")
