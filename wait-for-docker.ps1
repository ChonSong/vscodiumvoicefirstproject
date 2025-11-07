# Wait for Docker Desktop to be ready
Write-Host "Waiting for Docker Desktop to start..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    
    try {
        $result = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Docker Desktop is ready!" -ForegroundColor Green
            docker info | Select-String -Pattern "Server Version" | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "Docker is fully operational. You can now run:" -ForegroundColor Cyan
                Write-Host "  docker-compose up --build" -ForegroundColor Yellow
                Write-Host ""
                exit 0
            }
        }
    } catch {
        # Ignore errors, keep waiting
    }
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "⚠ Docker Desktop may still be starting." -ForegroundColor Yellow
Write-Host "Please check the Docker Desktop window and wait for it to show 'Docker Desktop is running'." -ForegroundColor Yellow
Write-Host ""
Write-Host "You can manually check with: docker info" -ForegroundColor Cyan

