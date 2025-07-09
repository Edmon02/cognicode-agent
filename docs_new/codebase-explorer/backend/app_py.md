# The Heartbeat: `server/app.py` – Orchestrating the Backend Symphony

Welcome to the core of our backend operations: `server/app.py`. If CogniCode Agent's backend is an orchestra, then `app.py` is the conductor, the main score, and the concert hall all in one. This Python script, built using the Flask microframework, is the central nervous system that receives requests from the frontend, dispatches tasks to our specialized AI agents, and manages the real-time flow of information via WebSockets.

**Key Responsibilities of `app.py`:**

*   **Flask Application Setup:** Initializes and configures the Flask web server.
*   **Socket.IO Integration:** Sets up and manages WebSocket communication for real-time interaction with the frontend using Flask-SocketIO.
*   **API Endpoints:** Defines essential HTTP endpoints (e.g., for health checks, agent status).
*   **Agent Management:** Implements and utilizes the `AgentPool` to efficiently manage instances of our AI agents (Linter, Refactor, TestGen).
*   **Request Handling:** Processes incoming data from the frontend (code, language, analysis requests).
*   **Event Emission:** Sends results, progress updates, and errors back to the frontend via WebSockets.
*   **Configuration:** Manages application settings through an `AppConfig` class and environment variables.
*   **Logging & Error Handling:** Implements basic logging and error management for backend operations.

This file is dense with critical logic, so we'll break it down section by section, exploring its nuances and the design decisions behind them. Prepare for a deep dive into the engine room!

---

*(Detailed walkthrough for `server/app.py` will follow, section by section, after a thorough re-read of the source code for detailed annotation.)*

---

## 📜 Imports & Initial Setup: Laying the Groundwork

Every Python script begins its tale with imports, and `app.py` is no different. These initial lines pull in the necessary tools and libraries that our backend server will rely upon. We also see some early configuration to ensure Python can find our custom modules.

```python
# server/app.py

# 0. Docstring: A brief overview of the file's purpose and key features/optimizations.
"""
CogniCode Agent - Flask Backend Server
Multi-agent AI system for code analysis, refactoring, and test generation

Performance optimizations:
- Lazy loading of AI models
- Connection pooling
- Memory-efficient data structures
- Async processing where possible
"""

# 1. Standard Library Imports: The essentials from Python's own toolkit
import os          # For interacting with the operating system (e.g., environment variables)
import sys         # For system-specific parameters and functions (e.g., modifying path)
import weakref     # For creating weak references (used in AgentPool for connections)
import threading   # For multi-threading capabilities (used for locking in AgentPool)
from datetime import datetime # For working with dates and times (e.g., timestamps)
from typing import Dict, Any, Optional # For type hinting, improving code readability
from contextlib import asynccontextmanager # For async context managers (though not explicitly used in this snippet)
from functools import lru_cache # For memoization, caching results of functions
import gc          # For interacting with the garbage collector

# 2. Third-Party Library Imports: Tools from the wider Python ecosystem
from flask import Flask, request, jsonify # Core Flask components for web server functionality
from flask_socketio import SocketIO, emit # For WebSocket communication with Flask
from flask_cors import CORS               # For handling Cross-Origin Resource Sharing
import logging                            # For application logging

# 3. Local Application Imports: Bringing in our own custom modules
# This line ensures Python can find modules in the current directory (server/)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.linter_agent import LinterAgent       # Our Linter AI agent
from agents.refactor_agent import RefactorAgent   # Our Refactor AI agent
from agents.testgen_agent import TestGenAgent     # Our Test Generation AI agent
from services.code_service import CodeService     # Service layer for code processing
from utils.logger import setup_logger, log_performance # Logging utilities
```

**Dissecting the Overture:**

0.  **Docstring**: The file starts with a multiline string (docstring) that serves as a quick explanation of what this script does. It highlights the project name, its purpose (multi-agent AI system), and importantly, mentions key performance optimizations like lazy loading and connection pooling. This is great practice, giving anyone opening the file an immediate high-level understanding.

