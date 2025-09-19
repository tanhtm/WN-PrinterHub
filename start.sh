#!/bin/bash
# WN-PrinterHub Startup Script for Unix/Linux/macOS

set -e

echo "🖨️  WN-PrinterHub Startup Script"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed: $(uv --version)"

# Check if .env file exists, if not create from example
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env file and update WN_API_TOKEN before running the server!"
        echo "   Current token is: $(grep WN_API_TOKEN .env | cut -d'=' -f2)"
    else
        echo "⚠️  No .env.example found. Please create .env file manually."
    fi
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Check if this is first run (token not changed)
if grep -q "YOUR_SECURE_TOKEN_HERE_CHANGE_ME" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: Default API token detected in .env file!"
    echo "   Please change WN_API_TOKEN to a secure value before running."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Please update your .env file first."
        exit 1
    fi
fi

# Run the server
echo "🚀 Starting WN-PrinterHub server..."
echo "   Access the API at: http://localhost:8088"
echo "   API Documentation: http://localhost:8088/docs"
echo "   Press Ctrl+C to stop"
echo ""

uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload