# Docker Setup Script for ADK IDE
# This script helps set up and run the ADK IDE using Docker

Write-Host "=== ADK IDE Docker Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
$dockerInstalled = $false

try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
        $dockerInstalled = $true
    }
} catch {
    Write-Host "✗ Docker not found" -ForegroundColor Red
}

if (-not $dockerInstalled) {
    Write-Host ""
    Write-Host "Docker is not installed. Please install Docker Desktop first:" -ForegroundColor Red
    Write-Host "1. Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "2. Run the installer" -ForegroundColor Yellow
    Write-Host "3. Restart your computer" -ForegroundColor Yellow
    Write-Host "4. Launch Docker Desktop" -ForegroundColor Yellow
    Write-Host "5. Wait for Docker to start (whale icon in system tray)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Cyan
    Write-Host ""
    
    # Offer to open download page
    $response = Read-Host "Would you like to open the Docker download page? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Start-Process "https://www.docker.com/products/docker-desktop/"
    }
    
    exit 1
}

# Check if docker-compose is available
Write-Host "Checking docker-compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ docker-compose found: $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "⚠ docker-compose not found, using 'docker compose' (newer syntax)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ docker-compose not found, will use 'docker compose' (newer syntax)" -ForegroundColor Yellow
}

# Check if .env file exists
Write-Host ""
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Write-Host "  Creating template .env file..." -ForegroundColor Yellow
    
    $envContent = @"
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_API_KEY=your-api-key

# Environment
ENVIRONMENT=development

# Project Base Path
PROJECT_BASE_PATH=/app
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "  ✓ Created .env template - please update with your credentials" -ForegroundColor Yellow
}

# Check if Docker is running
Write-Host ""
Write-Host "Checking if Docker is running..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker is not running" -ForegroundColor Red
        Write-Host "  Please start Docker Desktop and wait for it to be ready." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ Cannot connect to Docker daemon" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and wait for it to be ready." -ForegroundColor Yellow
    exit 1
}

# Build and start containers
Write-Host ""
Write-Host "Building and starting containers..." -ForegroundColor Cyan
Write-Host ""

# Try docker-compose first, fall back to docker compose
$composeCommand = "docker-compose"
try {
    docker-compose --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $composeCommand = "docker compose"
    }
} catch {
    $composeCommand = "docker compose"
}

Write-Host "Using command: $composeCommand" -ForegroundColor Gray
Write-Host ""

# Build and start
& $composeCommand up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Setup Complete! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view logs: $composeCommand logs -f" -ForegroundColor Yellow
    Write-Host "To stop: $composeCommand down" -ForegroundColor Yellow
    Write-Host ""
    
    # Wait a moment for the container to start
    Start-Sleep -Seconds 3
    
    # Check if the health endpoint is responding
    Write-Host "Checking backend health..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend is healthy!" -ForegroundColor Green
            $response.Content | ConvertFrom-Json | Format-List
        }
    } catch {
        Write-Host "⚠ Backend may still be starting up. Please wait a moment and check: http://localhost:8000/health" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "✗ Failed to start containers" -ForegroundColor Red
    Write-Host "  Check logs with: $composeCommand logs" -ForegroundColor Yellow
    exit 1
}