1.  **Standard Library Imports**:
    *   `os`, `sys`: Classic imports for interacting with the operating system environment and Python's runtime system. `sys.path.append` is used later to ensure our local `agents`, `services`, and `utils` modules can be imported correctly.
    *   `weakref`: Used by the `AgentPool` to track active connections without preventing those connection objects from being garbage collected if they are no longer referenced elsewhere. This is a subtle but important detail for memory management.
    *   `threading`: The `AgentPool` uses a `threading.Lock` to ensure its operations are thread-safe, which is crucial in a web server environment that might handle multiple requests or WebSocket connections concurrently (especially with Flask-SocketIO's `async_mode='threading'`).
    *   `datetime`: For generating timestamps, likely used in logging or status information.
    *   `typing`: Provides `Dict`, `Any`, `Optional` for type hints, making the code more understandable and maintainable, especially in a larger project.
    *   `contextlib.asynccontextmanager`: While imported, it doesn't seem to be explicitly used in the provided snippet of `app.py`. It's for creating asynchronous context managers, often used with `async with`.
    *   `functools.lru_cache`: A decorator for memoizing function calls (caching their results based on arguments). Used for `get_memory_usage()`.
    *   `gc`: Python's garbage collector interface. Explicitly calling `gc.collect()` is sometimes done to try and free up memory, as seen in `handle_disconnect` and `cleanup_resources`.

2.  **Third-Party Library Imports**:
    *   `flask`: The core components of the Flask framework. `Flask` is the main application class, `request` provides access to incoming HTTP request data, and `jsonify` converts Python dicts to JSON responses.
    *   `flask_socketio`: `SocketIO` is the main class for adding WebSocket capabilities to our Flask app, and `emit` is used to send messages to connected clients.
    *   `flask_cors`: `CORS` is an extension to handle Cross-Origin Resource Sharing, essential for allowing our frontend (running on a different port, e.g., `localhost:3000`) to communicate with this backend (e.g., `localhost:5000` or `localhost:8000`).
    *   `logging`: Python's standard logging library.

3.  **Local Application Imports**:
    *   `sys.path.append(...)`: This line is a common way to modify Python's search path at runtime. It adds the directory containing `app.py` (i.e., `server/`) to the list of places Python looks for modules. This allows us to use absolute-style imports for our local packages like `from agents.linter_agent import LinterAgent`.
    *   We then import our specialized AI agents (`LinterAgent`, `RefactorAgent`, `TestGenAgent`), the `CodeService` (which likely orchestrates work between `app.py` and the agents), and logging utilities (`setup_logger`, `log_performance`) from our `utils` package.

This setup is clean and organized, clearly separating standard library, third-party, and local application modules. The early inclusion of `sys.path.append` is a practical solution for module resolution in this project structure.

---

## ⚙️ `AppConfig` Class: Central Command for Configuration

Following the imports, we encounter the `AppConfig` class. This is a smart way to centralize and manage all application-level configurations. Instead of scattering magic strings or environment variable lookups throughout the code, they are all neatly organized here.

```python
# server/app.py (continued)

# Application configuration
class AppConfig:
    """Centralized application configuration"""
    # 1. SECRET_KEY: Crucial for session security in Flask.
    # Defaults to a placeholder if not found in environment variables.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cognicode-secret-key-2025')

    # 2. FLASK_ENV: Determines the environment (development/production).
    # Affects debugging, logging levels, etc. Defaults to 'production'.
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')

    # 3. PORT: The network port the server will listen on.
    # Defaults to 8000 if not specified.
    PORT = int(os.environ.get('PORT', 8000)) # Ensure it's an integer

    # 4. MAX_CONTENT_LENGTH: Limits the size of incoming requests (e.g., uploaded code).
    # Set to 16MB by default.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

    # 5. Performance-related settings (configurable via environment variables)
    MAX_CONNECTIONS = int(os.environ.get('MAX_CONNECTIONS', 100))
    AGENT_POOL_SIZE = int(os.environ.get('AGENT_POOL_SIZE', 3)) # Might relate to pre-initialized agents
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3600))  # 1 hour for some cache

    # 6. @property for is_development: A convenient boolean flag.
    @property
    def is_development(self) -> bool:
        return self.FLASK_ENV == 'development'

    # 7. @property for cors_origins: Dynamically determines allowed origins for CORS.
    @property
    def cors_origins(self) -> list:
        if self.is_development:
            return ["*"] # Allow all origins in development for ease of use
        # In production, restrict to specific known frontend URLs
        return [
            "http://localhost:3000", # Local frontend dev
            "https://*.vercel.app",  # Allow any subdomain of vercel.app
            "https://cognicode-agent.vercel.app" # Specific production frontend URL
        ]

# 8. Create an instance of AppConfig to be used by the application.
config = AppConfig()
```

**Decoding `AppConfig`:**

This class is a best-practice pattern for handling configurations in applications.

1.  **`SECRET_KEY`**: This is vital for Flask applications. It's used to cryptographically sign session cookies and other security-sensitive data. The `os.environ.get()` method attempts to read it from an environment variable named `SECRET_KEY`. If not found, it falls back to a default string `'cognicode-secret-key-2025'`. **Crucial Note:** For any real deployment, this default key *must* be overridden with a strong, unique, and secret key set as an environment variable. Using a hardcoded default in production is a major security risk.

2.  **`FLASK_ENV`**: Controls Flask's operating mode.
    *   `'development'`: Enables debug mode (which provides detailed error pages and auto-reloads the server on code changes), sets more verbose logging, etc.
    *   `'production'`: Disables debug mode and generally uses more optimized settings.
    *   The default here is `'production'`, which is a safe default. Developers would typically set `FLASK_ENV=development` in their local `.env` file.

3.  **`PORT`**: The port number for the backend server. It defaults to `8000`. Note the `int()` conversion, as environment variables are typically strings. *The frontend's `NEXT_PUBLIC_BACKEND_URL` must point to this port.*

4.  **`MAX_CONTENT_LENGTH`**: Sets a limit on the size of incoming request data (e.g., the code submitted for analysis). This helps prevent denial-of-service attacks or accidental overloads from excessively large inputs. Here, it's set to 16 megabytes.

5.  **Performance Settings**:
    *   `MAX_CONNECTIONS`: Likely relates to the maximum number of concurrent WebSocket connections or perhaps a limit for the `AgentPool`.
    *   `AGENT_POOL_SIZE`: Could define the number of pre-warmed or maximum agent instances in the `AgentPool`.
    *   `CACHE_TIMEOUT`: Specifies a timeout for some caching mechanism within the application, defaulting to 1 hour (3600 seconds).
    These provide knobs for tuning the application's performance characteristics based on the deployment environment.

6.  **`@property def is_development(self) -> bool:`**: This is a Pythonic way to create a read-only computed property. Instead of writing `if config.FLASK_ENV == 'development':` elsewhere, you can just write `if config.is_development:`. It's cleaner and encapsulates the logic.

7.  **`@property def cors_origins(self) -> list:`**: Another computed property that dynamically determines the list of allowed origins for Cross-Origin Resource Sharing (CORS).
    *   In development (`config.is_development` is true), it allows `["*"]` (all origins). This is convenient for local development where the frontend might be served from various ports or setups.
    *   In production, it restricts allowed origins to a specific list: the local frontend development URL (`http://localhost:3000`), any Vercel deployment (`https://*.vercel.app`), and the specific production Vercel URL (`https://cognicode-agent.vercel.app`). This is a crucial security measure to prevent unauthorized websites from making requests to your backend API.

8.  **`config = AppConfig()`**: A global instance of `AppConfig` is created. This `config` object will be imported and used by other parts of the application (like the Flask app setup) to access configuration values.

Using a dedicated configuration class like `AppConfig` makes the code:
*   **Organized:** All configuration variables are in one place.
*   **Readable:** Easy to see what's configurable and what the defaults are.
*   **Maintainable:** Changing a default or adding a new configuration is straightforward.
*   **Testable:** You could potentially create different `AppConfig` instances for testing different scenarios.

This robust configuration setup is a strong foundation for the application.

---
Return to: [Backend Overview](README.md) | [Main `app.py` Overview](#the-heartbeat-serverapppy--orchestrating-the-backend-symphony)
Next Section: [Flask App & SocketIO Initialization](#flask-app--socketio-initialization) (Link to be activated)

---

## 🚀 Flask App & SocketIO Initialization: Setting the Stage for Web Communication

With our configuration neatly defined in the `config` object, the next crucial step is to initialize the Flask application itself and then extend it with WebSocket capabilities using Flask-SocketIO. We also set up logging here.

```python
# server/app.py (continued)

# ... (AppConfig class and config = AppConfig() instance previously defined) ...

# 1. Initialize Flask app with optimized settings
app = Flask(__name__) # Standard Flask app instantiation
app.config.update({   # Apply configurations from our AppConfig instance
    'SECRET_KEY': config.SECRET_KEY,
    'MAX_CONTENT_LENGTH': config.MAX_CONTENT_LENGTH,
    'JSON_SORT_KEYS': False,  # Optimization: Disable sorting of keys in JSON responses
})

# 2. Enable CORS for all routes, using dynamically determined origins
CORS(app,
     origins=config.cors_origins,    # Get allowed origins from AppConfig
     supports_credentials=True)     # Allow credentials (e.g., cookies) if needed

# 3. Initialize SocketIO with optimized settings
socketio = SocketIO(
    app,                             # Attach SocketIO to our Flask app
    cors_allowed_origins=config.cors_origins, # Crucial for WebSocket CORS
    async_mode='threading',          # Asynchronous mode for handling connections
    max_http_buffer_size=config.MAX_CONTENT_LENGTH, # Max buffer for SocketIO messages
    ping_timeout=60,                 # Timeout for client ping responses (seconds)
    ping_interval=25                 # Interval for sending pings (seconds)
)

# 4. Setup application-wide logging
logger = setup_logger('cognicode-backend') # Uses our custom logger setup from utils
```

**Unpacking the Initialization:**

1.  **`app = Flask(__name__)`**: This is the standard way to create a Flask application instance. `__name__` is a special Python variable that gets the name of the current module. Flask uses this to determine the root path for the application, helping it find templates and static files (though we primarily use it as an API and WebSocket server).

    **`app.config.update({...})`**: We immediately update the Flask application's configuration dictionary.
    *   `'SECRET_KEY': config.SECRET_KEY`: Sets the secret key obtained from our `AppConfig`.
    *   `'MAX_CONTENT_LENGTH': config.MAX_CONTENT_LENGTH`: Applies the maximum request size limit defined in `AppConfig` to Flask itself.
    *   `'JSON_SORT_KEYS': False`: This is a minor performance optimization. By default, Flask's `jsonify` function sorts JSON keys alphabetically. For APIs where key order doesn't matter (which is most of the time for machine-to-machine communication), disabling this can save a tiny bit of processing time on each JSON response. Every millisecond counts!

2.  **`CORS(app, origins=config.cors_origins, supports_credentials=True)`**:
    *   **CORS (Cross-Origin Resource Sharing)** is a browser security mechanism that restricts web pages from making requests to a different domain than the one that served the page. Since our frontend (e.g., `http://localhost:3000`) and backend (e.g., `http://localhost:8000`) run on different ports (and thus are considered different origins), we *must* configure CORS on the backend to allow the frontend to make requests.
    *   `origins=config.cors_origins`: This is where our dynamic `cors_origins` property from `AppConfig` comes into play. In development, it allows `*` (any origin), but in production, it restricts access to our known frontend URLs. This is a critical security feature.
    *   `supports_credentials=True`: If our frontend ever needed to send credentials (like cookies or HTTP authentication) with its requests, this flag would allow it.

3.  **`socketio = SocketIO(...)`**: This line initializes the Flask-SocketIO extension, wrapping our Flask `app` to add WebSocket capabilities.
    *   `cors_allowed_origins=config.cors_origins`: This is **extremely important**. Standard HTTP CORS headers (set by `Flask-CORS`) do *not* apply to WebSocket connections. Flask-SocketIO needs its own CORS configuration. We reuse our `config.cors_origins` here to ensure consistency. Without this, WebSocket connection attempts from the frontend would likely fail due to CORS errors in the browser console.
    *   `async_mode='threading'`: Flask-SocketIO can use different asynchronous modes. `'threading'` means each WebSocket client connection can be handled in its own thread (or a thread from a pool). This allows the server to handle multiple clients concurrently without blocking. Other options include `eventlet` or `gevent` (which use greenlets for even higher concurrency but require specific server setups) or `asyncio` (for Python's native async/await, also requiring a compatible ASGI server like Uvicorn instead of Gunicorn/Werkzeug for full async benefits). `'threading'` is a good, robust default for many Flask setups.
    *   `max_http_buffer_size=config.MAX_CONTENT_LENGTH`: Sets the maximum size for messages that can be buffered by Socket.IO, aligning with our general request size limit.
    *   `ping_timeout=60`, `ping_interval=25`: These settings control the heartbeat mechanism of Socket.IO. The server sends a "ping" to the client every `ping_interval` seconds. If the client doesn't respond with a "pong" within `ping_timeout` seconds, the server considers the connection dropped. This helps detect and clean up dead connections.

4.  **`logger = setup_logger('cognicode-backend')`**: This initializes our application logger using the `setup_logger` function imported from `utils.logger`. This function likely configures a logger instance (e.g., setting its level, format, and handlers like logging to console or a file). Having a dedicated logger named `'cognicode-backend'` allows for more organized and filterable log output.

At this point, our Flask application `app` is created, configured for basic web requests and security (CORS, secret key), and supercharged with real-time capabilities by `socketio`. The stage is set for defining routes and WebSocket event handlers.

---
Return to: [Backend Overview](README.md) | [Main `app.py` Overview](#the-heartbeat-serverapppy--orchestrating-the-backend-symphony)
Next Section: [The `AgentPool` Class: Managing Our AI Workforce](#the-agentpool-class-managing-our-ai-workforce) (Link to be activated)

---

## 🤖 The `AgentPool` Class: Managing Our AI Workforce

The `AgentPool` class is a custom-designed component within `app.py` responsible for managing the lifecycle and access to our specialized AI agents (Linter, Refactor, TestGen). Given that AI models can be resource-intensive (both in terms of memory and initialization time), simply creating a new agent instance for every request would be highly inefficient. The `AgentPool` addresses this by providing a centralized way to access agent instances, incorporating lazy loading and thread safety.

Think of the `AgentPool` as the HR department and dispatcher for our team of AI expert agents. It ensures they are hired (initialized) when needed and that requests are routed to an available expert.

```python
# server/app.py (continued)

# ... (Flask app and SocketIO setup previously defined) ...
# logger = setup_logger('cognicode-backend')

# Agent pool for better resource management
class AgentPool:
    """Thread-safe agent pool for resource management"""

    def __init__(self):
        # 1. Private lists to hold agent instances (currently supports one of each)
        self._linter_agents = []
        self._refactor_agents = []
        self._testgen_agents = []

        # 2. Threading lock for ensuring thread-safe operations when accessing/modifying agent lists
        self._lock = threading.Lock()
        self._initialized = False # Flag to track if initial pool setup is done

        # 3. WeakSet to track active connections without preventing their garbage collection
        self._active_connections = weakref.WeakSet()

    # 4. Initialize method for lazy loading and initial setup of agents
    def initialize(self) -> bool:
        """Initialize agent pool with lazy loading of one of each agent type."""
        if self._initialized: # If already initialized, do nothing
            return True

        with self._lock: # Acquire lock for thread-safe initialization
            if self._initialized: # Double-check after acquiring lock
                return True

            try:
                logger.info("Initializing agent pool...")

                # 5. Create one instance of each agent type
                # These LinterAgent(), RefactorAgent(), TestGenAgent() calls
                # likely load their respective models, which can be time-consuming.
                self._linter_agents.append(LinterAgent())
                self._refactor_agents.append(RefactorAgent())
                self._testgen_agents.append(TestGenAgent())

                # 6. Explicitly initialize these first agent instances
                # Each agent class is assumed to have an `initialize()` method.
                for agent in [self._linter_agents[0], self._refactor_agents[0], self._testgen_agents[0]]:
                    if not agent.initialize(): # Call the agent's own init logic
                        # This could involve loading models, setting up internal state, etc.
                        raise RuntimeError(f"Failed to initialize {agent.agent_name}") # agent_name assumed attr

                self._initialized = True # Mark initialization as complete
                logger.info("Agent pool initialized successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to initialize agent pool: {str(e)}")
                return False # Return False on failure

    # 7. Getter methods for each agent type
    def get_linter_agent(self) -> LinterAgent:
        """Get available linter agent. Creates one if none exist."""
        with self._lock: # Ensure thread safety
            if not self._linter_agents: # If no linter agent instance exists yet
                agent = LinterAgent()    # Create a new one
                agent.initialize()       # Initialize it (loads model)
                self._linter_agents.append(agent) # Add to our list
            return self._linter_agents[0] # Return the (first/only) instance

    def get_refactor_agent(self) -> RefactorAgent:
        """Get available refactor agent. Creates one if none exist."""
        with self._lock:
            if not self._refactor_agents:
                agent = RefactorAgent()
                agent.initialize()
                self._refactor_agents.append(agent)
            return self._refactor_agents[0]

    def get_testgen_agent(self) -> TestGenAgent:
        """Get available test generation agent. Creates one if none exist."""
        with self._lock:
            if not self._testgen_agents:
                agent = TestGenAgent()
                agent.initialize()
                self._testgen_agents.append(agent)
            return self._testgen_agents[0]

    # 8. Methods for tracking active WebSocket connections
    def add_connection(self, connection_id: str):
        """Track active connection using its session ID."""
        self._active_connections.add(connection_id)

    def remove_connection(self, connection_id: str):
        """Remove connection tracking."""
        try:
            self._active_connections.discard(connection_id) # Safely remove
        except: # Broad except, could be more specific if needed
            pass

    # 9. Method to get the status of the agent pool
    def get_status(self) -> Dict[str, Any]:
        """Get pool status including agent counts and active connections."""
        return {
            'linter_agents': len(self._linter_agents),
            'refactor_agents': len(self._refactor_agents),
            'testgen_agents': len(self._testgen_agents),
            'active_connections': len(self._active_connections),
            'initialized': self._initialized
        }

# 10. Global instance of AgentPool and CodeService
agent_pool = AgentPool()
code_service = CodeService()
```

**Journey into the `AgentPool`:**

1.  **Agent Storage (`_linter_agents`, etc.)**: The pool currently maintains separate lists for each type of agent. The implementation suggests it's designed to hold only *one* instance of each agent type at the moment (e.g., `return self._linter_agents[0]`). For a true "pool" that manages multiple instances of the same agent type for higher concurrency, these would typically store multiple agent objects, and the getter methods would implement logic to find an available one or create a new one up to a certain limit.
    *   *Self-correction/Observation:* The current design is more of an "Agent Manager" or "Agent Registry" that ensures a single, lazily-initialized instance of each agent type. This is still beneficial for resource management by centralizing access and initialization.

2.  **`_lock = threading.Lock()`**: This is crucial for thread safety. In a multi-threaded environment (like Flask with its default development server or Gunicorn with multiple worker threads, and Flask-SocketIO using `async_mode='threading'`), multiple requests or WebSocket events could try to access or modify the agent lists (`_linter_agents`, etc.) or the `_initialized` flag simultaneously. The `with self._lock:` statement in methods like `initialize` and the `get_..._agent` methods ensures that only one thread can execute the code block within the `with` statement at a time, preventing race conditions and data corruption.

3.  **`_active_connections = weakref.WeakSet()`**:
    *   A `WeakSet` is a set-like collection that stores "weak references" to its elements. This means that the references stored in the `WeakSet` do not prevent the objects from being garbage collected if those objects have no other strong references pointing to them.
    *   In this context, it's used to track active WebSocket connection session IDs (`sid`). If a connection object associated with an `sid` is properly cleaned up elsewhere in the application (e.g., by Flask-SocketIO upon disconnect), the `WeakSet` won't keep it alive unnecessarily. This is a good memory management practice.

4.  **`initialize()` Method**:
    *   This method handles the initial, potentially expensive, setup of the agents. It's designed to be called once (e.g., when the first client connects or at application startup).
    *   The `if self._initialized:` check and the double-check within the `with self._lock:` block (double-checked locking pattern) ensure that the initialization logic runs only once, even if multiple threads call `initialize()` concurrently.
    *   **Lazy Loading**: It seems the primary initialization of the *pool itself* (creating one of each agent and calling their `initialize()` methods) happens here. The `get_..._agent()` methods also have a form of lazy loading: if an agent list is empty, they create and initialize an agent on demand.

5.  **Agent Instantiation (`LinterAgent()`, etc.)**: When an agent is instantiated (e.g., `self._linter_agents.append(LinterAgent())`), its `__init__` method is called. This is typically where an agent might load its specific AI model using libraries like Transformers/PyTorch. This model loading can be a significant operation.

6.  **Agent's Own `initialize()`**: The pool calls an `initialize()` method on each agent instance. This suggests that agents might have a two-stage setup: their Python `__init__` and then a separate `initialize()` method (perhaps to be called by the pool at a controlled time, or to perform setup that can fail and be reported). The code assumes each agent class has an `initialize()` method and an `agent_name` attribute (used in the error message).

7.  **`get_..._agent()` Methods**: These methods provide access to the agent instances.
    *   They are thread-safe due to the `with self._lock:`.
    *   They implement a lazy initialization for the specific agent type: if the list for that agent type is empty (meaning no instance has been created and initialized yet), they create a new instance, initialize it, and add it to the list.
    *   Currently, they always return the first (and only) agent in their respective lists. This reinforces the idea that it's managing single instances rather than a pool of multiple identical agents.

8.  **Connection Tracking (`add_connection`, `remove_connection`)**: These methods allow the application (specifically, the SocketIO `connect` and `disconnect` handlers) to inform the `AgentPool` about active client connections. This is useful for monitoring and potentially for resource management decisions in a more advanced pooling scenario. The `try-except` block in `remove_connection` makes it robust against trying to remove an ID that might already be gone.

9.  **`get_status()` Method**: Provides a dictionary with the current state of the pool, including the number of initialized agents of each type, the count of active connections, and whether the pool itself has been initialized. This is useful for monitoring and diagnostics (e.g., via the `/api/agents/status` endpoint).

10. **Global Instances (`agent_pool = AgentPool()`, `code_service = CodeService()`)**: Single, global instances of `AgentPool` and `CodeService` are created when `app.py` is loaded. This makes them easily accessible throughout the application as singletons.

**In Summary:** The `AgentPool` class, while perhaps more accurately an "Agent Manager" in its current form (managing one instance per agent type), is a vital component for organizing AI agent access. It ensures thread-safe, lazy initialization of resource-intensive agents and provides a central point for their management. The use of `threading.Lock` is key for concurrent environments, and `weakref.WeakSet` is a nice touch for memory-conscious connection tracking. This centralized approach is much better than instantiating agents directly within request handlers.

---
Return to: [Backend Overview](README.md) | [Main `app.py` Overview](#the-heartbeat-serverapppy--orchestrating-the-backend-symphony)
Next Section: [Error Handlers & API Routes](#error-handlers--api-routes) (Link to be activated)

---

## 🛡️ Error Handlers & 📡 API Routes: Graceful Exits and Status Checks

A robust web application needs to handle errors gracefully and provide ways to inspect its status. `app.py` defines standard Flask error handlers and a couple of HTTP API routes for these purposes.

```python
# server/app.py (continued)

# ... (AgentPool and code_service instances previously defined) ...

# 1. Error handlers for common HTTP errors
@app.errorhandler(413) # HTTP 413: Payload Too Large
def request_entity_too_large(error):
    """Handle request too large errors (e.g., code submitted exceeds MAX_CONTENT_LENGTH)."""
    return jsonify({'error': 'Request entity too large'}), 413

@app.errorhandler(500) # HTTP 500: Internal Server Error
def internal_server_error(error):
    """Handle unexpected internal server errors."""
    logger.error(f"Internal server error: {str(error)}") # Log the error for debugging
    return jsonify({'error': 'Internal server error'}), 500

# 2. API Route for Agent Status
@app.route('/api/agents/status', methods=['GET']) # Defines a GET endpoint
@log_performance # Custom decorator to log the performance of this route handler
def get_agents_status():
    """Get detailed status of all AI agents and the agent pool."""
    try:
        # Retrieve instances of each agent from the pool
        # This also ensures they are initialized if not already.
        linter_agent = agent_pool.get_linter_agent()
        refactor_agent = agent_pool.get_refactor_agent()
        testgen_agent = agent_pool.get_testgen_agent()

        # Construct the JSON response
        return jsonify({
            'agents': [ # Array of agent statuses
                {
                    'id': 'linter',
                    'name': 'Linter Agent',
                    # Assumes each agent has a 'status' property/method and 'model_name' attribute
                    'status': linter_agent.status,
                    'capabilities': ['bug_detection', 'style_analysis', 'security_check'],
                    'model': linter_agent.model_name,
                    'last_run': linter_agent.last_run.isoformat() if linter_agent.last_run else None
                },
                {
                    'id': 'refactor',
                    'name': 'Refactor Agent',
                    'status': refactor_agent.status,
                    'capabilities': ['code_optimization', 'pattern_improvement', 'performance_tuning'],
                    'model': refactor_agent.model_name,
                    'last_run': refactor_agent.last_run.isoformat() if refactor_agent.last_run else None
                },
                {
                    'id': 'testgen',
                    'name': 'Test Generation Agent',
                    'status': testgen_agent.status,
                    'capabilities': ['unit_tests', 'integration_tests', 'edge_cases'],
                    'model': testgen_agent.model_name,
                    'last_run': testgen_agent.last_run.isoformat() if testgen_agent.last_run else None
                }
            ],
            'pool_status': agent_pool.get_status() # Get status from the AgentPool instance
        })
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        return jsonify({'error': 'Failed to get agent status'}), 500

# 3. API Route for Health Check (defined later in the file, but logically fits here)
# @app.route('/health', methods=['GET'])
# @log_performance
# def health_check(): ... (will be detailed with its full code later)

```

**Navigating Errors and Status Reports:**

1.  **Error Handlers (`@app.errorhandler(...)`)**:
    *   These decorators register functions to handle specific HTTP error codes. When Flask encounters an error (or an error is raised programmatically with `abort(code)`), it will invoke the corresponding handler.
    *   **`@app.errorhandler(413)` (`request_entity_too_large`)**: This handles the "Payload Too Large" error. It's triggered if an incoming request (e.g., code submitted by the user) exceeds the `MAX_CONTENT_LENGTH` defined in `AppConfig` and applied to the Flask app. It returns a clean JSON response with a 413 status code.
    *   **`@app.errorhandler(500)` (`internal_server_error`)**: This is a catch-all for unexpected errors within the application. It logs the error (which is crucial for debugging production issues) and returns a generic "Internal server error" JSON message with a 500 status code. This prevents exposing sensitive stack traces to the client.

2.  **Agent Status API Route (`/api/agents/status`)**:
    *   **`@app.route('/api/agents/status', methods=['GET'])`**: This decorator maps HTTP GET requests to the `/api/agents/status` URL path to the `get_agents_status` function.
    *   **`@log_performance`**: This is a custom decorator (presumably defined in `utils.logger`) that measures and logs the execution time of the `get_agents_status` function. This is helpful for monitoring API endpoint performance.
    *   **Functionality**:
        *   It retrieves instances of each agent type from the `agent_pool`. Calling these `get_..._agent()` methods ensures that the agents (and their AI models) are initialized if they haven't been already.
        *   It then constructs a JSON response containing:
            *   An array named `agents`, where each element is an object detailing the status of an individual AI agent. This assumes each agent object has `status`, `model_name`, and `last_run` attributes/properties. The `capabilities` are hardcoded here, providing metadata about what each agent can do. `last_run` is formatted as an ISO string if available.
            *   An object named `pool_status`, which is the dictionary returned by `agent_pool.get_status()`, showing counts of agents, active connections, and the pool's initialization state.
        *   A `try-except` block handles potential errors during status retrieval, logs them, and returns a 500 error response.

3.  **Health Check API Route (`/health`)**: (The full code for this is typically defined towards the end of `app.py` after `initialize_application`, but it's conceptually an API route.)
    *   This endpoint is essential for monitoring systems (like Docker health checks or cloud platform health probes) to determine if the application is running and healthy.
    *   It usually returns a simple success response (e.g., `{'status': 'healthy'}`) with a 200 OK status if the application is operational. The actual implementation in this file is more comprehensive, also including agent pool status and memory usage.

These error handlers and API routes enhance the robustness and observability of the backend server. Error handlers provide a better user experience than default error pages, and status/health endpoints are vital for operational monitoring and automated systems.

---
Return to: [Backend Overview](README.md) | [Main `app.py` Overview](#the-heartbeat-serverapppy--orchestrating-the-backend-symphony)
Next Section: [WebSocket Event Handlers](#websocket-event-handlers-the-real-time-core) (Link to be activated)

---

## 💬 WebSocket Event Handlers: The Real-Time Core

This is where the real-time magic of CogniCode Agent happens! Flask-SocketIO allows us to define handlers for specific events emitted by clients (our frontend). These handlers process incoming data, interact with AI agents (via the `agent_pool` and `code_service`), and emit results or progress updates back to the client.

```python
# server/app.py (continued)

# ... (API routes previously defined) ...

# WebSocket event handlers with improved error handling
# 1. Handle Client Connection
@socketio.on('connect')
def handle_connect():
    """Handle new client connection and initialize resources if needed."""
    try:
        # flask_request.sid is the session ID for the connected client
        session_id = getattr(request, 'sid', 'unknown') # Use Flask's request object
        agent_pool.add_connection(session_id) # Track this new connection
        logger.info(f'Client connected: {session_id}')

        # Lazy initialization of the agent pool upon first connection
        if not agent_pool._initialized: # Check if the pool has run its main init
            if agent_pool.initialize():
                logger.info('Agent pool initialized successfully on first connect.')
            else:
                logger.error('Failed to initialize agent pool on first connect!')
                # Emit an error to the client if backend init fails
                emit('error', {'message': 'Backend initialization failed, please try reconnecting.'})
                return # Prevent further processing for this client if pool failed

        # Emit a 'connected' event back to the client with session info
        emit('connected', {
            'message': 'Connected to CogniCode AI backend',
            'session_id': session_id,
            'server_time': datetime.utcnow().isoformat() # Provide server time as ISO string
        })
    except Exception as e:
        logger.error(f"Connection error for client {request.sid if request else 'unknown'}: {str(e)}", exc_info=True)
        # Try to emit an error to the client if possible during connection setup
        try:
            emit('error', {'message': f'Connection setup failed: {str(e)}'})
        except Exception as emit_e:
            logger.error(f"Failed to emit connection error: {str(emit_e)}")


# 2. Handle Client Disconnection
@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection and perform cleanup."""
    try:
        session_id = getattr(request, 'sid', 'unknown')
        agent_pool.remove_connection(session_id) # Untrack the connection
        logger.info(f'Client disconnected: {session_id}')

        # Trigger garbage collection to potentially free up resources
        gc.collect()
    except Exception as e:
        logger.error(f"Disconnection error for client {request.sid if request else 'unknown'}: {str(e)}", exc_info=True)

# 3. Handle 'analyze_code' Event - The Core Analysis Workflow
@socketio.on('analyze_code')
@log_performance # Decorator to log execution time of this handler
def handle_analyze_code(data: dict): # Type hint for incoming data
    """Handle code analysis request from the client."""
    session_id = getattr(request, 'sid', 'unknown') # Get client session ID

    try:
        # Input Validation: Ensure data is a dict and contains necessary fields
        if not data or not isinstance(data, dict):
            emit('error', {'message': 'Invalid data format for analyze_code'})
            return

        code = data.get('code', '').strip() # Get code, default to empty, strip whitespace
        language = data.get('language', 'javascript').lower() # Get lang, default to JS, lowercase

        if not code: # Ensure code is not empty
            emit('error', {'message': 'No code provided for analysis'})
            return

        # Check against max content length
        if len(code) > config.MAX_CONTENT_LENGTH:
            emit('error', {'message': f'Code exceeds maximum size limit of {config.MAX_CONTENT_LENGTH // (1024*1024)}MB'})
            return

        logger.info(f'Analyzing {language} code (len: {len(code)}) for client {session_id}')

        # Optional: Check cache first (not explicitly shown in this snippet but good practice)
        # cached_result = code_service.get_cached_analysis(code, language)
        # if cached_result:
        #     emit('analysis_complete', cached_result)
        #     logger.info(f'Returned cached analysis for client {session_id}')
        #     return

        # Emit progress updates to the client
        emit('analysis_progress', {'progress': 25, 'message': 'Initializing analysis...'})

        linter_agent = agent_pool.get_linter_agent() # Get a linter agent instance

        emit('analysis_progress', {'progress': 50, 'message': 'Running AI Linter Agent...'})

        # Perform the actual analysis (this is a blocking call in 'threading' mode)
        # For very long tasks, consider background threads/tasks for true async.
        analysis_results = linter_agent.analyze(code, language) # Assumes analyze method exists

        emit('analysis_progress', {'progress': 75, 'message': 'Processing results...'})

        # Process results via CodeService (e.g., formatting, adding metadata)
        processed_results = code_service.process_analysis(analysis_results, code, language)

        # Emit final completion event with the processed results
        emit('analysis_complete', processed_results)
        logger.info(f'Analysis completed for client {session_id}')

    except Exception as e:
        logger.error(f'Error analyzing code for {session_id}: {str(e)}', exc_info=True)
        emit('error', {'message': f'Analysis failed on server: {str(e)}'})
    finally:
        # Optional: A small delay if needed for messages to flush before client might do something else.
        # socketio.sleep(0.1) # Example: sleep for 100ms
        pass


# 4. Handle 'generate_refactoring' Event
@socketio.on('generate_refactoring')
@log_performance
def handle_generate_refactoring(data: dict):
    """Handle refactoring generation request."""
    session_id = getattr(request, 'sid', 'unknown')
    try:
        code = data.get('code', '').strip()
        language = data.get('language', 'javascript').lower()
        # 'issues' might be passed from frontend's current analysis state
        issues = data.get('analysis', []) # Renamed from 'analysis' to 'issues' for clarity

        if not code:
            emit('error', {'message': 'No code provided for refactoring'})
            return

        logger.info(f'Generating refactoring for {language} code (len: {len(code)}) for client {session_id}')
        emit('analysis_progress', {'progress': 25, 'message': 'Initializing refactor...'}) # Generic progress

        refactor_agent = agent_pool.get_refactor_agent()
        emit('analysis_progress', {'progress': 50, 'message': 'Running AI Refactor Agent...'})

        # Pass code, language, and potentially existing issues to the agent
        suggestions = refactor_agent.generate_suggestions(code, language, issues) # Assumed method

        emit('analysis_progress', {'progress': 75, 'message': 'Processing suggestions...'})
        processed_suggestions = code_service.process_refactor_suggestions(suggestions) # Assumed service method

        emit('refactor_suggestions', processed_suggestions) # Emit specific event for refactor results
        logger.info(f'Refactoring suggestions generated for client {session_id}')

    except Exception as e:
        logger.error(f'Error generating refactoring for {session_id}: {str(e)}', exc_info=True)
        emit('error', {'message': f'Refactoring generation failed: {str(e)}'})

# 5. Handle 'generate_tests' Event
@socketio.on('generate_tests')
@log_performance
def handle_generate_tests(data: dict):
    """Handle test generation request."""
    session_id = getattr(request, 'sid', 'unknown')
    try:
        code = data.get('code', '').strip()
        language = data.get('language', 'javascript').lower()
        # 'functions' might be a list of function names/signatures extracted by frontend or previous analysis
        functions_to_test = data.get('functions', []) # Renamed for clarity

        if not code:
            emit('error', {'message': 'No code provided for test generation'})
            return

        logger.info(f'Generating tests for {language} code (len: {len(code)}) for client {session_id}')
        emit('analysis_progress', {'progress': 25, 'message': 'Initializing test generation...'})

        testgen_agent = agent_pool.get_testgen_agent()
        emit('analysis_progress', {'progress': 50, 'message': 'Running AI TestGen Agent...'})

        # Pass code, language, and potentially specific functions to target
        test_cases = testgen_agent.generate_tests(code, language, functions_to_test) # Assumed method

        emit('analysis_progress', {'progress': 75, 'message': 'Processing test cases...'})
        processed_tests = code_service.process_test_cases(test_cases) # Assumed service method

        emit('test_cases_generated', processed_tests) # Emit specific event for test results
        logger.info(f'Test cases generated for client {session_id}')

    except Exception as e:
        logger.error(f'Error generating tests for {session_id}: {str(e)}', exc_info=True)
        emit('error', {'message': f'Test generation failed: {str(e)}'})

```

**Orchestrating Real-Time Interactions:**

These handlers are the backbone of the application's interactive nature.

1.  **`@socketio.on('connect') def handle_connect():`**
    *   **Trigger:** This function is automatically invoked by Flask-SocketIO whenever a new client successfully establishes a WebSocket connection.
    *   **Session ID (`request.sid`):** Flask-SocketIO assigns a unique session ID (`sid`) to each connected client. We retrieve it using `getattr(request, 'sid', 'unknown')` for robust access.
    *   **Connection Tracking:** `agent_pool.add_connection(session_id)` registers the new client with our `AgentPool`, potentially for monitoring.
    *   **Lazy Agent Pool Initialization:** A crucial piece of logic here is `if not agent_pool._initialized: agent_pool.initialize()`. This ensures that the potentially resource-intensive initialization of AI agents (loading models, etc.) is deferred until the *first client connects*. This can significantly speed up initial server startup time. If initialization fails, an error is emitted to the client.
    *   **Welcome Message:** Upon successful connection and pool initialization, the server emits a `'connected'` event back to the client, including the `session_id` and current server time. This confirms to the frontend that it's good to go.
    *   **Error Handling:** A `try-except` block wraps the connection logic to catch any unexpected errors during this setup phase, log them, and attempt to notify the client.

2.  **`@socketio.on('disconnect') def handle_disconnect():`**
    *   **Trigger:** Invoked when a client disconnects (either intentionally or due to network issues).
    *   **Connection Untracking:** `agent_pool.remove_connection(session_id)` removes the client from the active connections list.
    *   **Garbage Collection (`gc.collect()`):** An explicit call to Python's garbage collector. This is a hint that the developers are conscious of memory usage, especially after a client (which might have triggered resource-intensive operations) disconnects. While Python's GC usually runs automatically, explicit calls can sometimes be beneficial in specific scenarios, though their impact should be measured.

3.  **`@socketio.on('analyze_code') def handle_analyze_code(data: dict):`**
    *   **Trigger:** This is the main workhorse, called when the frontend emits an `'analyze_code'` event (e.g., when the user clicks the "Analyze" button). The `data` payload from the client (containing `code` and `language`) is passed as an argument.
    *   **`@log_performance`**: Our custom decorator makes another appearance, logging the time taken by this handler.
    *   **Input Validation:**
        *   Checks if `data` is a dictionary.
        *   Retrieves `code` and `language` from `data`, providing defaults and stripping/lowercasing.
        *   Ensures `code` is not empty.
        *   Checks if `code` length exceeds `config.MAX_CONTENT_LENGTH`.
        *   If validation fails, an `'error'` event is emitted back to the client, and the function returns early.
    *   **Logging:** Informative log message about the analysis request.
    *   **Caching (Conceptual):** The commented-out lines suggest a caching mechanism (`code_service.get_cached_analysis`) could be (or was intended to be) implemented to return results quickly for previously analyzed code.
    *   **Progress Emission:** The handler emits `'analysis_progress'` events at various stages (`Initializing`, `Running AI Linter Agent`, `Processing results`) with a percentage and a message. This allows the frontend to display a responsive progress bar or status updates to the user, which is excellent UX for potentially long-running AI operations.
    *   **Agent Interaction:**
        *   `linter_agent = agent_pool.get_linter_agent()`: Retrieves an initialized Linter Agent.
        *   `analysis_results = linter_agent.analyze(code, language)`: Calls the agent's `analyze` method (this is an assumed method name based on the context; the actual method name in `LinterAgent` would need to be verified). This is the core AI processing step.
    *   **Result Processing:** `processed_results = code_service.process_analysis(...)`: The raw results from the agent are passed to the `CodeService`, which might format them, add metadata, or perform other transformations to make them suitable for the frontend.
    *   **Completion Event:** Finally, `'analysis_complete'` is emitted with the `processed_results`.
    *   **Error Handling:** A global `try-except` block catches any errors during the process, logs them with `exc_info=True` (to include stack trace in logs), and emits an `'error'` event to the client.
    *   **`finally` block with `socketio.sleep(0.1)` (commented out):** The `socketio.sleep()` function is a non-blocking sleep for Flask-SocketIO. A very short sleep here *could* be used to ensure that messages emitted (like `'analysis_complete'` or `'error'`) have a chance to be sent over the network before the handler function fully exits and potentially releases resources or before the client immediately sends another request. However, it's often not strictly necessary and was commented out in the original code snippet you provided earlier (in `app.py` it was `socketio.sleep(1)` and uncommented). If used, the duration should be minimal.

4.  **`@socketio.on('generate_refactoring') def handle_generate_refactoring(data: dict):`**
    *   Similar structure to `handle_analyze_code`.
    *   Receives `code`, `language`, and optionally `analysis` (likely previous linting issues that might inform refactoring).
    *   Uses `agent_pool.get_refactor_agent()`.
    *   Calls an assumed `refactor_agent.generate_suggestions(...)` method.
    *   Processes results via `code_service.process_refactor_suggestions(...)`.
    *   Emits results on a specific `'refactor_suggestions'` event.
    *   Includes progress updates and robust error handling.

5.  **`@socketio.on('generate_tests') def handle_generate_tests(data: dict):`**
    *   Follows the same pattern again.
    *   Receives `code`, `language`, and optionally `functions` (e.g., a list of functions to generate tests for, perhaps identified by a previous analysis).
    *   Uses `agent_pool.get_testgen_agent()`.
    *   Calls an assumed `testgen_agent.generate_tests(...)` method.
    *   Processes results via `code_service.process_test_cases(...)`.
    *   Emits results on a specific `'test_cases_generated'` event.
    *   Includes progress updates and robust error handling.

**Overall, these WebSocket handlers are the dynamic core of the backend. They demonstrate:**
*   **Clear Event-Driven Logic:** Each handler is tied to a specific client-side action.
*   **Input Validation:** Basic checks are in place for incoming data.
*   **Modular Design:** Interaction with specialized agents and a service layer for processing.
*   **User Experience Focus:** Emission of progress updates and clear error messages.
*   **Resource Management Awareness:** Use of the `AgentPool` and logging.

These handlers effectively bridge the gap between the user's actions on the frontend and the powerful AI capabilities of the backend agents.

---
Return to: [Backend Overview](README.md) | [Main `app.py` Overview](#the-heartbeat-serverapppy--orchestrating-the-backend-symphony)
Next Section: [Utility Functions & Application Startup](#utility-functions--application-startup) (Link to be activated)

---

## 🛠️ Utility Functions, Initialization & Startup: The Supporting Cast and Grand Finale

The final sections of `app.py` include helper utilities, functions to ensure the application starts correctly, and the main script execution block that kicks everything off when `app.py` is run directly.

```python
# server/app.py (continued)

# ... (WebSocket event handlers previously defined) ...

# 1. Utility function to get memory usage (with LRU cache)
@lru_cache(maxsize=1) # Cache the result to avoid frequent calls
def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics using psutil if available."""
    try:
        # Attempt to import psutil, a cross-platform library for process and system utilities
        try:
            import psutil
            process = psutil.Process() # Get the current process
            memory_info = process.memory_info() # Get memory info for this process

            return {
                'rss': memory_info.rss,  # Resident Set Size (actual physical memory)
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': process.memory_percent(), # Memory usage as a percentage
                'available': psutil.virtual_memory().available # System-wide available memory
            }
        except ImportError:
            # Fallback if psutil is not installed (e.g., in a minimal environment)
            logger.warning("psutil library not found, memory usage reporting will be basic.")
            return {
                'rss': 0, 'vms': 0,
                'note': 'psutil not available, limited memory stats'
            }
    except Exception as e:
        logger.error(f'Error getting memory usage: {str(e)}')
        return {'error': str(e), 'note': 'Failed to retrieve memory stats'}

# 2. Resource cleanup function
def cleanup_resources():
    """Cleanup resources like caches and trigger garbage collection."""
    try:
        # Clear any application-level caches (e.g., in CodeService)
        code_service.clear_old_cache() # Assumes CodeService has this method

        # Clear the cache for the get_memory_usage function itself
        get_memory_usage.cache_clear()

        # Explicitly trigger garbage collection
        gc.collect()

        logger.info("Resource cleanup completed successfully.")
    except Exception as e:
        logger.error(f"Error during resource cleanup: {str(e)}")

# 3. Application initialization function
def initialize_application():
    """Initialize critical application components like the agent pool."""
    try:
        logger.info("🚀 Initializing CogniCode Agent backend...")

        # Initialize the agent pool (loads models, etc.)
        if not agent_pool.initialize():
            logger.error("Failed to initialize agent pool during application startup.")
            # This is a critical failure, so raise an error to prevent app from starting improperly
            raise RuntimeError("Agent pool initialization failed. Server cannot start.")

        logger.info("✅ Agent pool initialized successfully.")

        # Optional: A quick test to see if agents are basically functional
        try:
            _ = agent_pool.get_linter_agent() # Attempt to get an agent
            logger.info("✅ Basic agent functionality verified (Linter agent retrieved).")
        except Exception as e:
            # Log as warning, as the main initialization succeeded.
            logger.warning(f"Agent verification step warning: {str(e)}")

        logger.info("🎉 CogniCode Agent backend initialization complete!")
        return True # Indicate success

    except Exception as e:
        logger.error(f"❌ Application initialization failed critically: {str(e)}")
        return False # Indicate failure

# 4. Health check endpoint (Full definition)
@app.route('/health', methods=['GET'])
@log_performance
def health_check():
    """Enhanced health check endpoint with comprehensive status."""
    try:
        # Ensure agent pool is initialized if it wasn't at startup (e.g., if app was imported)
        if not agent_pool._initialized:
            logger.info("Health check: Agent pool not initialized, attempting initialization...")
            # This is a good place to ensure critical components are ready.
            # If it fails here, the health check should reflect that.
            if not initialize_application(): # Try to initialize the whole app
                 return jsonify({
                    'status': 'unhealthy',
                    'reason': 'Agent pool failed to initialize on demand.',
                    'timestamp': datetime.utcnow().isoformat()
                 }), 503 # Service Unavailable

        pool_status = agent_pool.get_status()

        # Construct a detailed status response
        status_response = {
            'status': 'healthy' if agent_pool._initialized else 'degraded', # More nuanced status
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0', # Example version, could be dynamic
            'environment': config.FLASK_ENV,
            'agents': {
                'linter_agents': pool_status.get('linter_agents', 0),
                'refactor_agents': pool_status.get('refactor_agents', 0),
                'testgen_agents': pool_status.get('testgen_agents', 0),
                'active_connections': pool_status.get('active_connections', 0),
                'initialized': pool_status.get('initialized', False)
            },
            'memory': get_memory_usage() # Include memory usage stats
        }

        # Determine HTTP status code based on health
        http_status_code = 200 if status_response['status'] == 'healthy' else 503 # 503 Service Unavailable

        return jsonify(status_response), http_status_code

    except Exception as e:
        logger.error(f"Health check endpoint failed: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500 # Internal Server Error

# 5. Application factory pattern (optional, but good practice)
def create_app():
    """Application factory: Initializes and returns the Flask app instance."""
    # The initialize_application() call is now primarily done in the `if __name__ == '__main__':` block
    # or on first connect / first health check, to ensure it runs when the app effectively "starts".
    # If this `create_app` were used by Gunicorn, init should happen here or be triggered by Gunicorn hooks.
    # For simplicity in current structure, main init is at startup.
    # initialize_application() # Call this here if deploying with Gunicorn directly using create_app
    return app

# 6. Main execution block: Runs when script is executed directly
if __name__ == '__main__':
    try:
        logger.info('Attempting to initialize CogniCode AI backend application...')
        # Attempt to initialize the application's core components (like AgentPool)
        if not initialize_application():
            # If critical initialization fails, log and exit to prevent running in a bad state.
            logger.critical("CRITICAL: Application initialization failed. Exiting.")
            sys.exit(1) # Exit with a non-zero status code to indicate failure

        logger.info('All core components initialized successfully.')

        # Register the cleanup_resources function to be called when the application exits
        import atexit
        atexit.register(cleanup_resources)

        # Start the Flask-SocketIO development server
        logger.info(f'Starting CogniCode backend server on host 0.0.0.0, port {config.PORT}...')
        socketio.run(
            app,
            host='0.0.0.0', # Listen on all available network interfaces
            port=config.PORT,
            debug=config.is_development, # Enable/disable Flask debug mode based on config
            use_reloader=False, # Disable Werkzeug reloader for production/stability, esp. with threads/models
                                # Development mode (FLASK_ENV=development) might still use Next.js reloader for frontend.
            log_output=config.is_development # Show SocketIO logs if in development
        )

    except KeyboardInterrupt: # Handle Ctrl+C gracefully
        logger.info("Server shutdown requested by user (KeyboardInterrupt).")
        # Cleanup is handled by atexit, but can add specific shutdown logs here if needed.
    except Exception as e: # Catch any other exceptions during startup
        logger.critical(f'FATAL: Failed to start server: {str(e)}', exc_info=True)
        sys.exit(1) # Exit with error
```

**Wrapping Up `app.py`:**

1.  **`get_memory_usage()` Function**:
    *   **`@lru_cache(maxsize=1)`**: This decorator is from `functools`. It implements a Least Recently Used (LRU) cache. With `maxsize=1`, it means the result of the *last call* to `get_memory_usage` (with no arguments, so effectively just one cached result) will be stored. Subsequent calls within a short period (before the "cache entry" is considered old, though for `maxsize=1` it just stores the last result) will return the cached value instead of re-computing. This is useful if memory stats are requested frequently (e.g., by multiple health checks) as getting process info can have a small overhead.
    *   It attempts to import `psutil`, a powerful cross-platform library for retrieving information on running processes and system utilization.
    *   If `psutil` is available, it gathers various memory statistics: RSS (Resident Set Size - actual physical memory used), VMS (Virtual Memory Size), percentage memory usage of the current process, and system-wide available memory.
    *   If `psutil` is *not* available (e.g., not installed), it logs a warning and returns basic/default values with a note. This graceful degradation is good practice.
    *   Includes a `try-except` for other potential errors during metric collection.

2.  **`cleanup_resources()` Function**:
    *   This function is intended to be called when the application shuts down (see `atexit.register` later).
    *   `code_service.clear_old_cache()`: Calls a method on the `code_service` instance, presumably to clear any application-level caches it might be maintaining.
    *   `get_memory_usage.cache_clear()`: Clears the LRU cache for the `get_memory_usage` function itself.
    *   `gc.collect()`: Explicitly invokes the Python garbage collector. This can be helpful to try and reclaim memory, especially if there might be objects with circular references that the GC needs an explicit nudge to clean up, or just before shutdown to free resources.
    *   Logs completion or any errors during cleanup.

3.  **`initialize_application()` Function**:
    *   This function centralizes the startup initialization logic for critical components.
    *   Its primary responsibility here is to call `agent_pool.initialize()`. If the agent pool (which loads AI models) fails to initialize, it's considered a critical failure, and a `RuntimeError` is raised, which should prevent the application from starting in a non-functional state.
    *   It includes an optional "verification" step by trying to get an agent instance, logging a warning if it fails but not necessarily crashing the app if the main pool initialization seemed to succeed. This is a pragmatic approach.
    *   Returns `True` on success, `False` on critical failure.

4.  **`health_check()` Function (Full Definition)**:
    *   This is the complete implementation of the `/health` endpoint.
    *   It first checks if `agent_pool` is initialized. If not (which could happen if the app was imported as a module and `if __name__ == '__main__':` didn't run, or if the initial startup call failed silently), it attempts to call `initialize_application()` again. This makes the health check more robust by trying to ensure critical components are ready. If on-demand initialization fails, it returns a 503 "Service Unavailable" status.
    *   It then constructs a detailed `status_response` including:
        *   A more nuanced overall status (`'healthy'` or `'degraded'` if the agent pool isn't initialized).
        *   Timestamp, version (hardcoded here as '2.0.0', could be made dynamic).
        *   Environment (`config.FLASK_ENV`).
        *   Detailed agent pool status from `agent_pool.get_status()`.
        *   Memory usage statistics from `get_memory_usage()`.
    *   The HTTP status code of the response is set to `200` if healthy, or `503` if degraded/uninitialized.
    *   Includes a `try-except` for any other unexpected errors, returning a 500.
    *   This comprehensive health check is excellent for monitoring and diagnosing the application's state.

5.  **`create_app()` Function (Application Factory)**:
    *   This defines a function that returns the configured Flask `app` instance. This is known as the "Application Factory" pattern in Flask.
    *   **Purpose**: It's particularly useful for:
        *   Creating multiple instances of the app with different configurations (e.g., for testing).
        *   Allowing deployment tools like Gunicorn to discover and run the app (e.g., `gunicorn 'your_module:create_app()'`).
    *   The comment correctly notes that if Gunicorn were to use `create_app()`, `initialize_application()` might need to be called within `create_app()` or via Gunicorn server hooks to ensure initialization happens before requests are served. In the current script structure, initialization is primarily handled in the `if __name__ == '__main__':` block.

6.  **`if __name__ == '__main__':` Block**:
    *   This is the standard Python entry point that executes only when the script (`app.py`) is run directly (e.g., `python server/app.py`), not when it's imported as a module.
    *   **Critical Initialization**: It first calls `initialize_application()`. If this fails (returns `False`), it logs a critical error and exits the script using `sys.exit(1)` (a non-zero exit code indicates an error). This is a robust way to prevent the server from starting if essential components like AI models couldn't be loaded.
    *   **`atexit.register(cleanup_resources)`**: This registers the `cleanup_resources` function to be called automatically when the Python interpreter exits (e.g., on normal shutdown or unhandled exceptions leading to termination, though graceful shutdown via `KeyboardInterrupt` is handled separately). This ensures resources are attempted to be cleaned up.
    *   **`socketio.run(app, ...)`**: This is what actually starts the web server.
        *   `host='0.0.0.0'`: Makes the server listen on all available network interfaces, meaning it can be accessed from other machines on the network (not just `localhost`).
        *   `port=config.PORT`: Uses the port defined in our `AppConfig`.
        *   `debug=config.is_development`: Enables Flask's debug mode if `FLASK_ENV` is 'development'.
        *   `use_reloader=False`: Explicitly disables Werkzeug's (Flask's development server) auto-reloader. This is generally a good idea for stability when dealing with multi-threading, external resources like AI models, or when running in a more production-like local setup. The frontend (Next.js) has its own hot-reloading.
        *   `log_output=config.is_development`: Controls whether Flask-SocketIO's own logs are output to the console, typically enabled for development.
    *   **Exception Handling for Startup**:
        *   `except KeyboardInterrupt`: Catches `Ctrl+C` to allow for a graceful shutdown message. Cleanup is handled by `atexit`.
        *   `except Exception as e`: Catches any other unexpected errors during the server startup process, logs them critically, and exits.

This `app.py` is well-structured, demonstrating good practices for configuration, resource management (AgentPool, cleanup), real-time communication, error handling, and application startup/shutdown. The inclusion of detailed health checks and performance logging are also commendable.

---
Return to: [Backend Overview](README.md) | [Main `app.py` Overview](#the-heartbeat-serverapppy--orchestrating-the-backend-symphony)
Next: [The Agents Directory: Our Specialized AI Experts](../agents_directory.md)
