# PowerShell script to run Theia with full ADK functionality
# This script handles the complete startup process

Write-Host "🚀 Starting Theia with Full ADK Functionality" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check/Start Backend
Write-Host "📡 Step 1: Checking Backend..." -ForegroundColor Yellow
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is already running!" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host "⚠️  Backend is not running." -ForegroundColor Yellow
    Write-Host "   Starting backend in a new window..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; if (Test-Path '.venv\Scripts\python.exe') { . '.venv\Scripts\Activate.ps1'; Write-Host 'Starting FastAPI backend...' -ForegroundColor Green; uvicorn main:app --reload --host 0.0.0.0 --port 8000 } else { Write-Host 'Virtual environment not found. Please run setup.ps1 first.' -ForegroundColor Red; pause }" -WindowStyle Normal
    Write-Host "   Waiting 5 seconds for backend to start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 5
}

Write-Host ""

# Step 2: Build from Theia root (proper monorepo build)
Write-Host "📦 Step 2: Building Theia packages (this may take a few minutes)..." -ForegroundColor Yellow
Set-Location "theia-fresh"

# Check if node_modules exists at root
if (-not (Test-Path "node_modules")) {
    Write-Host "   Installing root dependencies..." -ForegroundColor Cyan
    npm.cmd install --no-audit --no-fund
}

# Compile all packages (including adk-ide)
Write-Host "   Compiling TypeScript packages..." -ForegroundColor Cyan
npm.cmd run compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Compilation failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "✅ Packages compiled successfully!" -ForegroundColor Green
Write-Host ""

# Step 3: Build browser application
Write-Host "🏗️  Step 3: Building Browser Application..." -ForegroundColor Yellow
npm.cmd run build:browser

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Browser build failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "✅ Browser application built successfully!" -ForegroundColor Green
Write-Host ""

# Step 4: Start Theia
Write-Host "🎯 Step 4: Starting Theia..." -ForegroundColor Yellow
Set-Location "examples\browser"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✨ Theia is starting and will be available at:" -ForegroundColor Green
Write-Host "   http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Available ADK Features:" -ForegroundColor Yellow
Write-Host "   • HIA Chat: Ctrl+Shift+A or View → ADK IDE → HIA Chat" -ForegroundColor White
Write-Host "   • Agent Status: Ctrl+Shift+S or View → ADK IDE → Agent Status" -ForegroundColor White
Write-Host "   • Code Execution: Ctrl+Shift+E or View → ADK IDE → Code Execution" -ForegroundColor White
Write-Host "   • Cloud Status: View → ADK IDE → Cloud Status" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

npm.cmd run start

