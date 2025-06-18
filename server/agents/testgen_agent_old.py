"""
Test Generation Agent for automated unit test creation
Uses AI models and template-based generation for comprehensive test coverage
Optimized for performance and memory efficiency
"""

import re
import ast
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent

class TestGenAgent(BaseAgent):
    """AI agent for automated test generation with enhanced capabilities"""
    
    def __init__(self):
        super().__init__('TestGenAgent', 'microsoft/codebert-base-mlm')
        self.test_templates = {
            'javascript': self._generate_javascript_tests,
            'typescript': self._generate_typescript_tests,
            'python': self._generate_python_tests,
            'java': self._generate_java_tests
        }
        
    def _load_model(self) -> bool:
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
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to load model: {str(e)}')
            return False
    
    def generate_tests(self, code: str, language: str, functions: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive unit tests for the given code"""
        start_time = datetime.utcnow()
        
        try:
            self.status = 'running'
            self.last_run = start_time
            
            # Validate inputs
            if not code or not code.strip():
                return []
            
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
            end_time = datetime.utcnow()
            self._track_performance(start_time, end_time)
            
            return test_cases
            
        except Exception as e:
            self.logger.error(f'Test generation failed: {str(e)}')
            self.status = 'error'
            end_time = datetime.utcnow()
            self._track_performance(start_time, end_time)
            raise
    
    def _extract_functions(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract function information from code with enhanced parsing"""
        functions = []
        
        if language == 'javascript' or language == 'typescript':
            # Match function declarations and expressions
            patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)',
                r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
                r'(\w+)\s*:\s*\(([^)]*)\)\s*=>'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    func_name = match.group(1)
                    params = match.group(2) if len(match.groups()) > 1 else ''
                    
                    functions.append({
                        'name': func_name,
                        'parameters': [p.strip() for p in params.split(',') if p.strip()],
                        'start_line': code[:match.start()].count('\n') + 1,
                        'complexity': 1,
                        'type': 'function'
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
                            'complexity': 1,
                            'type': 'function',
                            'returns': self._infer_return_type(node, code)
                        })
                    elif isinstance(node, ast.ClassDef):
                        functions.append({
                            'name': node.name,
                            'parameters': [],
                            'start_line': node.lineno,
                            'complexity': 1,
                            'type': 'class'
                        })
            except SyntaxError:
                self.logger.warning("Could not parse Python code for function extraction")
        
        return functions
    
    def _infer_return_type(self, node: ast.FunctionDef, code: str) -> str:
        """Infer return type from function body"""
        # Simple heuristic to infer return type
        if any(isinstance(child, ast.Return) for child in ast.walk(node)):
            return 'mixed'
        return 'void'
    
    def _generate_javascript_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate comprehensive JavaScript/TypeScript tests"""
        test_cases = []
        
        for func in functions:
            func_name = func['name']
            
            # Basic functionality test
            test_cases.append({
                'name': f'should test {func_name} basic functionality',
                'description': f'Test basic functionality of {func_name}',
                'type': 'unit',
                'code': self._generate_js_basic_test(func_name, func['parameters']),
                'expected_result': 'pass',
                'framework': 'jest'
            })
            
            # Edge cases
            if 'fibonacci' in func_name.lower():
                test_cases.extend(self._generate_fibonacci_tests(func_name))
            
            # Parameter validation tests
            if func['parameters']:
                test_cases.append({
                    'name': f'should test {func_name} with invalid parameters',
                    'description': f'Test {func_name} with invalid input parameters',
                    'type': 'unit',
                    'code': self._generate_js_invalid_params_test(func_name, func['parameters']),
                    'expected_result': 'pass',
                    'framework': 'jest'
                })
        
        return test_cases
    
    def _generate_js_basic_test(self, func_name: str, parameters: List[str]) -> str:
        """Generate basic JavaScript test"""
        if not parameters:
            return f'''describe('{func_name}', () => {{
    test('should execute without errors', () => {{
        expect(() => {func_name}()).not.toThrow();
    }});
}});'''
        
        test_values = self._get_test_values(parameters)
        return f'''describe('{func_name}', () => {{
    test('should return expected result for valid input', () => {{
        const result = {func_name}({test_values});
        expect(result).toBeDefined();
        expect(typeof result).toBe('number'); // Adjust type as needed
    }});
}});'''
    
    def _generate_js_invalid_params_test(self, func_name: str, parameters: List[str]) -> str:
        """Generate invalid parameter test"""
        return f'''describe('{func_name} parameter validation', () => {{
    test('should handle null input', () => {{
        expect(() => {func_name}(null)).not.toThrow();
    }});
    
    test('should handle undefined input', () => {{
        expect(() => {func_name}(undefined)).not.toThrow();
    }});
    
    test('should handle invalid type input', () => {{
        expect(() => {func_name}('invalid')).not.toThrow();
    }});
}});'''
    
    def _generate_fibonacci_tests(self, func_name: str) -> List[Dict[str, Any]]:
        """Generate specialized Fibonacci tests"""
        return [
            {
                'name': f'should test {func_name} with base cases',
                'description': f'Test {func_name} with base cases (0, 1)',
                'type': 'unit',
                'code': f'''describe('{func_name} base cases', () => {{
    test('should return 0 for fibonacci(0)', () => {{
        expect({func_name}(0)).toBe(0);
    }});
    
    test('should return 1 for fibonacci(1)', () => {{
        expect({func_name}(1)).toBe(1);
    }});
}});''',
                'expected_result': 'pass',
                'framework': 'jest'
            },
            {
                'name': f'should test {func_name} with known values',
                'description': f'Test {func_name} with known Fibonacci values',
                'type': 'unit',
                'code': f'''describe('{func_name} known values', () => {{
    test('should return correct values for small inputs', () => {{
        expect({func_name}(2)).toBe(1);
        expect({func_name}(3)).toBe(2);
        expect({func_name}(4)).toBe(3);
        expect({func_name}(5)).toBe(5);
        expect({func_name}(6)).toBe(8);
    }});
}});''',
                'expected_result': 'pass',
                'framework': 'jest'
            },
            {
                'name': f'should test {func_name} performance',
                'description': f'Test {func_name} performance with larger inputs',
                'type': 'performance',
                'code': f'''describe('{func_name} performance', () => {{
    test('should complete within reasonable time for moderate input', () => {{
        const start = Date.now();
        const result = {func_name}(10);
        const duration = Date.now() - start;
        
        expect(result).toBe(55);
        expect(duration).toBeLessThan(1000); // Should complete within 1 second
    }});
}});''',
                'expected_result': 'pass',
                'framework': 'jest'
            }
        ]
    
    def _generate_python_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate comprehensive Python tests"""
        test_cases = []
        
        for func in functions:
            if func['type'] == 'function':
                test_cases.extend(self._generate_python_function_tests(func))
            elif func['type'] == 'class':
                test_cases.extend(self._generate_python_class_tests(func))
        
        return test_cases
    
    def _generate_python_function_tests(self, func: Dict) -> List[Dict[str, Any]]:
        """Generate Python function tests"""
        func_name = func['name']
        
        tests = [
            {
                'name': f'test_{func_name}_basic',
                'description': f'Test basic functionality of {func_name}',
                'type': 'unit',
                'code': f'''import unittest

class Test{func_name.capitalize()}(unittest.TestCase):
    
    def test_{func_name}_basic(self):
        """Test basic functionality of {func_name}"""
        result = {func_name}({self._get_test_values(func['parameters'])})
        self.assertIsNotNone(result)
    
    def test_{func_name}_type_validation(self):
        """Test type validation for {func_name}"""
        with self.assertRaises((TypeError, ValueError)):
            {func_name}(None)

if __name__ == '__main__':
    unittest.main()''',
                'expected_result': 'pass',
                'framework': 'unittest'
            }
        ]
        
        # Add Fibonacci-specific tests for Python
        if 'fibonacci' in func_name.lower():
            tests.append({
                'name': f'test_{func_name}_fibonacci_sequence',
                'description': f'Test {func_name} with Fibonacci sequence values',
                'type': 'unit',
                'code': f'''def test_{func_name}_fibonacci_sequence(self):
    """Test Fibonacci sequence correctness"""
    expected_values = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    for i, expected in enumerate(expected_values):
        with self.subTest(i=i):
            self.assertEqual({func_name}(i), expected)''',
                'expected_result': 'pass',
                'framework': 'unittest'
            })
        
        return tests
    
    def _generate_python_class_tests(self, func: Dict) -> List[Dict[str, Any]]:
        """Generate Python class tests"""
        class_name = func['name']
        
        return [{
            'name': f'test_{class_name.lower()}_instantiation',
            'description': f'Test {class_name} class instantiation',
            'type': 'unit',
            'code': f'''import unittest

class Test{class_name}(unittest.TestCase):
    
    def test_instantiation(self):
        """Test {class_name} can be instantiated"""
        instance = {class_name}()
        self.assertIsInstance(instance, {class_name})
    
    def test_methods_exist(self):
        """Test expected methods exist"""
        instance = {class_name}()
        # Add specific method tests based on class analysis

if __name__ == '__main__':
    unittest.main()''',
            'expected_result': 'pass',
            'framework': 'unittest'
        }]
    
    def _generate_typescript_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate TypeScript-specific tests"""
        # TypeScript tests are similar to JavaScript but with type checking
        js_tests = self._generate_javascript_tests(code, functions)
        
        # Add TypeScript-specific type tests
        for test in js_tests:
            if 'framework' in test:
                test['framework'] = 'jest-typescript'
            
            # Add type checking assertions
            if 'should return expected result' in test['name']:
                test['code'] = test['code'].replace(
                    'expect(typeof result).toBe(',
                    'expect(typeof result).toBe('
                )
        
        return js_tests
    
    def _generate_java_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate Java JUnit tests"""
        test_cases = []
        
        for func in functions:
            func_name = func['name']
            
            test_cases.append({
                'name': f'test{func_name.capitalize()}Basic',
                'description': f'Test basic functionality of {func_name}',
                'type': 'unit',
                'code': f'''import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class {func_name.capitalize()}Test {{
    
    @Test
    void test{func_name.capitalize()}Basic() {{
        // Test basic functionality
        assertDoesNotThrow(() -> {{
            {func_name}({self._get_test_values(func['parameters'])});
        }});
    }}
    
    @Test
    void test{func_name.capitalize()}NullInput() {{
        // Test null input handling
        assertThrows(IllegalArgumentException.class, () -> {{
            {func_name}(null);
        }});
    }}
}}''',
                'expected_result': 'pass',
                'framework': 'junit5'
            })
        
        return test_cases
    
    def _generate_generic_tests(self, code: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate generic tests for unsupported languages"""
        test_cases = []
        
        for func in functions:
            test_cases.append({
                'name': f'test_{func["name"]}_generic',
                'description': f'Generic test for {func["name"]}',
                'type': 'unit',
                'code': f'''// Generic test template for {func["name"]}
// Implement language-specific test framework
function test_{func["name"]}() {{
    // Test implementation
    assert({func["name"]}() !== undefined);
}}''',
                'expected_result': 'pass',
                'framework': 'generic'
            })
        
        return test_cases
    
    def _generate_edge_cases(self, code: str, language: str, functions: List[Dict]) -> List[Dict[str, Any]]:
        """Generate AI-powered edge case tests"""
        edge_cases = []
        
        for func in functions:
            func_name = func['name']
            
            # Generate boundary value tests
            if func['parameters']:
                edge_cases.append({
                    'name': f'{func_name}_boundary_values',
                    'description': f'Test {func_name} with boundary values',
                    'type': 'edge_case',
                    'code': self._generate_boundary_test(func_name, language),
                    'expected_result': 'pass',
                    'framework': self._get_framework_for_language(language)
                })
            
            # Generate negative test cases
            edge_cases.append({
                'name': f'{func_name}_negative_cases',
                'description': f'Test {func_name} with negative scenarios',
                'type': 'negative',
                'code': self._generate_negative_test(func_name, language),
                'expected_result': 'pass',
                'framework': self._get_framework_for_language(language)
            })
        
        return edge_cases
    
    def _generate_boundary_test(self, func_name: str, language: str) -> str:
        """Generate boundary value tests"""
        if language in ['javascript', 'typescript']:
            return f'''describe('{func_name} boundary tests', () => {{
    test('should handle zero', () => {{
        expect(() => {func_name}(0)).not.toThrow();
    }});
    
    test('should handle negative numbers', () => {{
        expect(() => {func_name}(-1)).not.toThrow();
    }});
    
    test('should handle large numbers', () => {{
        expect(() => {func_name}(Number.MAX_SAFE_INTEGER)).not.toThrow();
    }});
}});'''
        elif language == 'python':
            return f'''def test_{func_name}_boundary_values(self):
    """Test boundary values"""
    # Test with zero
    self.assertIsNotNone({func_name}(0))
    
    # Test with negative numbers
    try:
        result = {func_name}(-1)
    except ValueError:
        pass  # Expected for some functions
    
    # Test with large numbers
    try:
        result = {func_name}(sys.maxsize)
    except (OverflowError, RecursionError):
        pass  # Expected for some functions'''
        
        return f'// Boundary test for {func_name}'
    
    def _generate_negative_test(self, func_name: str, language: str) -> str:
        """Generate negative test cases"""
        if language in ['javascript', 'typescript']:
            return f'''describe('{func_name} negative tests', () => {{
    test('should handle empty string', () => {{
        expect(() => {func_name}('')).not.toThrow();
    }});
    
    test('should handle array input', () => {{
        expect(() => {func_name}([])).not.toThrow();
    }});
}});'''
        elif language == 'python':
            return f'''def test_{func_name}_negative_cases(self):
    """Test negative cases"""
    # Test with empty string
    try:
        result = {func_name}('')
    except (TypeError, ValueError):
        pass  # Expected
    
    # Test with list input
    try:
        result = {func_name}([])
    except (TypeError, ValueError):
        pass  # Expected'''
        
        return f'// Negative test for {func_name}'
    
    def _get_test_values(self, parameters: List[str]) -> str:
        """Get appropriate test values for parameters"""
        if not parameters:
            return ''
        
        if len(parameters) == 1:
            return '5'  # Default test value
        
        return ', '.join(['5'] * len(parameters))
    
    def _get_framework_for_language(self, language: str) -> str:
        """Get appropriate test framework for language"""
        frameworks = {
            'javascript': 'jest',
            'typescript': 'jest',
            'python': 'unittest',
            'java': 'junit5'
        }
        return frameworks.get(language, 'generic')
    
    def process(self, code: str, language: str, **kwargs) -> List[Dict[str, Any]]:
        """Main processing method"""
        functions = kwargs.get('functions', [])
        return self.generate_tests(code, language, functions)
    
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