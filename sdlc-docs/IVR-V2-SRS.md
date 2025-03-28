# Pulsara IVR v2 - Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose
The purpose of Pulsara IVR v2 is to provide a **scalable, automated phone system** for restaurants that supports **dynamic call forwarding** while allowing for future feature expansion such as analytics, email notifications, and a web portal.

### 1.2 Scope
Pulsara IVR v2 will:
- **Receive and handle customer calls** via Twilio
- **Identify the restaurant dynamically** from the database
- **Forward the call to the restaurant’s main phone line**
- **Log call details** for future analytics

### 1.3 Intended Users
- **Restaurant Owners** → Receive automated call handling and forwarding.
- **Restaurant Staff** → Answer AI-filtered calls with pre-screened customer requests.
- **Developers** → Maintain and extend the system with new features.

---

## 2. System Architecture

### 2.1 High-Level Architecture
   +--------------+       +-------------+       +------------+
   |   Twilio     | ----> |  Pulsara API | ----> |  Database  |
   +--------------+       +-------------+       +------------+
          |                     |
          |                     |
          |                     V
          |              +------------------+
          |              |  ElevenLabs AI   |
          |              +------------------+
          |                     |
          |                     V
          |              +------------------+
          |              |   Call Logging   |
          |              +------------------+
### 2.2 Components

#### **Twilio (Telephony Layer)**
- Handles **incoming calls** and **forwards audio** to the Pulsara API.
- Connects **Twilio Media Streams** for real-time voice processing.

#### **Pulsara API (Middleware Layer)**
- Handles **all call logic** and **data retrieval**.
- Dynamically determines **which restaurant is being called**.
- Decides **whether to forward** the call or let AI handle it.

#### **Database (Storage Layer)**
- Stores **restaurant profiles** including:
  - **Twilio number**
  - **Forwarding number**
  - **Business hours**
  - **Call logs**

#### **ElevenLabs (AI Processing Layer)**
- Processes **real-time speech interactions**.
- Can respond to FAQs or **invoke call forwarding tools**.

---

## 3. Functional Requirements

### 3.1 Call Handling

#### **3.1.1 Inbound Call Processing**
**Description:** Handles **incoming Twilio calls** and routes them properly.

**Trigger:** Customer dials a restaurant’s number.

**Flow:**
1. Twilio **receives the call** and forwards it to the Pulsara API.
2. Pulsara API **identifies the restaurant** using the database.
3. API determines **whether to forward the call or let AI handle it**.

**API Endpoint:**
Post /twilio/inbound_call
**Request:**
```json
{
  "CallSid": "CA1234567890abcdef",
  "From": "+15551234567",
  "To": "+15557654321"
}
Response (TwiML):
<Response>
    <Connect>
        <Stream url="wss://your-server.example.com/media-stream">
            <Parameter name="restaurant_id" value="d34db33f"/>
        </Stream>
    </Connect>
</Response>

3.2 Call Forwarding

3.2.1 Forwarding to Restaurant

Description: If AI determines a human is needed, the call is forwarded.

Trigger: AI decides human intervention is required.

Flow:
	1.	AI calls the /api/tools/forward_call endpoint.
	2.	API retrieves restaurant’s forwarding number from the database.
	3.	API updates Twilio to redirect the call to the restaurant.

API Endpoint:
POST /api/tools/forward_call

Request:
{
  "restaurant_id": "d34db33f"
}

Response:
{
  "status": "success",
  "message": "Call forwarded to +15557654321"
}
3.3 Call Logging

3.3.1 Store Call Details

Description: Logs basic call details for analytics.

Trigger: Every time a call is received or forwarded.

Flow:
	1.	API records call start time, duration, and caller number.
	2.	If AI was used, logs AI interaction data.
	3.	If forwarded, logs whether the call was answered.

API Endpoint:
POST /api/logs/store_call
Request:
{
  "restaurant_id": "d34db33f",
  "caller_number": "+15551234567",
  "call_duration": 120,
  "forwarding_status": "Forwarded"
}
4. Non-Functional Requirements

4.1 Performance Requirements
	•	API response time: <1 second for Twilio call handling.
	•	AI response time: <2 seconds for generating speech.
	•	Call forwarding delay: <3 seconds from request to execution.

4.2 Security & Authentication
	•	Database connections must be encrypted (SSL/TLS).
	•	Twilio webhook validation required to prevent spoofing.
	•	API keys required for any administrative actions.

4.3 Scalability Considerations
	•	Must support multiple restaurants dynamically.
	•	API must handle high concurrent call volumes without degradation.

⸻

5. Current Limitations & Future Enhancements

5.1 Limitations
	•	No customer recognition (calls are treated as first-time).
	•	No menu lookups or ordering integration.
	•	No analytics dashboard yet.

5.2 Future Enhancements
	•	Email notifications for every call.
	•	Restaurant self-serve portal to manage call settings.
	•	Advanced AI conversation features (handling more customer inquiries).

⸻

6. Deployment Considerations

6.1 Infrastructure
	•	Backend: FastAPI (Python) running on AWS/GCP.
	•	Database: PostgreSQL or Firebase for scalability.
	•	Logging & Monitoring: CloudWatch/Prometheus for API health.

6.2 Deployment Pipeline
	•	Staging Environment for testing new features.
	•	CI/CD Pipeline for automatic API updates.
	•	Automated failover setup for Twilio call handling.

⸻

7. Summary

Why IVR v2?
	•	Scalable multi-restaurant support (no hardcoded values).
	•	Automated call forwarding with logging.
	•	Clean API architecture with room for future growth.

Immediate Next Steps

1️⃣ Set up database schema for restaurant profiles.
2️⃣ Modify Twilio webhook to retrieve restaurant settings dynamically.
3️⃣ Implement basic call forwarding & logging.
4️⃣ Test scalability & error handling before future features.

