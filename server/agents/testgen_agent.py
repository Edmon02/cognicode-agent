"""
Test Generation Agent for automated unit test creation
Uses AI models and template-based generation for comprehensive test coverage
"""

import re
import ast
from typing import Dict, Any, List
from .base_agent import BaseAgent

class TestGenAgent(BaseAgent):
    """AI agent for automated test generation"""
    
    def __init__(self):
        super().__init__('TestGenAgent', 'microsoft/codebert-base-mlm')
        self.test_templates = {
            'javascript': self._generate_javascript_tests,
            'typescript': self._generate_typescript_tests,
            'python': self._generate_python_tests,
            'java': self._generate_java_tests
        }
        
    def _load_model(self):
        """Load model for test generation"""
        try:
            # In a real implementation, load the actual model
            # from transformers import AutoTokenizer, AutoModelForMaskedLM
            # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            # self.model = AutoModelForMaskedLM.from_pretrained(self.model_name)
            
            # For demo purposes, simulate model loading
            self.logger.info(f'Loading {self.model_name} for test generation...')
            self.model = "simulated_test_model"
            self.tokenizer = "simulated_tokenizer"
            
        except Exception as e:
            self.logger.error(f'Failed to load model: {str(e)}')
            raise
    
    def generate_tests(self, code: str, language: str, functions: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive unit tests for the given code"""
        try:
            self.status = 'running'
            
            cleaned_code = self._preprocess_code(code, language)
            test_cases = []
            
            # Extract functions if not provided
            if not functions:
                functions = self._extract_functions(cleaned_code, language)
            
            # Generate tests using language-specific templates
            if language in self.test_templates:
                test_cases = self.test_templates[language](cleaned_code, functions)
            else:
                test_cases = self._generate_generic_tests(cleaned_code, functions)
            
            # Add AI-generated edge cases
            edge_cases = self._generate_edge_cases(cleaned_code, language, functions)
            test_cases.extend(edge_cases)
            
            self.status = 'ready'
            return test_cases
            
        except Exception as e:
            self.logger.error(f'Test generation failed: {str(e)}')
            self.status = 'error'
            raise
    
    def _extract_functions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract function information from code"""
        functions = []
        
        if language == 'javascript' or language == 'typescript':
            # Match function declarations
            func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
            matches = re.finditer(func_pattern, code)
            
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                    'start_line': code[:match.start()].count('\n') + 1,
                    'complexity': 1
                })
        
        elif language == 'python':
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append({
                            'name': node.name,
                            'parameters': [arg.arg for arg in node.args.args],
                            'start_line': node.lineno,
                            'complexity': 1
                        })
            except SyntaxError:
                pass
        
        return functions
    
    def _generate_javascript_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate JavaScript/Jest tests"""
        test_cases = []
        
        for func in functions:
            func_name = func['name']
            
            # Generate basic test cases
            if func_name == 'fibonacci':
                test_cases.extend([
                    {
                        'name': f'{func_name} should return 0 for input 0',
                        'description': f'Test base case where n is 0',
                        'type': 'unit',
                        'framework': 'jest',
                        'code': f'''test('{func_name}(0) should return 0', () => {{
  expect({func_name}(0)).toBe(0);
}});''',
                        'expected_result': 'pass',
                        'test_data': {'input': 0, 'expected': 0}
                    },
                    {
                        'name': f'{func_name} should return 1 for input 1',
                        'description': f'Test base case where n is 1',
                        'type': 'unit',
                        'framework': 'jest',
                        'code': f'''test('{func_name}(1) should return 1', () => {{
  expect({func_name}(1)).toBe(1);
}});''',
                        'expected_result': 'pass',
                        'test_data': {'input': 1, 'expected': 1}
                    },
                    {
                        'name': f'{func_name} should calculate sequence correctly',
                        'description': f'Test recursive calculation for various inputs',
                        'type': 'unit',
                        'framework': 'jest',
                        'code': f'''test('{func_name} sequence calculation', () => {{
  expect({func_name}(5)).toBe(5);
  expect({func_name}(8)).toBe(21);
  expect({func_name}(10)).toBe(55);
}});''',
                        'expected_result': 'pass',
                        'test_data': {
                            'inputs': [5, 8, 10],
                            'expected': [5, 21, 55]
                        }
                    }
                ])
            else:
                # Generic function tests
                test_cases.append({
                    'name': f'{func_name} should be defined',
                    'description': f'Test that {func_name} function exists',
                    'type': 'unit',
                    'framework': 'jest',
                    'code': f'''test('{func_name} should be defined', () => {{
  expect(typeof {func_name}).toBe('function');
}});''',
                    'expected_result': 'pass',
                    'test_data': None
                })
        
        return test_cases
    
    def _generate_typescript_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate TypeScript tests"""
        # Similar to JavaScript but with type checking
        test_cases = self._generate_javascript_tests(code, functions)
        
        # Add TypeScript-specific tests
        for func in functions:
            test_cases.append({
                'name': f'{func["name"]} should handle type safety',
                'description': f'Test type safety for {func["name"]}',
                'type': 'unit',
                'framework': 'jest',
                'code': f'''test('{func["name"]} type safety', () => {{
  // TypeScript compilation ensures type safety
  expect(() => {func["name"]}("invalid")).toThrow();
}});''',
                'expected_result': 'pass',
                'test_data': None
            })
        
        return test_cases
    
    def _generate_python_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate Python/pytest tests"""
        test_cases = []
        
        for func in functions:
            func_name = func['name']
            
            if func_name == 'fibonacci':
                test_cases.extend([
                    {
                        'name': f'test_{func_name}_base_cases',
                        'description': f'Test base cases for {func_name}',
                        'type': 'unit',
                        'framework': 'pytest',
                        'code': f'''def test_{func_name}_base_cases():
    assert {func_name}(0) == 0
    assert {func_name}(1) == 1''',
                        'expected_result': 'pass',
                        'test_data': {'inputs': [0, 1], 'expected': [0, 1]}
                    },
                    {
                        'name': f'test_{func_name}_sequence',
                        'description': f'Test {func_name} sequence calculation',
                        'type': 'unit',
                        'framework': 'pytest',
                        'code': f'''def test_{func_name}_sequence():
    assert {func_name}(5) == 5
    assert {func_name}(8) == 21
    assert {func_name}(10) == 55''',
                        'expected_result': 'pass',
                        'test_data': {
                            'inputs': [5, 8, 10],
                            'expected': [5, 21, 55]
                        }
                    }
                ])
            else:
                test_cases.append({
                    'name': f'test_{func_name}_exists',
                    'description': f'Test that {func_name} function exists',
                    'type': 'unit',
                    'framework': 'pytest',
                    'code': f'''def test_{func_name}_exists():
    assert callable({func_name})''',
                    'expected_result': 'pass',
                    'test_data': None
                })
        
        return test_cases
    
    def _generate_java_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate Java/JUnit tests"""
        test_cases = []
        
        for func in functions:
            func_name = func['name']
            
            test_cases.append({
                'name': f'test{func_name.capitalize()}',
                'description': f'Test {func_name} method',
                'type': 'unit',
                'framework': 'junit',
                'code': f'''@Test
public void test{func_name.capitalize()}() {{
    // Add appropriate assertions based on function logic
    assertNotNull({func_name});
}}''',
                'expected_result': 'pass',
                'test_data': None
            })
        
        return test_cases
    
    def _generate_generic_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate generic tests for unsupported languages"""
        test_cases = []
        
        for func in functions:
            test_cases.append({
                'name': f'test_{func["name"]}',
                'description': f'Generic test for {func["name"]}',
                'type': 'unit',
                'framework': 'generic',
                'code': f'// Test for {func["name"]} function\n// Add appropriate test logic here',
                'expected_result': 'pass',
                'test_data': None
            })
        
        return test_cases
    
    def _generate_edge_cases(self, code: str, language: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate edge case tests using AI analysis"""
        edge_cases = []
        
        for func in functions:
            func_name = func['name']
            
            # Generate edge cases based on function analysis
            if 'fibonacci' in func_name.lower():
                if language in ['javascript', 'typescript']:
                    edge_cases.extend([
                        {
                            'name': f'{func_name} should handle negative input',
                            'description': 'Test behavior with negative numbers',
                            'type': 'edge_case',
                            'framework': 'jest',
                            'code': f'''test('{func_name} handles negative input', () => {{
  expect(() => {func_name}(-1)).toThrow();
  // Or expect specific behavior for negative inputs
}});''',
                            'expected_result': 'pass',
                            'test_data': {'input': -1, 'expected': 'error'}
                        },
                        {
                            'name': f'{func_name} should handle large input',
                            'description': 'Test performance with large numbers',
                            'type': 'performance',
                            'framework': 'jest',
                            'code': f'''test('{func_name} handles large input', () => {{
  const start = Date.now();
  const result = {func_name}(30);
  const duration = Date.now() - start;
  
  expect(result).toBeGreaterThan(0);
  expect(duration).toBeLessThan(1000); // Should complete within 1 second
}});''',
                            'expected_result': 'pass',
                            'test_data': {'input': 30, 'max_duration': 1000}
                        }
                    ])
        
        return edge_cases
    
    def process(self, code: str, language: str, **kwargs) -> List[Dict[str, Any]]:
        """Main processing method"""
        functions = kwargs.get('functions', [])
        return self.generate_tests(code, language, functions)