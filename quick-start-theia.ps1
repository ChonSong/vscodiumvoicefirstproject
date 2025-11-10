# Quick start script for Theia with ADK - uses watch mode for faster startup
# This avoids the long full compile by using incremental compilation

Write-Host "🚀 Quick Start: Theia with ADK Functionality" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check/Start Backend
Write-Host "📡 Checking Backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Backend not running. Starting in new window..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; if (Test-Path '.venv\Scripts\python.exe') { . '.venv\Scripts\Activate.ps1'; Write-Host 'Starting FastAPI backend...' -ForegroundColor Green; uvicorn main:app --reload --host 0.0.0.0 --port 8000 } else { Write-Host 'Virtual environment not found!' -ForegroundColor Red; pause }" -WindowStyle Normal
    Start-Sleep -Seconds 3
}

Write-Host ""

# Step 2: Navigate to browser example
Write-Host "📦 Preparing Theia..." -ForegroundColor Yellow
Set-Location "theia-fresh\examples\browser"

# Step 3: Use rebuild (faster than full compile) or start:watch
Write-Host "🔨 Rebuilding browser packages (this is faster than full compile)..." -ForegroundColor Cyan
npm.cmd run rebuild

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✨ Starting Theia in watch mode..." -ForegroundColor Green
Write-Host "   This will compile incrementally as needed." -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Theia will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 ADK Features:" -ForegroundColor Yellow
Write-Host "   • HIA Chat: Ctrl+Shift+A" -ForegroundColor White
Write-Host "   • Agent Status: Ctrl+Shift+S" -ForegroundColor White
Write-Host "   • Code Execution: Ctrl+Shift+E" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Start in watch mode - this compiles incrementally
npm.cmd run start:watch




