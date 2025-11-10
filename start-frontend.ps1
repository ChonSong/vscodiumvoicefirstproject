# Start ADK IDE Frontend (React)
# This script starts the React development server

Write-Host "=== Starting ADK IDE Frontend ===" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16+ first." -ForegroundColor Red
    Write-Host "  See SETUP_PREREQUISITES.md for installation instructions" -ForegroundColor Yellow
    exit 1
}

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "✗ Frontend directory not found!" -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Push-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠ node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
}

# Start the React development server
Write-Host ""
Write-Host "Starting React development server on http://localhost:3000" -ForegroundColor Green
Write-Host "The frontend will automatically reload on code changes" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm start

Pop-Location





