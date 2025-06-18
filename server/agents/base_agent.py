"""
Base Agent class for CogniCode AI agents with improved performance and memory management
"""

import os
import logging
import weakref
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import threading
import gc

class BaseAgent(ABC):
    """Base class for all CogniCode AI agents with optimized resource management"""
    
    def __init__(self, agent_name: str, model_name: Optional[str] = None):
        self.agent_name = agent_name
        self.model_name = model_name or f"default-{agent_name.lower()}"
        self.status = 'idle'
        self.last_run: Optional[datetime] = None
        self.model = None
        self.tokenizer = None
        self.logger = logging.getLogger(f'cognicode.agents.{agent_name.lower()}')
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Weak references for memory management
        self._cache = weakref.WeakValueDictionary()
        
        # Performance tracking
        self._performance_stats = {
            'total_runs': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'last_performance': 0.0
        }
        
    def initialize(self) -> bool:
        """Initialize the agent and load required models with error handling"""
        with self._lock:
            try:
                if self.status == 'ready':
                    return True
                    
                self.logger.info(f'Initializing {self.agent_name}...')
                self.status = 'initializing'
                
                # Load model (implementation specific)
                success = self._load_model()
                
                if success:
                    self.status = 'ready'
                    self.logger.info(f'{self.agent_name} initialized successfully')
                    return True
                else:
                    self.status = 'error'
                    self.logger.error(f'Failed to initialize {self.agent_name}')
                    return False
                    
            except Exception as e:
                self.logger.error(f'Failed to initialize {self.agent_name}: {str(e)}')
                self.status = 'error'
                return False
    
    @abstractmethod
    def _load_model(self) -> bool:
        """Load the specific model for this agent"""
        pass
    
    @abstractmethod
    def process(self, code: str, language: str, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Process the code and return results"""
        pass
    
    def _preprocess_code(self, code: str, language: str) -> str:
        """Preprocess code before analysis with performance optimization"""
        if not code or not code.strip():
            return ""
        
        # Use more efficient string operations
        lines = code.splitlines()
        
        # Remove excessive whitespace efficiently
        cleaned_lines = [line.rstrip() for line in lines if line.strip() or len(lines) < 100]
        
        # Remove empty lines at the beginning and end
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
    
    def _postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess results before returning with metadata"""
        if not isinstance(results, dict):
            results = {'data': results}
            
        results.update({
            'agent': self.agent_name,
            'model': self.model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'performance': self._performance_stats['last_performance']
        })
        return results
    
    def _track_performance(self, start_time: datetime, end_time: datetime):
        """Track performance metrics"""
        duration = (end_time - start_time).total_seconds()
        
        with self._lock:
            self._performance_stats['total_runs'] += 1
            self._performance_stats['total_time'] += duration
            self._performance_stats['avg_time'] = (
                self._performance_stats['total_time'] / self._performance_stats['total_runs']
            )
            self._performance_stats['last_performance'] = duration
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status with performance metrics"""
        return {
            'name': self.agent_name,
            'status': self.status,
            'model': self.model_name,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'performance': self._performance_stats.copy(),
            'cache_size': len(self._cache)
        }
    
    def cleanup(self):
        """Cleanup resources and trigger garbage collection"""
        try:
            with self._lock:
                self._cache.clear()
                gc.collect()
                self.logger.debug(f"Cleaned up resources for {self.agent_name}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction