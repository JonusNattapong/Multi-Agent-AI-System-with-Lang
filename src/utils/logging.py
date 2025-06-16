"""
Logging utilities for the Multi-Agent AI System
"""
import logging
import sys
from typing import Optional
from src.config import settings

def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Setup application logging configuration"""
    
    log_level = level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("multi_agent_system")
    logger.setLevel(numeric_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    return logging.getLogger(f"multi_agent_system.{name}")

# Global logger instance
logger = setup_logging()
