# 📡 API Reference

> Complete API documentation for CogniCode Agent

## 🎯 API Overview

CogniCode Agent provides both RESTful HTTP endpoints and real-time WebSocket connections for code analysis, refactoring, and test generation.

**Base URL**: `http://localhost:5000/api`

**Available Protocols**:
- 🌐 **HTTP REST API**: Synchronous request/response
- ⚡ **WebSocket API**: Real-time bidirectional communication

## 🔐 Authentication

CogniCode Agent currently runs locally without authentication. For production deployments, consider adding:

- API Keys for service authentication
- Rate limiting per client
- CORS configuration for web clients

## 🌐 REST API Endpoints

### Code Analysis

#### `POST /api/analyze`

Analyze code for bugs, performance issues, and quality metrics.

**Request:**
```http
POST /api/analyze HTTP/1.1
Content-Type: application/json

{
  "code": "function fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}",
  "language": "javascript",
  "options": {
    "depth": "standard",
    "focus": ["performance", "security"],
    "include_metrics": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid-12345",
  "timestamp": "2025-07-02T10:30:00Z",
  "results": {
    "issues": [
      {
        "type": "performance",
        "severity": "warning",
        "line": 3,
        "column": 10,
        "message": "Recursive function may cause exponential time complexity",
        "suggestion": "Consider using memoization or iterative approach",
        "rule": "avoid-exponential-recursion"
      }
    ],
    "metrics": {
      "quality_score": 65,
      "complexity": {
        "cyclomatic": 2,
        "cognitive": 3,
        "halstead_volume": 45.2
      },
      "maintainability": {
        "index": 78,
        "technical_debt": "1.5 hours"
      }
    },
    "security": {
      "vulnerabilities": [],
      "risk_score": 0
    }
  }
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Source code to analyze |
| `language` | string | Yes | Programming language (javascript, python, java, etc.) |
| `options.depth` | string | No | Analysis depth: "quick", "standard", "deep" (default: "standard") |
| `options.focus` | array | No | Focus areas: ["performance", "security", "maintainability", "style"] |
| `options.include_metrics` | boolean | No | Include detailed metrics (default: true) |

### Code Refactoring

#### `POST /api/refactor`

Get intelligent refactoring suggestions and optimized code.

**Request:**
```http
POST /api/refactor HTTP/1.1
Content-Type: application/json

{
  "code": "var users = [];\nfor (var i = 0; i < data.length; i++) {\n  if (data[i].active == true) {\n    users.push(data[i]);\n  }\n}",
  "language": "javascript",
  "options": {
    "focus": ["modernization", "performance"],
    "preserve_functionality": true,
    "target_version": "es2020"
  }
}
```

**Response:**
```json
{
  "success": true,
  "refactor_id": "uuid-67890",
  "timestamp": "2025-07-02T10:35:00Z",
  "suggestions": [
    {
      "type": "modernization",
      "priority": "high",
      "title": "Use modern ES6+ syntax",
      "description": "Replace var with const/let and use array methods",
      "before": "var users = [];\nfor (var i = 0; i < data.length; i++) {\n  if (data[i].active == true) {\n    users.push(data[i]);\n  }\n}",
      "after": "const users = data.filter(item => item.active === true);",
      "benefits": [
        "Reduced code complexity",
        "Better readability",
        "Improved performance"
      ],
      "confidence": 0.95
    }
  ],
  "refactored_code": "const users = data.filter(item => item.active === true);",
  "improvements": {
    "lines_reduced": 4,
    "complexity_reduction": 60,
    "performance_gain": "estimated 15% faster"
  }
}
```

### Test Generation

#### `POST /api/generate-tests`

Generate comprehensive unit tests for the provided code.

**Request:**
```http
POST /api/generate-tests HTTP/1.1
Content-Type: application/json

