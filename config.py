"""
Configuration module for Pulsara IVR v2.
Centralizes all configuration settings and environment variables.
"""

import os
import pytz
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

# Time Zone Configuration
TIMEZONE = pytz.timezone('America/Chicago')  # CST

# Voice Configuration
VOICE_ID = "tnSpp4vdxKPjI9w0GnoV"  # Default voice ID

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Menu Database - Will be implemented in v2
MENU_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "menu.json")
