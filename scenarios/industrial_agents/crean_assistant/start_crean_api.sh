#!/bin/bash

# CreaTech API Server Startup Script
# This script starts the CreaTech API server for bolt.diy integration

echo "🚀 Starting CreaTech API Server..."

# Set environment variables
export AMPLIFIER_ROOT="/home/markimus/projects/microsoft-amplifier"
export BOLT_PROJECT_ROOT="/home/markimus/projects/bolt.diy"
export CREANTECH_API_KEY="crean-api-key-local"
export CREANTECH_BASE_URL="http://localhost:8001"

# Change to the CreaTech directory
cd "$(dirname "$0")"

# Check if required dependencies are available
echo "📦 Checking dependencies..."

# Check Python dependencies
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Installing missing dependencies..."
    pip install fastapi uvicorn pydantic
fi

# Check if CreaTech components exist
if [ ! -f "main_assistant.py" ]; then
    echo "❌ Error: CreaTech components not found. Please ensure you're in the correct directory."
    exit 1
fi

echo "✅ Dependencies verified"

# Start the API server
echo "🌐 Starting CreaTech API server on http://localhost:8001"
echo "📊 Health check: http://localhost:8001/health"
echo "🤖 Models endpoint: http://localhost:8001/models"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 api_server.py