# CogniCode Agent 🧠

> Multi-agent AI system for real-time code analysis, refactoring, and test generation

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Next.js](https://img.shields.io/badge/Next.js-13.5+-black)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-blue)](https://flask.palletsprojects.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple)](https://github.com/Edmon02/cognicode-agent)

CogniCode Agent is a privacy-first, AI-powered development tool that provides real-time code analysis, intelligent refactoring suggestions, and automated unit test generation. Built for Hackathon 2025 with a focus on developer productivity and code quality.

![CogniCode Agent Dashboard](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=CogniCode+Agent+Dashboard)

## ✨ Features

- **🔍 Real-time Code Analysis**: Instant bug detection, style checks, and performance insights
- **⚡ Intelligent Refactoring**: AI-powered suggestions to improve code quality and performance
- **🧪 Automated Test Generation**: Comprehensive unit test creation with edge cases
- **🔒 Privacy-First**: All AI processing runs locally - your code never leaves your machine
- **🌐 Multi-language Support**: JavaScript, TypeScript, Python, Java, and more
- **📊 Code Metrics**: Complexity analysis, maintainability scores, and quality insights
- **🎨 Beautiful UI**: Modern, responsive design with real-time updates

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ and pip
- 4GB+ RAM (8GB+ recommended for AI models)
- 5GB+ free disk space for AI models

### Automated Setup

```bash
# Clone the repository
git clone https://github.com/Edmon02/cognicode-agent.git
cd cognicode-agent

# Run the setup script
chmod +x setup.sh
./setup.sh

# Start the full application
./run-dev.sh
```

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### Frontend Setup
```bash
npm install
```

#### Backend Setup
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Download AI Models (Optional)
```bash
cd server
python scripts/download_models.py
```

#### Start Services
```bash
# Terminal 1 - Backend
cd server && source venv/bin/activate && python app.py

# Terminal 2 - Frontend  
npm run dev
```

</details>

## 📖 Documentation

**📚 [Complete Documentation](docs/README.md)** - Comprehensive guides and references

### Quick Links
- **🚀 [Installation Guide](docs/user-guide/installation.md)** - Detailed setup instructions
- **📖 [Basic Usage](docs/user-guide/basic-usage.md)** - Getting started guide  
- **🎯 [Features Overview](docs/user-guide/features.md)** - All capabilities explained
- **🏗️ [Architecture](docs/developer-guide/architecture.md)** - Technical architecture
- **📡 [API Reference](docs/api/README.md)** - Complete API documentation
- **🎬 [Demo Guide](docs/demo/demo-guide.md)** - Professional demo materials

## 📖 Quick Usage

1. **Open the Application**: Navigate to `http://localhost:3000`
2. **Write/Paste Code**: Use the Monaco editor to input your code
3. **Select Language**: Choose from JavaScript, TypeScript, Python, Java, etc.
4. **Analyze Code**: Click "Analyze" to run AI-powered analysis
5. **Review Results**: Check the Analysis, Refactor, and Tests tabs
6. **Apply Suggestions**: Click "Apply" on refactoring suggestions
7. **Download Tests**: Export generated unit tests

👉 **[Detailed Usage Guide](docs/user-guide/basic-usage.md)**

### Example Workflow

```javascript
// Paste this code and click "Analyze"
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

console.log(fibonacci(10));
```

The AI will detect:
- ⚠️ Performance issue (exponential time complexity)
- 💡 Refactoring suggestion (memoization)
- 🧪 Generated unit tests with edge cases

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│   Linter Agent  │    │ Refactor Agent     │    │ TestGen Agent   │
│                 │    │                    │    │                 │
│ • Bug Detection │    │ • Code Optimization│    │ • Unit Tests    │
│ • Style Analysis│    │ • Pattern Improve. │    │ • Edge Cases    │
│ • Security Check│    │ • Performance Tune │    │ • Integration   │
└─────────────────┘    └────────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Code Service   │
                    │                 │
                    │ • Result        │
                    │   Processing    │
                    │ • Caching       │
                    │ • Coordination  │
                    └─────────────────┘
```

### Tech Stack

**Frontend**
- Next.js 13+ (App Router)
- React 18 with TypeScript
- Tailwind CSS + shadcn/ui
- Monaco Editor
- Socket.IO Client
- Framer Motion

**Backend**
- Flask + Flask-SocketIO
- PyTorch + Transformers
- CodeBERT (Analysis)
- CodeT5 (Refactoring)
- Multi-agent Architecture

**AI Models**
- `microsoft/codebert-base` - Code analysis and bug detection
- `Salesforce/codet5-small` - Code generation and refactoring
- Local execution for privacy

## 🔧 Configuration

### Environment Variables

**Frontend (`.env.local`)**
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=CogniCode Agent
```

**Backend (`server/.env`)**
```env
FLASK_ENV=development
PORT=5000
MODELS_PATH=./models
USE_DEMO_MODE=true
LOG_LEVEL=INFO
```

### Model Configuration

Models are automatically downloaded to `server/models/`. For custom models:

```python
# server/agents/base_agent.py
CUSTOM_MODELS = {
    'linter': 'your-custom/codebert-model',
    'refactor': 'your-custom/codet5-model',
    'testgen': 'your-custom/test-model'
}
```

## 🚀 Deployment

### Local Development
```bash
./run-dev.sh
```

### Production with Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual services
docker build -t cognicode-frontend .
docker build -t cognicode-backend ./server
```

### Cloud Deployment

**Frontend (Vercel)**
```bash
# Deploy to Vercel
npm run build
vercel --prod
```

**Backend (Docker/Cloud)**
```bash
# Build production image
docker build -t cognicode-backend ./server

# Deploy to your preferred cloud provider
# (AWS ECS, Google Cloud Run, Azure Container Instances, etc.)
```

## 🧪 Testing

### Frontend Tests
```bash
npm test
npm run test:watch
```

### Backend Tests
```bash
cd server
source venv/bin/activate
pytest
pytest --coverage
```

### Integration Tests
```bash
# Start both services and run E2E tests
npm run test:e2e
```

## 📊 Performance

### Benchmarks

| Operation | Time | Memory |
|-----------|------|--------|
| Code Analysis | <500ms | ~200MB |
| Refactor Generation | <1s | ~300MB |
| Test Generation | <1.5s | ~250MB |
| Model Loading | ~10s | ~1GB |

### Optimization Tips

- **CPU**: Use quantized models for faster inference
- **Memory**: Enable model caching and batch processing
- **Storage**: Models require 2-5GB disk space
- **Network**: All processing is local (no API calls)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/Edmon02/cognicode-agent.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and test
npm test
cd server && pytest

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Hackathon 2025

CogniCode Agent was built for Hackathon 2025, targeting these challenges:

- **🤖 AI Innovation**: Multi-agent architecture with local AI models
- **⚡ Real-time Applications**: WebSocket-based live code analysis
- **🔒 Privacy-First Solutions**: All processing runs locally
- **🛠️ Developer Tools**: Productivity-focused development experience

### Awards Targeting
- Best Use of AI
- Best Solo Project
- Most Innovative Solution
- Best Developer Tool

## 🔗 Links

- **Demo**: [https://cognicode-agent.vercel.app](https://cognicode-agent.vercel.app)
- **GitHub**: [https://github.com/Edmon02/cognicode-agent](https://github.com/Edmon02/cognicode-agent)
- **Author**: [Edmon02](https://github.com/Edmon02)
- **Portfolio**: [https://github.com/Edmon02](https://github.com/Edmon02)

## 📞 Support

- 📧 Email: [Create an issue](https://github.com/Edmon02/cognicode-agent/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Edmon02/cognicode-agent/discussions)
- 🐛 Bug Reports: [GitHub Issues](https://github.com/Edmon02/cognicode-agent/issues)

---

<div align="center">

**Built with ❤️ for developers by developers**

[⭐ Star this repo](https://github.com/Edmon02/cognicode-agent) | [🍴 Fork it](https://github.com/Edmon02/cognicode-agent/fork) | [📝 Contribute](CONTRIBUTING.md)

</div>