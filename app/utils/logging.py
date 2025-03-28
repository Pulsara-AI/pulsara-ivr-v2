"""
Logging configuration module for Pulsara IVR v2.
"""

import logging
from config.settings import LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """
    Set up logging with proper log levels and format.
    """
    # Set up root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )
    
    # Get the root logger
    logger = logging.getLogger()
    
    # Set individual logger levels to control verbosity
    # Keep twilio-related logs at INFO level
    logging.getLogger("twilio").setLevel(logging.INFO)
    # Set our message handling logs to a higher level to reduce noise
    logging.getLogger("twilio_audio_interface").setLevel(logging.INFO)
    
    return logger

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
