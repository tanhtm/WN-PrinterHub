#!/bin/bash

# WN-PrinterHub Server Startup Script
# Usage: ./runserver.sh [dev|prod]

set -e  # Exit on error

echo "🖨️  WN-PrinterHub Startup Script"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed!"
    echo "   Install from: https://github.com/astral-sh/uv"
    exit 1
fi

echo "✅ uv is installed: $(uv --version)"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Get mode parameter (default: dev)
MODE=${1:-dev}

if [ "$MODE" = "prod" ]; then
    echo "🚀 Starting WN-PrinterHub in PRODUCTION mode..."
    echo "   Access the API at: http://localhost:8088"
    echo "   API Documentation: http://localhost:8088/docs"
    echo "   Press Ctrl+C to stop"
    echo ""
    
    # Production mode - no reload, optimized settings
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --workers 1
    
elif [ "$MODE" = "dev" ]; then
    echo "🔧 Starting WN-PrinterHub in DEVELOPMENT mode..."
    echo "   Access the API at: http://localhost:8088" 
    echo "   API Documentation: http://localhost:8088/docs"
    echo "   Hot reload enabled - files will be watched for changes"
    echo "   Press Ctrl+C to stop"
    echo ""
    
    # Development mode - with reload and debug features
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
    
else
    echo "❌ Error: Invalid mode '$MODE'"
    echo "   Usage: $0 [dev|prod]"
    echo "   Examples:"
    echo "     $0          # Development mode (default)"
    echo "     $0 dev      # Development mode with hot reload"
    echo "     $0 prod     # Production mode"
    exit 1
fi 