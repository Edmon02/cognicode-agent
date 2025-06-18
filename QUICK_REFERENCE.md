# 🎬 QUICK REFERENCE - Demo Recording

## 📸 SCREENSHOT ORDER:
1. **Hero Interface** (`01_hero_interface.png`) - JavaScript fibonacci code
2. **Analysis Results** (`02_analysis_results.png`) - Click Analyze, show results
3. **Refactor Suggestions** (`03_refactor_suggestions.png`) - Switch to Refactor tab
4. **Generated Tests** (`04_generated_tests.png`) - Switch to Tests tab
5. **Python Demo** (`05_python_demo.png`) - Change to Python, analyze

## 🎥 VIDEO TIMELINE (2:30 min):
- **0:00-0:15** → Opening Hook (show interface)
- **0:15-0:30** → Problem Setup (point to code issues)
- **0:30-1:15** → Analysis Demo (click Analyze, show results)
- **1:15-1:45** → Refactoring Demo (show suggestions)
- **1:45-2:15** → Test Generation (show tests)
- **2:15-2:30** → Closing (privacy + productivity)

## 🗣️ KEY PHRASES:
- "AI-powered development tool"
- "Multiple specialized agents"
- "Real-time analysis"
- "Intelligent solutions"
- "Runs locally - privacy-first"
- "Boost productivity"

## 📱 RECORDING SETUP:
- QuickTime Player → New Screen Recording
- Select browser window only
- Internal microphone ON
- 1080p resolution
- Do Not Disturb mode ON

## 🚀 DEMO CODE READY:
**JavaScript:**
```javascript
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

function processUserData(users) {
    var results = [];
    for (var i = 0; i < users.length; i++) {
        if (users[i].active == true) {
            results.push({
                id: users[i].id,
                name: users[i].name.toUpperCase(),
                score: fibonacci(users[i].level)
            });
        }
    }
    return results;
}

const users = [
    { id: 1, name: "alice", active: true, level: 10 },
    { id: 2, name: "bob", active: false, level: 15 },
    { id: 3, name: "charlie", active: true, level: 8 }
];

console.log(processUserData(users));
```

**Python:**
```python
def calculate_discount(price, discount_percent, user_type):
    if user_type == "premium":
        discount_percent = discount_percent + 10
    
    discount_amount = price * discount_percent / 100
    final_price = price - discount_amount
    
    if final_price < 0:
        final_price = 0
        
    return final_price

print(calculate_discount(100, 20, "premium"))
print(calculate_discount(50, 15, "regular"))
print(calculate_discount(30, 100, "regular"))
```
