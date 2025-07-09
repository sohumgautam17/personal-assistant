#!/bin/bash

# Start Server Script for Personal Assistant

echo "🚀 Starting Personal Assistant Server..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if requirements are installed
echo "📋 Checking dependencies..."
python3 -c "import fastapi, httpx" 2>/dev/null || {
    echo "⚠️  Installing dependencies..."
    pip install -r requirements.txt
}

# Check environment variables
echo "🔍 Checking environment..."
python3 debug_env.py

echo "🌟 Starting FastAPI server on port 8000..."
echo "🔧 Status dashboard at: http://localhost:8000/"
echo "🤖 Hypermode API ready for AI responses"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py 