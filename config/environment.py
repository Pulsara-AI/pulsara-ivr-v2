"""
Environment configuration module for Pulsara IVR v2.
Centralizes all environment variables loading.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Restaurant Information
RESTAURANT_OWNER_PHONE = os.getenv("RESTAURANT_OWNER_PHONE", "224-651-4178")
RESTAURANT_ADDRESS = os.getenv("RESTAURANT_ADDRESS", "1509 W Taylor St, Chicago, IL 60607")
RESTAURANT_NAME = os.getenv("RESTAURANT_NAME", "Pulsara Restaurant")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
