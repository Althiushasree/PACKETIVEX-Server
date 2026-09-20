"""
Google OAuth Authentication Module with Debug Logging
Validates Google ID tokens and checks domain authorization
"""

import os
import logging
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure debug logging
DEBUG_LOGGING = os.getenv("DEBUG_LOGGING", "true").lower() == "true"
logger = logging.getLogger(__name__)

if DEBUG_LOGGING:
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - [GOOGLE_AUTH] - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
else:
    logger.setLevel(logging.INFO)

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "cutmap.ac.in")

logger.debug(f"Google Auth Module Initialized - Domain: {ALLOWED_EMAIL_DOMAIN}")


def validate_google_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validates Google ID token and extracts user information.
    
    Args:
        token: Google ID token string
        
    Returns:
        Dict with user info (email, name, picture) if valid, None otherwise
    """
    logger.debug(f"Starting token validation (token length: {len(token)})")
    
    try:
        if not GOOGLE_CLIENT_ID:
            logger.error("GOOGLE_CLIENT_ID not configured in environment variables")
            return None
            
        logger.debug(f"Validating token against Google Client ID: {GOOGLE_CLIENT_ID[:10]}...")
        
        # Verify token signature with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        logger.debug(f"Token signature verified. Subject (user ID): {idinfo.get('sub', 'unknown')}")
        
        # Extract email and validate domain
        email = idinfo.get("email")
        logger.debug(f"Extracted email from token: {email}")
        
        if not email:
            logger.warning("Token does not contain email claim")
            return None
        
        # Check domain
        email_domain = email.split("@")[1] if "@" in email else None
        logger.debug(f"Email domain extracted: {email_domain}")
        
        if email_domain != ALLOWED_EMAIL_DOMAIN:
            logger.warning(
                f"Domain validation failed - Expected: {ALLOWED_EMAIL_DOMAIN}, "
                f"Got: {email_domain} for email: {email}"
            )
            return None
        
        logger.info(f"✓ Token validation successful for email: {email}")
        
        # Extract user info
        user_info = {
            "email": email,
            "name": idinfo.get("name", ""),
            "picture": idinfo.get("picture", ""),
            "email_verified": idinfo.get("email_verified", False),
            "sub": idinfo.get("sub")  # Google user ID
        }
        
        logger.debug(f"User info extracted: {user_info}")
        return user_info
        
    except ValueError as e:
        logger.error(f"Invalid token format or signature: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {type(e).__name__} - {str(e)}")
        return None


def validate_email_domain(email: str) -> bool:
    """
    Validates if email belongs to allowed domain.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email domain matches allowed domain, False otherwise
    """
    logger.debug(f"Validating email domain: {email}")
    
    if "@" not in email:
        logger.warning(f"Invalid email format: {email}")
        return False
    
    email_domain = email.split("@")[1]
    is_valid = email_domain == ALLOWED_EMAIL_DOMAIN
    
    if is_valid:
        logger.debug(f"✓ Email domain validation passed for: {email}")
    else:
        logger.warning(
            f"Email domain validation failed for: {email} "
            f"(domain: {email_domain}, allowed: {ALLOWED_EMAIL_DOMAIN})"
        )
    
    return is_valid
