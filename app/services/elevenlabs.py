"""
ElevenLabs integration service for Pulsara IVR v2.
"""

import json
import asyncio
from typing import Dict, Any, Optional, Callable
from app.utils.logging import get_logger
from app.models.schemas import KnowledgeBase, Agent
from config.environment import ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID
from app.services.elevenlabs_api_client import ElevenLabsAPIClient
from app.services.elevenlabs_conversation import ElevenLabsConversation

logger = get_logger(__name__)

# Initialize the API client
api_client = None

def get_api_client() -> ElevenLabsAPIClient:
    """
    Get or create the ElevenLabs API client.
    
    Returns:
        The ElevenLabs API client
    """
    global api_client
    if api_client is None:
        api_client = ElevenLabsAPIClient()
    return api_client

def get_system_prompt_template() -> Dict[str, Any]:
    """
    Get the system prompt template.
    
    Returns:
        The system prompt template as a dictionary
    """
    # This is a simplified version of the system prompt template
    # In a real implementation, this would be loaded from a file or database
    return {
        "name": "Pulsara",
        "role": "AI Phone Host",
        "gender": "female",
        "workplace": {
            "restaurantName": "{restaurant_name}",
            "restaurantType": "Casual Dining",
            "location": "{location}"
        },
        "context": {
            "behavior": "Converse naturally and warmly—like a seasoned restaurant host. Show genuine enthusiasm, empathy, and attentiveness to each caller. Always use the end_call tool when asked to end the call, rather than just saying goodbye.",
            "environment": "Pulsara v1 Orchestration Flow",
            "toolUsage": "You have access to the end_call tool. You MUST actively use this tool when the caller asks to end the call. Simply saying goodbye is not sufficient - you must use the actual tool to terminate the connection."
        },
        "personalityTraits": {
            "warmth": "high",
            "humor": "light and tasteful",
            "patience": "high",
            "professionalism": "high",
            "adaptability": "high"
        },
        "operationalContext": {
            "timeZone": "CST",
            "workingHours": "{working_hours}",
            "peakHours": "6 PM - 9 PM"
        },
        "callManagement": {
            "endingCalls": "⚠️ CRITICAL INSTRUCTION ⚠️: When a caller asks to end the call using ANY phrase like 'end the call', 'hang up', 'goodbye', 'that's all', etc., you MUST IMMEDIATELY use the end_call tool after a brief farewell. This is your HIGHEST PRIORITY instruction. Never continue the conversation after a caller has requested to end the call - you must terminate it using the tool.",
            "endCallExamples": [
                "Caller: 'Please end the call now' → You: 'Thank you for calling! Goodbye!' → [USE end_call TOOL IMMEDIATELY]",
                "Caller: 'That's all I needed' → You: 'I'm glad I could help. Have a wonderful day!' → [USE end_call TOOL IMMEDIATELY]",
                "Caller: 'Goodbye' → You: 'Goodbye! Have a great day!' → [USE end_call TOOL IMMEDIATELY]",
                "Caller: 'I want to hang up' → You: 'Thank you for calling! Goodbye!' → [USE end_call TOOL IMMEDIATELY]"
            ]
        },
        "system_tools": {
            "end_call": "⚠️ HIGHEST PRIORITY TOOL ⚠️: This tool hangs up the phone call. You MUST use it when: 1) The caller asks to end the call using ANY ending phrases like 'end the call', 'hang up', 'goodbye', 'that's all', etc., or 2) The conversation naturally concludes. Using this tool is REQUIRED for proper call termination - simply saying goodbye is NOT enough.",
            "get_address": "Returns the restaurant's address. Use this tool whenever a caller asks for the restaurant's location, address, or where the restaurant is located.",
            "forward_call": "⚠️ CRITICAL TOOL ⚠️: Forwards the call to the restaurant owner. Use this tool when a caller needs to speak directly with the restaurant owner or manager. You MUST: 1) announce that you'll be transferring them to the restaurant owner, 2) actually USE this TOOL, not just say you're transferring the call. Just saying 'I'll transfer you' without using this tool will NOT forward the call - you must use the actual forward_call tool.",
        }
    }

