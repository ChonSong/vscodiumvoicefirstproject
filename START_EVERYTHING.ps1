# Start Everything - Full Functionality
# Run this script to start both backend and frontend

Write-Host "🚀 Starting Full Functionality Mode" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

$rootDir = Get-Location

# Check if backend is running
Write-Host "📡 Checking Backend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Backend is already running" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Backend is not running" -ForegroundColor Yellow
    Write-Host "   Starting backend in a new window..." -ForegroundColor Yellow
    
    $backendScript = @"
cd '$rootDir'
Write-Host '🚀 Starting FastAPI Backend Server...' -ForegroundColor Green
Write-Host 'Backend URL: http://localhost:8000' -ForegroundColor Cyan
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host ''
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal
    Write-Host "   ✅ Backend server starting..." -ForegroundColor Green
    Write-Host "   Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "🌐 Starting Theia Frontend..." -ForegroundColor Cyan
Write-Host ""

$theiaDir = Join-Path $rootDir "theia-fresh\examples\browser"
if (-not (Test-Path $theiaDir)) {
    Write-Host "   ❌ Theia directory not found: $theiaDir" -ForegroundColor Red
    exit 1
}

Set-Location $theiaDir

# Check if dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "   ⚠️  Theia dependencies not installed" -ForegroundColor Yellow
    Write-Host "   Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
    Write-Host "   Please wait..." -ForegroundColor Gray
    npm.cmd install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ Theia dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✨ Starting Theia IDE..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Theia will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 ADK Features:" -ForegroundColor Yellow
Write-Host "   • HIA Chat: View → ADK IDE → HIA Chat (Ctrl+Shift+A)" -ForegroundColor White
Write-Host "   • Agent Status: View → ADK IDE → Agent Status (Ctrl+Shift+S)" -ForegroundColor White
Write-Host "   • Code Execution: View → ADK IDE → Code Execution (Ctrl+Shift+E)" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔗 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Theia in watch mode..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop Theia" -ForegroundColor Yellow
Write-Host ""

# Start Theia
npm.cmd run start:watch




