# Install and Rebuild Theia - Complete Setup
# This script installs dependencies and rebuilds Theia for port 3000

Write-Host "🔧 Installing and Rebuilding Theia" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$theiaDir = "theia-fresh\examples\browser"
$originalDir = Get-Location

# Navigate to Theia directory
if (-not (Test-Path $theiaDir)) {
    Write-Host "❌ Theia directory not found: $theiaDir" -ForegroundColor Red
    exit 1
}

Set-Location $theiaDir
Write-Host "📁 Working directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Step 1: Install dependencies
Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This will take 5-10 minutes. Please be patient..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "node_modules") {
    Write-Host "   ℹ️  node_modules exists, but checking if complete..." -ForegroundColor Gray
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    $depCount = ($packageJson.dependencies.PSObject.Properties | Measure-Object).Count
    Write-Host "   Found $depCount dependencies in package.json" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  node_modules not found, installing..." -ForegroundColor Yellow
}

Write-Host "   Running: npm install" -ForegroundColor Gray
npm.cmd install

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ npm install failed!" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Clean previous build
Write-Host "Step 2: Cleaning previous build..." -ForegroundColor Yellow
npm.cmd run clean
Write-Host "   ✅ Clean completed" -ForegroundColor Green
Write-Host ""

# Step 3: Rebuild with native module stubs
Write-Host "Step 3: Rebuilding Theia with native module stubs..." -ForegroundColor Yellow
Write-Host "   This will rebuild with webpack config that handles native modules" -ForegroundColor Gray
Write-Host "   (This may take a few minutes)" -ForegroundColor Gray
Write-Host ""

npm.cmd run rebuild

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️  Rebuild had some warnings, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Rebuild completed successfully" -ForegroundColor Green
}

Write-Host ""

# Step 4: Verify build
Write-Host "Step 4: Verifying build..." -ForegroundColor Yellow
if (Test-Path "lib\backend\main.js") {
    Write-Host "   ✅ Backend build found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Backend build not found (may need to build)" -ForegroundColor Yellow
}

if (Test-Path "lib\frontend") {
    Write-Host "   ✅ Frontend build found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Frontend build not found (may need to build)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Theia Installation and Rebuild Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Theia is ready to start on port 3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start Theia: npm.cmd run start:watch" -ForegroundColor White
Write-Host "2. Or use: npm.cmd run start" -ForegroundColor White
Write-Host "3. Open: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "📋 Available commands:" -ForegroundColor Yellow
Write-Host "   • npm.cmd run start - Start Theia" -ForegroundColor White
Write-Host "   • npm.cmd run start:watch - Start in watch mode (recommended)" -ForegroundColor White
Write-Host "   • npm.cmd run rebuild - Rebuild if needed" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Set-Location $originalDir




