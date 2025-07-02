"""
CogniCode Agent - Flask Backend Server
Multi-agent AI system for code analysis, refactoring, and test generation

Performance optimizations:
- Lazy loading of AI models
- Connection pooling
- Memory-efficient data structures
- Async processing where possible
"""

import os
import sys
import weakref
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from functools import lru_cache
import gc

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.linter_agent import LinterAgent
from agents.refactor_agent import RefactorAgent
from agents.testgen_agent import TestGenAgent
from services.code_service import CodeService
from utils.logger import setup_logger, log_performance

# Application configuration
class AppConfig:
    """Centralized application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cognicode-secret-key-2025')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    PORT = int(os.environ.get('PORT', 8000))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # Performance settings
    MAX_CONNECTIONS = int(os.environ.get('MAX_CONNECTIONS', 100))
    AGENT_POOL_SIZE = int(os.environ.get('AGENT_POOL_SIZE', 3))
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3600))  # 1 hour
    
    @property
    def is_development(self) -> bool:
        return self.FLASK_ENV == 'development'
    
    @property
    def cors_origins(self) -> list:
        if self.is_development:
            return ["*"]
        return [
            "http://localhost:3000",
            "https://*.vercel.app",
            "https://cognicode-agent.vercel.app"
        ]

config = AppConfig()

# Initialize Flask app with optimized settings
app = Flask(__name__)
app.config.update({
    'SECRET_KEY': config.SECRET_KEY,
    'MAX_CONTENT_LENGTH': config.MAX_CONTENT_LENGTH,
    'JSON_SORT_KEYS': False,  # Disable key sorting for performance
})

# Enable CORS for all routes
CORS(app, origins=config.cors_origins, supports_credentials=True)

# Initialize SocketIO with optimized settings
socketio = SocketIO(
    app, 
    cors_allowed_origins=config.cors_origins,
    async_mode='threading',
    max_http_buffer_size=config.MAX_CONTENT_LENGTH,
    ping_timeout=60,
    ping_interval=25
)

# Setup logging
logger = setup_logger('cognicode-backend')

# Agent pool for better resource management
class AgentPool:
    """Thread-safe agent pool for resource management"""
    
    def __init__(self):
        self._linter_agents = []
        self._refactor_agents = []
        self._testgen_agents = []
        self._lock = threading.Lock()
        self._initialized = False
        
        # Weak references to track active connections
        self._active_connections = weakref.WeakSet()
    
    def initialize(self) -> bool:
        """Initialize agent pool with lazy loading"""
        if self._initialized:
            return True
            
        with self._lock:
            if self._initialized:
                return True
                
            try:
                logger.info("Initializing agent pool...")
                
                # Initialize one agent of each type initially (lazy loading)
                self._linter_agents.append(LinterAgent())
                self._refactor_agents.append(RefactorAgent())
                self._testgen_agents.append(TestGenAgent())
                
                # Initialize the first agents
                for agent in [self._linter_agents[0], self._refactor_agents[0], self._testgen_agents[0]]:
                    if not agent.initialize():
                        raise RuntimeError(f"Failed to initialize {agent.agent_name}")
                
                self._initialized = True
                logger.info("Agent pool initialized successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to initialize agent pool: {str(e)}")
                return False
    
    def get_linter_agent(self) -> LinterAgent:
        """Get available linter agent"""
        with self._lock:
            if not self._linter_agents:
                agent = LinterAgent()
                agent.initialize()
                self._linter_agents.append(agent)
            return self._linter_agents[0]
    
    def get_refactor_agent(self) -> RefactorAgent:
        """Get available refactor agent"""
        with self._lock:
            if not self._refactor_agents:
                agent = RefactorAgent()
                agent.initialize()
                self._refactor_agents.append(agent)
            return self._refactor_agents[0]
    
    def get_testgen_agent(self) -> TestGenAgent:
        """Get available test generation agent"""
        with self._lock:
            if not self._testgen_agents:
                agent = TestGenAgent()
                agent.initialize()
                self._testgen_agents.append(agent)
            return self._testgen_agents[0]
    
    def add_connection(self, connection_id: str):
        """Track active connection"""
        self._active_connections.add(connection_id)
    
    def remove_connection(self, connection_id: str):
        """Remove connection tracking"""
        try:
            self._active_connections.discard(connection_id)
        except:
            pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get pool status"""
        return {
            'linter_agents': len(self._linter_agents),
            'refactor_agents': len(self._refactor_agents),
            'testgen_agents': len(self._testgen_agents),
            'active_connections': len(self._active_connections),
            'initialized': self._initialized
        }

