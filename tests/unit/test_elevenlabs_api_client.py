"""
Unit tests for the ElevenLabs API client.
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock
from app.services.elevenlabs_api_client import ElevenLabsAPIClient
from app.models.schemas import Agent, KnowledgeBase

@pytest.fixture
def api_client():
    """Create an ElevenLabs API client for testing."""
    with patch('app.services.elevenlabs_api_client.ELEVENLABS_API_KEY', 'test_api_key'):
        client = ElevenLabsAPIClient()
        yield client

@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    mock = MagicMock()
    mock.status_code = 200
    mock.headers = {'content-type': 'application/json'}
    mock.json.return_value = {'success': True}
    mock.raise_for_status = MagicMock()
    return mock

@pytest.fixture
def mock_httpx_client():
    """Create a mock HTTPX client."""
    with patch('app.services.elevenlabs_api_client.httpx.AsyncClient') as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        
        # Mock HTTP methods
        client_instance.get = MagicMock()
        client_instance.post = MagicMock()
        client_instance.patch = MagicMock()
        client_instance.delete = MagicMock()
        
        yield client_instance

@pytest.mark.asyncio
async def test_create_agent(api_client, mock_httpx_client, mock_response):
    """Test creating an agent."""
    # Setup
    mock_httpx_client.post.return_value = mock_response
    mock_response.json.return_value = {'agent_id': 'test_agent_id'}
    
    # Create a test agent
    agent_config = {
        'conversation_config': {
            'agent': {
                'prompt': {
                    'prompt': json.dumps({}),
                    'tools': []
                },
                'first_message': 'Hello',
                'language': 'en'
            },
            'tts': {
                'voice_id': 'test_voice_id'
            }
        },
        'name': 'Test Agent'
    }
    
    # Call the method
    result = await api_client._make_request('POST', 'convai/agents/create', data=agent_config)
    
    # Assertions
    mock_httpx_client.post.assert_called_once()
    assert result == {'agent_id': 'test_agent_id'}

@pytest.mark.asyncio
async def test_get_agent(api_client, mock_httpx_client, mock_response):
    """Test getting an agent."""
    # Setup
    mock_httpx_client.get.return_value = mock_response
    mock_response.json.return_value = {
        'agent_id': 'test_agent_id',
        'name': 'Test Agent',
        'conversation_config': {}
    }
    
    # Call the method
    result = await api_client._make_request('GET', 'convai/agents/test_agent_id')
    
    # Assertions
    mock_httpx_client.get.assert_called_once()
    assert result['agent_id'] == 'test_agent_id'
    assert result['name'] == 'Test Agent'

@pytest.mark.asyncio
async def test_update_agent(api_client, mock_httpx_client, mock_response):
    """Test updating an agent."""
    # Setup
    mock_httpx_client.patch.return_value = mock_response
    mock_response.json.return_value = {
        'agent_id': 'test_agent_id',
        'name': 'Updated Agent'
    }
    
    # Create update data
    update_data = {
        'name': 'Updated Agent'
    }
    
    # Call the method
    result = await api_client._make_request('PATCH', 'convai/agents/test_agent_id', data=update_data)
    
    # Assertions
    mock_httpx_client.patch.assert_called_once()
    assert result['name'] == 'Updated Agent'

@pytest.mark.asyncio
async def test_list_knowledge_base(api_client, mock_httpx_client, mock_response):
    """Test listing knowledge base documents."""
    # Setup
    mock_httpx_client.get.return_value = mock_response
    mock_response.json.return_value = {
        'documents': [
            {
                'id': 'doc1',
                'name': 'Document 1'
            },
            {
                'id': 'doc2',
                'name': 'Document 2'
            }
        ],
        'has_more': False
    }
    
    # Call the method
    result = await api_client._make_request('GET', 'convai/knowledge-base')
    
    # Assertions
    mock_httpx_client.get.assert_called_once()
    assert len(result['documents']) == 2
    assert result['documents'][0]['name'] == 'Document 1'
    assert result['documents'][1]['name'] == 'Document 2'

@pytest.mark.asyncio
async def test_get_knowledge_base_document(api_client, mock_httpx_client, mock_response):
    """Test getting a knowledge base document."""
    # Setup
    mock_httpx_client.get.return_value = mock_response
    mock_response.json.return_value = {
        'id': 'doc1',
        'name': 'Document 1',
        'type': 'file',
        'metadata': {
            'created_at_unix_secs': 1234567890,
            'last_updated_at_unix_secs': 1234567890,
            'size_bytes': 1024
        }
    }
    
    # Call the method
    result = await api_client._make_request('GET', 'convai/knowledge-base/doc1')
    
    # Assertions
    mock_httpx_client.get.assert_called_once()
    assert result['id'] == 'doc1'
    assert result['name'] == 'Document 1'
    assert result['type'] == 'file'

@pytest.mark.asyncio
async def test_create_knowledge_base_document(api_client, mock_httpx_client, mock_response):
    """Test creating a knowledge base document."""
    # Setup
    mock_httpx_client.post.return_value = mock_response
    mock_response.json.return_value = {
        'id': 'new_doc',
        'prompt_injectable': True
    }
    
    # Call the method
    result = await api_client._make_request('POST', 'convai/knowledge-base', data={'name': 'New Document'})
    
    # Assertions
    mock_httpx_client.post.assert_called_once()
    assert result['id'] == 'new_doc'
    assert result['prompt_injectable'] is True

@pytest.mark.asyncio
async def test_delete_knowledge_base_document(api_client, mock_httpx_client, mock_response):
    """Test deleting a knowledge base document."""
    # Setup
    mock_httpx_client.delete.return_value = mock_response
    mock_response.json.return_value = {'key': 'value'}
    
    # Call the method
    result = await api_client._make_request('DELETE', 'convai/knowledge-base/doc1')
    
    # Assertions
    mock_httpx_client.delete.assert_called_once()
    assert result == {'key': 'value'}

@pytest.mark.asyncio
async def test_error_handling(api_client, mock_httpx_client):
    """Test error handling."""
    # Setup
    error_response = MagicMock()
    error_response.status_code = 422
    error_response.text = '{"error": "Unprocessable Entity"}'
    error_response.json.return_value = {'error': 'Unprocessable Entity'}
    error_response.raise_for_status.side_effect = Exception('HTTP Error')
    
    mock_httpx_client.get.return_value = error_response
    
    # Call the method and expect an exception
    with pytest.raises(Exception):
        await api_client._make_request('GET', 'convai/agents/invalid_id')
    
    # Assertions
    mock_httpx_client.get.assert_called_once()
