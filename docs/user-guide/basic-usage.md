# 🎯 Basic Usage Guide

> Learn how to use CogniCode Agent effectively

## 🚀 Getting Started

CogniCode Agent is designed to be intuitive and powerful. This guide will walk you through the basic usage patterns and core features.

## 📝 Interface Overview

### Main Components

```
┌─────────────────────────────────────────────────────────────┐
│ 🏠 CogniCode Agent          Language: [JavaScript ▼]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │                     │    │  📊 Analysis                │ │
│  │                     │    │  🔄 Refactor               │ │
│  │  Monaco Code Editor │    │  🧪 Tests                  │ │
│  │                     │    │                             │ │
│  │                     │    │  [Results Panel]            │ │
│  │                     │    │                             │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
│                                                             │
│  [🔍 Analyze Code]  [🧹 Clear]  [💾 Save]  [📤 Export]    │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements

1. **Code Editor**: Monaco-based editor with syntax highlighting
2. **Language Selector**: Choose your programming language
3. **Action Buttons**: Analyze, Clear, Save, Export
4. **Results Panel**: Three tabs for different analysis types
5. **Status Indicator**: Shows connection and processing status

## 🎮 Basic Workflow

### 1. Input Code

There are several ways to add code to the editor:

**Option A: Type Directly**
```javascript
function calculateSum(numbers) {
    let sum = 0;
    for (let i = 0; i < numbers.length; i++) {
        sum += numbers[i];
    }
    return sum;
}
```

**Option B: Paste Existing Code**
- Copy code from your IDE
- Paste it into the Monaco editor
- The editor will auto-detect and apply syntax highlighting

**Option C: Upload File**
- Use the file upload feature (coming soon)
- Drag and drop code files

### 2. Select Language

Click the language dropdown and select your programming language:

**Supported Languages:**
- JavaScript
- TypeScript
- Python
- Java
- C++
- C#
- Go
- Rust
- PHP
- Ruby
- And more...

### 3. Analyze Code

Click the **🔍 Analyze Code** button to start the analysis:

```
Processing... ⏳
├── Syntax Analysis ✅
├── Code Quality Check ✅  
├── Performance Analysis ✅
├── Security Scan ✅
└── Generating Insights ✅
```

### 4. Review Results

Check the three result tabs:

#### 📊 Analysis Tab
- **Issues Found**: Bugs, warnings, style issues
- **Quality Score**: Overall code quality rating
- **Metrics**: Complexity, maintainability, performance
- **Security**: Potential vulnerabilities

#### 🔄 Refactor Tab
- **Optimizations**: Performance improvements
- **Style Fixes**: Code style enhancements
- **Pattern Improvements**: Better coding patterns
- **Before/After**: Side-by-side comparisons

#### 🧪 Tests Tab
- **Unit Tests**: Generated test cases
- **Edge Cases**: Boundary condition tests
- **Integration Tests**: Component interaction tests
- **Coverage**: Test coverage analysis

## 📋 Practical Examples

### Example 1: Performance Optimization

**Input Code:**
```javascript
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

**Analysis Results:**
- ⚠️ **Performance Issue**: Exponential time complexity O(2^n)
- 💡 **Suggestion**: Use memoization or iterative approach
- 🧪 **Tests Generated**: Edge cases for n=0, n=1, large values

**Refactored Code:**
```javascript
function fibonacci(n, memo = {}) {
    if (n in memo) return memo[n];
    if (n <= 1) return n;
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo);
    return memo[n];
}
```

### Example 2: Code Quality Improvement

**Input Code:**
```python
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
```

**Analysis Results:**
- 💡 **Style**: Use list comprehension for better readability
- 🔧 **Optimization**: More Pythonic approach available
- 📝 **Naming**: Consider more descriptive variable names

**Refactored Code:**
```python
def double_positive_values(numbers):
    """Return a list of doubled positive numbers from input."""
    return [num * 2 for num in numbers if num > 0]
```

### Example 3: Security Enhancement

**Input Code:**
```javascript
function getUserData(userId) {
    const query = "SELECT * FROM users WHERE id = " + userId;
    return database.query(query);
}
```

**Analysis Results:**
- 🚨 **Security Risk**: SQL injection vulnerability
- 🔒 **Solution**: Use parameterized queries
- 🧪 **Tests**: Security test cases generated

## 🎛️ Advanced Features

### Language-Specific Analysis

Different languages have specialized analysis:

**JavaScript/TypeScript:**
- ESLint-style issues
- TypeScript type checking
- React/Node.js best practices
- Performance optimizations

**Python:**
- PEP 8 compliance
- Type hints suggestions
- Performance improvements
- Security best practices

**Java:**
- Code conventions
- Design patterns
- Performance optimization
- Memory management

### Customization Options

**Analysis Depth:**
- Quick Scan (30 seconds)
- Standard Analysis (1-2 minutes)
- Deep Analysis (3-5 minutes)

**Focus Areas:**
- Performance
- Security
- Maintainability
- Style & Conventions

## 💡 Pro Tips

### 1. Incremental Analysis
Instead of analyzing large files:
```javascript
// Good: Analyze functions individually
function calculateTax(income) {
    // Function logic here
}
```

### 2. Use Meaningful Examples
Provide realistic code samples:
```python
# Good: Real-world example
def calculate_shipping_cost(weight, distance, express=False):
    base_cost = weight * 0.5 + distance * 0.1
    return base_cost * 1.5 if express else base_cost
```

### 3. Leverage Suggestions
Apply refactoring suggestions incrementally:
- Start with critical issues
- Apply performance improvements
- Clean up style issues
- Add generated tests

### 4. Combine with Your Workflow
- Analyze code before commits
- Use for code reviews
- Generate tests for new features
- Optimize performance bottlenecks

## 🔧 Troubleshooting

### Common Issues

**Analysis Takes Too Long**
- Try smaller code snippets
- Check internet connection
- Verify backend status

**No Results Shown**
- Ensure valid syntax
- Check language selection
- Look for error messages

**Suggestions Not Helpful**
- Provide more context
- Use complete functions
- Try different analysis depth

## 📊 Understanding Results

### Quality Scores

| Score | Meaning | Action Needed |
|-------|---------|---------------|
| 90-100 | Excellent | Minor improvements |
| 70-89 | Good | Some optimization |
| 50-69 | Fair | Several improvements |
| 30-49 | Poor | Major refactoring |
| 0-29 | Critical | Complete rewrite |

### Issue Severity

- 🚨 **Critical**: Must fix (security, bugs)
- ⚠️ **Warning**: Should fix (performance, maintainability)
- 💡 **Info**: Consider fixing (style, conventions)

## 🎯 Next Steps

Once you're comfortable with basic usage:

1. **Explore [Advanced Features](features.md)** for power user capabilities
2. **Check [API Documentation](../api/)** for integration options
3. **Read [Best Practices](best-practices.md)** for optimal usage
4. **Join the [Community](https://github.com/Edmon02/cognicode-agent/discussions)** for tips and tricks

---

<div align="center">

**🎉 You're ready to boost your code quality!**

[🚀 Advanced Features](features.md) | [❓ FAQ](faq.md) | [🏠 Back to Docs](../README.md)

</div>