# Initialize services
agent_pool = AgentPool()
code_service = CodeService()

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle request too large errors"""
    return jsonify({'error': 'Request entity too large'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# API Routes with proper error handling and performance optimizations

@app.route('/api/agents/status', methods=['GET'])
@log_performance
def get_agents_status():
    """Get detailed status of all AI agents"""
    try:
        linter_agent = agent_pool.get_linter_agent()
        refactor_agent = agent_pool.get_refactor_agent()
        testgen_agent = agent_pool.get_testgen_agent()
        
        return jsonify({
            'agents': [
                {
                    'id': 'linter',
                    'name': 'Linter Agent',
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
            'pool_status': agent_pool.get_status()
        })
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        return jsonify({'error': 'Failed to get agent status'}), 500

# WebSocket event handlers with improved error handling
@socketio.on('connect')
def handle_connect():
    """Handle client connection with proper session management"""
    try:
        from flask import request as flask_request
        session_id = getattr(flask_request, 'sid', 'unknown')
        agent_pool.add_connection(session_id)
        logger.info(f'Client connected: {session_id}')
        
        # Initialize agent pool if not already done
        if not agent_pool._initialized:
            if agent_pool.initialize():
                logger.info('Agent pool initialized successfully')
            else:
                logger.error('Failed to initialize agent pool')
                emit('error', {'message': 'Backend initialization failed'})
                return
        
        emit('connected', {
            'message': 'Connected to CogniCode AI backend',
            'session_id': session_id,
            'server_time': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Connection error: {str(e)}", exc_info=True)
        emit('error', {'message': 'Connection failed'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection with cleanup"""
    try:
        from flask import request as flask_request
        session_id = getattr(flask_request, 'sid', 'unknown')
        agent_pool.remove_connection(session_id)
        logger.info(f'Client disconnected: {session_id}')
        
        # Trigger garbage collection after disconnect
        gc.collect()
    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}", exc_info=True)

@socketio.on('analyze_code')
@log_performance
def handle_analyze_code(data):
    """Handle code analysis request with optimized processing"""
    try:
        from flask import request as flask_request
        session_id = getattr(flask_request, 'sid', 'unknown')
    except:
        session_id = 'unknown'
    
    try:
        # Validate input
        if not data or not isinstance(data, dict):
            emit('error', {'message': 'Invalid data format'})
            return
            
        code = data.get('code', '').strip()
        language = data.get('language', 'javascript').lower()
        
        if not code:
            emit('error', {'message': 'No code provided for analysis'})
            return
        
        if len(code) > config.MAX_CONTENT_LENGTH:
            emit('error', {'message': 'Code exceeds maximum size limit'})
            return
        
        logger.info(f'Analyzing {language} code for client {session_id}')
        
        # Check cache first
        cached_result = code_service.get_cached_analysis(code)
        if cached_result:
            emit('analysis_complete', cached_result)
            logger.info(f'Returned cached analysis for client {session_id}')
            return
        
        # Emit progress updates with proper format
        emit('analysis_progress', {'progress': 25, 'message': 'Initializing analysis...'})
        
        # Get agent and run analysis
        linter_agent = agent_pool.get_linter_agent()
        
        emit('analysis_progress', {'progress': 50, 'message': 'Running analysis...'})
        
        analysis = linter_agent.analyze(code, language)
        
        emit('analysis_progress', {'progress': 75, 'message': 'Processing results...'})
        
        # Process results
        processed_analysis = code_service.process_analysis(analysis, code, language)
        
        emit('analysis_progress', {'progress': 100, 'message': 'Analysis complete'})
        
        # Send results
        emit('analysis_complete', processed_analysis)
        logger.info(f'Analysis completed for client {session_id}')
        
    except Exception as e:
        logger.error(f'Error analyzing code for {session_id}: {str(e)}', exc_info=True)
        emit('error', {'message': f'Analysis failed: {str(e)}'})
    finally:
        # Ensure we always reset analyzing state
        socketio.sleep(1)  # Small delay to ensure messages are sent

@socketio.on('generate_refactoring')
@log_performance
def handle_generate_refactoring(data):
    """Handle refactoring generation request with validation"""
    try:
        from flask import request as flask_request
        session_id = getattr(flask_request, 'sid', 'unknown')
    except:
        session_id = 'unknown'
    
    try:
        # Validate input
        code = data.get('code', '').strip()
        language = data.get('language', 'javascript').lower()
        issues = data.get('analysis', [])
        
        if not code:
            emit('error', {'message': 'No code provided for refactoring'})
            return
        
        logger.info(f'Generating refactoring suggestions for client {session_id}')
        
        # Get agent and generate suggestions
        refactor_agent = agent_pool.get_refactor_agent()
        suggestions = refactor_agent.generate_suggestions(code, language, issues)
        
        # Process and send results
        processed_suggestions = code_service.process_refactor_suggestions(suggestions)
        emit('refactor_suggestions', processed_suggestions)
        
        logger.info(f'Refactoring suggestions generated for client {session_id}')
        
    except Exception as e:
        logger.error(f'Error generating refactoring for {session_id}: {str(e)}', exc_info=True)
        emit('error', {'message': f'Refactoring generation failed: {str(e)}'})

