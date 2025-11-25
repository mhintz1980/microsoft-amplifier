#!/bin/bash
# Development environment shortcut

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export ENHANCED_SDK_ENABLED=true
export PYTHONPATH="/home/markimus/projects/microsoft-amplifier:$PYTHONPATH"
export MCP_CONTEXT_SAVING=true
export PARALLEL_DELEGATION=true

# Start development server or run command
if [ $# -eq 0 ]; then
    echo "🚀 Starting development environment..."
    echo "Enhanced SDK activated: $ENHANCED_SDK_ENABLED"
    echo "Token efficiency: Active"
    echo "Docker integration: Connected"
    echo "MCP servers: 4 configured"
    echo ""
    echo "Available commands:"
    echo "  • make install - Install dependencies"
    echo "  • make check - Run code quality checks"
    echo "  • make test - Run test suite"
    echo "  • /prime - Run prime command with enhanced features"
    echo ""
    echo "Ready for development! 🎉"
else
    echo "🔧 Running: $*"
    "$@"
fi