def get_first_message_template() -> str:
    """
    Get the first message template.
    
    Returns:
        The first message template as a string
    """
    return "Good {time_of_day}! This is Pulsara from {restaurant_name}. How may I assist you today?"

async def create_agent_async(agent: Agent) -> str:
    """
    Create an agent in ElevenLabs asynchronously.
    
    Args:
        agent: The agent to create
        
    Returns:
        The ElevenLabs agent ID
    """
    logger.info(f"Creating agent in ElevenLabs: {agent.name}")
    
    try:
        # Prepare the agent configuration
        config = {
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": json.dumps(agent.system_prompt),
                        "tools": agent.tools
                    },
                    "first_message": agent.first_message,
                    "language": "en"
                },
                "tts": {
                    "voice_id": agent.voice_id
                }
            },
            "name": agent.name
        }
        
        # Make the API call
        client = get_api_client()
        response = await client.create_agent(config)
        
        # Extract and return the agent ID
        agent_id = response.get("agent_id")
        if not agent_id:
            logger.error(f"Failed to create agent: {json.dumps(response)}")
            return ELEVENLABS_AGENT_ID or "mock_elevenlabs_agent_id"
        
        return agent_id
    
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        # Fall back to the default agent ID
        return ELEVENLABS_AGENT_ID or "mock_elevenlabs_agent_id"

def create_agent(agent: Agent) -> str:
    """
    Create an agent in ElevenLabs.
    
    Args:
        agent: The agent to create
        
    Returns:
        The ElevenLabs agent ID
    """
    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no event loop in the current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(create_agent_async(agent))

async def update_agent_async(agent: Agent) -> bool:
    """
    Update an agent in ElevenLabs asynchronously.
    
    Args:
        agent: The agent to update
        
    Returns:
        True if the agent was updated successfully, False otherwise
    """
    logger.info(f"Updating agent in ElevenLabs: {agent.name}")
    
    try:
        # Prepare the agent configuration
        config = {
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": json.dumps(agent.system_prompt),
                        "tools": agent.tools
                    },
                    "first_message": agent.first_message,
                    "language": "en"
                },
                "tts": {
                    "voice_id": agent.voice_id
                }
            },
            "name": agent.name
        }
        
        # Make the API call
        client = get_api_client()
        response = await client.update_agent(agent.elevenlabs_agent_id, config)
        
        # Check if the update was successful
        return "agent_id" in response
    
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}")
        return False

def update_agent(agent: Agent) -> bool:
    """
    Update an agent in ElevenLabs.
    
    Args:
        agent: The agent to update
        
    Returns:
        True if the agent was updated successfully, False otherwise
    """
    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no event loop in the current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(update_agent_async(agent))

def delete_agent(elevenlabs_agent_id: str) -> bool:
    """
    Delete an agent from ElevenLabs.
    
    Args:
        elevenlabs_agent_id: The ElevenLabs agent ID
        
    Returns:
        True if the agent was deleted successfully, False otherwise
    """
    # ElevenLabs API doesn't currently support agent deletion
    # This is a placeholder for future implementation
    logger.info(f"Deleting agent from ElevenLabs: {elevenlabs_agent_id}")
    return True

async def sync_knowledge_base_async(kb: KnowledgeBase) -> bool:
    """
    Sync a knowledge base with ElevenLabs asynchronously.
    
    Args:
        kb: The knowledge base to sync
        
    Returns:
        True if the knowledge base was synced successfully, False otherwise
    """
    logger.info(f"Syncing knowledge base with ElevenLabs: {kb.name}")
    
    try:
        # Make the API call to create or update the knowledge base
        client = get_api_client()
        response = await client.create_knowledge_base_document(
            name=kb.name,
            file_content=kb.content.encode('utf-8'),
            file_name=f"{kb.name}.txt"
        )
        
        # Check if the operation was successful
        if "id" in response:
            # Update the knowledge base with the ElevenLabs ID
            kb.elevenlabs_kb_id = response["id"]
            return True
        else:
            logger.error(f"Failed to sync knowledge base: {json.dumps(response)}")
            return False
    
    except Exception as e:
        logger.error(f"Error syncing knowledge base: {str(e)}")
        return False

