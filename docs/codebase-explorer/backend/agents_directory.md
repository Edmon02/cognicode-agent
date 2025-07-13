# The Brains: `server/agents/` – Our Specialized AI Experts

Welcome to the `agents/` directory, the intellectual core of CogniCode Agent's backend! This is where our team of specialized AI "agents" resides. Each agent is a Python class designed to perform a specific type of code analysis, refactoring, or test generation, leveraging powerful pre-trained AI models.

Think of this directory as the "Department of Specialized AI Research" within our backend. Each agent is a lead researcher in its field.

## The Agent Philosophy: Divide and Conquer

Instead of one massive AI trying to do everything, we've adopted a multi-agent architecture. This means:
*   **Specialization:** Each agent focuses on what it does best.
*   **Modularity:** Agents can be developed, updated, and even replaced independently.
*   **Clarity:** The purpose of each agent is clear and distinct.
*   **Resource Management:** We can potentially load different AI models for different agents, optimizing resource use.

## Key Files We'll Explore:

1.  **`base_agent.py`**: The foundational blueprint. This abstract base class likely defines the common interface, properties, and perhaps some shared utilities (like model loading or caching stubs) that all concrete agents will inherit or implement. Understanding the base agent is key to understanding how all other agents are structured.
2.  **`linter_agent.py` (Example Concrete Agent)**: We'll take a deep dive into the Linter Agent as a representative example. This will show us how a specific agent implements the base agent's contract, loads its particular AI model (e.g., CodeBERT), processes code, and generates its specific type of output (linting issues, code metrics).
3.  **Other Agents (`refactor_agent.py`, `testgen_agent.py`)**: While we'll focus in detail on the Linter Agent, we'll also touch upon the roles and likely mechanisms of the Refactor and Test Generation agents based on our understanding of the system.

Let's meet the brains behind the operation!

---

---

## 🏛️ `base_agent.py`: The Agent Blueprint – Foundation for Intelligence

The `base_agent.py` file defines the `BaseAgent` class, which serves as the abstract foundation for all specialized AI agents within CogniCode. Think of it as the master blueprint from which all our expert agent researchers (`LinterAgent`, `RefactorAgent`, `TestGenAgent`) derive their core structure and shared functionalities.

**Purpose of `BaseAgent`:**
*   To establish a common interface that all concrete agent classes must adhere to (via abstract methods).
*   To provide shared attributes and functionalities like status tracking, performance monitoring, logging, basic caching, and resource cleanup.
*   To enforce a consistent initialization pattern.
*   To promote code reuse and a standardized way of interacting with agents.

Let's delve into the architecture of this foundational class:

