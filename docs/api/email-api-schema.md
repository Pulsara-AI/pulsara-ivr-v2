# Email Notification API Schema

## Overview

The Email Notification API handles the management and sending of email notifications in the Pulsara system.

## Requirements

- Email template management
- Call summary emails
- Recipient management
- Attachment options (audio, transcript)

## Why This Matters

- **Immediate Notification**: Every time a call ends, we need to notify the restaurant owner
- **Complete Context**: Transcripts provide full context of the conversation
- **Quality Assurance**: Audio recordings may be needed for training or quality control
- **Customization**: Different restaurants may need different email templates
- **Priority Handling**: Some calls may need immediate attention (negative sentiment, specific requests)

## Base URL

```
https://api.pulsara.ai/v1
```

For local development:
```
http://localhost:5000/api
```

## Endpoints

### Get Email Templates

```
GET /restaurants/:restaurantId/email-templates
```

Returns all email templates for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "template_id",
        "restaurant_id": "restaurant_id",
        "template_type": "call_summary",
        "subject": "Call Summary - {{call_date}}",
        "body": "Dear {{recipient_name}},\n\nA call was received at {{call_time}}.\n\nSummary: {{call_summary}}\n\nSentiment: {{sentiment}}\n\n{{#if include_transcript}}Transcript: {{transcript}}{{/if}}\n\nRegards,\nPulsara AI",
        "created_at": "2025-03-01T00:00:00.000Z",
        "updated_at": "2025-03-01T00:00:00.000Z"
      }
    ]
  }
}
```

### Get Email Template by ID

```
GET /restaurants/:restaurantId/email-templates/:id
```

Returns a specific email template.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Email Template ID

**Response:**
```json
{
  "success": true,
  "data": {
    "template": {
      "id": "template_id",
      "restaurant_id": "restaurant_id",
      "template_type": "call_summary",
      "subject": "Call Summary - {{call_date}}",
      "body": "Dear {{recipient_name}},\n\nA call was received at {{call_time}}.\n\nSummary: {{call_summary}}\n\nSentiment: {{sentiment}}\n\n{{#if include_transcript}}Transcript: {{transcript}}{{/if}}\n\nRegards,\nPulsara AI",
      "created_at": "2025-03-01T00:00:00.000Z",
      "updated_at": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Create Email Template

```
POST /restaurants/:restaurantId/email-templates
```

Creates a new email template.

**URL Parameters:**
- restaurantId: Restaurant ID

**Request Body:**
```json
{
  "template_type": "call_summary",
  "subject": "Call Summary - {{call_date}}",
  "body": "Dear {{recipient_name}},\n\nA call was received at {{call_time}}.\n\nSummary: {{call_summary}}\n\nSentiment: {{sentiment}}\n\n{{#if include_transcript}}Transcript: {{transcript}}{{/if}}\n\nRegards,\nPulsara AI"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email template created successfully",
  "data": {
    "template": {
      "id": "template_id",
      "restaurant_id": "restaurant_id",
      "template_type": "call_summary",
      "subject": "Call Summary - {{call_date}}",
      "body": "Dear {{recipient_name}},\n\nA call was received at {{call_time}}.\n\nSummary: {{call_summary}}\n\nSentiment: {{sentiment}}\n\n{{#if include_transcript}}Transcript: {{transcript}}{{/if}}\n\nRegards,\nPulsara AI",
      "created_at": "2025-03-01T00:00:00.000Z",
      "updated_at": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Update Email Template

```
PUT /restaurants/:restaurantId/email-templates/:id
```

Updates an existing email template.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Email Template ID

**Request Body:**
```json
{
  "subject": "Updated Call Summary - {{call_date}}",
  "body": "Dear {{recipient_name}},\n\nA call was received at {{call_time}}.\n\nSummary: {{call_summary}}\n\nSentiment: {{sentiment}}\n\n{{#if include_transcript}}Transcript: {{transcript}}{{/if}}\n\nThank you,\nPulsara AI"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email template updated successfully",
  "data": {
    "template": {
      "id": "template_id",
      "restaurant_id": "restaurant_id",
      "template_type": "call_summary",
      "subject": "Updated Call Summary - {{call_date}}",
      "body": "Dear {{recipient_name}},\n\nA call was received at {{call_time}}.\n\nSummary: {{call_summary}}\n\nSentiment: {{sentiment}}\n\n{{#if include_transcript}}Transcript: {{transcript}}{{/if}}\n\nThank you,\nPulsara AI",
      "created_at": "2025-03-01T00:00:00.000Z",
      "updated_at": "2025-03-01T00:00:00.000Z"
    }
  }
}
```

### Delete Email Template

```
DELETE /restaurants/:restaurantId/email-templates/:id
```

Deletes an email template.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Email Template ID

**Response:**
```json
{
  "success": true,
  "message": "Email template deleted successfully"
}
```

### Get Email Recipients

```
GET /restaurants/:restaurantId/email-recipients
```

Returns all email recipients for a restaurant.

**URL Parameters:**
- restaurantId: Restaurant ID

**Response:**
```json
{
  "success": true,
  "data": {
    "recipients": [
      {
        "id": "recipient_id",
        "restaurant_id": "restaurant_id",
        "name": "John Doe",
        "email": "john@example.com",
        "role": "Owner",
        "notification_types": ["call_summary", "negative_sentiment"],
        "created_at": "2025-03-01T00:00:00.000Z",
        "updated_at": "2025-03-01T00:00:00.000Z"
      }
    ]
  }
}
```

### Send Test Email

```
POST /restaurants/:restaurantId/email-templates/:id/test
```

Sends a test email using the specified template.

**URL Parameters:**
- restaurantId: Restaurant ID
- id: Email Template ID

**Request Body:**
```json
{
  "recipient": "test@example.com",
  "test_data": {
    "call_date": "March 18, 2025",
    "call_time": "3:30 PM",
    "call_summary": "Customer inquired about business hours",
    "sentiment": "Positive",
    "transcript": "Sample transcript for testing purposes"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test email sent successfully",
  "data": {
    "sentTo": "test@example.com",
    "sentAt": "2025-03-01T12:45:00.000Z"
  }
}
```

## Database Schema

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

### Email Recipients Table

```sql
CREATE TABLE email_recipients (
  id UUID PRIMARY KEY,
  restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  role VARCHAR(50),
  notification_types JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Notes

1. Email templates should support variable substitution using handlebars syntax
2. Email sending should be handled asynchronously to prevent blocking
3. Email templates should be created automatically when a restaurant is created
4. Email recipients should be validated for proper email format
5. Email sending should be rate-limited to prevent abuse
6. Email templates should support HTML formatting
7. Automatic emails should be triggered by call completion events
8. Email attachments (audio, transcript) should be securely stored and accessible only to authorized recipients
