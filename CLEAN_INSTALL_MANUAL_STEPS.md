# Clean Install and Rebuild - Manual Steps

## Problem
The `lib/backend/main.js` file contains errors because it was built with old/corrupted dependencies. We need to perform a clean install and rebuild.

## Solution: Manual Steps

Run these commands **one at a time** in PowerShell:

### Step 1: Navigate to Theia Root
```powershell
    cd D:\vscodiumvoicefirstproject\theia-fresh
```

### Step 2: Remove node_modules and Lock Files
```powershell
# Remove node_modules (this may take a minute)
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

# Remove lock files
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
Remove-Item -Force yarn.lock -ErrorAction SilentlyContinue
```

### Step 3: Clean Browser Example
```powershell
cd examples\browser

# Remove browser node_modules
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

# Remove build files (THIS IS IMPORTANT - regenerates lib/backend/main.js)
Remove-Item -Recurse -Force lib -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force src-gen -ErrorAction SilentlyContinue

# Remove lock files
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
```

### Step 4: Return to Theia Root and Install Dependencies
```powershell
cd ..\..\..
cd theia-fresh

# Install dependencies (takes 10-15 minutes)
npm.cmd install
```

### Step 5: Install Browser Example Dependencies
```powershell
cd examples\browser

# Install dependencies (takes 5-10 minutes)
npm.cmd install
```

### Step 6: Clean Build
```powershell
npm.cmd run clean
```

### Step 7: Rebuild (Regenerates lib/backend/main.js)
```powershell
# This regenerates lib/backend/main.js with all our fixes
npm.cmd run bundle
```

### Step 8: Start Theia
```powershell
npm.cmd run start
```

## Quick Copy-Paste Commands

Copy and paste these commands **one section at a time**:

```powershell
# Step 1-2: Clean Theia root
cd D:\vscodiumvoicefirstproject\theia-fresh
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
```

```powershell
# Step 3: Clean browser example
cd examples\browser
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force lib -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force src-gen -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
```

```powershell
# Step 4: Install Theia root dependencies
cd ..\..\..
cd theia-fresh
npm.cmd install
```

```powershell
# Step 5: Install browser dependencies
cd examples\browser
npm.cmd install
```

```powershell
# Step 6-7: Clean and rebuild
npm.cmd run clean
npm.cmd run bundle
```

```powershell
# Step 8: Start Theia
npm.cmd run start
```

## Important Notes

1. **Removing `lib` directory is critical** - This forces regeneration of `lib/backend/main.js` with all our webpack fixes
2. **Each npm install takes time** - Be patient, don't cancel
3. **Run commands one at a time** - Wait for each to complete before running the next
4. **Total time**: 15-20 minutes for all steps

## What This Fixes

- ✅ Regenerates `lib/backend/main.js` with drivelist stubs
- ✅ Applies all webpack configuration fixes
- ✅ Removes corrupted/incomplete dependencies
- ✅ Ensures clean build with all fixes

## After Rebuild

Once `npm.cmd run bundle` completes:
- `lib/backend/main.js` will be regenerated
- All webpack fixes (drivelist stubs) will be applied
- Theia should start without errors
- Port 3000 will be available

---

**Run these commands manually, one section at a time. Don't try to automate - run them step by step.**




