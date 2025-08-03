#!/bin/bash

# Background Remover Flask Application
# Startup script for Unix/Linux systems

echo "🚀 Starting Background Remover Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads outputs

# Start the Flask application
echo "🌐 Starting Flask application..."
echo "✅ Application is running at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python app.py 