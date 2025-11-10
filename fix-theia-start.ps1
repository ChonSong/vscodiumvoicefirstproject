# Fix Theia Startup - Port 3000
# This script fixes the Theia startup issues

Write-Host "🔧 Fixing Theia Startup Issues" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

$theiaDir = "theia-fresh\examples\browser"
Set-Location $theiaDir

Write-Host "Step 1: Checking dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "   ⚠️  Dependencies not installed" -ForegroundColor Yellow
    Write-Host "   Installing dependencies (this will take 5-10 minutes)..." -ForegroundColor Cyan
    Write-Host "   Please wait..." -ForegroundColor Gray
    npm.cmd install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Cleaning previous build..." -ForegroundColor Yellow
npm.cmd run clean
Write-Host "   ✅ Clean completed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Rebuilding Theia with native module stubs..." -ForegroundColor Yellow
Write-Host "   This will rebuild with webpack config that handles native modules" -ForegroundColor Gray
npm.cmd run rebuild
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️  Rebuild had issues, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Starting Theia..." -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✨ Theia will start on http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop Theia" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Start Theia in watch mode
npm.cmd run start:watch



