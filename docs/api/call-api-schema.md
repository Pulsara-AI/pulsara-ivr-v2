# Call Management API Schema

## Overview

The Call Management API handles the recording, retrieval, and analysis of phone calls in the Pulsara system.

## Requirements

- Call history with filtering and pagination
- Call detail view with transcript and sentiment
- Call statistics and analytics
- Email summary functionality

## Why This Matters

- **Business Intelligence**: Call history provides valuable business insights
- **Quality Assurance**: Transcripts help restaurant owners review conversations
- **Customer Satisfaction**: Sentiment analysis identifies potential issues
- **Performance Metrics**: Statistics help measure AI system effectiveness
- **Immediate Notification**: Email summaries allow quick response to important calls

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

### Get Calls

```
GET /restaurants/:restaurantId/calls
```

Returns calls for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Query Parameters:**
- page (optional): Page number for pagination (default: 1)
- limit (optional): Number of calls per page (default: 10)
- search (optional): Search term to filter calls by transcript content
- startDate (optional): Filter calls after this date (ISO format)
- endDate (optional): Filter calls before this date (ISO format)
- sentiment (optional): Filter by sentiment ('positive', 'neutral', 'negative')
- handled (optional): Filter by handling type ('ai', 'forwarded')

**Response:**
```json
{
  "success": true,
  "data": {
    "calls": [
      {
        "id": "call_id",
        "duration": 120,
        "timestamp": "2025-03-01T12:30:00.000Z",
        "handledBy": "ai",
        "transcript": "Full call transcript here...",
        "sentimentScore": 85,
        "sentimentLabel": "positive",
        "summary": "Customer called about operating hours",
        "reason": "Hours",
        "audioUrl": "https://storage.pulsara.ai/calls/call_id.mp3",
        "agentResponses": [
          {
            "text": "Our hours are 9 AM to 9 PM.",
            "timestamp": "2025-03-01T12:30:15.000Z"
          }
        ],
        "forwardedTime": null,
        "forwardedReason": null
      }
    ],
    "pagination": {
      "totalCalls": 50,
      "totalPages": 5,
      "currentPage": 1,
      "limit": 10
    }
  }
}
```

### Get Call by ID

```
GET /restaurants/:restaurantId/calls/:id
```

Returns a specific call by ID.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Call ID

**Response:**
```json
{
  "success": true,
  "data": {
    "call": {
      "id": "call_id",
      "duration": 120,
      "timestamp": "2025-03-01T12:30:00.000Z",
      "handledBy": "ai",
      "transcript": "Full call transcript here...",
      "sentimentScore": 85,
      "sentimentLabel": "positive",
      "summary": "Customer called about operating hours",
      "reason": "Hours",
      "audioUrl": "https://storage.pulsara.ai/calls/call_id.mp3",
      "agentResponses": [
        {
          "text": "Our hours are 9 AM to 9 PM.",
          "timestamp": "2025-03-01T12:30:15.000Z"
        }
      ],
      "forwardedTime": null,
      "forwardedReason": null
    }
  }
}
```

### Get Call Statistics

```
GET /restaurants/:restaurantId/calls/stats
```

Returns call statistics for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Query Parameters:**
- timeRange (optional): Time range for statistics ('1d', '7d', '30d', '90d', default: '30d')

**Response:**
```json
{
  "success": true,
  "data": {
    "totalCalls": 120,
    "aiHandled": 105,
    "forwarded": 15,
    "avgDuration": 95,
    "sentimentBreakdown": {
      "positive": 75,
      "neutral": 20,
      "negative": 5
    },
    "callReasons": {
      "Hours": 35,
      "Menu": 30,
      "Order": 40,
      "Reservation": 10,
      "Other": 5
    },
    "callsByDay": {
      "labels": ["2025-02-01", "2025-02-02", "..."],
      "data": [5, 8, "..."]
    }
  }
}
```

### Send Email Summary

```
POST /restaurants/:restaurantId/calls/:callId/email-summary
```

Sends an email summary of a call to the restaurant owner.

**URL Parameters:**
- restaurantId: Restaurant ID
- callId: Call ID

**Request Body:**
```json
{
  "recipients": ["owner@restaurant.com", "manager@restaurant.com"],
  "includeAudio": true,
  "includeTranscript": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email summary sent successfully",
  "data": {
    "sentTo": ["owner@restaurant.com", "manager@restaurant.com"],
    "sentAt": "2025-03-01T12:45:00.000Z"
  }
}
```

## Database Schema

### Calls Table

```sql
CREATE TABLE calls (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  call_sid VARCHAR(255) NOT NULL,
  stream_sid VARCHAR(255),
  caller_number VARCHAR(20) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  duration INTEGER,
  handled_by VARCHAR(20) NOT NULL DEFAULT 'ai',
  forwarded BOOLEAN NOT NULL DEFAULT false,
  forwarded_to VARCHAR(100),
  forwarded_time TIMESTAMP,
  transcript TEXT,
  sentiment_score INTEGER,
  sentiment_label VARCHAR(20),
  summary TEXT,
  reason VARCHAR(50),
  audio_url VARCHAR(255),
  agent_responses JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Notes

1. Call data should be recorded in real-time during the call
2. Sentiment analysis should be performed automatically on call completion
3. Call summaries should be generated using AI
4. Call audio should be stored securely and accessible only to authorized users
5. **Email summaries should be sent automatically when a call ends**
6. Call statistics should be updated in real-time for dashboard display
7. Personally identifiable information should be handled according to privacy regulations
