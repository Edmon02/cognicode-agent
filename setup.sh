#!/bin/bash
# CogniCode Agent Setup Script

set -e

echo "🧠 Setting up CogniCode Agent..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check Node.js version
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 16 ]; then
    print_error "Node.js version 16+ is required. Current version: $(node --version)"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    print_error "Python 3.8+ is required. Current version: $(python3 --version)"
    exit 1
fi

print_success "System requirements check passed"

# Setup frontend
print_status "Setting up frontend dependencies..."
if [ -f "package.json" ]; then
    npm install
    print_success "Frontend dependencies installed"
else
    print_error "package.json not found. Are you in the correct directory?"
    exit 1
fi

# Setup backend
print_status "Setting up backend dependencies..."
if [ -d "server" ]; then
    cd server
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Backend dependencies installed"
    else
        print_error "requirements.txt not found in server directory"
        exit 1
    fi
    
    cd ..
else
    print_error "Server directory not found"
    exit 1
fi

# Download AI models (optional for demo)
print_status "Setting up AI models..."
print_warning "For full functionality, AI models need to be downloaded (2-5GB)"
read -p "Download AI models now? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd server
    source venv/bin/activate
    python scripts/download_models.py
    cd ..
    print_success "AI models setup complete"
else
    print_warning "Skipping AI model download. Demo mode will be used."
    print_status "You can download models later by running: cd server && python scripts/download_models.py"
fi

# Create environment files
print_status "Creating environment configuration..."

# Frontend environment
cat > .env.local << EOF
# CogniCode Agent Frontend Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=CogniCode Agent
NEXT_PUBLIC_APP_VERSION=1.0.0
EOF

# Backend environment
cat > server/.env << EOF
# CogniCode Agent Backend Configuration
FLASK_ENV=development
FLASK_APP=app.py
PORT=5000
PYTHONPATH=.

# AI Model Configuration
MODELS_PATH=./models
USE_DEMO_MODE=true

# Logging
LOG_LEVEL=INFO
EOF

print_success "Environment files created"

# Create run scripts
print_status "Creating run scripts..."

# Frontend run script
cat > run-frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting CogniCode Agent Frontend..."
npm run dev
EOF

# Backend run script
cat > run-backend.sh << 'EOF'
#!/bin/bash
echo "🤖 Starting CogniCode Agent Backend..."
cd server
source venv/bin/activate
python app.py
EOF

# Full stack run script
cat > run-dev.sh << 'EOF'
#!/bin/bash
echo "🧠 Starting CogniCode Agent (Full Stack)..."

# Function to kill background processes on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT

# Start backend
echo "Starting backend..."
cd server
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait for processes
wait
EOF

# Make scripts executable
chmod +x run-frontend.sh run-backend.sh run-dev.sh

print_success "Run scripts created"

# Setup complete
print_success "🎉 CogniCode Agent setup complete!"
echo
print_status "To start the application:"
echo "  Frontend only: ./run-frontend.sh"
echo "  Backend only:  ./run-backend.sh"
echo "  Full stack:    ./run-dev.sh"
echo
print_status "URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:5000"
echo
print_status "For production deployment, see README.md"
print_warning "Remember to create your GitHub repository at: https://github.com/Edmon02/cognicode-agent"