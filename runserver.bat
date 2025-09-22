@echo off
REM WN-PrinterHub Server Startup Script for Windows
REM Usage: runserver.bat [dev|prod]

setlocal enabledelayedexpansion

echo 🖨️  WN-PrinterHub Startup Script
echo ==================================

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: uv is not installed!
    echo    Install from: https://github.com/astral-sh/uv
    echo    Or run: pip install uv
    pause
    exit /b 1
)

REM Get uv version
for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
echo ✅ uv is installed: %UV_VERSION%

REM Install dependencies
echo 📦 Installing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to install dependencies!
    pause
    exit /b 1
)

REM Get mode parameter (default: dev)
set MODE=%1
if "%MODE%"=="" set MODE=dev

if /i "%MODE%"=="prod" (
    echo 🚀 Starting WN-PrinterHub in PRODUCTION mode...
    echo    Access the API at: http://localhost:8088
    echo    API Documentation: http://localhost:8088/docs
    echo    Press Ctrl+C to stop
    echo.
    
    REM Production mode - no reload, optimized settings
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --workers 1
    
) else if /i "%MODE%"=="dev" (
    echo 🔧 Starting WN-PrinterHub in DEVELOPMENT mode...
    echo    Access the API at: http://localhost:8088
    echo    API Documentation: http://localhost:8088/docs
    echo    Hot reload enabled - files will be watched for changes
    echo    Press Ctrl+C to stop
    echo.
    
    REM Development mode - with reload and debug features
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
    
) else (
    echo ❌ Error: Invalid mode '%MODE%'
    echo    Usage: %0 [dev^|prod]
    echo    Examples:
    echo      %0          # Development mode (default^)
    echo      %0 dev      # Development mode with hot reload
    echo      %0 prod     # Production mode
    pause
    exit /b 1
)

REM If we get here, the server has stopped
echo.
echo 🛑 WN-PrinterHub server stopped.
pause