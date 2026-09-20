import os
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

API_KEY_ENV = os.getenv("API_KEY", "nt04-network-admin-secret-token")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

logger = logging.getLogger(__name__)


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if not x_api_key or x_api_key.strip() != API_KEY_ENV.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header"
        )
    return x_api_key


def generate_jwt_token(email: str, expires_delta: int = 24) -> str:
    """
    Generate JWT token for authenticated user.
    
    Args:
        email: User email
        expires_delta: Token expiration time in hours (default 24)
        
    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + timedelta(hours=expires_delta)
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"JWT token generated for user: {email}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error generating JWT token: {str(e)}")
        raise


def verify_jwt_token(token: str) -> str:
    """
    Verify JWT token and return email.
    
    Args:
        token: JWT token string
        
    Returns:
        Email from token
        
    Raises:
        HTTPException if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        logger.debug(f"JWT token verified for user: {email}")
        return email
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
