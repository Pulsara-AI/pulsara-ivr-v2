"""
Helper utilities for Pulsara IVR v2.
"""

import json
import uuid
from datetime import datetime
import pytz
from config.settings import TIMEZONE

def generate_connection_id():
    """
    Generate a unique connection ID for tracking calls.
    
    Returns:
        A short unique ID string
    """
    return str(uuid.uuid4())[:8]  # Use shorter ID for logging

def get_current_time():
    """
    Get the current time in the configured timezone.
    
    Returns:
        A datetime object in the configured timezone
    """
    return datetime.now(TIMEZONE)

def get_formatted_time(format_string='%I:%M %p'):
    """
    Get the current time formatted as a string.
    
    Args:
        format_string: The format string to use
        
    Returns:
        A formatted time string
    """
    return get_current_time().strftime(format_string)

def safe_json_loads(json_string, default=None):
    """
    Safely load a JSON string, returning a default value if parsing fails.
    
    Args:
        json_string: The JSON string to parse
        default: The default value to return if parsing fails
        
    Returns:
        The parsed JSON object or the default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}

def safe_json_dumps(obj, default=None):
    """
    Safely dump an object to a JSON string, returning a default value if serialization fails.
    
    Args:
        obj: The object to serialize
        default: The default value to return if serialization fails
        
    Returns:
        A JSON string or the default value
    """
    try:
        return json.dumps(obj)
    except (TypeError, OverflowError):
        return default if default is not None else "{}"
