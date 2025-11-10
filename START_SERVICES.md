# 🚀 Starting Full Functionality

## Current Status

### ✅ Backend Server
- **Status**: Starting in separate window
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **Proxy Endpoint**: http://localhost:8000/proxy/schemastore/{path}

### ⏳ Theia Frontend
- **Status**: Ready to start
- **URL**: http://localhost:3000 (once started)
- **Dependencies**: Need to be installed

## Quick Start Commands

### Option 1: Use the Startup Script (Recommended)

```powershell
.\start-full-functionality.ps1
```

This script will:
1. ✅ Check backend dependencies
2. ✅ Start backend server (if not running)
3. ✅ Check Theia dependencies
4. ✅ Install Theia dependencies (if needed)
5. ✅ Start Theia frontend

### Option 2: Manual Start

#### Terminal 1: Backend (Already Started)
The backend should be running in a separate window. If not:

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Theia Frontend

```powershell
cd theia-fresh\examples\browser

# Install dependencies (first time only)
npm install

# Start Theia
npm run start:watch
```

## Verification

### Backend Health Check
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "adk-ide"
}
```

### Proxy Endpoint Test
```powershell
curl http://localhost:8000/proxy/schemastore/api/json/catalog.json
```

### Theia Access
Once Theia starts, open: http://localhost:3000

## Available Features

### ADK IDE Features in Theia
- **HIA Chat**: View → ADK IDE → HIA Chat (Ctrl+Shift+A)
- **Agent Status**: View → ADK IDE → Agent Status (Ctrl+Shift+S)
- **Code Execution**: View → ADK IDE → Code Execution (Ctrl+Shift+E)
- **Cloud Status**: View → ADK IDE → Cloud Status

### Backend Endpoints
- `GET /health` - Health check
- `POST /orchestrate` - Agent orchestration
- `POST /execute` - Code execution
- `POST /session/new` - Session management
- `GET /proxy/schemastore/{path}` - Schema store proxy (NEW)
- `WS /ws` - WebSocket endpoint
- `GET /docs` - API documentation

## Configuration

### JSON Extension Settings
- `json.schemaDownload.enable`: `false` (prevents CORS)
- `http.proxy`: `""` (empty)
- `http.proxyStrictSSL`: `true`
- `http.proxyAuthorization`: `null`

### Environment Variables
Ensure `.env` file exists with:
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_API_KEY`

## Troubleshooting

### Backend Not Starting
1. Check if port 8000 is available
2. Verify dependencies: `python -m pip install -r requirements.txt`
3. Check `.env` file exists

### Theia Not Starting
1. Install dependencies: `cd theia-fresh\examples\browser && npm install`
2. Check Node.js version: `node --version` (should be 16+)
3. Check if port 3000 is available

### CORS Errors
- JSON schema downloads are disabled by default
- Use the proxy endpoint: `/proxy/schemastore/{path}`

## Next Steps

1. ✅ Backend server started
2. ⏳ Start Theia frontend
3. ⏳ Verify both services are running
4. ⏳ Test ADK features in Theia

---

**Status**: Backend starting, Theia ready to start



