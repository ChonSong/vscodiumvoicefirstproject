# Fix Node.js Version and Rebuild Theia

## Problems Identified

1. **EBUSY Errors**: Files are locked by VSCodium or other processes
2. **Node.js Version Incompatibility**: Using Node 24.11.0, but Theia requires Node 20 (LTS)

## Solution: Complete Fix

### Step 1: Close Everything

**This is critical - do this first:**

1. **Close VSCodium completely**
   - File → Exit
   - Check Task Manager for any `Code.exe` or `VSCodium.exe` processes

2. **Close all PowerShell/terminal windows**
   - Close all terminal windows
   - Check Task Manager for any `node.exe` processes

3. **Kill any remaining processes**
   - Press `Ctrl+Shift+Esc` to open Task Manager
   - End any processes: `node.exe`, `Code.exe`, `VSCodium.exe`, `npm.exe`
   - End any processes related to `theia-fresh`

### Step 2: Manually Delete Files

**Use Windows File Explorer (not PowerShell):**

1. Navigate to: `D:\vscodiumvoicefirstproject\theia-fresh\`
2. Manually delete:
   - `node_modules` folder (if it exists)
   - `package-lock.json` file (if it exists)
3. Navigate to: `D:\vscodiumvoicefirstproject\theia-fresh\examples\browser\`
4. Manually delete:
   - `node_modules` folder (if it exists)
   - `lib` folder (if it exists)
   - `src-gen` folder (if it exists)
   - `package-lock.json` file (if it exists)

**If deletion fails:**
- Restart your computer
- Try deleting again after restart

### Step 3: Install Node Version Manager (nvm-windows)

1. **Download nvm-windows:**
   - Go to: https://github.com/coreybutler/nvm-windows/releases
   - Download `nvm-setup.exe` (latest release)

2. **Install nvm-windows:**
   - Run `nvm-setup.exe`
   - Follow the installation wizard
   - Accept all defaults

3. **Close and reopen PowerShell:**
   - Close your current PowerShell window
   - Open a **new** PowerShell window (as Administrator if possible)
   - This is required for nvm to work

### Step 4: Install and Use Node 20 (LTS)

**In your new PowerShell window, run these commands:**

```powershell
# Install Node.js v20 (LTS)
nvm install 20

# Switch to Node.js v20
nvm use 20

# Verify it worked (should show v20.x.x)
node -v

# Verify npm version
npm -v
```

**Expected output:**
- `node -v` should show: `v20.x.x` (not v24.x.x)
- `npm -v` should show: `10.x.x` or similar

### Step 5: Reinstall Theia Project

**Now install with the correct Node version:**

```powershell
# Navigate to Theia root
cd D:\vscodiumvoicefirstproject\theia-fresh

# Install dependencies (takes 10-15 minutes)
npm.cmd install
```

**Wait for this to complete successfully.**

### Step 6: Install Browser Example Dependencies

```powershell
# Navigate to browser example
cd examples\browser

# Install dependencies (takes 5-10 minutes)
npm.cmd install
```

### Step 7: Clean and Rebuild

```powershell
# Clean previous build
npm.cmd run clean

# Rebuild (regenerates lib/backend/main.js with all fixes)
npm.cmd run bundle
```

**This step is critical - it regenerates `lib/backend/main.js` with all our webpack fixes.**

### Step 8: Start Theia

```powershell
# Start Theia
npm.cmd run start
```

Then open: http://localhost:3000

## Verification Checklist

Before starting installation:

- [ ] VSCodium is completely closed
- [ ] All terminal windows are closed
- [ ] Task Manager shows no `node.exe` or `Code.exe` processes
- [ ] `node_modules` folders are manually deleted
- [ ] `lib` and `src-gen` folders are manually deleted
- [ ] nvm-windows is installed
- [ ] Node.js v20 is installed and active (`node -v` shows v20.x.x)

## Troubleshooting

### If nvm commands don't work:
- Close and reopen PowerShell
- Run PowerShell as Administrator
- Check if nvm is in PATH: `nvm version`

### If Node version doesn't switch:
```powershell
# List installed versions
nvm list

# Install if not listed
nvm install 20

# Use Node 20
nvm use 20

# Verify
node -v
```

### If installation still fails:
1. Restart computer
2. Open PowerShell as Administrator
3. Run `nvm use 20`
4. Try installation again

## Why Node 20?

- **Node 24** is too new for Theia's dependencies
- **Node 20** is LTS (Long-Term Support) - stable and compatible
- Theia's dependencies (core-js@2, rimraf@2, etc.) are tested with Node 20
- C++ build tools work correctly with Node 20

## Expected Timeline

- **Step 1-2**: 5 minutes (close everything, delete files)
- **Step 3**: 5 minutes (install nvm-windows)
- **Step 4**: 2 minutes (install Node 20)
- **Step 5**: 10-15 minutes (install Theia dependencies)
- **Step 6**: 5-10 minutes (install browser dependencies)
- **Step 7**: 5-10 minutes (rebuild)
- **Step 8**: 1-2 minutes (start)

**Total**: ~30-45 minutes

---

**Follow these steps in order. Don't skip steps. This will fix both the file locking and build issues.**



