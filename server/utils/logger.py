"""
Logging utilities for CogniCode backend
Enhanced with performance monitoring and structured logging
"""

import logging
import sys
import time
import threading
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional
import os

# Thread-local storage for request context
_local = threading.local()

class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Add memory usage if available
        try:
            import psutil
            process = psutil.Process()
            record.memory_percent = round(process.memory_percent(), 2)
            record.cpu_percent = round(process.cpu_percent(), 2)
        except ImportError:
            record.memory_percent = 0.0
            record.cpu_percent = 0.0
        
        # Add request ID if available
        record.request_id = getattr(_local, 'request_id', 'none')
        
        return True

class ColoredFormatter(logging.Formatter):
    """Colored formatter for better console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logger(name: str, level: str = 'INFO', use_colors: bool = True) -> logging.Logger:
    """Setup logger with enhanced formatting and performance tracking"""
    
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Add performance filter
    performance_filter = PerformanceFilter()
    handler.addFilter(performance_filter)
    
    # Create formatter
    if use_colors and os.getenv('NO_COLOR') != '1':
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s '
            '(Memory: %(memory_percent)s%%, CPU: %(cpu_percent)s%%)',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s '
            '(Memory: %(memory_percent)s%%, CPU: %(cpu_percent)s%%)',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger

def set_request_id(request_id: str):
    """Set request ID for current thread"""
    _local.request_id = request_id

def get_request_id() -> str:
    """Get request ID for current thread"""
    return getattr(_local, 'request_id', 'none')

def log_performance(func: Optional[Callable] = None, *, logger_name: Optional[str] = None):
    """
    Decorator to log function performance with detailed metrics
    
    Args:
        func: Function to decorate (when used without parameters)
        logger_name: Custom logger name (when used with parameters)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get logger
            log_name = logger_name or f.__module__
            logger = logging.getLogger(log_name)
            
            # Record start time and memory
            start_time = time.time()
            start_memory = _get_memory_usage()
            
            try:
                # Execute function
                result = f(*args, **kwargs)
                
                # Calculate metrics
                duration = time.time() - start_time
                end_memory = _get_memory_usage()
                memory_delta = end_memory - start_memory if start_memory else 0
                
                # Log success
                logger.info(
                    f'{f.__name__} completed successfully in {duration:.3f}s '
                    f'(Memory delta: {memory_delta:+.2f}MB)'
                )
                
                return result
                
            except Exception as e:
                # Calculate metrics for failed execution
                duration = time.time() - start_time
                
                # Log failure
                logger.error(
                    f'{f.__name__} failed after {duration:.3f}s: {str(e)}'
                )
                raise
        
        return wrapper
    
    # Handle both @log_performance and @log_performance()
    if func is None:
        return decorator
    else:
        return decorator(func)

def log_api_call(endpoint: str, method: str = 'GET'):
    """Decorator to log API calls with request/response details"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger('cognicode.api')
            
            # Generate request ID
            request_id = f"{int(time.time()*1000)}"
            set_request_id(request_id)
            
            start_time = time.time()
            
            try:
                logger.info(f'{method} {endpoint} - Request started')
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(f'{method} {endpoint} - Request completed in {duration:.3f}s')
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f'{method} {endpoint} - Request failed after {duration:.3f}s: {str(e)}')
                raise
            finally:
                # Clear request ID
                _local.request_id = 'none'
        
        return wrapper
    return decorator

def log_agent_operation(agent_name: str, operation: str):
    """Decorator to log AI agent operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(f'cognicode.agents.{agent_name.lower()}')
            
            start_time = time.time()
            logger.debug(f'{agent_name} {operation} started')
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(f'{agent_name} {operation} completed in {duration:.3f}s')
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f'{agent_name} {operation} failed after {duration:.3f}s: {str(e)}')
                raise
        
        return wrapper
    return decorator

def _get_memory_usage() -> float:
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    except ImportError:
        return 0.0
    except Exception:
        return 0.0

class LoggingContext:
    """Context manager for structured logging"""
    
    def __init__(self, logger: logging.Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        context_str = ', '.join(f'{k}={v}' for k, v in self.context.items())
        self.logger.debug(f'{self.operation} started - {context_str}')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            self.logger.info(f'{self.operation} completed in {duration:.3f}s')
        else:
            self.logger.error(f'{self.operation} failed after {duration:.3f}s: {exc_val}')
    
    def log(self, level: int, message: str, **extra):
        """Log a message with context"""
        extra.update(self.context)
        self.logger.log(level, f'{self.operation}: {message}', extra=extra)

# Convenience function to create logging contexts
def log_context(logger: logging.Logger, operation: str, **context) -> LoggingContext:
    """Create a logging context for structured logging"""
    return LoggingContext(logger, operation, **context)