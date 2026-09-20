"""
Centralized Logging Configuration with Debug Support
Provides structured logging without disrupting functionality
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Load from environment
DEBUG_LOGGING = os.getenv("DEBUG_LOGGING", "true").lower() == "true"


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(name: str = __name__, level: Optional[str] = None) -> logging.Logger:
    """
    Setup application-wide logging with debug support.
    
    Args:
        name: Logger name (usually __name__)
        level: Override logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Determine logging level
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    elif DEBUG_LOGGING:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter with timestamp
    formatter = ColoredFormatter(
        '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Log startup info
    if DEBUG_LOGGING and log_level == logging.DEBUG:
        logger.debug(f"✓ Debug logging enabled for module: {name}")
        logger.debug(f"Log level: {logging.getLevelName(log_level)}")
    
    return logger


def log_request_info(logger: logging.Logger, endpoint: str, method: str, **kwargs):
    """
    Log incoming request information for debugging.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint
        method: HTTP method (GET, POST, etc)
        **kwargs: Additional info to log (user_email, session_id, etc)
    """
    if DEBUG_LOGGING:
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.debug(f"[REQUEST] {method} {endpoint} | {extra_info if extra_info else 'no params'}")


def log_response_info(logger: logging.Logger, endpoint: str, status_code: int, **kwargs):
    """
    Log response information for debugging.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint
        status_code: HTTP status code
        **kwargs: Additional info to log
    """
    if DEBUG_LOGGING:
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        status_emoji = "✓" if status_code < 400 else "✗"
        logger.debug(f"[RESPONSE] {status_emoji} {status_code} {endpoint} | {extra_info if extra_info else 'no data'}")


def log_database_operation(logger: logging.Logger, operation: str, table: str, **kwargs):
    """
    Log database operations for debugging.
    
    Args:
        logger: Logger instance
        operation: Operation type (INSERT, SELECT, UPDATE, DELETE)
        table: Table name
        **kwargs: Additional info
    """
    if DEBUG_LOGGING:
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.debug(f"[DB] {operation} on {table} | {extra_info if extra_info else 'no filters'}")


def log_auth_event(logger: logging.Logger, event: str, user_email: Optional[str] = None, **kwargs):
    """
    Log authentication events.
    
    Args:
        logger: Logger instance
        event: Event description (login_success, domain_validation_failed, etc)
        user_email: User email (can be masked for privacy)
        **kwargs: Additional info
    """
    email_display = f"{user_email[:3]}***@{user_email.split('@')[1]}" if user_email else "unknown"
    if DEBUG_LOGGING:
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.debug(f"[AUTH] {event} | email: {email_display} | {extra_info if extra_info else ''}")
    else:
        logger.info(f"[AUTH] {event}")
