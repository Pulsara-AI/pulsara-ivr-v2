# Menu Management API Schema

## Overview

The Menu Management API handles the creation, retrieval, updating, and deletion of menu items for restaurants in the Pulsara system.

## Requirements

- CRUD operations for menu items
- Category management
- Item availability toggling
- Menu item ordering

## Why This Matters

- **Core Information**: Menu is critical information for restaurant phone calls
- **Frequent Updates**: Menus change frequently and need easy updates
- **Organization**: Categories help organize large menus
- **Presentation**: Item ordering affects how information is presented to callers
- **Knowledge Base Integration**: Menu items feed into the AI agent's knowledge base

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

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

## Database Schema

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

## Implementation Notes

1. Menu updates should automatically trigger knowledge base updates
2. Categories should be consistent across a restaurant's menu
3. Price formatting should follow restaurant's locale settings
4. Menu item ordering should be maintained within categories
5. Menu items should be validated for required fields
6. Menu items should support images in future iterations