```python
# server/agents/base_agent.py
"""
Base Agent class for CogniCode AI agents with improved performance and memory management
"""

import os
import logging
import weakref # For memory-efficient caching
from abc import ABC, abstractmethod # For creating abstract base classes
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import threading # For thread safety
import gc # For garbage collection

class BaseAgent(ABC): # 1. Inherits from ABC to become an Abstract Base Class
    """Base class for all CogniCode AI agents with optimized resource management"""

    def __init__(self, agent_name: str, model_name: Optional[str] = None):
        # 2. Core attributes initialized for every agent
        self.agent_name = agent_name # Name of the specific agent (e.g., "LinterAgent")
        self.model_name = model_name or f"default-{agent_name.lower()}" # Associated AI model name
        self.status = 'idle' # Initial status: idle, initializing, ready, running, error
        self.last_run: Optional[datetime] = None # Timestamp of the last processing run
        self.model = None # Placeholder for the loaded AI model instance
        self.tokenizer = None # Placeholder for the model's tokenizer

        # 3. Dedicated logger for each agent instance
        self.logger = logging.getLogger(f'cognicode.agents.{agent_name.lower()}')

        # 4. Threading lock for ensuring thread-safe operations on agent's state
        self._lock = threading.Lock()

        # 5. WeakValueDictionary for caching results without preventing garbage collection
        # of cached values if they are no longer strongly referenced elsewhere.
        self._cache = weakref.WeakValueDictionary()

        # 6. Dictionary for tracking performance metrics
        self._performance_stats = {
            'total_runs': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'last_performance': 0.0 # Duration of the last run
        }

    # 7. Initialization method (called by AgentPool or explicitly)
    def initialize(self) -> bool:
        """Initialize the agent and load required models with error handling."""
        with self._lock: # Ensure thread-safe initialization
            try:
                if self.status == 'ready': # If already initialized, do nothing
                    return True

                self.logger.info(f'Initializing {self.agent_name}...')
                self.status = 'initializing'

                # 8. Call the abstract _load_model() method (implemented by subclasses)
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

    # 9. Abstract method: _load_model - must be implemented by subclasses
    @abstractmethod
    def _load_model(self) -> bool:
        """Load the specific model for this agent.
        Subclasses must implement this to load their respective AI models and tokenizers.
        Should set self.model and self.tokenizer.
        Returns True on success, False on failure.
        """
        pass

    # 10. Abstract method: process - must be implemented by subclasses
    @abstractmethod
    def process(self, code: str, language: str, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Process the code and return results.
        This is the main entry point for an agent to perform its specific task.
        Subclasses must implement this method.
        **kwargs allows for additional parameters specific to an agent.
        """
        pass

    # 11. Utility method: _preprocess_code
    def _preprocess_code(self, code: str, language: str) -> str:
        """Preprocess code before analysis with performance optimization.
        Removes excessive whitespace and empty lines.
        """
        if not code or not code.strip(): # Handle empty or whitespace-only code
            return ""

        lines = code.splitlines() # Split into lines

        # Efficiently remove trailing whitespace from each line.
        # Conditionally keeps lines if they are not blank OR if the total number of lines is small.
        # This condition `len(lines) < 100` seems a bit arbitrary for keeping blank lines
        # in short code snippets; its intent might need clarification. Usually, all blank lines
        # (especially those made of only whitespace) are stripped if not significant.
        cleaned_lines = [line.rstrip() for line in lines if line.strip() or len(lines) < 100]

        # Remove empty lines from the beginning of the list
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        # Remove empty lines from the end of the list
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()

        return '\n'.join(cleaned_lines) # Join back into a single string

    # 12. Utility method: _postprocess_results
    def _postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess results before returning by adding common metadata."""
        if not isinstance(results, dict): # Ensure results is a dictionary
            # If not, wrap it in a dictionary for consistent metadata addition.
            results = {'data': results}

        # Add standard metadata to all agent results
        results.update({
            'agent': self.agent_name,
            'model': self.model_name,
            'timestamp': datetime.utcnow().isoformat(), # ISO 8601 timestamp
            'performance': self._performance_stats['last_performance'] # Duration of last run
        })
        return results

    # 13. Utility method: _track_performance
    def _track_performance(self, start_time: datetime, end_time: datetime):
        """Track performance metrics for agent runs."""
        duration = (end_time - start_time).total_seconds() # Calculate duration in seconds

        with self._lock: # Ensure thread-safe updates to performance stats
            self._performance_stats['total_runs'] += 1
            self._performance_stats['total_time'] += duration
            self._performance_stats['avg_time'] = (
                self._performance_stats['total_time'] / self._performance_stats['total_runs']
            )
            self._performance_stats['last_performance'] = duration # Store duration of this specific run

    # 14. Method to get current status and performance info
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status with performance metrics."""
        return {
            'name': self.agent_name,
            'status': self.status,
            'model': self.model_name,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'performance': self._performance_stats.copy(), # Return a copy to prevent external modification
            'cache_size': len(self._cache) # Current size of the weak-value cache
        }

    # 15. Method for resource cleanup
    def cleanup(self):
        """Cleanup resources like the cache and trigger garbage collection."""
        try:
            with self._lock: # Thread-safe cleanup
                self._cache.clear() # Clear the weak-value dictionary
                gc.collect() # Suggest garbage collection
                self.logger.debug(f"Cleaned up resources for {self.agent_name}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    # 16. Destructor method
    def __del__(self):
        """Destructor to attempt cleanup when an agent instance is garbage collected."""
        try:
            self.cleanup() # Call the main cleanup method
        except:
            # It's generally advisable to avoid errors in __del__ or keep them minimal.
            # Silently passing here prevents errors during garbage collection from propagating.
            pass
```

**Unpacking the `BaseAgent` Blueprint:**

1.  **`class BaseAgent(ABC):`**: By inheriting from `ABC` (Abstract Base Class) from the `abc` module, `BaseAgent` declares itself as an abstract class. This means it cannot be instantiated directly and is intended to be subclassed.

2.  **`__init__(self, agent_name: str, model_name: Optional[str] = None)`**: The constructor initializes common attributes:
    *   `agent_name`: A string identifying the type of agent (e.g., "LinterAgent").
    *   `model_name`: The name or identifier of the AI model this agent will use. If not provided, it defaults to a generic name like "default-linteragent".
    *   `status`: Tracks the agent's current state ('idle', 'initializing', 'ready', 'running', 'error').
    *   `last_run`: A `datetime` object storing when the agent last processed something.
    *   `model` & `tokenizer`: Initialized to `None`; these will be populated by the subclass's `_load_model()` method.

3.  **`self.logger = logging.getLogger(...)`**: Each agent instance gets its own dedicated logger instance, named hierarchically (e.g., `cognicode.agents.linteragent`). This allows for fine-grained logging configuration and filtering if needed.

4.  **`self._lock = threading.Lock()`**: A `threading.Lock` is created for each agent. This is used to synchronize access to shared mutable state within the agent instance (like `_performance_stats` or during initialization) if the agent's methods could be called concurrently from different threads.

5.  **`self._cache = weakref.WeakValueDictionary()`**: This is a clever choice for a cache. A `WeakValueDictionary` stores values as weak references. This means that if a cached result is the *only* reference to that result object, the object can still be garbage collected by Python. This helps prevent the cache from keeping large result objects in memory indefinitely if they are no longer needed elsewhere, making it memory-efficient.