{
  "code": "function divide(a, b) {\n  if (b === 0) throw new Error('Division by zero');\n  return a / b;\n}",
  "language": "javascript",
  "options": {
    "test_framework": "jest",
    "include_edge_cases": true,
    "coverage_target": 90
  }
}
```

**Response:**
```json
{
  "success": true,
  "test_id": "uuid-11111",
  "timestamp": "2025-07-02T10:40:00Z",
  "tests": {
    "framework": "jest",
    "test_code": "describe('divide function', () => {\n  test('should divide positive numbers correctly', () => {\n    expect(divide(10, 2)).toBe(5);\n    expect(divide(15, 3)).toBe(5);\n  });\n\n  test('should handle negative numbers', () => {\n    expect(divide(-10, 2)).toBe(-5);\n    expect(divide(10, -2)).toBe(-5);\n  });\n\n  test('should throw error for division by zero', () => {\n    expect(() => divide(10, 0)).toThrow('Division by zero');\n  });\n});",
    "test_cases": [
      {
        "name": "should divide positive numbers correctly",
        "type": "positive_case",
        "inputs": [[10, 2], [15, 3]],
        "expected": [5, 5]
      },
      {
        "name": "should handle negative numbers",
        "type": "edge_case",
        "inputs": [[-10, 2], [10, -2]],
        "expected": [-5, -5]
      },
      {
        "name": "should throw error for division by zero",
        "type": "error_case",
        "inputs": [[10, 0]],
        "expected": "Error: Division by zero"
      }
    ],
    "coverage_estimate": 95
  }
}
```

### Service Health

#### `GET /api/health`

Check service health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-02T10:45:00Z",
  "version": "1.0.0",
  "services": {
    "linter_agent": "running",
    "refactor_agent": "running",
    "testgen_agent": "running",
    "model_cache": "ready"
  },
  "metrics": {
    "uptime": "2 days, 3 hours",
    "requests_served": 1247,
    "average_response_time": "850ms",
    "cache_hit_rate": 0.85
  }
}
```

#### `GET /api/metrics`

Get detailed performance metrics.

**Response:**
```json
{
  "timestamp": "2025-07-02T10:50:00Z",
  "performance": {
    "total_requests": 1247,
    "requests_per_minute": 12.3,
    "average_response_time": 850,
    "p95_response_time": 1200,
    "error_rate": 0.02
  },
  "memory": {
    "total_mb": 2048,
    "used_mb": 1456,
    "available_mb": 592,
    "cache_size_mb": 345
  },
  "models": {
    "linter_model": {
      "status": "loaded",
      "memory_mb": 234,
      "inference_count": 567,
      "average_inference_time": 420
    },
    "refactor_model": {
      "status": "loaded", 
      "memory_mb": 189,
      "inference_count": 423,
      "average_inference_time": 680
    }
  }
}
```

## ⚡ WebSocket API

### Connection

Connect to the WebSocket endpoint for real-time communication:

```javascript
const socket = io('http://localhost:5000', {
  transports: ['websocket'],
  reconnection: true,
  reconnectionAttempts: 5
});
```

### Events

#### Client → Server Events

**`analyze_code`** - Request code analysis
```javascript
socket.emit('analyze_code', {
  code: "function example() { ... }",
  language: "javascript",
  options: {
    depth: "standard",
    real_time: true
  }
});
```

**`refactor_code`** - Request refactoring suggestions
```javascript
socket.emit('refactor_code', {
  code: "var x = 1; var y = 2;",
  language: "javascript",
  focus: ["modernization"]
});
```

**`generate_tests`** - Request test generation
```javascript
socket.emit('generate_tests', {
  code: "function add(a, b) { return a + b; }",
  language: "javascript",
  framework: "jest"
});
```

**`cancel_operation`** - Cancel ongoing operation
```javascript
socket.emit('cancel_operation', {
  operation_id: "uuid-12345"
});
```

#### Server → Client Events

**`analysis_progress`** - Analysis progress updates
```javascript
socket.on('analysis_progress', (data) => {
  console.log(`Progress: ${data.percentage}% - ${data.stage}`);
  // data: { operation_id, percentage, stage, eta }
});
```

**`analysis_result`** - Analysis completed
```javascript
socket.on('analysis_result', (result) => {
  // Same structure as REST API response
  console.log('Analysis complete:', result);
});
```

**`refactor_result`** - Refactoring suggestions ready
```javascript
socket.on('refactor_result', (result) => {
  console.log('Refactor suggestions:', result.suggestions);
});
```

**`test_result`** - Generated tests ready
```javascript
socket.on('test_result', (result) => {
  console.log('Generated tests:', result.tests);
});
```

**`error`** - Error occurred
```javascript
socket.on('error', (error) => {
  console.error('API Error:', error);
  // error: { type, message, operation_id, details }
});
```

**`connection_status`** - Connection status updates
```javascript
socket.on('connection_status', (status) => {
  // status: { connected, agent_status, queue_length }
});
```

