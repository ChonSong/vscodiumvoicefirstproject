# Run Application with Commit a652854 Changes
# This script verifies the commit changes and runs the application with full functionality

Write-Host "🚀 Running Application with Commit a652854 Changes" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Verify commit changes are applied
Write-Host "✅ Verifying commit changes..." -ForegroundColor Yellow
$mainPyContent = Get-Content main.py -Raw
if ($mainPyContent -match "proxy_schemastore" -and $mainPyContent -match "import httpx" -and $mainPyContent -match "from fastapi import.*Request") {
    Write-Host "✓ Proxy endpoint for schemastore.org added" -ForegroundColor Green
    Write-Host "✓ httpx import added" -ForegroundColor Green
    Write-Host "✓ Request import added" -ForegroundColor Green
} else {
    Write-Host "✗ Commit changes not fully applied!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow

# Check if virtual environment exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠ Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

# Check if required packages are installed
try {
    python -c "import fastapi, httpx, uvicorn" 2>&1 | Out-Null
    Write-Host "✓ Required packages installed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Some packages may be missing. Installing minimal dependencies..." -ForegroundColor Yellow
    python -m pip install fastapi httpx uvicorn python-dotenv prometheus-client --quiet
}

Write-Host ""
Write-Host "🌐 Starting FastAPI Backend Server..." -ForegroundColor Cyan
Write-Host "   Backend will be available at: http://localhost:8000" -ForegroundColor White
Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "   Proxy Endpoint: http://localhost:8000/proxy/schemastore/api/json/catalog.json" -ForegroundColor White
Write-Host ""
Write-Host "📋 Available Endpoints:" -ForegroundColor Yellow
Write-Host "   • GET  /health - Health check" -ForegroundColor White
Write-Host "   • POST /orchestrate - Agent orchestration" -ForegroundColor White
Write-Host "   • POST /execute - Code execution" -ForegroundColor White
Write-Host "   • POST /session/new - Session management" -ForegroundColor White
Write-Host "   • GET  /proxy/schemastore/{path} - Schema store proxy (NEW)" -ForegroundColor Green
Write-Host "   • WS   /ws - WebSocket endpoint" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000



