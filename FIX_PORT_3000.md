# Fixing Port 3000 - Theia Startup Issues

## Problem
Port 3000 isn't working - Theia isn't starting.

## Root Cause
Theia has a native module error with `drivelist`. The webpack configuration has stubs for native modules, but Theia needs to be rebuilt with these stubs.

## Solution Steps

### Step 1: Install Dependencies
```powershell
cd theia-fresh\examples\browser
npm.cmd install
```

This will install all required Node.js packages (may take 5-10 minutes).

### Step 2: Clean and Rebuild
```powershell
# Clean previous build
npm.cmd run clean

# Rebuild with native module stubs
npm.cmd run rebuild
```

### Step 3: Start Theia
```powershell
# Option A: Start in watch mode (recommended for development)
npm.cmd run start:watch

# Option B: Start normally
npm.cmd run start
```

## Alternative: Quick Start Script

Use the provided script:
```powershell
.\START_EVERYTHING.ps1
```

This script will:
1. Check if backend is running
2. Install dependencies if needed
3. Start Theia frontend

## Verification

Once Theia starts, you should see:
```
Starting Theia backend on port 3000...
```

Then open: http://localhost:3000

## Troubleshooting

### Error: "unhandled module: drivelist"
**Solution**: Rebuild Theia with the webpack config that stubs native modules:
```powershell
npm.cmd run clean
npm.cmd run rebuild
```

### Error: Dependencies not installed
**Solution**: Install dependencies first:
```powershell
npm.cmd install
```

### Error: Port 3000 already in use
**Solution**: 
1. Find the process: `netstat -ano | findstr :3000`
2. Kill the process or use a different port

### Error: Execution policy
**Solution**: 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Current Status

- ✅ Backend: Running on port 8000
- ⏳ Theia: Installing dependencies and rebuilding
- ⏳ Port 3000: Will be available after rebuild




