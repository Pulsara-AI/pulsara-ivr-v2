# Pulsara Dashboard API Specification

This document outlines the complete API schema for the Pulsara Dashboard, including the new endpoints required to support the multi-restaurant IVR system.

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

---

## Table of Contents

1. [Authentication](#authentication)
2. [Restaurant Management](#restaurant-management)
3. [Agent Management](#agent-management)
4. [Knowledge Base Management](#knowledge-base-management)
5. [Menu Management](#menu-management)
6. [Settings Management](#settings-management)
7. [Call Management](#call-management)
8. [IVR Integration Points](#ivr-integration)
9. [Database Schema](#database-schema)

---

## Authentication

The Pulsara API uses JSON Web Tokens (JWT) for authentication. Most endpoints require a valid token to be included in the request header.

### Authentication Header

Include the JWT token in the request header:

```
Authorization: Bearer {your_access_token}
```

### Authentication Endpoints

#### Register User

```
POST /auth/register
```

Creates a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "role": "RESTAURANT_OWNER" // Or "ADMIN" (Admin creation restricted)
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": "user_id",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "RESTAURANT_OWNER"
  }
}
```

#### Login

```
POST /auth/login
```

Authenticates a user and returns access and refresh tokens.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "RESTAURANT_OWNER"
    }
  }
}
```

#### Refresh Token

```
POST /auth/refresh-token
```

Returns a new access token using a valid refresh token.

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### Get User Profile

```
GET /auth/me
```

Returns the current user's profile information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_id",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "RESTAURANT_OWNER",
    "restaurantId": "restaurant_id" // Only for RESTAURANT_OWNER role
  }
}
```

---

## Restaurant Management

### Get All Restaurants

```
GET /restaurants
```

Returns a list of all restaurants. Admin only.

**Query Parameters:**
- page (optional): Page number for pagination (default: 1)
- limit (optional): Number of restaurants per page (default: 10)
- search (optional): Search term to filter restaurants
- status (optional): Filter by status ('active' or 'inactive')

**Response:**
```json
{
  "success": true,
  "data": {
    "restaurants": [
      {
        "id": "restaurant_id",
        "name": "Restaurant Name",
        "owner": "Owner Name",
        "email": "contact@restaurant.com",
        "phone": "(555) 123-4567",
        "address": "123 Main St, City, State",
        "status": "active",
        "aiEnabled": true,
        "createdAt": "2025-03-01T00:00:00.000Z",
        "updatedAt": "2025-03-01T00:00:00.000Z"
      }
    ],
    "pagination": {
      "totalRestaurants": 50,
      "totalPages": 5,
      "currentPage": 1,
      "limit": 10
    }
  }
}
```

### Get My Restaurants

```
GET /restaurants/my
```

Returns restaurants owned by the current user.

**Response:**
```json
{
  "success": true,
  "data": {
    "restaurants": [
      {
        "id": "restaurant_id",
        "name": "Restaurant Name",
        "owner": "Owner Name",
        "email": "contact@restaurant.com",
        "phone": "(555) 123-4567",
        "address": "123 Main St, City, State",
        "status": "active",
        "aiEnabled": true,
        "createdAt": "2025-03-01T00:00:00.000Z",
        "updatedAt": "2025-03-01T00:00:00.000Z"
      }
    ]
  }
}
```

### Get Restaurant by ID

```
GET /restaurants/:id
```

Returns a specific restaurant by ID.

**URL Parameters:**
- id: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "restaurant": {
      "id": "restaurant_id",
      "name": "Restaurant Name",
      "owner": "Owner Name",
      "email": "contact@restaurant.com",
      "phone": "(555) 123-4567",
      "address": "123 Main St, City, State",
      "status": "active",
      "aiEnabled": true,
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Create Restaurant

```
POST /restaurants
```

Creates a new restaurant.

**Request Body:**
```json
{
  "name": "Restaurant Name",
  "owner": "Owner Name",
  "email": "contact@restaurant.com",
  "phone": "(555) 123-4567",
  "address": "123 Main St, City, State",
  "password": "securePassword123", // Only required for RESTAURANT_OWNER creating their first restaurant
  "status": "active",
  "aiEnabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Restaurant created successfully",
  "data": {
    "restaurant": {
      "id": "restaurant_id",
      "name": "Restaurant Name",
      "owner": "Owner Name",
      "email": "contact@restaurant.com",
      "phone": "(555) 123-4567",
      "address": "123 Main St, City, State",
      "status": "active",
      "aiEnabled": true,
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Update Restaurant

```
PUT /restaurants/:id
```

Updates an existing restaurant.

**URL Parameters:**
- id: Restaurant ID

**Request Body:**
```json
{
  "name": "Updated Restaurant Name",
  "owner": "Updated Owner Name",
  "email": "updated@restaurant.com",
  "phone": "(555) 123-4567",
  "address": "123 Main St, City, State",
  "status": "active",
  "aiEnabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Restaurant updated successfully",
  "data": {
    "restaurant": {
      "id": "restaurant_id",
      "name": "Updated Restaurant Name",
      "owner": "Updated Owner Name",
      "email": "updated@restaurant.com",
      "phone": "(555) 123-4567",
      "address": "123 Main St, City, State",
      "status": "active",
      "aiEnabled": true,
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Delete Restaurant

```
DELETE /restaurants/:id
```

Deletes a restaurant. Admin only.

**URL Parameters:**
- id: Restaurant ID

**Response:**
```json
{
  "success": true,
  "message": "Restaurant deleted successfully"
}
```

---

## Agent Management

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

---

## Knowledge Base Management

### List Knowledge Base Items

```
GET /restaurants/:restaurantId/knowledge
```

Returns all knowledge base items for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "knowledge_items": [
      {
        "id": "kb_item_id",
        "restaurant_id": "restaurant_id",
        "elevenlabs_kb_id": "elevenlabs_kb_id",
        "name": "Menu Items",
        "type": "menu",
        "content": "Pizza Margherita: $14\nPizza Pepperoni: $16\n...",
        "created_at": "2025-03-01T00:00:00.000Z",
        "updated_at": "2025-03-01T00:00:00.000Z"
      },
      {
        "id": "kb_item_id",
        "restaurant_id": "restaurant_id",
        "elevenlabs_kb_id": "elevenlabs_kb_id",
        "name": "Restaurant Information",
        "type": "info",
        "content": "Our restaurant is located at 123 Main St...",
        "created_at": "2025-03-01T00:00:00.000Z",
        "updated_at": "2025-03-01T00:00:00.000Z"
      }
    ]
  }
}
```

### Get Knowledge Base Item

```
GET /restaurants/:restaurantId/knowledge/:kb_id
```

Returns a specific knowledge base item.

**URL Parameters:**
- restaurantId: Restaurant ID
- kb_id: Knowledge Base Item ID

**Response:**
```json
{
  "success": true,
  "data": {
    "knowledge_item": {
      "id": "kb_item_id",
      "restaurant_id": "restaurant_id",
      "elevenlabs_kb_id": "elevenlabs_kb_id",
      "name": "Menu Items",
      "type": "menu",
      "content": "Pizza Margherita: $14\nPizza Pepperoni: $16\n...",
      "created_at": "2025-03-01T00:00:00.000Z",
      "updated_at": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Add Knowledge Base Item

```
POST /restaurants/:restaurantId/knowledge
```

Adds a new knowledge base item.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "name": "Menu Items",
  "type": "menu",
  "content": "Pizza Margherita: $14\nPizza Pepperoni: $16\n..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base item added successfully",
  "data": {
    "knowledge_item": {
      "id": "kb_item_id",
      "restaurant_id": "restaurant_id",
      "elevenlabs_kb_id": "elevenlabs_kb_id",
      "name": "Menu Items",
      "type": "menu",
      "content": "Pizza Margherita: $14\nPizza Pepperoni: $16\n...",
      "created_at": "2025-03-01T00:00:00.000Z",
      "updated_at": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Update Knowledge Base Item

```
PUT /restaurants/:restaurantId/knowledge/:kb_id
```

Updates an existing knowledge base item.

**URL Parameters:**
- restaurantId: Restaurant ID
- kb_id: Knowledge Base Item ID

**Request Body:**
```json
{
  "name": "Updated Menu Items",
  "type": "menu",
  "content": "Pizza Margherita: $15\nPizza Pepperoni: $17\n..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base item updated successfully",
  "data": {
    "knowledge_item": {
      "id": "kb_item_id",
      "restaurant_id": "restaurant_id",
      "elevenlabs_kb_id": "elevenlabs_kb_id",
      "name": "Updated Menu Items",
      "type": "menu",
      "content": "Pizza Margherita: $15\nPizza Pepperoni: $17\n...",
      "created_at": "2025-03-01T00:00:00.000Z",
      "updated_at": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Delete Knowledge Base Item

```
DELETE /restaurants/:restaurantId/knowledge/:kb_id
```

Deletes a knowledge base item.

**URL Parameters:**
- restaurantId: Restaurant ID
- kb_id: Knowledge Base Item ID

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base item deleted successfully"
}
```

---

## Menu Management

Menu items are managed within the context of a specific restaurant.

### Get All Menu Items

```
GET /restaurants/:restaurantId/menu
```

Returns all menu items for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "menuItems": [
      {
        "id": "menu_item_id",
        "name": "Menu Item Name",
        "description": "Menu item description",
        "price": 9.99,
        "category": "Appetizers",
        "isAvailable": true,
        "order": 1,
        "createdAt": "2025-03-01T00:00:00.000Z",
        "updatedAt": "2025-03-01T00:00:00.000Z"
      }
    ]
  }
}
```

### Get Menu Item by ID

```
GET /restaurants/:restaurantId/menu/:id
```

Returns a specific menu item.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Menu Item ID

**Response:**
```json
{
  "success": true,
  "data": {
    "menuItem": {
      "id": "menu_item_id",
      "name": "Menu Item Name",
      "description": "Menu item description",
      "price": 9.99,
      "category": "Appetizers",
      "isAvailable": true,
      "order": 1,
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Create Menu Item

```
POST /restaurants/:restaurantId/menu
```

Creates a new menu item.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "name": "Menu Item Name",
  "description": "Menu item description",
  "price": 9.99,
  "category": "Appetizers",
  "isAvailable": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Menu item created successfully",
  "data": {
    "menuItem": {
      "id": "menu_item_id",
      "name": "Menu Item Name",
      "description": "Menu item description",
      "price": 9.99,
      "category": "Appetizers",
      "isAvailable": true,
      "order": 1,
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Update Menu Item

```
PUT /restaurants/:restaurantId/menu/:id
```

Updates an existing menu item.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Menu Item ID

**Request Body:**
```json
{
  "name": "Updated Menu Item",
  "description": "Updated description",
  "price": 10.99,
  "category": "Appetizers",
  "isAvailable": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Menu item updated successfully",
  "data": {
    "menuItem": {
      "id": "menu_item_id",
      "name": "Updated Menu Item",
      "description": "Updated description",
      "price": 10.99,
      "category": "Appetizers",
      "isAvailable": true,
      "order": 1,
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Delete Menu Item

```
DELETE /restaurants/:restaurantId/menu/:id
```

Deletes a menu item.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Menu Item ID

**Response:**
```json
{
  "success": true,
  "message": "Menu item deleted successfully"
}
```

### Reorder Menu Items

```
POST /restaurants/:restaurantId/menu/reorder
```

Updates the order of menu items.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "itemIds": ["menu_item_1_id", "menu_item_2_id", "menu_item_3_id"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Menu items reordered successfully"
}
```

---

## Settings Management

Restaurant settings are managed within the context of a specific restaurant.

### Get Restaurant Settings

```
GET /restaurants/:restaurantId/settings
```

Returns settings for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "settings": {
      "id": "settings_id",
      "callHoursStart": "09:00",
      "callHoursEnd": "21:00",
      "aiEnabled": true,
      "postCallMessage": "Thank you for calling! Your order will be ready in 20 minutes.",
      "cateringEnabled": true,
      "cateringMinNotice": 24,
      "cateringMessage": "We require 24 hours notice for catering orders.",
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Update Restaurant Settings

```
PUT /restaurants/:restaurantId/settings
```

Updates all settings for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "callHoursStart": "08:00",
  "callHoursEnd": "22:00",
  "aiEnabled": true,
  "postCallMessage": "Thank you for calling! Your order will be ready in 15 minutes.",
  "cateringEnabled": true,
  "cateringMinNotice": 48,
  "cateringMessage": "We require 48 hours notice for catering orders."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settings updated successfully",
  "data": {
    "settings": {
      "id": "settings_id",
      "callHoursStart": "08:00",
      "callHoursEnd": "22:00",
      "aiEnabled": true,
      "postCallMessage": "Thank you for calling! Your order will be ready in 15 minutes.",
      "cateringEnabled": true,
      "cateringMinNotice": 48,
      "cateringMessage": "We require 48 hours notice for catering orders.",
      "createdAt": "2025-03-01T00:00:00.000Z",
      "updatedAt": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Update Call Hours

```
PUT /restaurants/:restaurantId/settings/call-hours
```

Updates only the call hours settings.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "callHoursStart": "08:00",
  "callHoursEnd": "22:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Call hours updated successfully",
  "data": {
    "callHoursStart": "08:00",
    "callHoursEnd": "22:00"
  }
}
```

### Update AI Call Handling

```
PUT /restaurants/:restaurantId/settings/ai-call-handling
```

Updates only the AI call handling setting.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "aiEnabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "AI call handling updated successfully",
  "data": {
    "aiEnabled": true
  }
}
```

---

## Call Management

Call management endpoints are used to access call data and statistics.

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

---

## IVR Integration Points

This section outlines the integration points for IVR (Interactive Voice Response) systems to connect with Pulsara AI.

### Check Restaurant Configuration

IVR systems should check if a restaurant is configured to use AI call handling before processing a call.

```
GET /ivr/restaurant/:restaurantId/config
```

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

Send call data to the Pulsara AI system for processing.

```
POST /ivr/call
```

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

Notify the Pulsara AI system when a call is completed.

```
POST /ivr/call/:callId/complete
```

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
    "duration": 120
  }
}
```

---

## Database Schema

This section outlines the database schema required to support the API.

### Restaurants Table

```sql
CREATE TABLE restaurants (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  owner VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(20) NOT NULL,
  address TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  ai_enabled BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

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

### Knowledge Base Table

```sql
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  elevenlabs_kb_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Menu Items Table

```sql
CREATE TABLE menu_items (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10, 2) NOT NULL,
  category VARCHAR(100) NOT NULL,
  is_available BOOLEAN NOT NULL DEFAULT true,
  order_position INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Settings Table

```sql
CREATE TABLE settings (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  call_hours_start VARCHAR(5) NOT NULL DEFAULT '09:00',
  call_hours_end VARCHAR(5) NOT NULL DEFAULT '21:00',
  ai_enabled BOOLEAN NOT NULL DEFAULT true,
  post_call_message TEXT,
  catering_enabled BOOLEAN NOT NULL DEFAULT false,
  catering_min_notice INTEGER DEFAULT 24,
  catering_message TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

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

### Users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'RESTAURANT_OWNER',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Restaurant Users Table

```sql
CREATE TABLE restaurant_users (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL DEFAULT 'OWNER',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, restaurant_id)
);
```

### Email Templates Table

```sql
CREATE TABLE email_templates (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  template_type VARCHAR(50) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
