"""
Configuration module for Pulsara IVR v2.
Centralizes all configuration settings.
"""

import os
import pytz
from config.environment import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_AGENT_ID,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    RESTAURANT_OWNER_PHONE,
    RESTAURANT_ADDRESS,
    RESTAURANT_NAME,
    HOST,
    PORT,
    LOG_LEVEL
)

# Time Zone Configuration
TIMEZONE = pytz.timezone('America/Chicago')  # CST

# Voice Configuration
VOICE_ID = "tnSpp4vdxKPjI9w0GnoV"  # Default voice ID

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Data Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MENU_DB_PATH = os.path.join(DATA_DIR, "menu.json")

# API Configuration
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Restaurant Configuration
RESTAURANT = {
    "name": RESTAURANT_NAME,
    "address": RESTAURANT_ADDRESS,
    "phone": RESTAURANT_OWNER_PHONE,
    "timezone": TIMEZONE,
}

# Agent Configuration
AGENT = {
    "voice_id": VOICE_ID,
    "elevenlabs_agent_id": ELEVENLABS_AGENT_ID,
}

# Server Configuration
SERVER = {
    "host": HOST,
    "port": PORT,
}