6.  **`self._performance_stats`**: A dictionary to store various performance metrics like total runs, total processing time, average time per run, and the duration of the most recent run.

7.  **`initialize(self) -> bool`**:
    *   This public method is intended to be called to perform the potentially expensive setup for an agent, primarily loading its AI model.
    *   It's thread-safe due to `with self._lock:`.
    *   It checks `self.status` to prevent re-initialization if already 'ready'.
    *   It sets the status to 'initializing', then calls the abstract `_load_model()` method.
    *   Based on the success of `_load_model()`, it updates the status to 'ready' or 'error' and logs the outcome.

8.  **`@abstractmethod def _load_model(self) -> bool:`**:
    *   This decorator marks `_load_model` as an abstract method. Subclasses of `BaseAgent` *must* implement this method.
    *   Its responsibility is to load the specific AI model and tokenizer required by the agent and assign them to `self.model` and `self.tokenizer`.
    *   It should return `True` if loading was successful, `False` otherwise.

9.  **`@abstractmethod def process(self, code: str, language: str, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:`**:
    *   Another abstract method that defines the main entry point for an agent's core functionality. Each specialized agent (Linter, Refactor, TestGen) will implement `process` to perform its unique task on the given `code` and `language`.
    *   `**kwargs` allows concrete agent implementations to accept additional, agent-specific parameters if needed.
    *   The return type `Union[Dict[str, Any], List[Dict[str, Any]]]` suggests that results can be a single dictionary or a list of dictionaries.

10. **`_preprocess_code(self, code: str, language: str) -> str`**:
    *   A utility method to perform basic cleaning of the input code before it's passed to an AI model or further analysis.
    *   It removes trailing whitespace from lines and strips blank lines from the beginning and end of the code.
    *   The condition `len(lines) < 100` in the list comprehension for `cleaned_lines` is a bit unusual. It means if the code has fewer than 100 lines, it will keep lines that are *only* whitespace (after `rstrip`), which might not always be desired. Typically, `if line.strip()` is sufficient to remove truly blank lines. This might be a specific choice to preserve some formatting in very short snippets.

11. **`_postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]`**:
    *   A utility method to add common metadata to the results returned by an agent.
    *   It ensures the `results` are in a dictionary (wrapping non-dict results if necessary).
    *   It adds the `agent` name, `model` name, a `timestamp` (in ISO 8601 format), and the `performance` (duration of the last run) to the results dictionary. This standardizes the output format across different agents.

12. **`_track_performance(self, start_time: datetime, end_time: datetime)`**:
    *   Calculates the duration of a processing run.
    *   Updates the `_performance_stats` dictionary in a thread-safe manner using `self._lock`.

13. **`get_status(self) -> Dict[str, Any]`**:
    *   Returns a dictionary containing the agent's current status, model name, last run time, a copy of its performance statistics, and the current size of its `_cache`. This is used by the `/api/agents/status` endpoint in `app.py`.

14. **`cleanup(self)`**:
    *   Provides a way to explicitly clean up resources used by the agent, primarily by clearing its `_cache` and suggesting garbage collection with `gc.collect()`.

15. **`__del__(self)`**:
    *   The destructor method. Python calls `__del__` when an object is about to be garbage collected.
    *   It attempts to call `self.cleanup()`. The `try-except pass` is important because destructors should generally not raise exceptions, as it can complicate the garbage collection process.

**`BaseAgent` is a well-thought-out abstract class that provides a strong, consistent foundation for building specialized AI agents. It handles common concerns like initialization, status tracking, logging, performance metrics, basic caching, and thread safety, allowing subclasses to focus on their specific AI model loading and processing logic.** The use of abstract methods ensures that concrete agents conform to a required interface.

