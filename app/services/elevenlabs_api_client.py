"""
ElevenLabs API client for direct API calls without using the SDK.
"""

import json
import asyncio
import websockets
import httpx
from typing import Dict, Any, Optional, List, Callable, Union
from app.utils.logging import get_logger
from config.environment import ELEVENLABS_API_KEY

logger = get_logger(__name__)

class ElevenLabsAPIClient:
    """
    Client for making direct API calls to ElevenLabs API.
    
    This client replaces the ElevenLabs SDK with direct API calls for better
    stability and control.
    """
    
    BASE_URL = "https://api.elevenlabs.io"
    API_VERSION = "v1"
    
    def __init__(self, api_key: str = None):
        """
        Initialize the ElevenLabs API client.
        
        Args:
            api_key: The ElevenLabs API key (defaults to environment variable)
        """
        self.api_key = api_key or ELEVENLABS_API_KEY
        if not self.api_key:
            logger.error("No ElevenLabs API key provided")
            raise ValueError("ElevenLabs API key is required")
        
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Initialize HTTP client with timeout and retry settings
        self.client = httpx.AsyncClient(
            timeout=30.0,  # 30 second timeout
            headers=self.headers
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build a full URL for the given endpoint.
        
        Args:
            endpoint: The API endpoint (without leading slash)
            
        Returns:
            The full URL
        """
        return f"{self.BASE_URL}/{self.API_VERSION}/{endpoint}"
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        files: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the ElevenLabs API.
        
        Args:
            method: The HTTP method (GET, POST, PATCH, DELETE)
            endpoint: The API endpoint (without leading slash)
            data: The request data (optional)
            params: The query parameters (optional)
            files: The files to upload (optional)
            
        Returns:
            The API response as a dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = self._build_url(endpoint)
        
        # Log the request (but mask sensitive data)
        safe_data = "**REDACTED**" if data else None
        logger.info(f"Making {method} request to {url} with params={params}")
        
        try:
            # Prepare headers based on whether we're sending files
            request_headers = self.headers.copy()
            if files:
                # Remove Content-Type for multipart/form-data (will be set automatically)
                request_headers.pop("Content-Type", None)
            
            # Make the request
            if method == "GET":
                response = await self.client.get(url, params=params, headers=request_headers)
            elif method == "POST":
                if files:
                    response = await self.client.post(url, data=data, files=files, params=params, headers=request_headers)
                else:
                    response = await self.client.post(url, json=data, params=params, headers=request_headers)
            elif method == "PATCH":
                response = await self.client.patch(url, json=data, params=params, headers=request_headers)
            elif method == "DELETE":
                response = await self.client.delete(url, params=params, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Raise an exception for 4XX/5XX responses
            response.raise_for_status()
            
            # Parse and return the response
            if response.headers.get("content-type") == "application/json":
                return response.json()
            else:
                return {"status": "success", "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            # Try to parse error response as JSON
            try:
                error_data = e.response.json()
                logger.error(f"Error details: {json.dumps(error_data)}")
            except:
                logger.error(f"Raw error response: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    # Agent Management API
    
    async def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new agent.
        
        Args:
            config: The agent configuration
            
        Returns:
            The created agent data
        """
        return await self._make_request("POST", "convai/agents/create", data=config)
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            The agent data
        """
        return await self._make_request("GET", f"convai/agents/{agent_id}")
    
    async def update_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an agent.
        
        Args:
            agent_id: The agent ID
            config: The updated agent configuration
            
        Returns:
            The updated agent data
        """
        return await self._make_request("PATCH", f"convai/agents/{agent_id}", data=config)
    
    # Knowledge Base API
    
    async def list_knowledge_base(self) -> Dict[str, Any]:
        """
        List all knowledge base documents.
        
        Returns:
            The knowledge base documents
        """
        return await self._make_request("GET", "convai/knowledge-base")
    
    async def get_knowledge_base_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a knowledge base document by ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            The document data
        """
        return await self._make_request("GET", f"convai/knowledge-base/{document_id}")
    
    async def create_knowledge_base_document(
        self, 
        name: str = None, 
        url: str = None, 
        file_content: bytes = None,
        file_name: str = None
    ) -> Dict[str, Any]:
        """
        Create a new knowledge base document.
        
        Args:
            name: The document name (optional)
            url: The document URL (optional)
            file_content: The file content (optional)
            file_name: The file name (optional)
            
        Returns:
            The created document data
        """
        data = {}
        files = None
        
        if name:
            data["name"] = name
        
        if url:
            data["url"] = url
        
        if file_content and file_name:
            files = {"file": (file_name, file_content)}
        
        return await self._make_request(
            "POST", 
            "convai/knowledge-base", 
            data=data, 
            files=files
        )
    
    async def delete_knowledge_base_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a knowledge base document.
        
        Args:
            document_id: The document ID
            
        Returns:
            The deletion result
        """
        return await self._make_request("DELETE", f"convai/knowledge-base/{document_id}")
    
    # Conversation API
    
    async def list_conversations(
        self, 
        agent_id: str = None,
        cursor: str = None,
        page_size: int = 30
    ) -> Dict[str, Any]:
        """
        List conversations.
        
        Args:
            agent_id: Filter by agent ID (optional)
            cursor: Pagination cursor (optional)
            page_size: Number of conversations per page (optional)
            
        Returns:
            The conversations data
        """
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        if cursor:
            params["cursor"] = cursor
        if page_size:
            params["page_size"] = page_size
            
        return await self._make_request("GET", "convai/conversations", params=params)
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation data
        """
        return await self._make_request("GET", f"convai/conversations/{conversation_id}")
    
    async def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Delete a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The deletion result
        """
        return await self._make_request("DELETE", f"convai/conversations/{conversation_id}")
    
    async def get_conversation_audio(self, conversation_id: str) -> bytes:
        """
        Get the audio for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The audio data as bytes
        """
        url = self._build_url(f"convai/conversations/{conversation_id}/audio")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error getting conversation audio: {str(e)}")
            raise
    
    # WebSocket Conversation API
    
    async def start_conversation(
        self,
        agent_id: str,
        audio_interface: Any,
        on_tool_use: Callable[[str, Dict[str, Any]], None] = None,
        on_agent_response: Callable[[str], None] = None,
        on_user_transcript: Callable[[str], None] = None
    ) -> Any:
        """
        Start a conversation with an agent using WebSockets.
        
        This is a placeholder for the WebSocket implementation that will replace
        the SDK's Conversation class. The actual implementation will be more complex
        and will need to handle WebSocket communication, audio streaming, etc.
        
        Args:
            agent_id: The agent ID
            audio_interface: The audio interface for sending/receiving audio
            on_tool_use: Callback for tool usage (optional)
            on_agent_response: Callback for agent responses (optional)
            on_user_transcript: Callback for user transcripts (optional)
            
        Returns:
            A conversation object
        """
        # This is a placeholder - the actual implementation will be more complex
        logger.info(f"Starting conversation with agent {agent_id}")
        
        # Return a placeholder conversation object
        return {
            "agent_id": agent_id,
            "status": "active",
            "end_session": lambda: logger.info(f"Ending conversation with agent {agent_id}")
        }
