# ADK IDE Setup Script for Windows
# This script automates the environment setup once Python and Node.js are installed

Write-Host "=== ADK IDE Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    Write-Host "  See SETUP_PREREQUISITES.md for installation instructions" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
    
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm found: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16+ first." -ForegroundColor Red
    Write-Host "  See SETUP_PREREQUISITES.md for installation instructions" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Setting up Python Virtual Environment ===" -ForegroundColor Cyan

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Setting up Frontend (React) ===" -ForegroundColor Cyan

# Check if frontend directory exists
if (Test-Path "frontend") {
    Push-Location frontend
    
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install Node.js dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Pop-Location
} else {
    Write-Host "⚠ Frontend directory not found, skipping frontend setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Environment Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Verify .env file exists and has required variables" -ForegroundColor White
Write-Host "2. Activate virtual environment: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. Run tests: pytest tests/ -v" -ForegroundColor White
Write-Host "4. Start backend: uvicorn main:app --reload" -ForegroundColor White
Write-Host "5. Start frontend: cd frontend && npm start" -ForegroundColor White
Write-Host ""



