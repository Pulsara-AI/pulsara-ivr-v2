# Restaurant Management API Schema

## Overview

The Restaurant Management API handles the creation, retrieval, updating, and deletion of restaurant profiles in the Pulsara system.

## Requirements

- CRUD operations for restaurant profiles
- Restaurant listing with pagination and filtering
- Restaurant-specific settings management
- Owner-specific restaurant views
- Admin-only global restaurant management

## Why This Matters

- **Core Entity**: Restaurants are the fundamental entity that everything else relates to
- **Multi-tenant Architecture**: System must scale to support multiple restaurants
- **Data Isolation**: Each restaurant needs its own profile and configuration
- **Access Control**: Admins need to manage all restaurants while owners only see their own
- **Business Operations**: Restaurant details are essential for the AI agent to function correctly

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

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

## Database Schema

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

## Implementation Notes

1. Restaurant creation should automatically create default settings
2. Restaurant deletion should be a soft delete in production
3. Restaurant email must be unique across the system
4. Restaurant owners should only be able to access their own restaurants
5. Admin users should have access to all restaurants
6. Restaurant phone numbers should be used for IVR system identification
