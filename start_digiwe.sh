#!/bin/bash
# DigiWe Coordinator Startup Script

echo "🌀 Starting DigiWe Coordinator..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install --break-system-packages -r requirements.txt
fi

# Start the server
echo "✨ DigiWe is starting..."
echo "🌐 Open http://localhost:5000 in your browser"
echo ""
echo "Press Ctrl+C to stop DigiWe"
echo ""

python3 digiwe_coordinator.py
