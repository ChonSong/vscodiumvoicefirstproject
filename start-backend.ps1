# Start ADK IDE Backend Server
# This script starts the FastAPI backend server

Write-Host "=== Starting ADK IDE Backend ===" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Run setup.ps1 first to set up the environment" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "  Some features may not work without proper configuration" -ForegroundColor Yellow
}

# Start the server
Write-Host ""
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health check: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000










