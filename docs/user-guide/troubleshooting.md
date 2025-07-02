# 🔧 Troubleshooting Guide

> Common issues and their solutions for CogniCode Agent

## 🚨 Recently Fixed Issues

### 1. Socket Connection Errors
**Symptoms**: 
- `❌ Socket error: Connection failed`
- `❌ Socket error: { message: "Connection failed" }`
- Connection issues on initial startup

**Solution**: 
- Enhanced connection handling with proper delays and retry logic
- Better error handling and initialization sequence
- Use the provided startup script for reliable initialization

### 2. React Rendering Error
**Symptoms**:
- `Error: Objects are not valid as a React child (found: object with keys {progress, message})`
- Analysis fails on first attempt

**Solution**:
- Fixed progress object handling in the frontend
- Added proper data extraction for progress updates
- Enhanced component safety with fallback values

### 3. Server WSGI Error
**Symptoms**:
- `AssertionError: write() before start_response`
- Backend crashes during analysis

**Solution**:
- Improved Flask-SocketIO error handling
- Enhanced session management
- Better exception handling and logging

## 🚀 Quick Start Solutions

### Option 1: Automated Startup (Recommended)
```bash
./start-dev.sh
```

### Option 2: Manual Startup
```bash
# Terminal 1 - Start Backend
cd server
python app.py

# Terminal 2 - Start Frontend (wait for backend to be ready)
npm run dev
```

## 🔍 Common Troubleshooting Steps

### Connection Issues
1. **Wait for Backend**: Allow 5-10 seconds after starting the backend before opening the frontend
2. **Health Check**: Verify backend is running at `http://localhost:8000/health`
3. **Port Conflicts**: Ensure ports 3000 and 8000 are available

### Analysis Issues
1. **First Click Problems**: Refresh the page and try again
2. **Console Errors**: Check browser console for JavaScript errors
3. **Backend Logs**: Review server logs for initialization issues

### Dependency Issues
```bash
# Python Backend Dependencies
cd server
pip install -r requirements.txt

# Frontend Dependencies  
npm install
```

## 🛠️ Advanced Troubleshooting

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-02T...",
  "version": "2.0.0",
  "agents": {
    "linter_agents": 1,
    "refactor_agents": 1,
    "testgen_agents": 1,
    "initialized": true
  }
}
```

### Socket Connection Testing
Open browser console and check for:
- `✅ Connected to CogniCode AI backend`
- Socket ID confirmation
- No connection error messages

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection failed` | Backend not ready | Wait longer, check backend status |
| `Objects are not valid as React child` | Old version | Code has been fixed |
| `write() before start_response` | WSGI error | Code has been fixed |
| `Port already in use` | Port conflict | Kill process or use different port |

## 📞 Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Review both frontend (browser console) and backend (terminal) logs
2. **GitHub Issues**: Search for similar issues in the repository
3. **Documentation**: Review the [User Guide](./basic-usage.md) and [FAQ](./faq.md)

## 🔄 Recent Improvements

- ✅ Enhanced socket connection reliability
- ✅ Better error handling and user feedback  
- ✅ Improved component safety and data handling
- ✅ Automated startup script for proper initialization
- ✅ Enhanced backend health monitoring
