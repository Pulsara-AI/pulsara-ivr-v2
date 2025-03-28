# IVR Integration API Schema

## Overview

The IVR Integration API provides endpoints for Interactive Voice Response (IVR) systems to connect with the Pulsara AI platform.

## Requirements

- Restaurant configuration endpoint
- Call processing endpoint
- Call completion logging
- Authentication for external IVR systems

## Why This Matters

- **System Integration**: IVR system needs to know which restaurant is being called
- **Data Logging**: Call data needs to be logged in the dashboard
- **Notification Trigger**: Call completion triggers email notifications
- **Security**: Secure authentication prevents unauthorized access
- **Multi-Restaurant Support**: System must identify the correct restaurant for each incoming call

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

### Check Restaurant Configuration

```
GET /ivr/restaurant/:restaurantId/config
```

IVR systems should check if a restaurant is configured to use AI call handling before processing a call.

**Headers:**
```
Authorization: Bearer {api_key}
```

**URL Parameters:**
- restaurantId: Restaurant ID or phone number

**Response:**
```json
{
  "success": true,
  "data": {
    "restaurantId": "restaurant_id",
    "name": "Restaurant Name",
    "aiEnabled": true,
    "callHoursStart": "09:00",
    "callHoursEnd": "21:00",
    "currentlyInCallHours": true,
    "agent": {
      "elevenlabs_agent_id": "elevenlabs_agent_id",
      "voice_id": "tnSpp4vdxKPjI9w0GnoV",
      "tools": ["end_call", "get_address", "forward_call"]
    },
    "forwarding_number": "(555) 123-4567"
  }
}
```

### Process Call

```
POST /ivr/call
```

Send call data to the Pulsara AI system for processing.

**Headers:**
```
Authorization: Bearer {api_key}
```

**Request Body:**
```json
{
  "restaurantId": "restaurant_id",
  "callId": "external_call_id",
  "timestamp": "2025-03-01T12:30:00.000Z",
  "callerNumber": "+15551234567",
  "transcript": "Customer call transcript",
  "audioUrl": "https://storage.pulsara.ai/calls/call_id.mp3"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Call processed successfully",
  "data": {
    "callId": "pulsara_call_id",
    "sentimentScore": 85,
    "sentimentLabel": "positive",
    "summary": "Customer called about operating hours",
    "reason": "Hours"
  }
}
```

### Log Call Completion

```
POST /ivr/call/:callId/complete
```

Notify the Pulsara AI system when a call is completed.

**Headers:**
```
Authorization: Bearer {api_key}
```

**URL Parameters:**
- callId: Pulsara call ID

**Request Body:**
```json
{
  "duration": 120,
  "forwardedTo": "manager", // If the call was forwarded
  "finalTranscript": "Complete call transcript",
  "audioUrl": "https://storage.pulsara.ai/calls/call_id.mp3"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Call completion logged successfully",
  "data": {
    "callId": "pulsara_call_id",
    "sentimentScore": 85,
    "sentimentLabel": "positive",
    "summary": "Customer called about operating hours",
    "reason": "Hours",
    "duration": 120,
    "emailSent": true,
    "emailRecipients": ["owner@restaurant.com"]
  }
}
```

### Register Webhook

```
POST /ivr/webhooks/register
```

Register a webhook to receive updates about restaurant configurations.

**Headers:**
```
Authorization: Bearer {api_key}
```

**Request Body:**
```json
{
  "callbackUrl": "https://your-ivr-system.com/callbacks/pulsara",
  "events": ["restaurant.updated", "settings.updated", "agent.updated"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook registered successfully",
  "data": {
    "webhookId": "webhook_id",
    "callbackUrl": "https://your-ivr-system.com/callbacks/pulsara",
    "events": ["restaurant.updated", "settings.updated", "agent.updated"]
  }
}
```

### Get API Key

```
POST /ivr/auth/api-key
```

Generate a new API key for IVR system authentication. Admin only.

**Headers:**
```
Authorization: Bearer {admin_access_token}
```

**Request Body:**
```json
{
  "name": "Twilio IVR Integration",
  "description": "API key for Twilio IVR system"
}
```

**Response:**
```json
{
  "success": true,
  "message": "API key generated successfully",
  "data": {
    "apiKey": "psk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "name": "Twilio IVR Integration",
    "createdAt": "2025-03-01T00:00:00.000Z"
  }
}
```

## Database Schema

### API Keys Table

```sql
CREATE TABLE api_keys (
  id UUID PRIMARY KEY,
  key_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_by UUID NOT NULL REFERENCES users(id),
  last_used TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Webhooks Table

```sql
CREATE TABLE webhooks (
  id UUID PRIMARY KEY,
  callback_url VARCHAR(255) NOT NULL,
  events JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Notes

1. API keys should be securely hashed in the database
2. Webhook calls should be retried on failure with exponential backoff
3. Restaurant identification should support lookup by phone number
4. Call completion should trigger email notifications automatically
5. API endpoints should be rate-limited to prevent abuse
6. Webhook payloads should include only necessary information
7. API key rotation should be supported for security
8. Call data should be validated before processing