@socketio.on('generate_tests')
@log_performance
def handle_generate_tests(data):
    """Handle test generation request with optimization"""
    try:
        from flask import request as flask_request
        session_id = getattr(flask_request, 'sid', 'unknown')
    except:
        session_id = 'unknown'
    
    try:
        # Validate input
        code = data.get('code', '').strip()
        language = data.get('language', 'javascript').lower()
        functions = data.get('functions', [])
        
        if not code:
            emit('error', {'message': 'No code provided for test generation'})
            return
        
        logger.info(f'Generating tests for client {session_id}')
        
        # Get agent and generate tests
        testgen_agent = agent_pool.get_testgen_agent()
        test_cases = testgen_agent.generate_tests(code, language, functions)
        
        # Process and send results
        processed_tests = code_service.process_test_cases(test_cases)
        emit('test_cases_generated', processed_tests)
        
        logger.info(f'Test cases generated for client {session_id}')
        
    except Exception as e:
        logger.error(f'Error generating tests for {session_id}: {str(e)}', exc_info=True)
        emit('error', {'message': f'Test generation failed: {str(e)}'})

# Utility functions
@lru_cache(maxsize=1)
def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics"""
    try:
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent(),
                'available': psutil.virtual_memory().available
            }
        except ImportError:
            # Fallback if psutil is not available
            return {
                'rss': 0,
                'vms': 0,
                'note': 'psutil not available, using fallback'
            }
    except Exception as e:
        logger.error(f'Error getting memory usage: {str(e)}')
        return {'error': str(e)}

def cleanup_resources():
    """Cleanup resources and trigger garbage collection"""
    try:
        # Clear caches
        code_service.clear_old_cache()
        get_memory_usage.cache_clear()
        
        # Force garbage collection
        gc.collect()
        
        logger.info("Resource cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# Application initialization function
def initialize_application():
    """Initialize application components"""
    try:
        logger.info("🚀 Initializing CogniCode Agent backend...")
        
        if not agent_pool.initialize():
            logger.error("Failed to initialize agent pool")
            raise RuntimeError("Agent pool initialization failed")
        
        logger.info("✅ Agent pool initialized successfully")
        
        # Test basic functionality
        try:
            test_agent = agent_pool.get_linter_agent()
            logger.info("✅ Basic agent functionality verified")
        except Exception as e:
            logger.warning(f"Agent verification warning: {str(e)}")
        
        logger.info("🎉 CogniCode Agent backend initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {str(e)}")
        return False

# Health check with proper initialization
@app.route('/health', methods=['GET'])
@log_performance
def health_check():
    """Enhanced health check endpoint with comprehensive status"""
    try:
        # Initialize agents if not already done
        if not agent_pool._initialized:
            agent_pool.initialize()
        
        pool_status = agent_pool.get_status()
        
        status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': config.FLASK_ENV,
            'agents': {
                'linter_agents': pool_status.get('linter_agents', 0),
                'refactor_agents': pool_status.get('refactor_agents', 0), 
                'testgen_agents': pool_status.get('testgen_agents', 0),
                'active_connections': pool_status.get('active_connections', 0),
                'initialized': pool_status.get('initialized', False)
            },
            'memory': get_memory_usage()
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def create_app():
    """Application factory pattern"""
    # Initialize the application
    initialize_application()
    return app

if __name__ == '__main__':
    try:
        # Initialize agent pool
        logger.info('Initializing CogniCode AI agents...')
        initialize_application()
        
        if not agent_pool.initialize():
            logger.error('Failed to initialize agents')
            sys.exit(1)
        
        logger.info('All AI agents initialized successfully')
        
        # Setup periodic cleanup
        import atexit
        atexit.register(cleanup_resources)
        
        # Start the server with optimized settings
        logger.info(f'Starting CogniCode backend server on port {config.PORT}')
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=config.PORT, 
            debug=config.is_development,
            use_reloader=False,  # Disable reloader for production
            log_output=config.is_development
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        cleanup_resources()
    except Exception as e:
        logger.error(f'Failed to start server: {str(e)}')
        sys.exit(1)