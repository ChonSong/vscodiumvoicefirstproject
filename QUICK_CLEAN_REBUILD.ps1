# Quick Clean Rebuild - Step by Step
# Run each section separately

Write-Host "🧹 Clean Install and Rebuild - Manual Steps" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Run each section separately, wait for completion." -ForegroundColor Yellow
Write-Host ""

Write-Host "Section 1: Clean Theia Root" -ForegroundColor Green
Write-Host "cd D:\vscodiumvoicefirstproject\theia-fresh" -ForegroundColor White
Write-Host "Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host "Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host ""

Write-Host "Section 2: Clean Browser Example" -ForegroundColor Green
Write-Host "cd examples\browser" -ForegroundColor White
Write-Host "Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host "Remove-Item -Recurse -Force lib -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host "Remove-Item -Recurse -Force src-gen -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host "Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host ""

Write-Host "Section 3: Install Theia Root Dependencies" -ForegroundColor Green
Write-Host "cd ..\..\.." -ForegroundColor White
Write-Host "cd theia-fresh" -ForegroundColor White
Write-Host "npm.cmd install" -ForegroundColor White
Write-Host "  (Takes 10-15 minutes)" -ForegroundColor Gray
Write-Host ""

Write-Host "Section 4: Install Browser Dependencies" -ForegroundColor Green
Write-Host "cd examples\browser" -ForegroundColor White
Write-Host "npm.cmd install" -ForegroundColor White
Write-Host "  (Takes 5-10 minutes)" -ForegroundColor Gray
Write-Host ""

Write-Host "Section 5: Clean and Rebuild" -ForegroundColor Green
Write-Host "npm.cmd run clean" -ForegroundColor White
Write-Host "npm.cmd run bundle" -ForegroundColor White
Write-Host "  (Takes 5-10 minutes - REGENERATES lib/backend/main.js)" -ForegroundColor Gray
Write-Host ""

Write-Host "Section 6: Start Theia" -ForegroundColor Green
Write-Host "npm.cmd run start" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Copy commands from CLEAN_INSTALL_MANUAL_STEPS.md" -ForegroundColor Yellow
Write-Host "Run each section separately, wait for completion." -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan



