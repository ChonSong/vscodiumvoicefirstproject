# 🚀 Running Full Functionality - Quick Guide

## ✅ Current Status

### Backend Server
- **Status**: ✅ Started in separate window
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Theia Frontend  
- **Status**: ⏳ Ready to start
- **URL**: http://localhost:3000 (once started)

## 🎯 Quick Start

### Step 1: Backend (Already Started)
The backend server should be running in a separate PowerShell window. If you need to restart it:

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Start Theia Frontend

Open a **new PowerShell window** and run:

```powershell
cd D:\vscodiumvoicefirstproject\theia-fresh\examples\browser

# Install dependencies (first time only - may take 5-10 minutes)
npm.cmd install

# Start Theia in watch mode
npm.cmd run start:watch
```

**Note**: If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Access Theia

Once Theia starts, open your browser and go to:
**http://localhost:3000**

## 📋 Available Features

### In Theia IDE (http://localhost:3000)

#### ADK IDE Features
- **HIA Chat**: `View → ADK IDE → HIA Chat` or `Ctrl+Shift+A`
- **Agent Status**: `View → ADK IDE → Agent Status` or `Ctrl+Shift+S`
- **Code Execution**: `View → ADK IDE → Code Execution` or `Ctrl+Shift+E`
- **Cloud Status**: `View → ADK IDE → Cloud Status`

### Backend API (http://localhost:8000)

#### Endpoints
- `GET /health` - Health check
- `POST /orchestrate` - Agent orchestration
- `POST /execute` - Code execution
- `POST /session/new` - Create session
- `POST /auth/login` - Login
- `GET /proxy/schemastore/{path}` - **NEW**: Schema store proxy (bypasses CORS)
- `WS /ws` - WebSocket endpoint
- `GET /docs` - Interactive API documentation
- `GET /metrics` - Prometheus metrics

## ✅ Verification

### Test Backend
```powershell
# Health check
curl http://localhost:8000/health

# Test proxy endpoint
curl http://localhost:8000/proxy/schemastore/api/json/catalog.json

# View API docs
start http://localhost:8000/docs
```

### Test Theia
1. Open http://localhost:3000 in your browser
2. Open a JSON file
3. Try the ADK IDE features from the View menu

## 🔧 Configuration

### JSON Extension Settings (Already Configured)
- `json.schemaDownload.enable`: `false` (prevents CORS errors)
- `http.proxy`: `""` (empty)
- `http.proxyStrictSSL`: `true`
- `http.proxyAuthorization`: `null`

Settings are configured in:
- `theia-fresh/examples/browser/.theia/settings.json`
- `theia-fresh/examples/browser/package.json`

### Environment Variables
Ensure `.env` file exists with Google Cloud credentials:
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_API_KEY`

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend won't start
**Solution**: 
1. Check if port 8000 is available
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Verify `.env` file exists

**Problem**: Import errors
**Solution**: Install missing packages:
```powershell
python -m pip install PyJWT opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

### Theia Issues

**Problem**: Execution policy error
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem**: Theia dependencies not installed
**Solution**:
```powershell
cd theia-fresh\examples\browser
npm.cmd install
```

**Problem**: Port 3000 already in use
**Solution**: 
1. Find process: `netstat -ano | findstr :3000`
2. Kill process or use different port

### CORS Issues

**Problem**: CORS errors in browser
**Solution**: 
- JSON schema downloads are disabled by default
- Use the proxy endpoint: `/proxy/schemastore/{path}`
- Settings are already configured correctly

## 📝 Summary

### What's Running
- ✅ **Backend**: FastAPI server on port 8000
- ✅ **Proxy Endpoint**: `/proxy/schemastore/{path}` for CORS bypass
- ✅ **API Docs**: http://localhost:8000/docs
- ⏳ **Theia**: Ready to start on port 3000

### Next Steps
1. ✅ Backend is running
2. ⏳ Start Theia: `cd theia-fresh\examples\browser && npm.cmd run start:watch`
3. ⏳ Open http://localhost:3000
4. ⏳ Test ADK IDE features

---

**All systems ready!** Start Theia frontend to begin using the full functionality.



