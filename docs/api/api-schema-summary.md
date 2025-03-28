# Pulsara Dashboard API Schema Summary

This document provides a summary of the API schema for the Pulsara Dashboard, explaining the purpose and relationships between the different components.

## Overview

The Pulsara Dashboard API is designed to support a multi-restaurant IVR system that uses ElevenLabs AI agents to handle phone calls. The API is organized into several interconnected components, each serving a specific purpose in the overall system.

## Components

### 1. Authentication API

**Purpose**: Handles user authentication and authorization.

**Key Features**:
- JWT-based authentication
- Role-based access control (Admin vs Restaurant Owner)
- User registration and profile management

**Why It Matters**: Security is critical for a multi-tenant system where restaurant owners should only see their own data while admins need global access.

### 2. Restaurant Management API

**Purpose**: Manages restaurant profiles and basic information.

**Key Features**:
- CRUD operations for restaurant profiles
- Restaurant listing with pagination and filtering
- Owner-specific restaurant views

**Why It Matters**: Restaurants are the core entity that everything else relates to in the system. Each restaurant needs its own profile and configuration.

### 3. Agent Management API

**Purpose**: Configures and manages AI agents for each restaurant.

**Key Features**:
- Agent configuration per restaurant
- System prompt management with restaurant-specific variables
- Tool configuration (end_call, get_address, forward_call)
- Agent testing interface

**Why It Matters**: Each restaurant needs its own AI agent with custom configuration tailored to its specific details, such as name, hours, and menu items.

### 4. Knowledge Base API

**Purpose**: Manages restaurant-specific knowledge that the AI agent can access during calls.

**Key Features**:
- CRUD operations for knowledge base items
- Support for different knowledge types (menu, hours, policies)
- ElevenLabs knowledge base integration

**Why It Matters**: Agents need restaurant-specific knowledge to answer questions accurately. Different types of knowledge need different handling.

### 5. Menu Management API

**Purpose**: Manages restaurant menu items.

**Key Features**:
- CRUD operations for menu items
- Category management
- Item availability toggling
- Menu item ordering

**Why It Matters**: Menu information is critical for restaurant phone calls and needs to be easily updatable as menus change frequently.

### 6. Settings Management API

**Purpose**: Configures restaurant-specific settings.

**Key Features**:
- Call hours management
- AI call handling toggle
- Catering settings
- Post-call message configuration

**Why It Matters**: Each restaurant has different operating hours and policies that the AI needs to follow.

### 7. Call Management API

**Purpose**: Records, retrieves, and analyzes phone calls.

**Key Features**:
- Call history with filtering and pagination
- Call detail view with transcript and sentiment
- Call statistics and analytics
- Email summary functionality

**Why It Matters**: Call history provides valuable business intelligence, and transcripts help restaurant owners review conversations.

### 8. Email Notification API

**Purpose**: Manages and sends email notifications.

**Key Features**:
- Email template management
- Call summary emails
- Recipient management
- Attachment options (audio, transcript)

**Why It Matters**: Every time a call ends, we need to notify the restaurant owner with the transcript and other relevant information.

### 9. IVR Integration API

**Purpose**: Provides integration points for IVR systems.

**Key Features**:
- Restaurant configuration endpoint
- Call processing endpoint
- Call completion logging
- Authentication for external IVR systems

**Why It Matters**: The IVR system needs to know which restaurant is being called and needs to log call data in the dashboard.

## Relationships Between Components

1. **Restaurant → Agent**: Each restaurant has one agent configuration.
2. **Restaurant → Knowledge Base**: Each restaurant has multiple knowledge base items.
3. **Restaurant → Menu**: Each restaurant has multiple menu items.
4. **Restaurant → Settings**: Each restaurant has one settings configuration.
5. **Restaurant → Calls**: Each restaurant has multiple call records.
6. **Restaurant → Email Templates**: Each restaurant has multiple email templates.
7. **Calls → Email Notifications**: Call completion triggers email notifications.
8. **Menu → Knowledge Base**: Menu items feed into the knowledge base.
9. **Settings → Agent**: Settings affect agent behavior.
10. **IVR → All Components**: IVR system interacts with all components through the integration API.

## Implementation Considerations

1. **Database Design**: The database schema should reflect these relationships with appropriate foreign keys and constraints.
2. **API Versioning**: As the system evolves, API versioning will be important to maintain backward compatibility.
3. **Authentication**: All endpoints should require authentication, with appropriate role-based access control.
4. **Rate Limiting**: API endpoints should be rate-limited to prevent abuse.
5. **Error Handling**: Consistent error handling across all endpoints is essential.
6. **Documentation**: Comprehensive API documentation is crucial for developers.
7. **Testing**: Thorough testing of all endpoints is necessary to ensure reliability.

## Conclusion

The Pulsara Dashboard API provides a comprehensive set of endpoints to support a multi-restaurant IVR system. By organizing the API into these logical components, we ensure a clean separation of concerns and make the system easier to maintain and extend.
