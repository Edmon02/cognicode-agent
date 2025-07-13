# The `utils/` Directory (Backend): Utility Belt for Server Operations

Welcome to the `utils/` directory of our backend! This is where we keep various utility modules and helper functions that support the main backend application (`app.py`), agents, and services. These utilities often handle cross-cutting concerns like logging, data manipulation, or other reusable logic that doesn't belong to a specific agent or service.

For CogniCode Agent's backend, a key utility is the logging setup.

## File We'll Explore:

*   **`logger.py`**: This module is responsible for configuring and providing access to the application's logging system. Good logging is crucial for debugging, monitoring, and understanding the behavior of the application, especially a complex one involving AI agents and real-time communication. It also contains a performance logging decorator.

Let's see how our backend keeps track of what's happening.

---

## 📜 `logger.py`: The Application Scribe and Timekeeper

The `logger.py` module in `server/utils/` is the backbone of our backend's observability. It doesn't just set up basic logging; it provides an enhanced logging experience with structured information, performance metrics, colored console output for readability, and context-aware logging capabilities. Good logging is like having a detailed flight recorder for your application – invaluable when things go wrong, and insightful even when they go right.

**Key Features of this Logging Module:**

*   **Custom Logger Setup (`setup_logger`):** Configures logger instances with specific levels, handlers, and formatters.
*   **Performance Filter (`PerformanceFilter`):** Enriches log records with real-time CPU and memory usage percentages, plus a request ID.
*   **Colored Formatter (`ColoredFormatter`):** Makes console logs easier to read by color-coding log levels (e.g., errors in red, info in green).
*   **Request ID Tracking:** Uses thread-local storage to associate log messages with specific requests, crucial for debugging in concurrent environments.
*   **Performance Logging Decorator (`@log_performance`):** A handy decorator to automatically log the execution time and memory change of functions.
*   **API Call & Agent Operation Decorators (`@log_api_call`, `@log_agent_operation`):** Specialized decorators for logging specific types of operations with relevant context.
*   **Structured Logging Context (`LoggingContext`):** A context manager to easily log the start, end, and duration of specific operations with associated context data.

Let's break down this diligent scribe.

