# Settings API Schema

## Overview

The Settings API handles the configuration of restaurant-specific settings in the Pulsara system.

## Requirements

- Call hours management
- AI call handling toggle
- Catering settings
- Post-call message configuration

## Why This Matters

- **Operational Control**: Restaurants have different operating hours
- **AI Flexibility**: Some restaurants may want to disable AI at certain times
- **Special Services**: Catering requires special handling and advance notice
- **Customer Experience**: Post-call messages can be customized per restaurant
- **Business Rules**: Each restaurant has unique policies that the AI needs to follow

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

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

## Database Schema

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

## Implementation Notes

1. Settings should be created automatically when a restaurant is created
2. Call hours should be validated for proper time format
3. Call hours should be stored in the restaurant's local timezone
4. Settings updates should trigger agent configuration updates
5. AI call handling toggle should affect the IVR system's behavior immediately
6. Post-call messages should be kept concise for better user experience
