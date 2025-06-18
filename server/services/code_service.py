"""
Code Service for processing and managing code analysis results
"""

from typing import Dict, Any, List
from datetime import datetime
import hashlib
import json

class CodeService:
    """Service for processing code analysis results"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def process_analysis(self, analysis: Dict[str, Any], code: str, language: str) -> Dict[str, Any]:
        """Process and format analysis results"""
        # Generate code hash for caching
        code_hash = self._generate_code_hash(code)
        
        # Format the analysis result
        processed_analysis = {
            'issues': self._format_issues(analysis.get('issues', [])),
            'metrics': self._format_metrics(analysis.get('metrics', {})),
            'functions': self._format_functions(analysis.get('functions', [])),
            'ai_insights': analysis.get('ai_insights', {}),
            'code_hash': code_hash,
            'language': language,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Cache the result
        self.analysis_cache[code_hash] = processed_analysis
        
        return processed_analysis
    
    def process_refactor_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format refactoring suggestions"""
        processed_suggestions = []
        
        for suggestion in suggestions:
            processed_suggestion = {
                'type': suggestion.get('type', 'general'),
                'description': suggestion.get('title', suggestion.get('description', '')),
                'originalCode': suggestion.get('original_code', ''),
                'refactoredCode': suggestion.get('refactored_code', ''),
                'lineStart': suggestion.get('line_start', 1),
                'lineEnd': suggestion.get('line_end', 1),
                'impact': suggestion.get('impact', 'medium'),
                'confidence': suggestion.get('confidence', 50),
                'benefits': suggestion.get('benefits', []),
                'estimatedImprovement': suggestion.get('estimated_improvement', '')
            }
            processed_suggestions.append(processed_suggestion)
        
        return processed_suggestions
    
    def process_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format test cases"""
        processed_tests = []
        
        for test_case in test_cases:
            processed_test = {
                'name': test_case.get('name', ''),
                'description': test_case.get('description', ''),
                'type': test_case.get('type', 'unit'),
                'code': test_case.get('code', ''),
                'expectedResult': test_case.get('expected_result', 'pass'),
                'testData': test_case.get('test_data'),
                'framework': test_case.get('framework', 'jest')
            }
            processed_tests.append(processed_test)
        
        return processed_tests
    
    def _generate_code_hash(self, code: str) -> str:
        """Generate hash for code caching"""
        return hashlib.md5(code.encode()).hexdigest()
    
    def _format_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format code issues"""
        formatted_issues = []
        
        for issue in issues:
            formatted_issue = {
                'severity': issue.get('severity', 'info'),
                'message': issue.get('message', ''),
                'line': issue.get('line', 1),
                'column': issue.get('column', 1),
                'suggestion': issue.get('suggestion', ''),
                'rule': issue.get('rule', '')
            }
            formatted_issues.append(formatted_issue)
        
        return formatted_issues
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format code metrics"""
        return {
            'complexity': min(metrics.get('complexity', 1), 10),
            'maintainability': min(metrics.get('maintainability', 10), 10),
            'codeQualityScore': self._calculate_quality_score(metrics),
            'linesOfCode': metrics.get('lines_of_code', 0),
            'cyclomaticComplexity': metrics.get('cyclomatic_complexity', 1)
        }
    
    def _format_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format function information"""
        formatted_functions = []
        
        for func in functions:
            formatted_function = {
                'name': func.get('name', ''),
                'startLine': func.get('start_line', 1),
                'endLine': func.get('end_line', 1),
                'complexity': func.get('complexity', 1),
                'parameters': func.get('parameters', [])
            }
            formatted_functions.append(formatted_function)
        
        return formatted_functions
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall code quality score"""
        complexity = metrics.get('complexity', 1)
        maintainability = metrics.get('maintainability', 10)
        
        # Simple scoring algorithm
        complexity_score = max(0, 10 - complexity)
        maintainability_score = maintainability
        
        # Weight the scores
        quality_score = int((complexity_score * 0.4 + maintainability_score * 0.6))
        return min(max(quality_score, 0), 100)
    
    def get_cached_analysis(self, code_hash: str) -> Dict[str, Any]:
        """Get cached analysis result"""
        return self.analysis_cache.get(code_hash)
    
    def clear_cache(self):
        """Clear analysis cache"""
        self.analysis_cache.clear()