```python
# server/utils/logger.py
"""
Logging utilities for CogniCode backend
Enhanced with performance monitoring and structured logging
"""

import logging
import sys
import time # For performance timing
import threading # For thread-local storage
from datetime import datetime # Not directly used in this snippet, but often in logging
from functools import wraps # For creating well-behaved decorators
from typing import Any, Callable, Optional
import os # For checking NO_COLOR environment variable

# 1. Thread-local storage for request context
# Each thread will have its own independent 'request_id'.
_local = threading.local()

# 2. PerformanceFilter: Adds dynamic data to log records
class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics (CPU, Memory) and request ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Attempt to import psutil and get CPU/memory stats
        # psutil is a cross-platform library for process and system utilities.
        try:
            import psutil
            process = psutil.Process() # Get current Python process
            record.memory_percent = round(process.memory_percent(), 2) # % memory usage
            record.cpu_percent = round(process.cpu_percent(), 2)    # % CPU usage
        except ImportError: # If psutil is not installed
            record.memory_percent = 0.0 # Default values
            record.cpu_percent = 0.0

        # Add request_id to the log record if it's set in thread-local storage
        record.request_id = getattr(_local, 'request_id', 'none') # Default to 'none'

        return True # Always return True to include the record

# 3. ColoredFormatter: For eye-pleasing console logs
class ColoredFormatter(logging.Formatter):
    """Colored formatter for better console output during development."""

    COLORS = { # ANSI escape codes for colors
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m' # ANSI code to reset color

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.RESET) # Get color for level
        # Modify the levelname in the record to include color codes
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record) # Call parent Formatter's format method

# 4. setup_logger: The main function to configure and get a logger instance
def setup_logger(name: str, level: str = 'INFO', use_colors: bool = True) -> logging.Logger:
    """Setup logger with enhanced formatting, performance tracking, and color options."""

    logger = logging.getLogger(name) # Get or create a logger instance

    # Prevent adding multiple handlers if logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper())) # Set logger level (e.g., INFO, DEBUG)

    handler = logging.StreamHandler(sys.stdout) # Log to standard output (console)
    handler.setLevel(getattr(logging, level.upper())) # Handler level should also be set

    # Add our custom PerformanceFilter to the handler
    performance_filter = PerformanceFilter()
    handler.addFilter(performance_filter)

    # Choose formatter based on use_colors and NO_COLOR environment variable
    log_format = ('%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s '
                  '(Memory: %(memory_percent)s%%, CPU: %(cpu_percent)s%%)')
    date_format = '%Y-%m-%d %H:%M:%S'

    if use_colors and os.getenv('NO_COLOR') != '1': # Check NO_COLOR convention
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)

    handler.setFormatter(formatter) # Apply formatter to the handler
    logger.addHandler(handler)      # Add handler to the logger

    logger.propagate = False # Prevent log messages from being passed to parent loggers
                             # This avoids duplicate log output if root logger also has a handler.

    return logger

# 5. Request ID Management using Thread-Local Storage
def set_request_id(request_id: str):
    """Set request ID for the current execution thread."""
    # `_local` ensures that `request_id` is specific to the current thread.
    # In a web server handling multiple requests concurrently, each request's
    # logs can be tagged with its unique ID.
    _local.request_id = request_id

def get_request_id() -> str:
    """Get request ID for the current execution thread."""
    return getattr(_local, 'request_id', 'none') # Default to 'none' if not set

# 6. @log_performance Decorator: Timing and Memory Profiling for Functions
def log_performance(func: Optional[Callable] = None, *, logger_name: Optional[str] = None):
    """
    Decorator to log function execution time and memory usage delta.
    Can be used as @log_performance or @log_performance(logger_name="my.logger").
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f) # Preserves metadata (name, docstring) of the decorated function
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log_name = logger_name or f.__module__ # Use provided logger name or function's module
            perf_logger = logging.getLogger(log_name) # Get a logger instance

            start_time = time.time() # Record start time
            start_memory = _get_memory_usage() # Record initial memory usage (in MB)

            try:
                result = f(*args, **kwargs) # Execute the decorated function
                duration = time.time() - start_time
                end_memory = _get_memory_usage()
                memory_delta = end_memory - start_memory if start_memory is not None and end_memory is not None else 0.0

                perf_logger.info( # Log success with performance metrics
                    f"PERF: {f.__name__} completed in {duration:.3f}s. "
                    f"Memory: {end_memory:.2f}MB (Delta: {memory_delta:+.2f}MB)"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                perf_logger.error( # Log failure with duration
                    f"PERF_ERROR: {f.__name__} failed after {duration:.3f}s: {str(e)}"
                )
                raise # Re-raise the exception
        return wrapper

    # This allows the decorator to be used with or without arguments:
    # @log_performance or @log_performance(logger_name="custom")
    if func is None: # Called as @log_performance() or @log_performance(logger_name=...)
        return decorator
    else: # Called as @log_performance
        return decorator(func)

# 7. Specialized Decorators (log_api_call, log_agent_operation)
# These are similar to log_performance but tailored for specific contexts.

def log_api_call(endpoint: str, method: str = 'GET'):
    """Decorator to log API calls, setting a request_id for the duration."""
    # ... (Implementation similar to log_performance, but sets/clears request_id using _local) ...
    # It would typically log "API CALL: GET /api/status - Request started [req_id=xyz]"
    # and "API CALL: GET /api/status - Request completed in 0.123s [req_id=xyz]"
    # (Full implementation details omitted for brevity, but structure is as above)
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger('cognicode.api') # Dedicated API logger
            req_id = f"req_{int(time.time()*1000)}_{threading.get_ident()}" # More unique request ID
            set_request_id(req_id)
            start_time = time.time()
            logger.info(f"API CALL: {method} {endpoint} - Started")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"API CALL: {method} {endpoint} - Completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"API CALL: {method} {endpoint} - Failed after {duration:.3f}s: {str(e)}", exc_info=True)
                raise
            finally:
                set_request_id('none') # Clear request ID
        return wrapper
    return decorator


def log_agent_operation(agent_name: str, operation: str):
    """Decorator to log specific AI agent operations."""
    # ... (Similar structure, logs agent_name and operation) ...
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(f'cognicode.agents.{agent_name.lower()}')
            start_time = time.time()
            logger.debug(f"AGENT_OP: {agent_name} - {operation} - Started")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"AGENT_OP: {agent_name} - {operation} - Completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"AGENT_OP: {agent_name} - {operation} - Failed after {duration:.3f}s: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator

# 8. Helper to get memory usage in MB
def _get_memory_usage() -> Optional[float]:
    """Get current process memory usage in MB using psutil if available."""
    try:
        import psutil
        process = psutil.Process(os.getpid()) # Get current process by PID
        return process.memory_info().rss / (1024 * 1024)  # RSS in MB
    except ImportError:
        return None # psutil not available
    except Exception: # Other psutil errors
        return None

# 9. LoggingContext: A context manager for structured logging of operations
class LoggingContext:
    """Context manager for logging the duration and context of an operation."""
    def __init__(self, logger: logging.Logger, operation: str, **context_data):
        self.logger = logger
        self.operation = operation
        self.context_data = context_data # Additional key-value pairs for context
        self.start_time: Optional[float] = None

    def __enter__(self): # Called when entering 'with' block
        self.start_time = time.time()
        context_str = ', '.join(f'{k}={v}' for k, v in self.context_data.items())
        self.logger.debug(f"CONTEXT: {self.operation} - Started - Context: {{{context_str}}}")
        return self # The object returned by __enter__ is assigned to the 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb): # Called when exiting 'with' block
        duration = time.time() - self.start_time if self.start_time else 0.0
        if exc_type is None: # No exception occurred
            self.logger.info(f"CONTEXT: {self.operation} - Completed in {duration:.3f}s")
        else: # An exception occurred
            self.logger.error(
                f"CONTEXT: {self.operation} - Failed after {duration:.3f}s: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb) # Log exception info
            )
        # Return False to propagate the exception if one occurred, True to suppress it.
        # Default behavior (returning None, which is falsy) propagates the exception.
        return False

# 10. Convenience function to create LoggingContext instances
def log_context(logger: logging.Logger, operation: str, **context) -> LoggingContext:
    """Factory function to easily create a LoggingContext."""
    return LoggingContext(logger, operation, **context)

```

