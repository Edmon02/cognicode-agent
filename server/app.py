"""
CogniCode Agent - Flask Backend Server
Multi-agent AI system for code analysis, refactoring, and test generation
"""

import os
import sys
from datetime import datetime
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
from utils.logger import setup_logger

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cognicode-secret-key-2025'

# Determine if we're in development mode
is_development = os.environ.get('FLASK_ENV') == 'development'

# Configure CORS origins based on environment
if is_development:
    cors_origins = "*"
else:
    cors_origins = ["http://localhost:3000", "https://*.vercel.app"]

# Enable CORS for all routes
CORS(app, origins=cors_origins)

# Initialize SocketIO with CORS support
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins,
    async_mode='threading'
)

# Setup logging
logger = setup_logger('cognicode-backend')

# Initialize AI agents
linter_agent = LinterAgent()
refactor_agent = RefactorAgent()
testgen_agent = TestGenAgent()
code_service = CodeService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'agents': {
            'linter': linter_agent.status,
            'refactor': refactor_agent.status,
            'testgen': testgen_agent.status
        }
    })

@app.route('/api/agents/status', methods=['GET'])
def get_agents_status():
    """Get status of all AI agents"""
    return jsonify({
        'agents': [
            {
                'id': 'linter',
                'name': 'Linter Agent',
                'status': linter_agent.status,
                'capabilities': ['bug_detection', 'style_analysis', 'security_check'],
                'model': linter_agent.model_name
            },
            {
                'id': 'refactor',
                'name': 'Refactor Agent',
                'status': refactor_agent.status,
                'capabilities': ['code_optimization', 'pattern_improvement', 'performance_tuning'],
                'model': refactor_agent.model_name
            },
            {
                'id': 'testgen',
                'name': 'Test Generation Agent',
                'status': testgen_agent.status,
                'capabilities': ['unit_tests', 'integration_tests', 'edge_cases'],
                'model': testgen_agent.model_name
            }
        ]
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to CogniCode AI backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('analyze_code')
def handle_analyze_code(data):
    """Handle code analysis request"""
    try:
        code = data.get('code', '')
        language = data.get('language', 'javascript')
        
        logger.info(f'Analyzing {language} code for client {request.sid}')
        
        # Emit progress updates
        emit('analysis_progress', 25)
        
        # Run linter agent
        analysis = linter_agent.analyze(code, language)
        emit('analysis_progress', 75)
        
        # Process results
        processed_analysis = code_service.process_analysis(analysis, code, language)
        emit('analysis_progress', 100)
        
        # Send results
        emit('analysis_complete', processed_analysis)
        logger.info(f'Analysis completed for client {request.sid}')
        
    except Exception as e:
        logger.error(f'Error analyzing code: {str(e)}')
        emit('error', f'Analysis failed: {str(e)}')

@socketio.on('generate_refactoring')
def handle_generate_refactoring(data):
    """Handle refactoring generation request"""
    try:
        code = data.get('code', '')
        language = data.get('language', 'javascript')
        issues = data.get('analysis', [])
        
        logger.info(f'Generating refactoring suggestions for client {request.sid}')
        
        # Run refactor agent
        suggestions = refactor_agent.generate_suggestions(code, language, issues)
        
        # Process and send results
        processed_suggestions = code_service.process_refactor_suggestions(suggestions)
        emit('refactor_suggestions', processed_suggestions)
        
        logger.info(f'Refactoring suggestions generated for client {request.sid}')
        
    except Exception as e:
        logger.error(f'Error generating refactoring: {str(e)}')
        emit('error', f'Refactoring generation failed: {str(e)}')

@socketio.on('generate_tests')
def handle_generate_tests(data):
    """Handle test generation request"""
    try:
        code = data.get('code', '')
        language = data.get('language', 'javascript')
        functions = data.get('functions', [])
        
        logger.info(f'Generating tests for client {request.sid}')
        
        # Run test generation agent
        test_cases = testgen_agent.generate_tests(code, language, functions)
        
        # Process and send results
        processed_tests = code_service.process_test_cases(test_cases)
        emit('test_cases_generated', processed_tests)
        
        logger.info(f'Test cases generated for client {request.sid}')
        
    except Exception as e:
        logger.error(f'Error generating tests: {str(e)}')
        emit('error', f'Test generation failed: {str(e)}')

if __name__ == '__main__':
    # Initialize agents on startup
    logger.info('Initializing CogniCode AI agents...')
    
    try:
        linter_agent.initialize()
        refactor_agent.initialize()
        testgen_agent.initialize()
        logger.info('All AI agents initialized successfully')
    except Exception as e:
        logger.error(f'Failed to initialize agents: {str(e)}')
        sys.exit(1)
    
    # Start the server
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f'Starting CogniCode backend server on port {port}')
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        allow_unsafe_werkzeug=True
    )