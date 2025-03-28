# Authentication API Schema

## Overview

The Authentication API handles user registration, login, token management, and profile access for the Pulsara Dashboard.

## Requirements

- User registration and login functionality
- Token-based authentication with JWT
- Role-based access control (Admin vs Restaurant Owner)
- Profile management
- Token refresh mechanism

## Why This Matters

- **Security**: A multi-restaurant system requires robust authentication to protect sensitive data
- **Access Control**: Different user roles need different access levels
- **Data Isolation**: Restaurant owners should only see their own data
- **Administration**: Admins need global access to manage all restaurants
- **User Experience**: Seamless authentication improves dashboard usability

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Authentication Header

Include the JWT token in the request header:

```
Authorization: Bearer {your_access_token}
```

## Endpoints

### Register User

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

### Login

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

### Refresh Token

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

### Get User Profile

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

## Database Schema

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

## Implementation Notes

1. Access tokens should expire after a reasonable time (e.g., 1 hour)
2. Refresh tokens should have a longer lifespan (e.g., 7 days)
3. Password hashing must use a strong algorithm (bcrypt recommended)
4. Admin role creation should be restricted to existing admins
5. Email verification should be implemented for production
