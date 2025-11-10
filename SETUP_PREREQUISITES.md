# Prerequisites Installation Guide - Windows

## Required Software Installation

To run the ADK IDE project, you need to install the following software:

### 1. Python 3.8+ Installation

#### Option A: Official Python Installer (Recommended)
1. **Download Python**:
   - Visit: https://www.python.org/downloads/
   - Download Python 3.11 or 3.12 (latest stable version)
   - Choose "Windows installer (64-bit)"

2. **Install Python**:
   - Run the installer
   - ✅ **IMPORTANT**: Check "Add Python to PATH" checkbox
   - Click "Install Now"
   - Verify installation: Open PowerShell and run:
     ```powershell
     python --version
     ```

#### Option B: Microsoft Store
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Click "Install"
4. Verify: `python --version`

### 2. Node.js 16+ Installation

1. **Download Node.js**:
   - Visit: https://nodejs.org/
   - Download LTS version (18.x or 20.x recommended)
   - Choose "Windows Installer (.msi)"

2. **Install Node.js**:
   - Run the installer
   - Follow the installation wizard (default options are fine)
   - Verify installation:
     ```powershell
     node --version
     npm --version
     ```

### 3. Git (Optional, but recommended)

If not already installed:
1. Visit: https://git-scm.com/download/win
2. Download and install
3. Verify: `git --version`

---

## Quick Verification

After installation, verify all prerequisites:

```powershell
# Check Python
python --version
# Should show: Python 3.x.x

# Check Node.js
node --version
# Should show: v18.x.x or v20.x.x

npm --version
# Should show: 9.x.x or 10.x.x

# Check Git (optional)
git --version
```

---

## After Installing Prerequisites

Once Python and Node.js are installed, return to `ASSESSMENT_AND_PLAN.md` and proceed with Phase 1 setup steps.