**Deep Dive into the Logger's Mechanisms:**

1.  **`_local = threading.local()`**: This creates an instance of `threading.local()`. Any attribute set on `_local` (e.g., `_local.request_id = 'some_id'`) will be specific to the current thread. In a multi-threaded web server, each request is often handled by a different thread. This allows us to store a `request_id` that is unique to the logs generated while processing that specific request, making it much easier to trace the flow of a single request through various parts of the application.

2.  **`PerformanceFilter(logging.Filter)`**:
    *   Custom logging filters allow you to modify or augment `LogRecord` objects before they are processed by handlers.
    *   `filter(self, record: logging.LogRecord)`: This method is called for every log record.
    *   It tries to import `psutil` (a library for system and process utilities). If available, it gets the current Python process's memory and CPU usage percentages and adds them as `record.memory_percent` and `record.cpu_percent` to the log record. If `psutil` isn't installed, it defaults these to 0.0.
    *   `record.request_id = getattr(_local, 'request_id', 'none')`: It retrieves the `request_id` from the thread-local storage (`_local`) and adds it to the log record. If no `request_id` is set for the current thread, it defaults to the string 'none'.
    *   These added attributes (`memory_percent`, `cpu_percent`, `request_id`) can then be used in the log formatter string.

3.  **`ColoredFormatter(logging.Formatter)`**:
    *   This custom formatter enhances console output by adding ANSI escape codes for colors based on the log level (e.g., INFO is green, ERROR is red). This significantly improves readability during development.
    *   `COLORS` dictionary maps log level names to their respective ANSI color codes. `RESET` resets the color.
    *   `format(self, record: logging.LogRecord)`: It temporarily modifies `record.levelname` to include the color codes before calling the parent class's `format` method, which then constructs the final log string.

4.  **`setup_logger(...)`**: This is the main function used to configure and retrieve logger instances.
    *   `logger = logging.getLogger(name)`: Gets a logger instance. Loggers are hierarchical, so names like "cognicode.agents.linter" create a child logger of "cognicode.agents".
    *   `if logger.handlers: return logger`: Prevents adding multiple handlers if the logger has already been configured (e.g., if `setup_logger` is called multiple times with the same name).
    *   `logger.setLevel(...)`: Sets the minimum severity level the logger will handle.
    *   `handler = logging.StreamHandler(sys.stdout)`: Creates a handler that sends log messages to the console (standard output).
    *   `handler.addFilter(performance_filter)`: Attaches our custom `PerformanceFilter` to this handler.
    *   **Formatter Selection**:
        *   It defines a `log_format` string that includes our custom fields: `%(request_id)s`, `%(memory_percent)s`, `%(cpu_percent)s`.
        *   It checks `if use_colors and os.getenv('NO_COLOR') != '1'`. This respects the `NO_COLOR` environment variable convention (if set to '1', colors are disabled) and the `use_colors` parameter.
        *   It then creates either a `ColoredFormatter` or a standard `logging.Formatter` with the defined `log_format`.
    *   `logger.addHandler(handler)`: Adds the configured handler to the logger.
    *   `logger.propagate = False`: This is important. It stops the log messages handled by this logger from being passed up to its parent loggers in the logging hierarchy. If the root logger also has a handler (e.g., a default one), setting `propagate = False` prevents duplicate log output.

