"""
Logging utilities for CogniCode backend
"""

import logging
import sys
from datetime import datetime

def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """Setup logger with consistent formatting"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger = logging.getLogger(func.__module__)
        logger.info(f'{func.__name__} completed in {duration:.3f}s')
        
        return result
    return wrapper