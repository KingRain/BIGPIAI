# BIGPIAI Production Deployment Script for Windows
# PowerShell script to deploy the application

Write-Host "BIGPIAI Production Deployment" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Green

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Warning: Virtual environment not detected!" -ForegroundColor Yellow
    Write-Host "Make sure to activate your venv first:" -ForegroundColor Yellow
    Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Choose deployment method:" -ForegroundColor White
Write-Host "1. Eventlet server (recommended for SocketIO)" -ForegroundColor Cyan
Write-Host "2. Gunicorn with eventlet worker (if available)" -ForegroundColor Cyan
Write-Host "3. Waitress with threading mode" -ForegroundColor Cyan
Write-Host "4. Exit" -ForegroundColor Red

$choice = Read-Host "`nEnter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "Starting with eventlet server..." -ForegroundColor Green
        $env:PRODUCTION = "true"
        $env:USE_WAITRESS = "false"
        python run.py
    }
    "2" {
        Write-Host "Starting with gunicorn..." -ForegroundColor Green
        try {
            gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:80 --timeout 120 --keep-alive 2 run:app
        }
        catch {
            Write-Host "Error: Gunicorn not found or not compatible with Windows" -ForegroundColor Red
            Write-Host "Consider using option 1 or 3 instead" -ForegroundColor Yellow
        }
    }
    "3" {
        Write-Host "Starting with waitress..." -ForegroundColor Green
        $env:PRODUCTION = "true"
        $env:USE_WAITRESS = "true"
        waitress-serve --listen=0.0.0.0:80 --threads=10 --connection-limit=1000 run:app
    }
    "4" {
        Write-Host "Goodbye!" -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice. Please try again." -ForegroundColor Red
    }
}
