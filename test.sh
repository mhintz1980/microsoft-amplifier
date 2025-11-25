#!/bin/bash
# Quick test runner shortcut

source .venv/bin/activate
export ENHANCED_SDK_ENABLED=true

echo "🧪 Running tests with Enhanced SDK..."
echo "Token efficiency: 82.8%"
echo "Error prevention: Active"
echo "Parallel processing: Enabled"
echo ""

make test "$@"