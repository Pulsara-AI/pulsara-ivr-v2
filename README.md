# Pulsara IVR v2

Pulsara IVR v2 is an enterprise-grade Interactive Voice Response (IVR) system designed for restaurants. It uses ElevenLabs' conversational AI to handle incoming calls, take reservations, answer questions, and forward calls to restaurant staff when necessary.

## Features

- **Multi-Restaurant Support**: Configurable for multiple restaurants with unique settings
- **AI-Powered Conversations**: Natural language processing using ElevenLabs' conversational AI
- **Call Forwarding**: Intelligent call forwarding to restaurant staff when needed
- **Knowledge Base Integration**: Restaurant-specific knowledge bases for accurate responses
- **Call Analytics**: Detailed call statistics and sentiment analysis
- **Dashboard Integration**: API integration with the Pulsara Dashboard

## Architecture

The application follows a modular, layered architecture:

- **API Layer**: FastAPI routes for handling HTTP and WebSocket requests
- **Core Layer**: Business logic for restaurants, agents, calls, and knowledge bases
- **Service Layer**: Integration with external services like Twilio and ElevenLabs
- **Data Layer**: In-memory data storage (will be replaced with a database in the future)

## Directory Structure

```
pulsara-ivr/
├── app/                      # Application code
│   ├── api/                  # API endpoints
│   ├── core/                 # Core business logic
│   ├── services/             # External service integrations
│   ├── models/               # Data models
│   └── utils/                # Utility functions
├── config/                   # Configuration
├── docs/                     # Documentation
├── tests/                    # Tests
├── scripts/                  # Utility scripts
├── .env.example              # Example environment variables
├── .gitignore
├── main.py                   # Application entry point
├── README.md
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Twilio account with a phone number
- ElevenLabs account with an agent

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pulsara/ivr-v2.git
   cd ivr-v2
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_AGENT_ID=your_elevenlabs_agent_id
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   RESTAURANT_OWNER_PHONE=restaurant_owner_phone_number
   ```

### Running the Application

1. Start the application:
   ```bash
   ./run_app.sh
   ```

2. Expose the application to the internet (for Twilio webhooks):
   ```bash
   ./run_ngrok.sh
   ```

3. Configure your Twilio phone number to use the ngrok URL as the webhook for incoming calls:
   ```
   https://your-ngrok-url/api/v1/calls/inbound_call
   ```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 style guidelines.

## License

Proprietary - All rights reserved.

## Contact

For support or inquiries, please contact support@pulsara.ai.