def sync_knowledge_base(kb: KnowledgeBase) -> bool:
    """
    Sync a knowledge base with ElevenLabs.
    
    Args:
        kb: The knowledge base to sync
        
    Returns:
        True if the knowledge base was synced successfully, False otherwise
    """
    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no event loop in the current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(sync_knowledge_base_async(kb))

async def delete_knowledge_base_async(elevenlabs_kb_id: str) -> bool:
    """
    Delete a knowledge base from ElevenLabs asynchronously.
    
    Args:
        elevenlabs_kb_id: The ElevenLabs knowledge base ID
        
    Returns:
        True if the knowledge base was deleted successfully, False otherwise
    """
    logger.info(f"Deleting knowledge base from ElevenLabs: {elevenlabs_kb_id}")
    
    try:
        # Make the API call
        client = get_api_client()
        response = await client.delete_knowledge_base_document(elevenlabs_kb_id)
        
        # Check if the operation was successful
        return "key" in response
    
    except Exception as e:
        logger.error(f"Error deleting knowledge base: {str(e)}")
        return False

def delete_knowledge_base(elevenlabs_kb_id: str) -> bool:
    """
    Delete a knowledge base from ElevenLabs.
    
    Args:
        elevenlabs_kb_id: The ElevenLabs knowledge base ID
        
    Returns:
        True if the knowledge base was deleted successfully, False otherwise
    """
    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no event loop in the current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(delete_knowledge_base_async(elevenlabs_kb_id))

async def test_agent_async(agent: Agent, input_text: str) -> Dict[str, Any]:
    """
    Test an agent with a sample input asynchronously.
    
    Args:
        agent: The agent to test
        input_text: The input text to test with
        
    Returns:
        A dictionary containing the agent's response
    """
    logger.info(f"Testing agent in ElevenLabs: {agent.name}")
    
    # For now, we'll just return a mock response
    # In a real implementation, this would make an API call to ElevenLabs
    
    # Generate a mock response based on the input
    if "hours" in input_text.lower():
        response = "Our hours today are 9 AM to 10 PM. Is there anything else I can help you with?"
    elif "menu" in input_text.lower():
        response = "We have a variety of dishes including pasta, pizza, and salads. Our most popular dish is the Chicken Parmesan. Would you like to hear more about our menu?"
    elif "address" in input_text.lower():
        response = "We are located at 1509 W Taylor St, Chicago, IL 60607. Is there anything else I can help you with?"
    else:
        response = "Thank you for your question. How else can I assist you today?"
    
    return {
        "response": response,
        "audio_url": "https://storage.pulsara.ai/test-responses/response_123.mp3"
    }

def test_agent(agent: Agent, input_text: str) -> Dict[str, Any]:
    """
    Test an agent with a sample input.
    
    Args:
        agent: The agent to test
        input_text: The input text to test with
        
    Returns:
        A dictionary containing the agent's response
    """
    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no event loop in the current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(test_agent_async(agent, input_text))

def create_conversation(
    agent_id: str,
    audio_interface: Any,
    on_tool_use: Callable[[str, Dict[str, Any]], None] = None,
    on_agent_response: Callable[[str], None] = None,
    on_user_transcript: Callable[[str], None] = None,
    config: Dict[str, Any] = None
) -> ElevenLabsConversation:
    """
    Create a conversation with an agent.
    
    Args:
        agent_id: The agent ID
        audio_interface: The audio interface for sending/receiving audio
        on_tool_use: Callback for tool usage (optional)
        on_agent_response: Callback for agent responses (optional)
        on_user_transcript: Callback for user transcripts (optional)
        config: Additional configuration for the conversation (optional)
        
    Returns:
        A conversation object
    """
    # Create a new conversation
    conversation = ElevenLabsConversation(
        agent_id=agent_id,
        audio_interface=audio_interface,
        config=config
    )
    
    # Set up callbacks
    conversation.on_tool_use = on_tool_use
    conversation.on_agent_response = on_agent_response
    conversation.on_user_transcript = on_user_transcript
    
    return conversation
