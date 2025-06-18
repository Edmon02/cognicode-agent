"""
Refactor Agent for intelligent code refactoring suggestions
Uses CodeT5 and pattern matching for code optimization
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent

class RefactorAgent(BaseAgent):
    """AI agent for code refactoring and optimization"""
    
    def __init__(self):
        super().__init__('RefactorAgent', 'Salesforce/codet5-small')
        self.refactoring_patterns = {
            'performance': self._performance_refactoring,
            'readability': self._readability_refactoring,
            'maintainability': self._maintainability_refactoring
        }
        
    def _load_model(self):
        """Load CodeT5 model for code generation"""
        try:
            # In a real implementation, load the actual model
            # from transformers import T5Tokenizer, T5ForConditionalGeneration
            # self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            # self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            
            # For demo purposes, simulate model loading
            self.logger.info(f'Loading {self.model_name} for code generation...')
            self.model = "simulated_codet5_model"
            self.tokenizer = "simulated_tokenizer"
            
        except Exception as e:
            self.logger.error(f'Failed to load model: {str(e)}')
            raise
    
    def generate_suggestions(self, code: str, language: str, issues: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate refactoring suggestions based on code analysis"""
        try:
            self.status = 'running'
            
            suggestions = []
            cleaned_code = self._preprocess_code(code, language)
            
            # Generate different types of refactoring suggestions
            for pattern_type, pattern_func in self.refactoring_patterns.items():
                pattern_suggestions = pattern_func(cleaned_code, language, issues or [])
                suggestions.extend(pattern_suggestions)
            
            # Sort suggestions by impact and confidence
            suggestions.sort(key=lambda x: (x['impact_score'], x['confidence']), reverse=True)
            
            self.status = 'ready'
            return suggestions
            
        except Exception as e:
            self.logger.error(f'Refactoring generation failed: {str(e)}')
            self.status = 'error'
            raise
    
    def _performance_refactoring(self, code: str, language: str, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate performance-focused refactoring suggestions"""
        suggestions = []
        
        # Detect recursive fibonacci pattern
        if 'fibonacci' in code and language in ['javascript', 'typescript']:
            if 'fibonacci(n - 1)' in code and 'fibonacci(n - 2)' in code:
                suggestions.append({
                    'type': 'performance',
                    'title': 'Optimize recursive fibonacci with memoization',
                    'description': 'Replace exponential recursion with memoized version for O(n) complexity',
                    'original_code': code,
                    'refactored_code': self._generate_memoized_fibonacci(language),
                    'line_start': 1,
                    'line_end': len(code.split('\n')),
                    'impact': 'high',
                    'impact_score': 9,
                    'confidence': 95,
                    'benefits': [
                        'Reduces time complexity from O(2^n) to O(n)',
                        'Eliminates redundant calculations',
                        'Improves performance for large inputs',
                        'Maintains same functionality'
                    ],
                    'estimated_improvement': '1000x faster for fibonacci(30)'
                })
        
        # Detect inefficient loops
        if re.search(r'for.*in.*length', code):
            suggestions.append({
                'type': 'performance',
                'title': 'Cache array length in loop',
                'description': 'Cache array length to avoid repeated property access',
                'original_code': code,
                'refactored_code': self._optimize_loop_length(code),
                'line_start': 1,
                'line_end': len(code.split('\n')),
                'impact': 'medium',
                'impact_score': 6,
                'confidence': 80,
                'benefits': [
                    'Reduces property access overhead',
                    'Slightly improves loop performance',
                    'Makes optimization intent clear'
                ]
            })
        
        return suggestions
    
    def _readability_refactoring(self, code: str, language: str, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate readability-focused refactoring suggestions"""
        suggestions = []
        
        # Suggest adding comments for complex functions
        if 'fibonacci' in code and '// ' not in code:
            suggestions.append({
                'type': 'readability',
                'title': 'Add function documentation',
                'description': 'Add JSDoc comments to explain function purpose and parameters',
                'original_code': code,
                'refactored_code': self._add_function_documentation(code, language),
                'line_start': 1,
                'line_end': 1,
                'impact': 'medium',
                'impact_score': 7,
                'confidence': 90,
                'benefits': [
                    'Improves code documentation',
                    'Makes function purpose clear',
                    'Helps with IDE intellisense',
                    'Better for team collaboration'
                ]
            })
        
        # Suggest better variable names
        if re.search(r'\b[a-z]\b', code):  # Single letter variables
            suggestions.append({
                'type': 'readability',
                'title': 'Use descriptive variable names',
                'description': 'Replace single-letter variables with descriptive names',
                'original_code': code,
                'refactored_code': self._improve_variable_names(code),
                'line_start': 1,
                'line_end': len(code.split('\n')),
                'impact': 'low',
                'impact_score': 5,
                'confidence': 85,
                'benefits': [
                    'Makes code more self-documenting',
                    'Reduces need for comments',
                    'Easier to understand for new developers'
                ]
            })
        
        return suggestions
    
    def _maintainability_refactoring(self, code: str, language: str, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate maintainability-focused refactoring suggestions"""
        suggestions = []
        
        # Suggest breaking down complex functions
        lines = code.split('\n')
        if len(lines) > 20:
            suggestions.append({
                'type': 'maintainability',
                'title': 'Break down large function',
                'description': 'Split large function into smaller, focused functions',
                'original_code': code,
                'refactored_code': self._break_down_function(code, language),
                'line_start': 1,
                'line_end': len(lines),
                'impact': 'high',
                'impact_score': 8,
                'confidence': 75,
                'benefits': [
                    'Improves code organization',
                    'Makes testing easier',
                    'Reduces cognitive complexity',
                    'Enables better reuse'
                ]
            })
        
        return suggestions
    
    def _generate_memoized_fibonacci(self, language: str) -> str:
        """Generate memoized fibonacci implementation"""
        if language == 'javascript':
            return '''/**
 * Optimized fibonacci function using memoization
 * Time complexity: O(n), Space complexity: O(n)
 */
const fibonacci = (() => {
    const cache = new Map();
    
    return function fib(n) {
        if (n <= 1) return n;
        
        if (cache.has(n)) {
            return cache.get(n);
        }
        
        const result = fib(n - 1) + fib(n - 2);
        cache.set(n, result);
        return result;
    };
})();

// Example usage
console.log(fibonacci(10)); // Much faster for large numbers'''
        
        elif language == 'python':
            return '''def fibonacci(n, cache={}):
    """
    Optimized fibonacci function using memoization
    Time complexity: O(n), Space complexity: O(n)
    """
    if n in cache:
        return cache[n]
    
    if n <= 1:
        return n
    
    cache[n] = fibonacci(n - 1, cache) + fibonacci(n - 2, cache)
    return cache[n]

# Example usage
print(fibonacci(10))  # Much faster for large numbers'''
        
        return code  # Fallback
    
    def _add_function_documentation(self, code: str, language: str) -> str:
        """Add documentation to functions"""
        if language == 'javascript':
            lines = code.split('\n')
            documented_lines = []
            
            for line in lines:
                if line.strip().startswith('function'):
                    documented_lines.extend([
                        '/**',
                        ' * Calculate the nth Fibonacci number using recursion',
                        ' * @param {number} n - The position in the Fibonacci sequence',
                        ' * @returns {number} The nth Fibonacci number',
                        ' */',
                        line
                    ])
                else:
                    documented_lines.append(line)
            
            return '\n'.join(documented_lines)
        
        return code
    
    def _improve_variable_names(self, code: str) -> str:
        """Improve variable names for better readability"""
        # Simple example - replace 'n' with 'position'
        improved_code = code.replace('(n)', '(position)')
        improved_code = improved_code.replace('n <=', 'position <=')
        improved_code = improved_code.replace('n - 1', 'position - 1')
        improved_code = improved_code.replace('n - 2', 'position - 2')
        return improved_code
    
    def _optimize_loop_length(self, code: str) -> str:
        """Optimize loops by caching length"""
        # This is a simplified example
        return code.replace(
            'for (let i = 0; i < array.length; i++)',
            'for (let i = 0, length = array.length; i < length; i++)'
        )
    
    def _break_down_function(self, code: str, language: str) -> str:
        """Break down large functions into smaller ones"""
        # This is a simplified example
        return f'''// Refactored to use smaller, focused functions
{code}

// Additional helper functions would be extracted here
// Example: validation, calculation, formatting functions'''
    
    def process(self, code: str, language: str, **kwargs) -> List[Dict[str, Any]]:
        """Main processing method"""
        issues = kwargs.get('issues', [])
        return self.generate_suggestions(code, language, issues)