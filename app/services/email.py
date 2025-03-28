"""
Email notification service for Pulsara IVR v2.
"""

from typing import Dict, Any, Optional, List
from app.utils.logging import get_logger
from app.models.schemas import Call
from app.core.restaurant import get_restaurant_by_id

logger = get_logger(__name__)

def send_email(to_email: str, subject: str, body: str, attachments: List[Dict[str, Any]] = None) -> bool:
    """
    Send an email.
    
    Args:
        to_email: The recipient email address
        subject: The email subject
        body: The email body
        attachments: A list of attachments (optional)
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    # In a real implementation, this would use an email service like SendGrid or SMTP
    # For now, we'll just log the email
    logger.info(f"Sending email to {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {body}")
    
    if attachments:
        logger.info(f"Attachments: {attachments}")
    
    # Mock successful email sending
    return True

def send_call_summary_email(call: Call) -> bool:
    """
    Send a call summary email.
    
    Args:
        call: The call to summarize
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(call.restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {call.restaurant_id}")
        return False
    
    # Get the restaurant owner's email
    # In a real implementation, this would be stored in the restaurant settings
    to_email = "owner@example.com"
    
    # Format the call duration
    duration_minutes = call.duration // 60 if call.duration else 0
    duration_seconds = call.duration % 60 if call.duration else 0
    duration_str = f"{duration_minutes}m {duration_seconds}s"
    
    # Create the email subject
    subject = f"Call Summary - {call.caller_number} - {duration_str}"
    
    # Create the email body
    body = f"""
    Call Summary
    ============
    
    Restaurant: {restaurant.name}
    Caller: {call.caller_number}
    Time: {call.start_time.strftime('%Y-%m-%d %H:%M:%S')}
    Duration: {duration_str}
    
    """
    
    # Add forwarding information if applicable
    if call.forwarded:
        body += f"Forwarded: Yes, to {call.forwarded_to}\n"
    else:
        body += "Forwarded: No\n"
    
    # Add transcript if available
    if call.transcript:
        body += f"\nTranscript:\n{call.transcript}\n"
    
    # Add summary if available
    if call.summary:
        body += f"\nSummary:\n{call.summary}\n"
    
    # Add sentiment if available
    if call.sentiment_label:
        body += f"\nSentiment: {call.sentiment_label.capitalize()}"
        if call.sentiment_score is not None:
            body += f" ({call.sentiment_score})"
        body += "\n"
    
    # Add reason if available
    if call.reason:
        body += f"\nReason for Call: {call.reason}\n"
    
    # Add audio link if available
    attachments = None
    if call.audio_url:
        body += f"\nAudio Recording: {call.audio_url}\n"
        attachments = [
            {
                "filename": f"call_{call.id}.mp3",
                "url": call.audio_url
            }
        ]
    
    # Send the email
    return send_email(to_email, subject, body, attachments)

def send_daily_summary_email(restaurant_id: str) -> bool:
    """
    Send a daily summary email.
    
    Args:
        restaurant_id: The restaurant ID
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    # Get the restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"Restaurant not found for ID: {restaurant_id}")
        return False
    
    # Get the restaurant owner's email
    # In a real implementation, this would be stored in the restaurant settings
    to_email = "owner@example.com"
    
    # Get call statistics
    from app.core.call import get_call_statistics
    stats = get_call_statistics(restaurant_id, days=1)
    
    # Create the email subject
    from app.utils.helpers import get_current_time
    date_str = get_current_time().strftime('%Y-%m-%d')
    subject = f"Daily Call Summary - {restaurant.name} - {date_str}"
    
    # Create the email body
    body = f"""
    Daily Call Summary for {restaurant.name}
    =====================================
    
    Date: {date_str}
    
    Total Calls: {stats['totalCalls']}
    AI Handled: {stats['aiHandled']}
    Forwarded: {stats['forwarded']}
    Average Duration: {int(stats['avgDuration'] // 60)}m {int(stats['avgDuration'] % 60)}s
    
    Sentiment Breakdown:
    - Positive: {stats['sentimentBreakdown']['positive']}
    - Neutral: {stats['sentimentBreakdown']['neutral']}
    - Negative: {stats['sentimentBreakdown']['negative']}
    
    """
    
    # Add call reasons if available
    if stats['callReasons']:
        body += "Call Reasons:\n"
        for reason, count in stats['callReasons'].items():
            body += f"- {reason}: {count}\n"
    
    # Send the email
    return send_email(to_email, subject, body)
