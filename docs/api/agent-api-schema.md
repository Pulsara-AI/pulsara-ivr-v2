# Agent Management API Schema

## Overview

The Agent Management API handles the configuration and management of AI agents for each restaurant in the Pulsara system.

## Requirements

- Agent configuration per restaurant
- System prompt management with restaurant-specific variables
- Tool configuration (end_call, get_address, forward_call)
- Agent testing interface
- Admin-only ElevenLabs agent ID management

## Why This Matters

- **Personalization**: Each restaurant needs its own AI agent with custom configuration
- **Contextual Awareness**: System prompts must be tailored to restaurant specifics (name, hours, etc.)
- **Functionality Control**: Agents need different tools enabled/disabled based on restaurant needs
- **Quality Assurance**: Testing is essential before deploying changes to live calls
- **Technical Integration**: Only admins should be able to set the actual ElevenLabs agent IDs

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

### Get Agent Configuration

```
GET /restaurants/:restaurantId/agent
```

Returns the current agent configuration for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "agent_uuid",
    "restaurant_id": "restaurant_uuid",
    "elevenlabs_agent_id": "elevenlabs_agent_id",
    "name": "Pulsara for Luigi's Pizza",
    "voice_id": "tnSpp4vdxKPjI9w0GnoV",
    "system_prompt": {
      "name": "Pulsara",
      "role": "AI Phone Host",
      "gender": "female",
      "workplace": {
        "restaurantName": "Luigi's Pizza",
        "restaurantType": "Italian Pizzeria",
        "location": "Chicago"
      },
      "context": {
        "behavior": "Converse naturally and warmly—like a seasoned restaurant host...",
        "environment": "Pulsara v1 Orchestration Flow",
        "toolUsage": "You have access to the end_call tool..."
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
        "workingHours": "11 AM - 10 PM",
        "peakHours": "6 PM - 9 PM"
      },
      "callManagement": {
        "endingCalls": "⚠️ CRITICAL INSTRUCTION ⚠️: When a caller asks to end the call...",
        "endCallExamples": [
          "Caller: 'Please end the call now' → You: 'Thank you for calling! Goodbye!' → [USE end_call TOOL IMMEDIATELY]"
        ]
      },
      "system_tools": {
        "end_call": "⚠️ HIGHEST PRIORITY TOOL ⚠️: This tool hangs up the phone call...",
        "get_address": "Returns the restaurant's address...",
        "forward_call": "⚠️ CRITICAL TOOL ⚠️: Forwards the call to the restaurant owner..."
      }
    },
    "tools": [
      {
        "name": "end_call",
        "enabled": true,
        "description": "Ends the current phone call completely."
      },
      {
        "name": "get_address",
        "enabled": true,
        "description": "Returns the restaurant's address."
      },
      {
        "name": "forward_call",
        "enabled": true,
        "description": "Forwards the call to the restaurant owner."
      }
    ],
    "created_at": "2025-03-01T00:00:00.000Z",
    "updated_at": "2025-03-01T00:00:00.000Z"
  }
}
```

### Update Agent Configuration

```
PUT /restaurants/:restaurantId/agent
```

Updates the agent configuration for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "name": "Pulsara for Luigi's Pizza",
  "system_prompt": {
    "workplace": {
      "restaurantName": "Luigi's Pizza",
      "restaurantType": "Italian Pizzeria",
      "location": "Chicago"
    },
    "operationalContext": {
      "workingHours": "11 AM - 10 PM",
      "peakHours": "6 PM - 9 PM"
    }
  },
  "tools": [
    {
      "name": "end_call",
      "enabled": true
    },
    {
      "name": "get_address",
      "enabled": true
    },
    {
      "name": "forward_call",
      "enabled": true
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent updated successfully",
  "data": {
    "id": "agent_uuid",
    "restaurant_id": "restaurant_uuid",
    "elevenlabs_agent_id": "elevenlabs_agent_id",
    "name": "Pulsara for Luigi's Pizza",
    "updated_at": "2025-03-01T00:00:00.000Z"
  }
}
```

### Test Agent

```
POST /restaurants/:restaurantId/agent/test
```

Tests the agent with a sample input.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "input": "What are your hours today?"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Our hours today are 11 AM to 10 PM. Is there anything else I can help you with?",
    "audio_url": "https://storage.pulsara.ai/test-responses/response_123.mp3"
  }
}
```

### Set Agent ID (Admin Only)

```
PUT /admin/restaurants/:restaurantId/agent/elevenlabs-id
```

Sets the ElevenLabs agent ID for a restaurant. Admin only.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "elevenlabs_agent_id": "new_elevenlabs_agent_id",
  "voice_id": "tnSpp4vdxKPjI9w0GnoV"
}
```

**Response:**
```json
{
  "success": true,
  "message": "ElevenLabs agent ID updated successfully",
  "data": {
    "elevenlabs_agent_id": "new_elevenlabs_agent_id",
    "voice_id": "tnSpp4vdxKPjI9w0GnoV"
  }
}
```

## Database Schema

### Agents Table

```sql
CREATE TABLE agents (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  elevenlabs_agent_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  voice_id VARCHAR(255) NOT NULL,
  system_prompt JSONB NOT NULL,
  tools JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Notes

1. Agent creation should happen automatically when a restaurant is created
2. System prompts should be templated with restaurant-specific information
3. Tool configuration should be validated to ensure required tools are enabled
4. Agent testing should use the ElevenLabs API but not affect live calls
5. Voice ID changes should be restricted to prevent disruption to caller experience
6. System prompt updates should be validated for required fields
