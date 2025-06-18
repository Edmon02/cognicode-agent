"""
Refactor Agent for intelligent code refactoring suggestions
Uses CodeT5 and pattern matching for code optimization
Optimized for performance and memory efficiency
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent

class RefactorAgent(BaseAgent):
    """AI agent for code refactoring and optimization with enhanced patterns"""
    
    def __init__(self):
        super().__init__('RefactorAgent', 'Salesforce/codet5-small')
        self.refactoring_patterns = {
            'performance': self._performance_refactoring,
            'readability': self._readability_refactoring,
            'maintainability': self._maintainability_refactoring
        }
        
    def _load_model(self) -> bool:
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
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to load model: {str(e)}')
            return False
    
    def generate_suggestions(self, code: str, language: str, issues: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """Generate refactoring suggestions based on code analysis"""
        start_time = datetime.utcnow()
        
        try:
            self.status = 'running'
            self.last_run = start_time
            
            # Validate inputs
            if not code or not code.strip():
                return []
            
            suggestions = []
            cleaned_code = self._preprocess_code(code, language)
            
            # Generate different types of refactoring suggestions
            for pattern_type, pattern_func in self.refactoring_patterns.items():
                try:
                    pattern_suggestions = pattern_func(cleaned_code, language, issues or [])
                    suggestions.extend(pattern_suggestions)
                except Exception as e:
                    self.logger.warning(f"Error in {pattern_type} refactoring: {str(e)}")
            
            # Sort suggestions by impact and confidence
            suggestions.sort(key=lambda x: (x.get('impact_score', 0), x.get('confidence', 0)), reverse=True)
            
            self.status = 'ready'
            end_time = datetime.utcnow()
            self._track_performance(start_time, end_time)
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f'Refactoring generation failed: {str(e)}')
            self.status = 'error'
            end_time = datetime.utcnow()
            self._track_performance(start_time, end_time)
            raise
    
    def _performance_refactoring(self, code: str, language: str, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate performance-focused refactoring suggestions"""
        suggestions = []
        
        # Detect recursive fibonacci pattern
        if self._detect_recursive_fibonacci(code):
            suggestions.append(self._create_fibonacci_optimization(code, language))
        
        # Detect inefficient loops
        if self._detect_inefficient_loops(code):
            suggestions.append(self._create_loop_optimization(code))
        
        # Detect unnecessary object creation in loops
        if self._detect_object_creation_in_loops(code):
            suggestions.append(self._create_object_optimization(code))
        
        # Detect inefficient string concatenation
        if self._detect_string_concatenation(code, language):
            suggestions.append(self._create_string_optimization(code, language))
        
        return suggestions
    
    def _detect_recursive_fibonacci(self, code: str) -> bool:
        """Detect recursive fibonacci implementation"""
        return ('fibonacci' in code and 
                'fibonacci(n - 1)' in code and 
                'fibonacci(n - 2)' in code)
    
    def _create_fibonacci_optimization(self, code: str, language: str) -> Dict[str, Any]:
        """Create fibonacci optimization suggestion"""
        return {
            'type': 'performance',
            'title': 'Optimize recursive fibonacci with memoization',
            'description': 'Replace exponential recursion with memoized version for O(n) complexity',
            'original_code': code,
            'refactored_code': self._generate_memoized_fibonacci(language),
            'line_start': 1,
            'line_end': len(code.splitlines()),
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
        }
    
    def _detect_inefficient_loops(self, code: str) -> bool:
        """Detect inefficient loop patterns"""
        return bool(re.search(r'for.*\.length', code))
    
    def _create_loop_optimization(self, code: str) -> Dict[str, Any]:
        """Create loop optimization suggestion"""
        return {
            'type': 'performance',
            'title': 'Cache array length in loop',
            'description': 'Cache array length to avoid repeated property access',
            'original_code': code,
            'refactored_code': self._optimize_loop_length(code),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'medium',
            'impact_score': 6,
            'confidence': 80,
            'benefits': [
                'Reduces property access overhead',
                'Slightly improves loop performance',
                'Makes optimization intent clear'
            ]
        }
    
    def _detect_object_creation_in_loops(self, code: str) -> bool:
        """Detect object creation inside loops"""
        return bool(re.search(r'for.*{.*new\s+\w+', code, re.DOTALL))
    
    def _create_object_optimization(self, code: str) -> Dict[str, Any]:
        """Create object creation optimization"""
        return {
            'type': 'performance',
            'title': 'Move object creation outside loop',
            'description': 'Avoid creating objects inside loops for better performance',
            'original_code': code,
            'refactored_code': self._optimize_object_creation(code),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'medium',
            'impact_score': 7,
            'confidence': 85,
            'benefits': [
                'Reduces memory allocation overhead',
                'Improves garbage collection efficiency',
                'Better memory usage patterns'
            ]
        }
    
    def _detect_string_concatenation(self, code: str, language: str) -> bool:
        """Detect inefficient string concatenation"""
        if language == 'javascript':
            return '+=' in code and 'string' in code.lower()
        elif language == 'python':
            return '+=' in code and any(x in code for x in ['"', "'"])
        return False
    
    def _create_string_optimization(self, code: str, language: str) -> Dict[str, Any]:
        """Create string concatenation optimization"""
        return {
            'type': 'performance',
            'title': 'Use efficient string building',
            'description': 'Replace string concatenation with more efficient methods',
            'original_code': code,
            'refactored_code': self._optimize_string_building(code, language),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'medium',
            'impact_score': 6,
            'confidence': 82,
            'benefits': [
                'Better performance for large strings',
                'Reduced memory allocations',
                'More efficient string operations'
            ]
        }
    
    def _readability_refactoring(self, code: str, language: str, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate readability-focused refactoring suggestions"""
        suggestions = []
        
        # Suggest adding comments for complex functions
        if self._needs_documentation(code):
            suggestions.append(self._create_documentation_suggestion(code, language))
        
        # Suggest better variable names
        if self._has_poor_variable_names(code):
            suggestions.append(self._create_variable_naming_suggestion(code))
        
        # Suggest extracting magic numbers
        if self._has_magic_numbers(code):
            suggestions.append(self._create_magic_number_suggestion(code))
        
        return suggestions
    
    def _needs_documentation(self, code: str) -> bool:
        """Check if code needs documentation"""
        return ('function' in code or 'def ' in code) and '//' not in code and '"""' not in code
    
    def _create_documentation_suggestion(self, code: str, language: str) -> Dict[str, Any]:
        """Create documentation suggestion"""
        return {
            'type': 'readability',
            'title': 'Add function documentation',
            'description': 'Add proper documentation to explain function purpose and parameters',
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
        }
    
    def _has_poor_variable_names(self, code: str) -> bool:
        """Check for poor variable names"""
        return bool(re.search(r'\b[a-z]\b', code))  # Single letter variables
    
    def _create_variable_naming_suggestion(self, code: str) -> Dict[str, Any]:
        """Create variable naming suggestion"""
        return {
            'type': 'readability',
            'title': 'Use descriptive variable names',
            'description': 'Replace single-letter variables with descriptive names',
            'original_code': code,
            'refactored_code': self._improve_variable_names(code),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'low',
            'impact_score': 5,
            'confidence': 85,
            'benefits': [
                'Makes code more self-documenting',
                'Reduces need for comments',
                'Easier to understand for new developers'
            ]
        }
    
    def _has_magic_numbers(self, code: str) -> bool:
        """Check for magic numbers"""
        return bool(re.search(r'\b\d{2,}\b', code))  # Numbers with 2+ digits
    
    def _create_magic_number_suggestion(self, code: str) -> Dict[str, Any]:
        """Create magic number suggestion"""
        return {
            'type': 'readability',
            'title': 'Extract magic numbers to constants',
            'description': 'Replace magic numbers with named constants',
            'original_code': code,
            'refactored_code': self._extract_magic_numbers(code),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'medium',
            'impact_score': 6,
            'confidence': 88,
            'benefits': [
                'Makes code more maintainable',
                'Centralizes configuration values',
                'Improves code clarity'
            ]
        }
    
    def _maintainability_refactoring(self, code: str, language: str, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate maintainability-focused refactoring suggestions"""
        suggestions = []
        
        # Suggest breaking down complex functions
        lines = code.splitlines()
        if len(lines) > 20:
            suggestions.append(self._create_function_breakdown_suggestion(code, language))
        
        # Suggest extracting duplicate code
        if self._has_duplicate_code(code):
            suggestions.append(self._create_duplicate_extraction_suggestion(code))
        
        return suggestions
    
    def _create_function_breakdown_suggestion(self, code: str, language: str) -> Dict[str, Any]:
        """Create function breakdown suggestion"""
        return {
            'type': 'maintainability',
            'title': 'Break down large function',
            'description': 'Split large function into smaller, focused functions',
            'original_code': code,
            'refactored_code': self._break_down_function(code, language),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'high',
            'impact_score': 8,
            'confidence': 75,
            'benefits': [
                'Improves code organization',
                'Makes testing easier',
                'Reduces cognitive complexity',
                'Enables better reuse'
            ]
        }
    
    def _has_duplicate_code(self, code: str) -> bool:
        """Detect duplicate code patterns"""
        lines = code.splitlines()
        line_counts = {}
        
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 10:  # Only check substantial lines
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        return any(count > 1 for count in line_counts.values())
    
    def _create_duplicate_extraction_suggestion(self, code: str) -> Dict[str, Any]:
        """Create duplicate code extraction suggestion"""
        return {
            'type': 'maintainability',
            'title': 'Extract duplicate code',
            'description': 'Extract duplicate code into reusable functions',
            'original_code': code,
            'refactored_code': self._extract_duplicate_code(code),
            'line_start': 1,
            'line_end': len(code.splitlines()),
            'impact': 'high',
            'impact_score': 8,
            'confidence': 80,
            'benefits': [
                'Reduces code duplication',
                'Improves maintainability',
                'Centralizes logic',
                'Easier to update and test'
            ]
        }
    
    # Helper methods for code transformations
    
    def _generate_memoized_fibonacci(self, language: str) -> str:
        """Generate memoized fibonacci implementation"""
        if language == 'javascript' or language == 'typescript':
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
            return '''from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    """
    Optimized fibonacci function using memoization
    Time complexity: O(n), Space complexity: O(n)
    """
    if n <= 1:
        return n
    
    return fibonacci(n - 1) + fibonacci(n - 2)

# Example usage
print(fibonacci(10))  # Much faster for large numbers'''
        
        return "// Original code would be returned if no optimization template matches"
    
    def _add_function_documentation(self, code: str, language: str) -> str:
        """Add documentation to functions"""
        if language == 'javascript' or language == 'typescript':
            lines = code.splitlines()
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
        
        elif language == 'python':
            lines = code.splitlines()
            documented_lines = []
            
            for line in lines:
                if line.strip().startswith('def '):
                    documented_lines.extend([
                        line,
                        '    """',
                        '    Calculate the nth Fibonacci number using recursion',
                        '    ',
                        '    Args:',
                        '        n: The position in the Fibonacci sequence',
                        '    ',
                        '    Returns:',
                        '        The nth Fibonacci number',
                        '    """'
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
        return code.replace(
            'for (let i = 0; i < array.length; i++)',
            'for (let i = 0, length = array.length; i < length; i++)'
        )
    
    def _optimize_object_creation(self, code: str) -> str:
        """Optimize object creation patterns"""
        # This is a simplified example
        return f'''// Moved object creation outside loop
const reusableObject = new SomeObject();

{code.replace("new SomeObject()", "reusableObject")}'''
    
    def _optimize_string_building(self, code: str, language: str) -> str:
        """Optimize string building patterns"""
        if language == 'javascript':
            return code.replace(
                'result += str',
                'parts.push(str); // Then use parts.join("")'
            )
        elif language == 'python':
            return code.replace(
                'result += str',
                'parts.append(str)  # Then use "".join(parts)'
            )
        return code
    
    def _extract_magic_numbers(self, code: str) -> str:
        """Extract magic numbers to constants"""
        # Simple example
        constants = []
        if '100' in code:
            constants.append('const MAX_ITEMS = 100;')
        if '50' in code:
            constants.append('const THRESHOLD = 50;')
        
        if constants:
            return '\n'.join(constants) + '\n\n' + code.replace('100', 'MAX_ITEMS').replace('50', 'THRESHOLD')
        return code
    
    def _break_down_function(self, code: str, language: str) -> str:
        """Break down large functions into smaller ones"""
        # This is a simplified example
        return f'''// Refactored to use smaller, focused functions
{code}

// Additional helper functions would be extracted here
// Example: validation, calculation, formatting functions'''
    
    def _extract_duplicate_code(self, code: str) -> str:
        """Extract duplicate code into functions"""
        # This is a simplified example
        return f'''// Extracted common functionality
function extractedFunction() {{
    // Common code would be extracted here
}}

{code}'''
    
    def process(self, code: str, language: str, **kwargs) -> List[Dict[str, Any]]:
        """Main processing method"""
        issues = kwargs.get('issues', [])
        return self.generate_suggestions(code, language, issues)