"""
Logging Configuration - Structured logging for observability

Provides:
- Structured logging with context
- Request/response logging
- Agent execution logging
- Error tracking
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json


class StructuredLogger:
    """
    Structured logger that adds context to all log messages.
    """
    
    def __init__(self, name: str):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually module name)
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Add context that will be included in all log messages"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context"""
        self.context = {}
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with context"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
            **self.context
        }
        if extra:
            log_data.update(extra)
        return json.dumps(log_data)
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(self._format_message(message, kwargs))
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(self._format_message(message, kwargs))


def setup_logging(log_level: str = "INFO"):
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Agent execution logger
agent_logger = get_logger("agent_execution")

# API logger
api_logger = get_logger("api")

# Security logger
security_logger = get_logger("security")
