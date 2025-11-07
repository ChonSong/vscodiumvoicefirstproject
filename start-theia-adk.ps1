# PowerShell script to start Theia with ADK functionality
# Run this script to start all components

Write-Host "🚀 Starting Theia with ADK Integration..." -ForegroundColor Green
Write-Host ""

# Check if backend is running
Write-Host "📡 Checking backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is already running!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Backend is not running. Starting backend..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please start the backend in a separate terminal:" -ForegroundColor Cyan
    Write-Host "  cd d:\vscodiumvoicefirstproject" -ForegroundColor White
    Write-Host "  uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host ""
}

# Build ADK IDE Extension
Write-Host "📦 Building ADK IDE Extension..." -ForegroundColor Yellow
Set-Location "theia-fresh\packages\adk-ide"
if (Test-Path "node_modules") {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
} else {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm.cmd install
}

Write-Host "Building extension..." -ForegroundColor Cyan
npm.cmd run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Extension built successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Extension build failed!" -ForegroundColor Red
    Set-Location "..\..\.."
    exit 1
}

# Build Theia Browser Application
Write-Host ""
Write-Host "🏗️  Building Theia Browser Application..." -ForegroundColor Yellow
Set-Location "..\..\.."

# Check if we need to compile
Write-Host "Compiling TypeScript packages..." -ForegroundColor Cyan
npm.cmd run compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Compile had issues, but continuing..." -ForegroundColor Yellow
}

Write-Host "Building browser application..." -ForegroundColor Cyan
npm.cmd run build:browser

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Theia browser application built successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Browser build failed!" -ForegroundColor Red
    exit 1
}

# Start Theia
Write-Host ""
Write-Host "🎯 Starting Theia..." -ForegroundColor Yellow
Set-Location "examples\browser"

Write-Host ""
Write-Host "✨ Theia will be available at: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Available ADK Features:" -ForegroundColor Cyan
Write-Host "  - HIA Chat: Ctrl+Shift+A or View → ADK IDE → HIA Chat" -ForegroundColor White
Write-Host "  - Agent Status: Ctrl+Shift+S or View → ADK IDE → Agent Status" -ForegroundColor White
Write-Host "  - Code Execution: Ctrl+Shift+E or View → ADK IDE → Code Execution" -ForegroundColor White
Write-Host "  - Cloud Status: View → ADK IDE → Cloud Status" -ForegroundColor White
Write-Host ""

npm.cmd run start

