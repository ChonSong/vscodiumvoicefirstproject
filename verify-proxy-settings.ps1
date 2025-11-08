# Verify JSON Extension Proxy Settings
# This script checks if the proxy settings are configured correctly

Write-Host "🔍 Verifying JSON Extension Proxy Settings" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Settings file exists
$settingsFile = "theia-fresh\examples\browser\.theia\settings.json"
Write-Host "1. Checking settings file..." -ForegroundColor Yellow
if (Test-Path $settingsFile) {
    Write-Host "   ✓ Settings file exists: $settingsFile" -ForegroundColor Green
    $settings = Get-Content $settingsFile | ConvertFrom-Json
    
    Write-Host "   Current settings:" -ForegroundColor Cyan
    Write-Host "   - http.proxy: $($settings.'http.proxy')" -ForegroundColor White
    Write-Host "   - http.proxyStrictSSL: $($settings.'http.proxyStrictSSL')" -ForegroundColor White
    Write-Host "   - http.proxyAuthorization: $($settings.'http.proxyAuthorization')" -ForegroundColor White
    Write-Host "   - json.schemaDownload.enable: $($settings.'json.schemaDownload.enable')" -ForegroundColor White
    
    # Check if settings are correct
    if ($settings.'json.schemaDownload.enable' -eq $false) {
        Write-Host "   ✓ json.schemaDownload.enable is disabled (prevents CORS)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ json.schemaDownload.enable is enabled (may cause CORS errors)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ Settings file not found: $settingsFile" -ForegroundColor Red
    Write-Host "   Creating settings file..." -ForegroundColor Yellow
    $settingsDir = Split-Path $settingsFile -Parent
    if (-not (Test-Path $settingsDir)) {
        New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
    }
    @{
        "http.proxy" = ""
        "http.proxyStrictSSL" = $true
        "http.proxyAuthorization" = $null
        "json.schemaDownload.enable" = $false
    } | ConvertTo-Json | Set-Content $settingsFile
    Write-Host "   ✓ Settings file created" -ForegroundColor Green
}

Write-Host ""

# Check 2: Package.json preferences
Write-Host "2. Checking package.json preferences..." -ForegroundColor Yellow
$packageJson = "theia-fresh\examples\browser\package.json"
if (Test-Path $packageJson) {
    $pkg = Get-Content $packageJson | ConvertFrom-Json
    $prefs = $pkg.theia.frontend.config.preferences
    
    if ($prefs.'json.schemaDownload.enable' -eq $false) {
        Write-Host "   ✓ json.schemaDownload.enable is disabled in package.json" -ForegroundColor Green
    } elseif ($prefs.'json.schemaDownload.enable' -eq $null) {
        Write-Host "   ⚠ json.schemaDownload.enable not set in package.json" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠ json.schemaDownload.enable is enabled in package.json" -ForegroundColor Yellow
    }
    
    if ($prefs.'http.proxy' -ne $null) {
        Write-Host "   ✓ http.proxy is set: $($prefs.'http.proxy')" -ForegroundColor Green
    } else {
        Write-Host "   ℹ http.proxy not set (using default: empty)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ✗ package.json not found" -ForegroundColor Red
}

Write-Host ""

# Check 3: Proxy endpoint
Write-Host "3. Checking proxy endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/proxy/schemastore/api/json/catalog.json" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Proxy endpoint is accessible" -ForegroundColor Green
        Write-Host "   ✓ Backend server is running on port 8000" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠ Proxy endpoint not accessible (backend may not be running)" -ForegroundColor Yellow
    Write-Host "   URL: http://localhost:8000/proxy/schemastore/api/json/catalog.json" -ForegroundColor Gray
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Recommended Configuration:" -ForegroundColor Yellow
Write-Host "  • http.proxy: '' (empty, no system proxy)" -ForegroundColor White
Write-Host "  • http.proxyStrictSSL: true (validate SSL certificates)" -ForegroundColor White
Write-Host "  • http.proxyAuthorization: null (no proxy auth)" -ForegroundColor White
Write-Host "  • json.schemaDownload.enable: false (disable to prevent CORS)" -ForegroundColor White
Write-Host ""
Write-Host "This configuration:" -ForegroundColor Yellow
Write-Host "  ✓ Prevents CORS errors" -ForegroundColor Green
Write-Host "  ✓ Works with the proxy endpoint at /proxy/schemastore/{path}" -ForegroundColor Green
Write-Host "  ✓ Matches commit a652854 recommendations" -ForegroundColor Green
Write-Host ""

