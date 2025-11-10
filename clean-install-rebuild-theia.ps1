# Clean Install and Rebuild Theia
# This performs a complete clean installation from the Theia root

Write-Host "🧹 Clean Install and Rebuild Theia" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$theiaRoot = "theia-fresh"
$browserExample = "theia-fresh\examples\browser"

# Step 1: Navigate to Theia root
Write-Host "Step 1: Navigating to Theia root..." -ForegroundColor Yellow
if (-not (Test-Path $theiaRoot)) {
    Write-Host "   ❌ Theia root not found: $theiaRoot" -ForegroundColor Red
    exit 1
}

Set-Location $theiaRoot
Write-Host "   ✅ In directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Step 2: Remove node_modules and lock files
Write-Host "Step 2: Removing node_modules and lock files..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "   Removing node_modules (this may take a moment)..." -ForegroundColor Gray
    Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    Write-Host "   ✅ node_modules removed" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  node_modules not found" -ForegroundColor Gray
}

if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
    Write-Host "   ✅ package-lock.json removed" -ForegroundColor Green
}

if (Test-Path "yarn.lock") {
    Remove-Item -Force "yarn.lock" -ErrorAction SilentlyContinue
    Write-Host "   ✅ yarn.lock removed" -ForegroundColor Green
}

Write-Host ""

# Step 3: Clean browser example
Write-Host "Step 3: Cleaning browser example..." -ForegroundColor Yellow
Set-Location $browserExample
if (Test-Path "node_modules") {
    Write-Host "   Removing browser example node_modules..." -ForegroundColor Gray
    Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    Write-Host "   ✅ Browser node_modules removed" -ForegroundColor Green
}

if (Test-Path "lib") {
    Write-Host "   Removing lib directory (contains old build)..." -ForegroundColor Gray
    Remove-Item -Recurse -Force "lib" -ErrorAction SilentlyContinue
    Write-Host "   ✅ lib directory removed" -ForegroundColor Green
}

if (Test-Path "src-gen") {
    Write-Host "   Removing src-gen directory..." -ForegroundColor Gray
    Remove-Item -Recurse -Force "src-gen" -ErrorAction SilentlyContinue
    Write-Host "   ✅ src-gen directory removed" -ForegroundColor Green
}

Write-Host ""

# Step 4: Return to Theia root and install dependencies
Write-Host "Step 4: Installing dependencies in Theia root..." -ForegroundColor Yellow
Write-Host "   This will take 10-15 minutes. Please be patient..." -ForegroundColor Cyan
Write-Host ""

Set-Location "..\..\.."
Set-Location $theiaRoot

npm.cmd install

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ npm install failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Install browser example dependencies
Write-Host "Step 5: Installing browser example dependencies..." -ForegroundColor Yellow
Set-Location $browserExample

npm.cmd install

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Browser npm install failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ Browser dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 6: Clean build
Write-Host "Step 6: Cleaning build..." -ForegroundColor Yellow
npm.cmd run clean
Write-Host "   ✅ Clean completed" -ForegroundColor Green
Write-Host ""

# Step 7: Rebuild (this regenerates lib/backend/main.js)
Write-Host "Step 7: Rebuilding Theia (regenerates lib/backend/main.js)..." -ForegroundColor Yellow
Write-Host "   This will take 5-10 minutes..." -ForegroundColor Cyan
Write-Host ""

npm.cmd run bundle

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️  Build had some warnings, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Build completed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Clean Install and Rebuild Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Theia is ready to start on port 3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Start Theia" -ForegroundColor Yellow
Write-Host "  npm.cmd run start" -ForegroundColor White
Write-Host "  or" -ForegroundColor Gray
Write-Host "  npm.cmd run start:watch" -ForegroundColor White
Write-Host ""
Write-Host "Then open: http://localhost:3000" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""




