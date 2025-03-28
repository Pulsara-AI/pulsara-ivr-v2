# Knowledge Base API Schema

## Overview

The Knowledge Base API handles the management of restaurant-specific knowledge that the AI agent can access during calls.

## Requirements

- CRUD operations for knowledge base items
- Support for different knowledge types (menu, hours, policies)
- Content management for each knowledge item
- ElevenLabs knowledge base integration

## Why This Matters

- **Accurate Responses**: Agents need restaurant-specific knowledge to answer questions accurately
- **Specialized Knowledge**: Different types of knowledge need different handling
- **Easy Updates**: Restaurant owners need to easily update their information
- **AI Integration**: Knowledge must be synced with ElevenLabs for agent access
- **Contextual Awareness**: The agent needs to know about specials, policies, and other restaurant-specific details

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

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

## Database Schema

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

## Implementation Notes

1. Knowledge base items should be automatically synced with ElevenLabs
2. Content updates should trigger reindexing in the ElevenLabs knowledge base
3. Different knowledge types may require different formatting
4. Menu items should be automatically extracted from the restaurant's menu
5. Knowledge base items should be validated for required fields
6. Large knowledge base items may need to be chunked for optimal AI retrieval