## 🔧 SDK and Client Libraries

### JavaScript/TypeScript SDK

```typescript
import { CogniCodeClient } from '@cognicode/client';

const client = new CogniCodeClient({
  baseUrl: 'http://localhost:5000',
  apiKey: 'optional-api-key'
});

// Analyze code
const analysis = await client.analyze({
  code: 'function example() { ... }',
  language: 'javascript'
});

// Real-time analysis
client.onAnalysisProgress((progress) => {
  console.log(`${progress.percentage}% complete`);
});

const result = await client.analyzeRealTime({
  code: 'function example() { ... }',
  language: 'javascript'
});
```

### Python SDK

```python
from cognicode_client import CogniCodeClient

client = CogniCodeClient(base_url='http://localhost:5000')

# Analyze code
result = await client.analyze(
    code='def example(): pass',
    language='python'
)

# Generate tests
tests = await client.generate_tests(
    code='def add(a, b): return a + b',
    language='python',
    framework='pytest'
)
```

## 🚨 Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 422 | Unprocessable Entity | Invalid code or language |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server processing error |
| 503 | Service Unavailable | AI models not ready |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "type": "validation_error",
    "message": "Invalid programming language specified",
    "code": "INVALID_LANGUAGE",
    "details": {
      "provided": "javascrpt",
      "supported": ["javascript", "typescript", "python", "java"]
    },
    "request_id": "uuid-error-123"
  }
}
```

### Common Error Types

**`validation_error`** - Invalid input parameters
```json
{
  "type": "validation_error",
  "message": "Code cannot be empty",
  "code": "EMPTY_CODE"
}
```

**`processing_error`** - AI model processing failed
```json
{
  "type": "processing_error", 
  "message": "Code analysis failed due to syntax errors",
  "code": "SYNTAX_ERROR",
  "details": {
    "line": 5,
    "column": 12,
    "syntax_error": "Unexpected token ';'"
  }
}
```

**`timeout_error`** - Request timeout
```json
{
  "type": "timeout_error",
  "message": "Analysis timeout after 30 seconds",
  "code": "ANALYSIS_TIMEOUT"
}
```

**`resource_error`** - Insufficient resources
```json
{
  "type": "resource_error",
  "message": "Insufficient memory to load AI model",
  "code": "OUT_OF_MEMORY"
}
```

## 🎛️ Rate Limiting

### Limits

| Endpoint | Requests per Minute | Burst Limit |
|----------|-------------------|-------------|
| `/api/analyze` | 30 | 5 |
| `/api/refactor` | 20 | 3 |
| `/api/generate-tests` | 15 | 2 |
| `/api/health` | 100 | 10 |

### Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1625097600
Retry-After: 60
```

## 🔄 Pagination

For endpoints returning lists, use pagination parameters:

```http
GET /api/analysis-history?page=2&limit=50&sort=timestamp&order=desc
```

**Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field
- `order`: Sort order (asc, desc)

## 🎯 Best Practices

### 1. Use WebSockets for Real-time Analysis
```javascript
// Good: Real-time updates
socket.emit('analyze_code', { code, language });
socket.on('analysis_progress', updateProgress);

// Avoid: Polling REST API
setInterval(() => checkAnalysisStatus(), 1000);
```

### 2. Implement Proper Error Handling
```javascript
try {
  const result = await client.analyze({ code, language });
  handleSuccess(result);
} catch (error) {
  if (error.code === 'SYNTAX_ERROR') {
    showSyntaxError(error.details);
  } else {
    showGenericError(error.message);
  }
}
```

### 3. Cache Results Appropriately
```javascript
const cacheKey = `${language}-${codeHash}`;
const cached = cache.get(cacheKey);
if (cached) {
  return cached;
}

const result = await client.analyze({ code, language });
cache.set(cacheKey, result, { ttl: 300 }); // 5 minutes
return result;
```

### 4. Handle Rate Limits Gracefully
```javascript
if (response.status === 429) {
  const retryAfter = response.headers['retry-after'];
  await sleep(retryAfter * 1000);
  return retryRequest();
}
```

---

<div align="center">

**📡 Complete API reference for seamless integration**

[🏗️ Architecture Guide](architecture.md) | [🛠️ Development Setup](development.md) | [🏠 Back to Docs](../README.md)

</div>
