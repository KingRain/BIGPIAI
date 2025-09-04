@echo off
REM BIGPIAI Production Server - Administrator Mode
REM This script runs the server on port 80 (requires admin privileges)
REM Right-click and "Run as administrator"

echo ========================================
echo BIGPIAI Production Server (Port 80)
echo Requires Administrator Privileges
echo ========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Running with administrator privileges
) else (
    echo ❌ Administrator privileges required for port 80
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

REM Change to project directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Set environment for port 80
set PORT=80
set HOST=0.0.0.0

echo 🚀 Starting production server on port 80...
echo 🌐 Will be accessible at: http://4.147.177.22
echo.

REM Run the production server
python run_production.py

pause
