# 🚀 Starting Theia with Full ADK Functionality

## Quick Start Guide

Follow these steps to run Theia IDE with all ADK features integrated.

### Step 1: Start the FastAPI Backend

**Terminal 1** - Start the backend server:

```powershell
cd d:\vscodiumvoicefirstproject
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**

### Step 2: Build ADK IDE Extension

**Terminal 2** - Build the extension:

```powershell
cd d:\vscodiumvoicefirstproject\theia-fresh\packages\adk-ide
npm.cmd run build
```

### Step 3: Build Theia Browser Application

**Terminal 3** - Build Theia (from root):

```powershell
cd d:\vscodiumvoicefirstproject\theia-fresh
npm.cmd run compile
npm.cmd run build:browser
```

### Step 4: Start Theia

**Terminal 4** - Run Theia:

```powershell
cd d:\vscodiumvoicefirstproject\theia-fresh\examples\browser
npm.cmd run start
```

Theia will be available at: **http://localhost:3000**

---

## 🎯 Available Features in Theia

Once Theia is running, you can access all ADK features:

### 1. HIA Chat Interface
- **Menu**: View → ADK IDE → HIA Chat
- **Keyboard**: `Ctrl+Shift+A`
- **Features**: Real-time chat with Human Interaction Agent, session management

### 2. Agent Status Monitoring
- **Menu**: View → ADK IDE → Agent Status
- **Keyboard**: `Ctrl+Shift+S`
- **Features**: Real-time agent status, auto-refresh every 5 seconds

### 3. Code Execution
- **Menu**: View → ADK IDE → Code Execution
- **Keyboard**: `Ctrl+Shift+E`
- **Features**: Execute Python code, load from editor, view execution history

### 4. Cloud Status
- **Menu**: View → ADK IDE → Cloud Status
- **Features**: Google Cloud configuration status, auto-refresh every 30 seconds

### 5. Execute Code Command
- **Command Palette**: `Ctrl+Shift+P` → "ADK IDE: Execute Code"
- **Features**: Automatically extracts and executes code from active editor

---

## 🔧 Troubleshooting

### If npm commands fail:
- Try using `npm.cmd` instead of `npm`
- Check PowerShell execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### If backend connection fails:
- Verify backend is running: `curl http://localhost:8000/health`
- Check environment variables in `.env` file
- Ensure backend is accessible from browser

### If widgets don't appear:
- Check browser console for errors
- Verify extension was built: `cd theia-fresh/packages/adk-ide && npm.cmd run build`
- Rebuild browser example: `cd theia-fresh/examples/browser && npm.cmd run build`

---

## 📝 Quick Commands Summary

```powershell
# Terminal 1: Backend
cd d:\vscodiumvoicefirstproject
uvicorn main:app --reload --port 8000

# Terminal 2: Build Extension
cd d:\vscodiumvoicefirstproject\theia-fresh\packages\adk-ide
npm.cmd run build

# Terminal 3: Build Theia
cd d:\vscodiumvoicefirstproject\theia-fresh
npm.cmd run compile
npm.cmd run build:browser

# Terminal 4: Run Theia
cd d:\vscodiumvoicefirstproject\theia-fresh\examples\browser
npm.cmd run start
```

---

**Last Updated**: 2025-11-05




