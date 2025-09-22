# WN-PrinterHub Server Startup Script for Windows PowerShell
# Usage: .\runserver.ps1 [dev|prod]

param(
    [string]$Mode = "dev"
)

Write-Host "🖨️  WN-PrinterHub Startup Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check if uv is installed
try {
    $uvVersion = uv --version 2>$null
    Write-Host "✅ uv is installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: uv is not installed!" -ForegroundColor Red
    Write-Host "   Install from: https://github.com/astral-sh/uv" -ForegroundColor Yellow
    Write-Host "   Or run: pip install uv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
try {
    uv sync
    if ($LASTEXITCODE -ne 0) {
        throw "uv sync failed"
    }
} catch {
    Write-Host "❌ Error: Failed to install dependencies!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Normalize mode parameter
$Mode = $Mode.ToLower()

switch ($Mode) {
    "prod" {
        Write-Host "🚀 Starting WN-PrinterHub in PRODUCTION mode..." -ForegroundColor Green
        Write-Host "   Access the API at: http://localhost:8088" -ForegroundColor White
        Write-Host "   API Documentation: http://localhost:8088/docs" -ForegroundColor White
        Write-Host "   Press Ctrl+C to stop" -ForegroundColor White
        Write-Host ""
        
        # Production mode - no reload, optimized settings
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --workers 1
    }
    "dev" {
        Write-Host "🔧 Starting WN-PrinterHub in DEVELOPMENT mode..." -ForegroundColor Blue
        Write-Host "   Access the API at: http://localhost:8088" -ForegroundColor White
        Write-Host "   API Documentation: http://localhost:8088/docs" -ForegroundColor White
        Write-Host "   Hot reload enabled - files will be watched for changes" -ForegroundColor White
        Write-Host "   Press Ctrl+C to stop" -ForegroundColor White
        Write-Host ""
        
        # Development mode - with reload and debug features
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
    }
    default {
        Write-Host "❌ Error: Invalid mode '$Mode'" -ForegroundColor Red
        Write-Host "   Usage: .\runserver.ps1 [dev|prod]" -ForegroundColor Yellow
        Write-Host "   Examples:" -ForegroundColor Yellow
        Write-Host "     .\runserver.ps1          # Development mode (default)" -ForegroundColor White
        Write-Host "     .\runserver.ps1 dev      # Development mode with hot reload" -ForegroundColor White
        Write-Host "     .\runserver.ps1 prod     # Production mode" -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# If we get here, the server has stopped
Write-Host ""
Write-Host "🛑 WN-PrinterHub server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"