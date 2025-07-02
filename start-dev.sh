#!/bin/bash

# CogniCode Agent - Development Startup Script
# This script ensures proper initialization order to prevent connection issues

echo "🚀 Starting CogniCode Agent Development Environment"

# Check if Python backend dependencies are installed
echo "📦 Checking Python dependencies..."
cd server

if [ ! -d "__pycache__" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the backend server
echo "🔧 Starting Python backend server..."
python app.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is responding
echo "🔍 Checking backend health..."
timeout 10 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 1; done' || {
    echo "❌ Backend failed to start properly"
    kill $BACKEND_PID 2>/dev/null
    exit 1
}

echo "✅ Backend is ready!"

# Go back to frontend directory
cd ..

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start the frontend development server
echo "🎨 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

echo "🎉 CogniCode Agent is starting up!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap interrupt signal
trap cleanup INT

# Wait for either process to exit
wait
