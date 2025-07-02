# 📦 Installation Guide

> Complete installation instructions for CogniCode Agent

## 🎯 Prerequisites

Before installing CogniCode Agent, ensure you have the following:

### System Requirements
- **Operating System**: macOS, Linux, or Windows 10+
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 5GB+ free disk space for AI models
- **Network**: Internet connection for initial setup

### Software Dependencies
- **Node.js**: Version 16.0 or higher
- **npm**: Version 8.0 or higher (comes with Node.js)
- **Python**: Version 3.8 or higher
- **pip**: Python package installer
- **Git**: For cloning the repository

### Verify Prerequisites

Check your installations:

```bash
# Check Node.js and npm
node --version    # Should be 16.0+
npm --version     # Should be 8.0+

# Check Python and pip
python3 --version # Should be 3.8+
pip --version     # Should be available

# Check Git
git --version     # Should be available
```

## 🚀 Quick Installation (Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/Edmon02/cognicode-agent.git
cd cognicode-agent
```

### 2. Automated Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh
```

The setup script will:
- Install frontend dependencies
- Create Python virtual environment
- Install backend dependencies
- Download AI models (optional)
- Configure environment variables

### 3. Start the Application

```bash
# Start both frontend and backend
./run-dev.sh
```

Open your browser to: `http://localhost:3000`

## 🔧 Manual Installation

If you prefer manual setup or the automated script fails:

### 1. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Verify installation
npm ls
```

### 2. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Environment Configuration

Create environment files:

**Frontend Environment (`.env.local`)**
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=CogniCode Agent
NEXT_PUBLIC_ENV=development
```

**Backend Environment (`server/.env`)**
```env
FLASK_ENV=development
PORT=5000
MODELS_PATH=./models
USE_DEMO_MODE=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### 4. Download AI Models (Optional)

```bash
cd server
python scripts/download_models.py
```

This downloads:
- CodeBERT model (~500MB)
- CodeT5 model (~300MB)
- Additional language models

### 5. Start Services Manually

**Terminal 1 - Backend:**
```bash
cd server
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## 🐳 Docker Installation

For containerized deployment:

### 1. Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/Edmon02/cognicode-agent.git
cd cognicode-agent

# Build and start services
docker-compose up --build
```

Services will be available at:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

### 2. Manual Docker Build

```bash
# Build frontend image
docker build -t cognicode-frontend .

# Build backend image
docker build -t cognicode-backend ./server

# Run containers
docker run -p 3000:3000 cognicode-frontend
docker run -p 5000:5000 cognicode-backend
```

## ✅ Verify Installation

### 1. Check Service Status

Visit `http://localhost:3000` and verify:
- ✅ Frontend loads successfully
- ✅ Monaco editor is functional
- ✅ Backend connection indicator shows "Connected"

### 2. Test Core Features

```javascript
// Paste this code in the editor and click "Analyze"
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
console.log(fibonacci(10));
```

Expected results:
- ✅ Analysis completes without errors
- ✅ Issues are detected and displayed
- ✅ Refactor suggestions are generated
- ✅ Unit tests are created

### 3. Check Logs

**Frontend logs:**
```bash
# Check Next.js development logs
npm run dev
```

**Backend logs:**
```bash
# Check Flask application logs
cd server
source venv/bin/activate
python app.py
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill processes using ports 3000 or 5000
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:5000 | xargs kill -9
```

#### 2. Python Virtual Environment Issues
```bash
# Remove and recreate venv
rm -rf server/venv
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Node Modules Issues
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 4. AI Models Not Loading
```bash
# Re-download models
cd server
rm -rf models/
python scripts/download_models.py
```

#### 5. Permission Issues (macOS/Linux)
```bash
# Fix script permissions
chmod +x setup.sh run-dev.sh

# Fix Python permissions
sudo chown -R $USER:$USER server/venv
```

### Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Review prerequisites** and verify all dependencies
3. **Consult the FAQ** in [FAQ.md](faq.md)
4. **Search existing issues** on [GitHub Issues](https://github.com/Edmon02/cognicode-agent/issues)
5. **Create a new issue** with detailed error information

## 🔄 Update Installation

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
npm install
cd server && pip install -r requirements.txt

# Restart services
./run-dev.sh
```

## 🎉 Next Steps

Once installed successfully:

1. **Read the [Basic Usage Guide](basic-usage.md)** to learn core features
2. **Explore [Features Overview](features.md)** for detailed capabilities
3. **Check [API Documentation](../api/)** for integration options
4. **Join [GitHub Discussions](https://github.com/Edmon02/cognicode-agent/discussions)** for community support

---

<div align="center">

**🎉 Installation Complete!**

[📖 Basic Usage Guide](basic-usage.md) | [🚀 Features Overview](features.md) | [🏠 Back to Docs](../README.md)

</div>
