"""
Base Agent class for CogniCode AI agents
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all CogniCode AI agents"""
    
    def __init__(self, agent_name: str, model_name: str = None):
        self.agent_name = agent_name
        self.model_name = model_name or f"default-{agent_name.lower()}"
        self.status = 'idle'
        self.last_run = None
        self.model = None
        self.tokenizer = None
        self.logger = logging.getLogger(f'cognicode.agents.{agent_name.lower()}')
        
    def initialize(self) -> bool:
        """Initialize the agent and load required models"""
        try:
            self.logger.info(f'Initializing {self.agent_name}...')
            self.status = 'initializing'
            
            # Load model (implementation specific)
            self._load_model()
            
            self.status = 'ready'
            self.logger.info(f'{self.agent_name} initialized successfully')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to initialize {self.agent_name}: {str(e)}')
            self.status = 'error'
            return False
    
    @abstractmethod
    def _load_model(self):
        """Load the specific model for this agent"""
        pass
    
    @abstractmethod
    def process(self, code: str, language: str, **kwargs) -> Dict[str, Any]:
        """Process the code and return results"""
        pass
    
    def _preprocess_code(self, code: str, language: str) -> str:
        """Preprocess code before analysis"""
        # Remove excessive whitespace
        lines = code.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # Remove empty lines at the beginning and end
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
    
    def _postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess results before returning"""
        results['agent'] = self.agent_name
        results['model'] = self.model_name
        results['timestamp'] = datetime.utcnow().isoformat()
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'name': self.agent_name,
            'status': self.status,
            'model': self.model_name,
            'last_run': self.last_run.isoformat() if self.last_run else None
        }