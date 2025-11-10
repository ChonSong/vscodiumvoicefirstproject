# Start Full Functionality: Backend + Theia Frontend
# This script starts both the FastAPI backend and Theia IDE with all features

Write-Host "🚀 Starting Full Functionality Mode" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Save current directory
$rootDir = Get-Location

# Step 1: Verify Backend Dependencies
Write-Host "📦 Step 1: Verifying Backend Dependencies..." -ForegroundColor Cyan
try {
    python -c "import fastapi, httpx, uvicorn" 2>&1 | Out-Null
    Write-Host "   ✅ Backend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend dependencies missing!" -ForegroundColor Red
    Write-Host "   Installing minimal dependencies..." -ForegroundColor Yellow
    python -m pip install fastapi httpx uvicorn python-dotenv prometheus-client --quiet
}

# Step 2: Check .env file
Write-Host ""
Write-Host "📝 Step 2: Checking Environment Configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env file not found (some features may not work)" -ForegroundColor Yellow
    Write-Host "   Ensure GOOGLE_CLOUD_PROJECT, GOOGLE_APPLICATION_CREDENTIALS, and GOOGLE_API_KEY are set" -ForegroundColor Yellow
}

# Step 3: Check if backend is already running
Write-Host ""
Write-Host "🔍 Step 3: Checking Backend Status..." -ForegroundColor Cyan
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is already running on port 8000" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host "   ℹ️  Backend is not running (will start it)" -ForegroundColor Gray
}

# Step 4: Start Backend (if not running)
if (-not $backendRunning) {
    Write-Host ""
    Write-Host "🚀 Step 4: Starting FastAPI Backend..." -ForegroundColor Cyan
    Write-Host "   Starting backend in a new window..." -ForegroundColor Yellow
    Write-Host "   Backend will be available at: http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   Proxy Endpoint: http://localhost:8000/proxy/schemastore/{path}" -ForegroundColor White
    
    # Start backend in a new window
    $backendScript = @"
cd '$rootDir'
Write-Host '🚀 Starting FastAPI Backend Server...' -ForegroundColor Green
Write-Host 'Backend URL: http://localhost:8000' -ForegroundColor Cyan
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host 'Health: http://localhost:8000/health' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Press Ctrl+C to stop the server' -ForegroundColor Yellow
Write-Host ''
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal
    Write-Host "   ✅ Backend server starting..." -ForegroundColor Green
    Write-Host "   Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

# Step 5: Verify Backend Health
Write-Host ""
Write-Host "🏥 Step 5: Verifying Backend Health..." -ForegroundColor Cyan
$maxRetries = 10
$retryCount = 0
$backendHealthy = $false

while ($retryCount -lt $maxRetries -and -not $backendHealthy) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Backend is healthy and responding" -ForegroundColor Green
            $backendHealthy = $true
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "   ⏳ Waiting for backend to start... (attempt $retryCount/$maxRetries)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $backendHealthy) {
    Write-Host "   ⚠️  Backend may not be fully started yet, but continuing..." -ForegroundColor Yellow
}

# Step 6: Check Theia Dependencies
Write-Host ""
Write-Host "📦 Step 6: Checking Theia Dependencies..." -ForegroundColor Cyan
$theiaDir = Join-Path $rootDir "theia-fresh\examples\browser"
if (Test-Path $theiaDir) {
    Set-Location $theiaDir
    if (Test-Path "node_modules") {
        Write-Host "   ✅ Theia dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Theia dependencies not installed" -ForegroundColor Yellow
        Write-Host "   Installing Theia dependencies (this may take a while)..." -ForegroundColor Yellow
        npm.cmd install
    }
} else {
    Write-Host "   ❌ Theia directory not found: $theiaDir" -ForegroundColor Red
    exit 1
}

# Step 7: Start Theia Frontend
Write-Host ""
Write-Host "🌐 Step 7: Starting Theia Frontend..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✨ Theia IDE Starting..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Theia will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Available Features:" -ForegroundColor Yellow
Write-Host "   • HIA Chat: View → ADK IDE → HIA Chat (Ctrl+Shift+A)" -ForegroundColor White
Write-Host "   • Agent Status: View → ADK IDE → Agent Status (Ctrl+Shift+S)" -ForegroundColor White
Write-Host "   • Code Execution: View → ADK IDE → Code Execution (Ctrl+Shift+E)" -ForegroundColor White
Write-Host "   • Cloud Status: View → ADK IDE → Cloud Status" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Backend Services:" -ForegroundColor Yellow
Write-Host "   • Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "   • Proxy Endpoint: http://localhost:8000/proxy/schemastore/{path}" -ForegroundColor White
Write-Host ""
Write-Host "⚙️  Configuration:" -ForegroundColor Yellow
Write-Host "   • JSON Schema Downloads: Disabled (prevents CORS)" -ForegroundColor White
Write-Host "   • HTTP Proxy: Not configured (using direct connection)" -ForegroundColor White
Write-Host "   • Proxy Endpoint: Available for schema store access" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Theia in watch mode (incremental compilation)..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop Theia" -ForegroundColor Yellow
Write-Host ""

# Start Theia in watch mode
npm.cmd run start:watch