---
Return to: [Backend Overview](README.md) | [Agents Directory Overview](#the-brains-serveragents--our-specialized-ai-experts)
Next Agent: [`linter_agent.py`](#-linter_agentpy-the-code-detective)

---

## 🕵️ `linter_agent.py`: The Code Detective - Uncovering Issues

The `LinterAgent` is our specialized AI agent responsible for static code analysis. Its mission is to meticulously examine source code to detect potential bugs, style violations, performance inefficiencies, and other issues without actually executing the code. It extends the `BaseAgent` and implements the logic for language-specific analysis, leveraging both rule-based checks and insights from AI models (though the AI model interaction is simulated in the provided code).

**Purpose of `LinterAgent`:**
*   To analyze code written in various supported languages (JavaScript, TypeScript, Python, Java).
*   To identify and report issues categorized by severity (error, warning, info).
*   To calculate basic code metrics (complexity, maintainability, lines of code).
*   To extract information about functions within the code.
*   To provide suggestions for fixing identified issues where possible.

Let's break down how this detective operates:

```python
# server/agents/linter_agent.py
"""
Linter Agent for code analysis and bug detection
Uses CodeBERT and rule-based analysis for comprehensive code linting
Optimized for performance and memory efficiency
"""

import re # For regular expression operations
import ast # For Abstract Syntax Tree parsing (used in Python analysis)
import json # Not explicitly used in snippet, but often useful for structured data
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent # Import the parent class

# 1. LinterAgent class definition, inheriting from BaseAgent
class LinterAgent(BaseAgent):
    """AI agent for code linting and bug detection with optimized processing"""

    def __init__(self):
        # 2. Initialize BaseAgent with agent name and default model name
        super().__init__('LinterAgent', 'microsoft/codebert-base')
        # 3. Dictionary mapping languages to their specific analysis methods
        self.language_parsers = {
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'python': self._analyze_python,
            'java': self._analyze_java,
            # Other languages could be added here
        }

    # 4. Implementation of the abstract _load_model method
    def _load_model(self) -> bool:
        """Load CodeBERT model for code analysis (Simulated)."""
        try:
            # In a real-world scenario, this is where you'd use:
            # from transformers import AutoTokenizer, AutoModel
            # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            # self.model = AutoModel.from_pretrained(self.model_name)
            # self.logger.info(f"Successfully loaded model and tokenizer: {self.model_name}")

            # For demonstration/current state, we simulate model loading:
            self.logger.info(f'Simulating load of {self.model_name} for code analysis...')
            self.model = "simulated_codebert_model_instance" # Placeholder for actual model object
            self.tokenizer = "simulated_tokenizer_instance" # Placeholder for actual tokenizer
            self.logger.info(f'{self.model_name} (simulated) loaded successfully.')
            return True # Indicate success

        except Exception as e:
            self.logger.error(f'Failed to load model {self.model_name}: {str(e)}')
            return False # Indicate failure

    # 5. Main analysis method (could also be named 'process' to match BaseAgent more directly)
    def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code for bugs, style issues, and improvements."""
        start_time = datetime.utcnow() # Record start time for performance tracking

        try:
            self.status = 'running' # Set agent status
            self.last_run = start_time

            if not code or not code.strip(): # Basic input validation
                # Return a default empty result structure if no code is provided
                return self._postprocess_results({
                    'issues': [],
                    'metrics': {'complexity': 0, 'maintainability': 10, 'lines_of_code': 0, 'codeQualityScore': 10},
                    'functions': [],
                    'ai_insights': {}
                })

            cleaned_code = self._preprocess_code(code, language) # Use preprocessing from BaseAgent

            # 6. Language-specific dispatching
            if language in self.language_parsers:
                # Call the appropriate private analysis method based on language
                results = self.language_parsers[language](cleaned_code)
            else:
                # Fallback to a generic analysis if the language is not specifically supported
                results = self._generic_analysis(cleaned_code)

            # 7. Simulate AI-based insights (would involve model inference in a real scenario)
            ai_insights = self._ai_analysis(cleaned_code, language)
            results['ai_insights'] = ai_insights # Add AI insights to the results

            self.status = 'ready' # Reset status after successful run
            end_time = datetime.utcnow()
            self._track_performance(start_time, end_time) # Track performance

            return self._postprocess_results(results) # Add common metadata via BaseAgent method

        except Exception as e:
            self.logger.error(f'Analysis failed for language {language}: {str(e)}', exc_info=True)
            self.status = 'error' # Set error status
            end_time = datetime.utcnow()
            self._track_performance(start_time, end_time) # Still track performance even on error
            # Re-raise the exception so it can be caught by the caller in app.py
            # which will then emit an error to the frontend.
            raise

    # --- Language-Specific Analysis Methods ---
    # These methods implement the actual linting logic for each language.
    # They primarily use regular expressions and, for Python, AST parsing.

    def _analyze_javascript(self, code: str) -> Dict[str, Any]: # 8. JavaScript Analysis
        """Analyze JavaScript code with enhanced pattern detection."""
        issues = []
        metrics = { 'complexity': 1, 'maintainability': 10, 'lines_of_code': len(code.splitlines()), 'codeQualityScore': 10 }
        functions = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            self._check_javascript_patterns(line_stripped, i, issues, metrics) # Helper for JS patterns

            # Regex to detect function declarations (simplified)
            func_matches = list(re.finditer(r'function\s+(\w+)', line_stripped))
            for func_match in func_matches:
                functions.append({'name': func_match.group(1), 'start_line': i, 'end_line': i + 5, 'complexity': 1})

        self._calculate_complexity(code, metrics) # Helper to calculate complexity
        # Adjust maintainability and quality score based on issues
        metrics['maintainability'] = max(1, 10 - len(issues) // 2 - metrics['complexity'] // 5)
        metrics['codeQualityScore'] = int(metrics['maintainability'] * 10) # Example calculation

        return {'issues': issues, 'metrics': metrics, 'functions': functions}

    def _check_javascript_patterns(self, line: str, line_num: int, issues: List[Dict], metrics: Dict): # 9. JS Pattern Checker
        """Check JavaScript-specific patterns efficiently."""
        patterns = [ # List of (regex, severity, message, suggestion)
            (r'\bvar\s+', 'warning', 'Use const or let instead of var', 'Replace var with const or let for better scoping'),
            (r'\b==\b(?!=)', 'warning', 'Use strict equality (===) instead of loose equality (==)', 'Replace == with === for type-safe comparison'),
            (r'console\.log', 'info', 'Console statement found', 'Remove console.log statements in production code'),
            (r'eval\s*\(', 'error', 'Avoid using eval() - security risk', 'Replace eval() with safer alternatives'),
            (r'innerHTML\s*=', 'warning', 'Potential XSS vulnerability with innerHTML', 'Use textContent or sanitize input'),
        ]
        for pattern, severity, message, suggestion in patterns:
            if re.search(pattern, line):
                issues.append({'severity': severity, 'message': message, 'line': line_num, 'suggestion': suggestion})
                if severity == 'error': metrics['complexity'] += 2
                elif severity == 'warning': metrics['complexity'] += 1

    def _calculate_complexity(self, code: str, metrics: Dict): # 10. Complexity Calculator
        """Calculate cyclomatic complexity more accurately (simplified)."""
        complexity_keywords = ['if', 'for', 'while', 'switch', 'case', 'catch', 'return']
        for keyword in complexity_keywords:
            count = len(re.findall(rf'\b{keyword}\b', code, re.IGNORECASE))
            metrics['complexity'] += count
        if 'fibonacci' in code and code.count('fibonacci(') > 1: # Special case for demo
            metrics['complexity'] += 5

    def _analyze_typescript(self, code: str) -> Dict[str, Any]: # 11. TypeScript Analysis
        """Analyze TypeScript code with TS-specific rules."""
        results = self._analyze_javascript(code) # Reuse JavaScript analysis
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if ': any' in line_stripped:
                results['issues'].append({'severity': 'warning', 'message': 'Avoid using any type', 'line': i, 'suggestion': 'Use specific types for better type safety'})
            if re.search(r'@ts-ignore', line_stripped):
                results['issues'].append({'severity': 'warning', 'message': 'Avoid @ts-ignore comments', 'line': i, 'suggestion': 'Fix the underlying TypeScript error instead'})
        return results

    def _analyze_python(self, code: str) -> Dict[str, Any]: # 12. Python Analysis (with AST)
        """Analyze Python code with AST parsing."""
        issues, metrics, functions = [], {'complexity': 1, 'maintainability': 10, 'lines_of_code': len(code.splitlines()), 'codeQualityScore': 10}, []
        try:
            tree = ast.parse(code) # Parse Python code into an Abstract Syntax Tree
            for node in ast.walk(tree): # Traverse the AST
                if isinstance(node, ast.FunctionDef):
                    functions.append({'name': node.name, 'start_line': node.lineno, 'end_line': getattr(node, 'end_lineno', node.lineno), 'complexity': 1, 'parameters': [arg.arg for arg in node.args.args]})
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)): metrics['complexity'] += 1
        except SyntaxError as e:
            issues.append({'severity': 'error', 'message': f'Syntax error: {str(e)}', 'line': getattr(e, 'lineno', 1), 'suggestion': 'Fix syntax error for full analysis'})
        self._check_python_patterns(code, issues) # Helper for Python-specific regex patterns
        metrics['maintainability'] = max(1, 10 - len(issues) // 2 - metrics['complexity'] // 5)
        metrics['codeQualityScore'] = int(metrics['maintainability'] * 10)
        return {'issues': issues, 'metrics': metrics, 'functions': functions}

    def _check_python_patterns(self, code: str, issues: List[Dict]): # Python Pattern Helper
        # ... (similar to _check_javascript_patterns but for Python) ...
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if re.search(r'print\s*\(', line_stripped): issues.append({'severity': 'info', 'message': 'Print statement found', 'line': i, 'suggestion': 'Use logging for production'})
            if 'import *' in line_stripped: issues.append({'severity': 'warning', 'message': 'Avoid wildcard imports', 'line': i, 'suggestion': 'Import specific names'})

    def _analyze_java(self, code: str) -> Dict[str, Any]: # 13. Java Analysis
        """Analyze Java code with Java-specific patterns."""
        # ... (Simplified regex-based analysis for Java) ...
        issues, metrics, functions = [], {'complexity': 1, 'maintainability': 10, 'lines_of_code': len(code.splitlines()), 'codeQualityScore': 10}, []
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if 'System.out.print' in line_stripped: issues.append({'severity': 'info', 'message': 'System.out.print found', 'line': i, 'suggestion': 'Use a logging framework'})
            method_pattern = r'(public|private|protected).*?(\w+)\s*\('
            for match in re.finditer(method_pattern, line_stripped):
                if match.group(2) not in ['class', 'interface', 'enum']: functions.append({'name': match.group(2), 'start_line': i, 'complexity': 1})
        metrics['maintainability'] = max(1, 10 - len(issues) // 2)
        metrics['codeQualityScore'] = int(metrics['maintainability'] * 10)
        return {'issues': issues, 'metrics': metrics, 'functions': functions}

    def _generic_analysis(self, code: str) -> Dict[str, Any]: # 14. Generic Fallback Analysis
        """Generic analysis for unsupported languages."""
        # ... (Very basic checks like line length, TODO/FIXME comments) ...
        issues, metrics = [], {'complexity': 1, 'maintainability': 8, 'lines_of_code': len(code.splitlines()), 'codeQualityScore': 8}
        for i, line in enumerate(code.splitlines(), 1):
            if len(line) > 120: issues.append({'severity': 'info', 'message': 'Line too long (>120 chars)', 'line': i})
            if re.search(r'(TODO|FIXME|HACK)', line, re.IGNORECASE): issues.append({'severity': 'info', 'message': 'TODO/FIXME/HACK comment found', 'line': i})
        return {'issues': issues, 'metrics': metrics, 'functions': []}

    def _ai_analysis(self, code: str, language: str) -> Dict[str, Any]: # 15. Simulated AI Analysis
        """AI-based code analysis using CodeBERT (simulated with realistic insights)."""
        # This method is currently a placeholder for true AI model inference.
        # It uses regex and heuristics to simulate what an AI might suggest.
        insights = {'semantic_issues': [], 'performance_suggestions': [], 'security_concerns': [], 'code_smells': []}
        if 'fibonacci' in code and 'fibonacci(' in code:
            insights['performance_suggestions'].append('Consider optimizing recursive calls with memoization for exponential performance improvement')
        if len(code.splitlines()) > 50: insights['code_smells'].append('Function or file appears to be quite large - consider breaking into smaller, focused components')
        # ... more simulated insights ...
        return insights

    # 16. Implementation of the abstract 'process' method from BaseAgent
    def process(self, code: str, language: str, **kwargs) -> Dict[str, Any]:
        """Main processing method, simply calls analyze for the LinterAgent."""
        # For this agent, 'process' is synonymous with 'analyze'.
        # **kwargs are not used in this specific implementation but are part of the base signature.
        return self.analyze(code, language)

```

**Decoding the Detective - `LinterAgent`:**

1.  **Inheritance (`class LinterAgent(BaseAgent):`)**: The `LinterAgent` proudly declares its lineage, inheriting from `BaseAgent`. This means it gets all the common attributes (logger, status, lock, etc.) and methods (preprocessing, postprocessing, performance tracking, cleanup) defined in the base class.

2.  **Constructor (`__init__`)**:
    *   `super().__init__('LinterAgent', 'microsoft/codebert-base')`: It calls the parent class's constructor, providing its specific name "LinterAgent" and the default AI model it intends to use, "microsoft/codebert-base" (a well-known model for code understanding tasks).
    *   `self.language_parsers`: This is a crucial dictionary. It acts as a dispatch table, mapping language strings (like 'javascript', 'python') to specific private methods within the `LinterAgent` class that are responsible for analyzing code of that particular language (e.g., `self._analyze_javascript`). This is a clean way to handle language-specific logic.

3.  **`_load_model(self) -> bool` (Implementing Abstract Method)**:
    *   This method fulfills the contract set by `BaseAgent`. Its job is to load the actual AI model and tokenizer.
    *   **Current State (Simulated):** The provided code *simulates* model loading. It logs a message and sets `self.model` and `self.tokenizer` to placeholder strings.
    *   **Real-World Scenario:** The commented-out lines (`# from transformers import ...`) show what this would look like with the Hugging Face Transformers library: `AutoTokenizer.from_pretrained(self.model_name)` and `AutoModel.from_pretrained(self.model_name)` would download (if not already cached locally by Transformers) and load the specified CodeBERT model and its associated tokenizer. This step can be time-consuming and memory-intensive, which is why it's part of the agent's `initialize()` flow managed by the `AgentPool`.

4.  **`analyze(self, code: str, language: str) -> Dict[str, Any]`**:
    *   This is the primary public method of the `LinterAgent` (it's also called by the `process` method to satisfy the `BaseAgent` interface). It orchestrates the entire linting process for a given piece of `code` and `language`.
    *   It records `start_time`, sets `self.status` to 'running', and updates `self.last_run`.
    *   Performs basic input validation (checks for empty code).
    *   Calls `self._preprocess_code(code, language)` inherited from `BaseAgent` to clean the input.
    *   **Language Dispatching:** Uses the `self.language_parsers` dictionary to call the appropriate language-specific analysis method (e.g., `_analyze_javascript(cleaned_code)`). If the language isn't found in the map, it falls back to `_generic_analysis`.
    *   **AI Insights (Simulated):** Calls `self._ai_analysis(cleaned_code, language)` which, in the current code, simulates AI-driven insights using heuristics. In a full implementation, this is where the loaded `self.model` and `self.tokenizer` would be used to perform inference on the code and extract deeper semantic understanding or patterns.
    *   It then updates the `results` dictionary with these `ai_insights`.
    *   Finally, it updates performance stats using `self._track_performance` and returns the results after passing them through `self._postprocess_results` (both inherited from `BaseAgent`) to add standard metadata.
    *   Includes a `try-except` block to catch any errors during analysis, log them, set the agent's status to 'error', and then re-raises the exception to be handled by `app.py`.

5.  **Language-Specific Analysis Methods (`_analyze_javascript`, `_analyze_typescript`, `_analyze_python`, `_analyze_java`)**:
    *   Each of these private methods is responsible for the detailed analysis of code for its respective language.
    *   **JavaScript/TypeScript (`_analyze_javascript`, `_analyze_typescript`)**:
        *   These primarily use regular expressions (`re.finditer`, `re.search`) via helper methods like `_check_javascript_patterns` to find common issues (e.g., use of `var`, `==`, `console.log`, `eval`, `innerHTML`) and to identify function declarations.
        *   `_analyze_typescript` reuses `_analyze_javascript` and then adds a few TypeScript-specific checks (like for `: any` or `@ts-ignore`).
        *   A helper `_calculate_complexity` (simplified) adjusts a complexity metric based on keywords.
    *   **Python (`_analyze_python`)**:
        *   This method takes a more sophisticated approach by using Python's built-in `ast` (Abstract Syntax Tree) module to parse the Python code. Walking the AST allows for more reliable detection of structures like function definitions (`ast.FunctionDef`), conditional statements (`ast.If`), and loops (`ast.For`, `ast.While`).
        *   It also includes a call to `_check_python_patterns` for regex-based checks.
        *   Handles `SyntaxError` if the Python code cannot be parsed.
    *   **Java (`_analyze_java`)**: Uses regex for basic issue detection (e.g., `System.out.print`) and method identification.
    *   All these methods construct a dictionary containing `issues` (a list of found problems), `metrics` (like complexity, lines of code, and a calculated `codeQualityScore`), and `functions` (a list of identified functions/methods).

6.  **`_generic_analysis(self, code: str) -> Dict[str, Any]`**: A fallback method for languages not explicitly supported by a dedicated parser. It performs very basic checks like line length and the presence of TODO/FIXME comments.

7.  **`_ai_analysis(self, code: str, language: str) -> Dict[str, Any]`**:
    *   As mentioned, this is currently a **simulation** of AI-driven analysis. It uses simple string checks and regex to provide example insights that a real CodeBERT-like model might generate (e.g., suggesting memoization for a Fibonacci function, warning about large functions).
    *   In a full-fledged implementation, this method would involve:
        1.  Tokenizing the `cleaned_code` using `self.tokenizer`.
        2.  Feeding the tokenized input to `self.model` for inference.
        3.  Processing the model's output (e.g., embeddings, logits, generated text) to extract meaningful semantic issues, performance suggestions, etc.

8.  **`process(self, code: str, language: str, **kwargs) -> Dict[str, Any]`**: This method directly implements the abstract `process` method from `BaseAgent`. For the `LinterAgent`, its core "processing" task *is* analysis, so it simply calls its own `analyze` method. `**kwargs` are accepted but not used in this particular agent.

**In essence, the `LinterAgent` acts as a specialized detective. It uses a combination of language-specific rules (regex, AST parsing) and (simulated) AI insights to scrutinize code. Its modular design, with dispatching to different analysis functions based on language, makes it extensible. While the current AI integration is largely placeholder, the structure is there to incorporate true model inference for deeper, more nuanced code understanding.**

---
Return to: [Backend Overview](README.md) | [Agents Directory Overview](#the-brains-serveragents--our-specialized-ai-experts)
Next Agent: [`refactor_agent.py`](#-refactor_agentpy-the-code-sculptor---suggesting-improvements)

---

## ✨ `refactor_agent.py`: The Code Sculptor - Suggesting Improvements

The `RefactorAgent` is designed to be the "Code Sculptor," analyzing code and suggesting intelligent refactorings to improve its quality, performance, readability, or maintainability. Like the `LinterAgent`, it extends `BaseAgent` and would ideally use an AI model (like CodeT5, as specified in its `__init__`) for more advanced suggestions.

**Key Responsibilities (based on the code structure):**
*   **Model Loading (`_load_model`):** Similar to the LinterAgent, it has a (currently simulated) method to load its designated AI model, which would be `Salesforce/codet5-small` for code generation and transformation tasks.
*   **Suggestion Generation (`generate_suggestions` / `process`):** This is its core method. It takes code, language, and optionally a list of existing issues (perhaps from the `LinterAgent`) as input.
*   **Pattern-Based Refactoring:** It appears to have a dictionary `self.refactoring_patterns` that maps categories like 'performance', 'readability', and 'maintainability' to specific private methods (e.g., `_performance_refactoring`, `_readability_refactoring`).
*   **Specific Refactoring Logic:**
    *   **Performance:** Methods like `_detect_recursive_fibonacci` and `_create_fibonacci_optimization` suggest it can identify common performance anti-patterns and offer concrete refactored code (e.g., memoized Fibonacci). It also looks for inefficient loops and string concatenations.
    *   **Readability:** It aims to suggest adding documentation (`_needs_documentation`), improving variable names (`_has_poor_variable_names`), and extracting magic numbers (`_has_magic_numbers`).
    *   **Maintainability:** It tries to identify overly long functions (`_create_function_breakdown_suggestion`) or duplicate code (`_has_duplicate_code`).
*   **Suggestion Structure:** Each suggestion is a dictionary containing:
    *   `type` (e.g., 'performance', 'readability').
    *   `title` and `description` of the suggested change.
    *   `original_code` and `refactored_code` (the latter is often a template or a transformed version).
    *   `line_start`, `line_end` indicating the relevant code section.
    *   `impact`, `impact_score`, `confidence` to rank suggestions.
    *   `benefits` and sometimes `estimated_improvement`.
*   **Helper Transformation Methods:** Includes private methods like `_generate_memoized_fibonacci`, `_add_function_documentation`, `_improve_variable_names`, etc., which provide the actual refactored code snippets or transformations. These are currently rule-based and template-driven.

**How It Works (Conceptual & Current):**
The `RefactorAgent` currently seems to rely heavily on rule-based pattern matching (often using regular expressions) and predefined templates for refactored code. For example, if it detects a recursive Fibonacci, it provides a template for a memoized version.

In a more advanced AI-driven scenario (using the loaded CodeT5 model):
1.  The agent might take the original code and a prompt (e.g., "Refactor this code for better performance" or "Make this code more readable").
2.  The CodeT5 model would then generate a refactored version of the code.
3.  The agent would then need to parse this generated code, compare it to the original, and structure it into the suggestion format.

The current implementation provides a solid framework with many common refactoring patterns already identified. Integrating true AI model inference for generating the `refactored_code` would be the next step to unlock its full potential.

---

## 🧪 `testgen_agent.py`: The Diligent Scribe - Automating Test Creation

The `TestGenAgent` is our automated test writer. Its goal is to analyze source code and generate unit test cases, helping developers achieve better test coverage and catch regressions more easily. It also extends `BaseAgent`.

**Key Responsibilities (based on the code structure):**
*   **Model Loading (`_load_model`):** It's configured to use a model like `microsoft/codebert-base-mlm` (Masked Language Model), which suggests it might use the model to understand code structure or fill in test templates. This is currently simulated.
*   **Test Case Generation (`generate_tests` / `process`):** This is the primary method. It takes the source `code`, `language`, and optionally a list of `functions` (which might have been extracted by the LinterAgent or another pre-processing step) as input.
*   **Function Extraction (`_extract_functions`):** If a list of functions isn't provided, this method attempts to parse the code to identify function definitions.
    *   For JavaScript/TypeScript, it uses regular expressions to find function declarations and expressions.
    *   For Python, it uses the `ast` module to parse the code and find `ast.FunctionDef` and `ast.ClassDef` nodes, which is a more robust approach for Python.
*   **Template-Based Test Generation:** It uses a `self.test_templates` dictionary to dispatch to language-specific test generation methods (e.g., `_generate_javascript_tests`, `_generate_python_tests`).
    *   These methods iterate over the identified functions and create test case dictionaries.
    *   The actual test code within these dictionaries appears to be largely template-based. For instance, for a 'fibonacci' function, it generates specific Jest or Pytest code for base cases and sequence checks. For other functions, it might generate a simple "should be defined" test.
*   **Edge Case Generation (`_generate_edge_cases`):** This method aims to create tests for edge cases. Currently, it has specific logic for 'fibonacci' (testing negative input, large input/performance). This section would greatly benefit from AI to predict more diverse and relevant edge cases for arbitrary functions.
*   **Test Case Structure:** Each generated test case is a dictionary containing:
    *   `name`: A descriptive name for the test.
    *   `description`: Further details about the test's purpose.
    *   `type`: ('unit', 'edge_case', 'performance').
    *   `framework`: (e.g., 'jest', 'pytest', 'junit').
    *   `code`: The actual string of test code to be generated.
    *   `expected_result`: (e.g., 'pass').
    *   `test_data`: Input and expected output for the test.

**How It Works (Conceptual & Current):**
The `TestGenAgent` primarily functions as a sophisticated test scaffolding tool. It identifies functions and then uses predefined templates to generate common test patterns for those functions, especially for known examples like Fibonacci. The language-specific generators tailor the syntax for popular testing frameworks (Jest for JS/TS, Pytest for Python).

The "AI-generated edge cases" part is currently heuristic (specifically for Fibonacci). A true AI-powered `TestGenAgent` using its CodeBERT-MLM model might:
1.  Analyze the function's structure and data flow more deeply.
2.  Use the Masked Language Model capabilities to predict plausible input values that could lead to edge conditions or to fill in parts of test templates more intelligently.
3.  Potentially generate more diverse test assertions based on the function's inferred behavior.

The current `TestGenAgent` provides a valuable starting point for test generation, especially for boilerplate tests, and has a structure that's ready for more advanced AI integration for smarter test case and edge case discovery.

This overview of the `RefactorAgent` and `TestGenAgent` shows that while they share the common structure of `BaseAgent`, their internal logic is tailored to their specific tasks of code transformation and test creation, respectively. Both currently utilize a mix of heuristic/rule-based approaches with a clear path towards deeper AI model integration.

---
Return to: [Backend Overview](README.md) | [Agents Directory Overview](#the-brains-serveragents--our-specialized-ai-experts)
Next: [The `services/` Directory: Backend Business Logic](../services_directory.md)
