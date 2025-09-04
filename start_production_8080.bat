@echo off
REM BIGPIAI Production Server - Port 8080 (No admin required)
REM Alternative to port 80 that doesn't require administrator privileges

echo ========================================
echo BIGPIAI Production Server (Port 8080)
echo No Administrator Privileges Required
echo ========================================

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

REM Set environment for port 8080
set PORT=8080
set HOST=0.0.0.0

echo 🚀 Starting production server on port 8080...
echo 🌐 Will be accessible at: http://4.147.177.22:8080
echo.

REM Run the production server
python run_production.py

pause