5.  **`set_request_id(request_id: str)` and `get_request_id() -> str`**: Simple functions to set and get the `request_id` on the `_local` thread-local storage. `log_api_call` decorator uses these.

6.  **`@log_performance(...)` Decorator**:
    *   This is a flexible decorator that can be used as `@log_performance` or with an argument `@log_performance(logger_name="my.module")`.
    *   `@wraps(f)`: Ensures that the `wrapper` function preserves the metadata (like `__name__`, `__doc__`) of the original decorated function `f`.
    *   **Inside `wrapper`**:
        *   It gets a logger instance (either the specified `logger_name` or the module name of the decorated function).
        *   Records `start_time` and initial `start_memory` (using `_get_memory_usage`).
        *   Executes the original function `f`.
        *   Calculates `duration` and memory `memory_delta`.
        *   Logs a message with these performance metrics. The `+` in `{memory_delta:+.2f}` ensures a sign is always shown for the delta.
        *   If an exception occurs, it logs an error message with the duration before re-raising the exception.

7.  **`@log_api_call(...)` and `@log_agent_operation(...)` Decorators**:
    *   These are specialized versions of a performance/context logger.
    *   `@log_api_call`:
        *   Generates a more unique `request_id` combining timestamp and thread ID.
        *   Uses `set_request_id()` to store it in thread-local storage at the beginning of the API call.
        *   Logs the start and completion (or failure) of the API call, including the `request_id` in the log message implicitly via the `PerformanceFilter`.
        *   Crucially, it clears the `request_id` in a `finally` block using `set_request_id('none')` to ensure it doesn't leak to subsequent operations on the same thread if they are not part of this specific API call.
    *   `@log_agent_operation`: Similar, but logs messages specific to an agent's operation, using a logger named after the agent.

8.  **`_get_memory_usage() -> Optional[float]`**: A helper that attempts to get the current process's Resident Set Size (RSS) memory in megabytes using `psutil`. Returns `None` if `psutil` is unavailable or an error occurs, allowing the performance logger to handle it gracefully.

9.  **`LoggingContext` Class**:
    *   A context manager (used with Python's `with` statement) for structured logging around a block of code.
    *   `__init__`: Takes a `logger` instance, an `operation` name (string), and arbitrary `**context_data` (key-value pairs).
    *   `__enter__`: Called when entering the `with` block. It records the `start_time` and logs a "started" message including the operation name and context data.
    *   `__exit__`: Called when exiting the `with` block. It calculates the `duration`.
        *   If no exception occurred (`exc_type is None`), it logs a "completed" message.
        *   If an exception occurred, it logs a "failed" message including the exception value and uses `exc_info` to include the traceback in the log.
        *   It returns `False` (or `None`), which means any exception that occurred within the `with` block will be re-raised after `__exit__` completes.
    *   `log(self, level: int, message: str, **extra)`: A helper method within the context to log additional messages that will automatically include the operation name and context data.

10. **`log_context(...)` Function**: A simple factory function that makes creating `LoggingContext` instances more concise (e.g., `with log_context(logger, "MyOp", user_id=123): ...`).

**This `logger.py` module provides a powerful and developer-friendly logging setup. Key takeaways:**
*   **Structured Context:** The inclusion of timestamp, logger name, level, request ID, memory, and CPU usage in every log message (via `PerformanceFilter` and format string) is excellent for diagnostics.
*   **Readability:** `ColoredFormatter` greatly enhances the developer experience when watching console logs.
*   **Thread-Safety for Request IDs:** `threading.local` is correctly used for `request_id`.
*   **Reusable Decorators:** `@log_performance`, `@log_api_call`, and `@log_agent_operation` reduce boilerplate for common logging patterns (timing, contextual info).
*   **Context Manager (`LoggingContext`):** Offers a clean way to log the duration and success/failure of specific blocks of code with rich contextual information.
*   **Graceful Degradation:** Handles the absence of `psutil` without crashing.

This logging utility is a significant asset to the CogniCode Agent backend, making it more transparent and easier to debug and monitor.

---
Return to: [Backend Overview](README.md) | [Utils Directory Overview](#the-utils-directory-backend-utility-belt-for-server-operations)
This completes the planned walkthrough of the backend `utils/` directory. Next, we'll transition to Phase 4: Documentation Generation - Supporting Content & Refinement.
