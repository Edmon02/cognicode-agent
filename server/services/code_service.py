"""
Code Service for processing and managing code analysis results
Optimized for performance and memory efficiency
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import json
import threading
import weakref
import gc

class CodeService:
    """Service for processing code analysis results with enhanced caching and memory management"""
    
    def __init__(self, cache_timeout: int = 3600):
        self.analysis_cache: Dict[str, Dict] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_timeout = cache_timeout
        self._lock = threading.Lock()
        
        # Memory management
        self._max_cache_size = 1000
        self._cache_access_count: Dict[str, int] = {}
        
    def process_analysis(self, analysis: Dict[str, Any], code: str, language: str) -> Dict[str, Any]:
        """Process and format analysis results with caching"""
        # Generate code hash for caching
        code_hash = self._generate_code_hash(code)
        
        # Check if already cached and still valid
        cached_result = self.get_cached_analysis(code)
        if cached_result:
            return cached_result
        
        # Format the analysis result
        processed_analysis = {
            'issues': self._format_issues(analysis.get('issues', [])),
            'metrics': self._format_metrics(analysis.get('metrics', {})),
            'functions': self._format_functions(analysis.get('functions', [])),
            'ai_insights': analysis.get('ai_insights', {}),
            'code_hash': code_hash,
            'language': language,
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time': self._get_processing_time(analysis)
        }
        
        # Cache the result with memory management
        self._cache_result(code_hash, processed_analysis)
        
        return processed_analysis
    
    def process_refactor_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format refactoring suggestions"""
        processed_suggestions = []
        
        for suggestion in suggestions:
            processed_suggestion = {
                'type': suggestion.get('type', 'general'),
                'title': suggestion.get('title', suggestion.get('description', '')),
                'description': suggestion.get('description', ''),
                'originalCode': suggestion.get('original_code', ''),
                'refactoredCode': suggestion.get('refactored_code', ''),
                'lineStart': suggestion.get('line_start', 1),
                'lineEnd': suggestion.get('line_end', 1),
                'impact': suggestion.get('impact', 'medium'),
                'impactScore': suggestion.get('impact_score', 5),
                'confidence': suggestion.get('confidence', 50),
                'benefits': suggestion.get('benefits', []),
                'estimatedImprovement': suggestion.get('estimated_improvement', ''),
                'id': self._generate_suggestion_id(suggestion)
            }
            processed_suggestions.append(processed_suggestion)
        
        # Sort by impact score and confidence
        processed_suggestions.sort(
            key=lambda x: (x.get('impactScore', 0), x.get('confidence', 0)), 
            reverse=True
        )
        
        return processed_suggestions
    
    def process_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format test cases"""
        processed_tests = []
        
        for i, test_case in enumerate(test_cases):
            processed_test = {
                'id': f"test_{i}_{self._generate_test_id(test_case)}",
                'name': test_case.get('name', f'Test {i+1}'),
                'description': test_case.get('description', ''),
                'type': test_case.get('type', 'unit'),
                'code': test_case.get('code', ''),
                'expectedResult': test_case.get('expected_result', 'pass'),
                'testData': test_case.get('test_data'),
                'framework': test_case.get('framework', 'jest'),
                'priority': self._calculate_test_priority(test_case),
                'estimatedExecutionTime': self._estimate_execution_time(test_case)
            }
            processed_tests.append(processed_test)
        
        # Sort by priority and type
        processed_tests.sort(
            key=lambda x: (x.get('priority', 0), x.get('type') == 'unit'), 
            reverse=True
        )
        
        return processed_tests
    
    def get_cached_analysis(self, code: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result with expiration check"""
        code_hash = self._generate_code_hash(code)
        
        with self._lock:
            if code_hash in self.analysis_cache:
                # Check if cache is still valid
                timestamp = self.cache_timestamps.get(code_hash)
                if timestamp and datetime.utcnow() - timestamp < timedelta(seconds=self.cache_timeout):
                    # Update access count for LRU
                    self._cache_access_count[code_hash] = self._cache_access_count.get(code_hash, 0) + 1
                    return self.analysis_cache[code_hash].copy()
                else:
                    # Cache expired, remove it
                    self._remove_from_cache(code_hash)
        
        return None
    
    def clear_old_cache(self):
        """Clear expired cache entries and manage memory"""
        with self._lock:
            current_time = datetime.utcnow()
            expired_keys = []
            
            for code_hash, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > timedelta(seconds=self.cache_timeout):
                    expired_keys.append(code_hash)
            
            for key in expired_keys:
                self._remove_from_cache(key)
            
            # If cache is still too large, remove least recently used items
            if len(self.analysis_cache) > self._max_cache_size:
                self._cleanup_lru_cache()
            
            # Trigger garbage collection
            gc.collect()
    
    def clear_cache(self):
        """Clear all cache entries"""
        with self._lock:
            self.analysis_cache.clear()
            self.cache_timestamps.clear()
            self._cache_access_count.clear()
            gc.collect()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'total_entries': len(self.analysis_cache),
                'max_size': self._max_cache_size,
                'cache_timeout': self.cache_timeout,
                'memory_usage': self._estimate_cache_memory(),
                'most_accessed': self._get_most_accessed_entries(5)
            }
    
    def _cache_result(self, code_hash: str, result: Dict[str, Any]):
        """Cache result with memory management"""
        with self._lock:
            # Check if we need to make space
            if len(self.analysis_cache) >= self._max_cache_size:
                self._cleanup_lru_cache()
            
            self.analysis_cache[code_hash] = result
            self.cache_timestamps[code_hash] = datetime.utcnow()
            self._cache_access_count[code_hash] = 1
    
    def _remove_from_cache(self, code_hash: str):
        """Remove entry from all cache structures"""
        self.analysis_cache.pop(code_hash, None)
        self.cache_timestamps.pop(code_hash, None)
        self._cache_access_count.pop(code_hash, None)
    
    def _cleanup_lru_cache(self):
        """Remove least recently used cache entries"""
        if not self._cache_access_count:
            return
        
        # Sort by access count (ascending) and remove the least used
        sorted_items = sorted(self._cache_access_count.items(), key=lambda x: x[1])
        items_to_remove = max(1, len(sorted_items) // 4)  # Remove 25%
        
        for code_hash, _ in sorted_items[:items_to_remove]:
            self._remove_from_cache(code_hash)
    
    def _generate_code_hash(self, code: str) -> str:
        """Generate hash for code caching"""
        return hashlib.md5(code.encode('utf-8')).hexdigest()
    
    def _generate_suggestion_id(self, suggestion: Dict[str, Any]) -> str:
        """Generate unique ID for refactoring suggestion"""
        content = f"{suggestion.get('type', '')}{suggestion.get('title', '')}{suggestion.get('line_start', 0)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _generate_test_id(self, test_case: Dict[str, Any]) -> str:
        """Generate unique ID for test case"""
        content = f"{test_case.get('name', '')}{test_case.get('type', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _format_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format code issues with enhanced information"""
        formatted_issues = []
        
        for issue in issues:
            formatted_issue = {
                'id': self._generate_issue_id(issue),
                'severity': issue.get('severity', 'info'),
                'message': issue.get('message', ''),
                'line': issue.get('line', 1),
                'column': issue.get('column', 1),
                'suggestion': issue.get('suggestion', ''),
                'rule': issue.get('rule', ''),
                'category': self._categorize_issue(issue),
                'fixable': self._is_fixable(issue)
            }
            formatted_issues.append(formatted_issue)
        
        # Sort by severity and line number
        severity_order = {'error': 3, 'warning': 2, 'info': 1}
        formatted_issues.sort(
            key=lambda x: (severity_order.get(x['severity'], 0), x['line']), 
            reverse=True
        )
        
        return formatted_issues
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format code metrics with additional calculations"""
        complexity = min(metrics.get('complexity', 1), 20)
        maintainability = min(metrics.get('maintainability', 10), 10)
        lines_of_code = metrics.get('lines_of_code', 0)
        
        return {
            'complexity': complexity,
            'maintainability': maintainability,
            'codeQualityScore': self._calculate_quality_score(metrics),
            'linesOfCode': lines_of_code,
            'cyclomaticComplexity': metrics.get('cyclomatic_complexity', complexity),
            'technicalDebt': self._calculate_technical_debt(complexity, maintainability),
            'readabilityScore': self._calculate_readability_score(metrics),
            'testabilityScore': self._calculate_testability_score(complexity)
        }
    
    def _format_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format function information with additional metadata"""
        formatted_functions = []
        
        for func in functions:
            formatted_function = {
                'id': self._generate_function_id(func),
                'name': func.get('name', ''),
                'startLine': func.get('start_line', 1),
                'endLine': func.get('end_line', 1),
                'complexity': func.get('complexity', 1),
                'parameters': func.get('parameters', []),
                'parameterCount': len(func.get('parameters', [])),
                'lineCount': func.get('end_line', 1) - func.get('start_line', 1) + 1,
                'type': func.get('type', 'function'),
                'returns': func.get('returns', 'unknown')
            }
            formatted_functions.append(formatted_function)
        
        # Sort by complexity and line count
        formatted_functions.sort(
            key=lambda x: (x.get('complexity', 0), x.get('lineCount', 0)), 
            reverse=True
        )
        
        return formatted_functions
    
    def _generate_issue_id(self, issue: Dict[str, Any]) -> str:
        """Generate unique ID for issue"""
        content = f"{issue.get('severity', '')}{issue.get('message', '')}{issue.get('line', 0)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _generate_function_id(self, func: Dict[str, Any]) -> str:
        """Generate unique ID for function"""
        content = f"{func.get('name', '')}{func.get('start_line', 0)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _categorize_issue(self, issue: Dict[str, Any]) -> str:
        """Categorize issue type"""
        message = issue.get('message', '').lower()
        
        if any(keyword in message for keyword in ['security', 'xss', 'sql', 'eval']):
            return 'security'
        elif any(keyword in message for keyword in ['performance', 'optimize', 'slow']):
            return 'performance'
        elif any(keyword in message for keyword in ['style', 'format', 'indent']):
            return 'style'
        elif any(keyword in message for keyword in ['type', 'undefined', 'null']):
            return 'type'
        else:
            return 'general'
    
    def _is_fixable(self, issue: Dict[str, Any]) -> bool:
        """Determine if issue can be automatically fixed"""
        fixable_patterns = ['console.log', 'var ', '==', 'unused', 'missing semicolon']
        message = issue.get('message', '').lower()
        return any(pattern in message for pattern in fixable_patterns)
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall code quality score (0-100)"""
        complexity = metrics.get('complexity', 1)
        maintainability = metrics.get('maintainability', 10)
        lines_of_code = metrics.get('lines_of_code', 0)
        
        # Normalize complexity (lower is better)
        complexity_score = max(0, 100 - (complexity * 5))
        
        # Normalize maintainability (higher is better)
        maintainability_score = (maintainability / 10) * 100
        
        # Penalize very long functions
        length_penalty = min(20, lines_of_code / 10) if lines_of_code > 50 else 0
        
        # Weight the scores
        quality_score = int(
            (complexity_score * 0.4 + maintainability_score * 0.5 - length_penalty * 0.1)
        )
        
        return min(max(quality_score, 0), 100)
    
    def _calculate_technical_debt(self, complexity: int, maintainability: int) -> str:
        """Calculate technical debt level"""
        debt_score = complexity * 2 - maintainability
        
        if debt_score <= 5:
            return 'low'
        elif debt_score <= 15:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_readability_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate readability score based on various factors"""
        lines_of_code = metrics.get('lines_of_code', 0)
        complexity = metrics.get('complexity', 1)
        
        # Base score
        score = 80
        
        # Penalize long functions
        if lines_of_code > 50:
            score -= min(30, (lines_of_code - 50) / 2)
        
        # Penalize high complexity
        if complexity > 10:
            score -= min(25, (complexity - 10) * 2)
        
        return max(0, min(100, int(score)))
    
    def _calculate_testability_score(self, complexity: int) -> int:
        """Calculate how easy the code is to test"""
        base_score = 100
        
        # Higher complexity reduces testability
        penalty = min(50, complexity * 3)
        
        return max(0, base_score - penalty)
    
    def _calculate_test_priority(self, test_case: Dict[str, Any]) -> int:
        """Calculate test priority (1-10, higher is more important)"""
        test_type = test_case.get('type', 'unit')
        
        priority_map = {
            'unit': 8,
            'integration': 6,
            'edge_case': 7,
            'performance': 5,
            'negative': 6
        }
        
        base_priority = priority_map.get(test_type, 5)
        
        # Boost priority for critical functions
        if 'fibonacci' in test_case.get('name', '').lower():
            base_priority += 1
        
        return min(10, base_priority)
    
    def _estimate_execution_time(self, test_case: Dict[str, Any]) -> str:
        """Estimate test execution time"""
        test_type = test_case.get('type', 'unit')
        
        time_estimates = {
            'unit': '< 10ms',
            'integration': '50-200ms',
            'edge_case': '10-50ms',
            'performance': '100ms-1s',
            'negative': '< 20ms'
        }
        
        return time_estimates.get(test_type, '< 50ms')
    
    def _get_processing_time(self, analysis: Dict[str, Any]) -> float:
        """Extract or estimate processing time"""
        return analysis.get('performance', 0.0)
    
    def _estimate_cache_memory(self) -> int:
        """Estimate cache memory usage in bytes"""
        try:
            import sys
            total_size = 0
            for cache_data in self.analysis_cache.values():
                total_size += sys.getsizeof(json.dumps(cache_data))
            return total_size
        except:
            return len(self.analysis_cache) * 1024  # Rough estimate
    
    def _get_most_accessed_entries(self, count: int) -> List[Dict[str, Any]]:
        """Get most accessed cache entries"""
        sorted_items = sorted(
            self._cache_access_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {'hash': hash_val[:8], 'access_count': access_count} 
            for hash_val, access_count in sorted_items[:count]
        ]