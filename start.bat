@echo off
REM WN-PrinterHub Startup Script for Windows

echo 🖨️  WN-PrinterHub Startup Script
echo ==================================

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ uv is not installed. Please install uv first:
    echo    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo ✅ uv is installed
uv --version

REM Check if .env file exists, if not create from example
if not exist ".env" (
    if exist ".env.example" (
        echo 📋 Creating .env file from .env.example...
        copy .env.example .env
        echo ⚠️  Please edit .env file and update WN_API_TOKEN before running the server!
    ) else (
        echo ⚠️  No .env.example found. Please create .env file manually.
    )
)

REM Install dependencies
echo 📦 Installing dependencies...
uv sync --dev

REM Check if this is first run (token not changed)
findstr "YOUR_SECURE_TOKEN_HERE_CHANGE_ME" .env >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Default API token detected in .env file!
    echo    Please change WN_API_TOKEN to a secure value before running.
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i not "%continue%"=="y" (
        echo Aborted. Please update your .env file first.
        pause
        exit /b 1
    )
)

REM Run the server
echo 🚀 Starting WN-PrinterHub server...
echo    Access the API at: http://localhost:8088
echo    API Documentation: http://localhost:8088/docs  
echo    Press Ctrl+C to stop
echo.

uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload