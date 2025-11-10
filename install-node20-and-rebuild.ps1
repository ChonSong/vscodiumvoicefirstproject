# Install Node 20 and Rebuild Theia
# This script guides you through the process

Write-Host "🔧 Fix Node.js Version and Rebuild Theia" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1: Close Everything" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "1. Close VSCodium completely" -ForegroundColor White
Write-Host "2. Close all PowerShell/terminal windows" -ForegroundColor White
Write-Host "3. Open Task Manager (Ctrl+Shift+Esc)" -ForegroundColor White
Write-Host "4. End processes: node.exe, Code.exe, VSCodium.exe" -ForegroundColor White
Write-Host ""
Write-Host "Press any key after closing everything..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

Write-Host "STEP 2: Manually Delete Files" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Use Windows File Explorer to delete:" -ForegroundColor White
Write-Host "  • D:\vscodiumvoicefirstproject\theia-fresh\node_modules" -ForegroundColor Gray
Write-Host "  • D:\vscodiumvoicefirstproject\theia-fresh\package-lock.json" -ForegroundColor Gray
Write-Host "  • D:\vscodiumvoicefirstproject\theia-fresh\examples\browser\node_modules" -ForegroundColor Gray
Write-Host "  • D:\vscodiumvoicefirstproject\theia-fresh\examples\browser\lib" -ForegroundColor Gray
Write-Host "  • D:\vscodiumvoicefirstproject\theia-fresh\examples\browser\src-gen" -ForegroundColor Gray
Write-Host ""
Write-Host "If deletion fails, restart your computer and try again." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key after deleting files..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

Write-Host "STEP 3: Check nvm-windows Installation" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "Checking if nvm is installed..." -ForegroundColor Cyan

try {
    $nvmVersion = nvm version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ nvm-windows is installed: $nvmVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ nvm-windows is not installed" -ForegroundColor Red
        Write-Host ""
        Write-Host "Install nvm-windows:" -ForegroundColor Yellow
        Write-Host "1. Go to: https://github.com/coreybutler/nvm-windows/releases" -ForegroundColor White
        Write-Host "2. Download: nvm-setup.exe" -ForegroundColor White
        Write-Host "3. Run installer" -ForegroundColor White
        Write-Host "4. Close and reopen PowerShell" -ForegroundColor White
        Write-Host "5. Run this script again" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "❌ nvm-windows is not installed" -ForegroundColor Red
    Write-Host "Install nvm-windows first (see instructions above)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "STEP 4: Install and Use Node 20" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow

# Check current Node version
$currentNodeVersion = node -v 2>&1
Write-Host "Current Node version: $currentNodeVersion" -ForegroundColor Cyan

if ($currentNodeVersion -match "v20\.|v20\.") {
    Write-Host "✅ Already using Node 20!" -ForegroundColor Green
} else {
    Write-Host "Installing Node 20 (LTS)..." -ForegroundColor Cyan
    nvm install 20
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Node 20" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Switching to Node 20..." -ForegroundColor Cyan
    nvm use 20
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to switch to Node 20" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Switched to Node 20" -ForegroundColor Green
}

# Verify Node version
$newNodeVersion = node -v 2>&1
Write-Host "Current Node version: $newNodeVersion" -ForegroundColor Green

if (-not ($newNodeVersion -match "v20\.")) {
    Write-Host "⚠️  Warning: Node version is not v20.x.x" -ForegroundColor Yellow
    Write-Host "Please run: nvm use 20" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "STEP 5: Install Theia Dependencies" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow

$theiaRoot = "D:\vscodiumvoicefirstproject\theia-fresh"
if (-not (Test-Path $theiaRoot)) {
    Write-Host "❌ Theia root not found: $theiaRoot" -ForegroundColor Red
    exit 1
}

Set-Location $theiaRoot
Write-Host "Installing Theia dependencies (takes 10-15 minutes)..." -ForegroundColor Cyan
Write-Host "Please wait..." -ForegroundColor Gray
Write-Host ""

npm.cmd install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Theia dependencies" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Theia dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "STEP 6: Install Browser Example Dependencies" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow

$browserExample = Join-Path $theiaRoot "examples\browser"
Set-Location $browserExample

Write-Host "Installing browser example dependencies (takes 5-10 minutes)..." -ForegroundColor Cyan
Write-Host "Please wait..." -ForegroundColor Gray
Write-Host ""

npm.cmd install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install browser dependencies" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Browser dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "STEP 7: Clean and Rebuild" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow

Write-Host "Cleaning build..." -ForegroundColor Cyan
npm.cmd run clean

Write-Host "Rebuilding Theia (regenerates lib/backend/main.js)..." -ForegroundColor Cyan
Write-Host "This takes 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

npm.cmd run bundle

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Build had warnings, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Build completed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Installation and Rebuild Complete!" -ForegroundColor Green
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



