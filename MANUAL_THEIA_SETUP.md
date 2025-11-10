# Manual Theia Setup - Step by Step

## Current Status
- ✅ In correct directory: `theia-fresh\examples\browser`
- ❌ Dependencies not installed: `node_modules` missing
- ⏳ Need to install dependencies first

## Manual Commands to Run

### Step 1: Install Dependencies
**This is the critical step that takes 5-10 minutes**

Open a PowerShell window and run:
```powershell
cd D:\vscodiumvoicefirstproject\theia-fresh\examples\browser
npm.cmd install
```

**Important**: 
- This will take 5-10 minutes
- Don't cancel it - let it complete
- You'll see lots of output as packages are installed
- Wait for it to finish completely

### Step 2: Verify Installation
After npm install completes, verify:
```powershell
Test-Path "node_modules"
Test-Path "node_modules\@theia\core"
```

Both should return `True`.

### Step 3: Clean Build
```powershell
npm.cmd run clean
```

### Step 4: Rebuild
```powershell
npm.cmd run rebuild
```

This will take 2-5 minutes.

### Step 5: Start Theia
```powershell
npm.cmd run start:watch
```

## Alternative: If npm install keeps failing

Try these alternatives:

### Option A: Install with verbose output
```powershell
npm.cmd install --verbose
```

### Option B: Clear cache and retry
```powershell
npm.cmd cache clean --force
npm.cmd install
```

### Option C: Install with legacy peer deps
```powershell
npm.cmd install --legacy-peer-deps
```

## Quick Check Commands

### Check if dependencies are installing
```powershell
cd D:\vscodiumvoicefirstproject\theia-fresh\examples\browser
Get-ChildItem "node_modules" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count
```

### Check npm version
```powershell
npm.cmd --version
```

### Check Node.js version
```powershell
node --version
```
Should be 16+ for Theia.

## Troubleshooting

### Issue: npm install is too slow
**Solution**: This is normal. Theia has hundreds of dependencies. Be patient.

### Issue: npm install fails with errors
**Solution**: 
1. Check internet connection
2. Try: `npm.cmd cache clean --force`
3. Try: `npm.cmd install --legacy-peer-deps`

### Issue: Script crashes instantly
**Solution**: Run commands manually one at a time in PowerShell.

## Expected Output

When npm install is working, you'll see:
```
added 1234 packages in 5m
```

When rebuild is working, you'll see:
```
native node modules are already rebuilt for browser
```

## Next Steps After Installation

Once `npm install` completes successfully:

1. **Clean**: `npm.cmd run clean`
2. **Rebuild**: `npm.cmd run rebuild`  
3. **Start**: `npm.cmd run start:watch`
4. **Open**: http://localhost:3000

---

**Status**: Waiting for `npm install` to complete. This is the longest step (5-10 minutes).



