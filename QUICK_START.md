# ADK IDE Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ **Python 3.8+** installed
- ✅ **Node.js 16+** installed
- ✅ **Git** (optional)

If you don't have these installed, see [SETUP_PREREQUISITES.md](SETUP_PREREQUISITES.md).

---

## Automated Setup (Recommended)

### Step 1: Run Setup Script

```powershell
# Run the automated setup script
.\setup.ps1
```

This will:
- ✅ Check for Python and Node.js
- ✅ Create/activate virtual environment
- ✅ Install Python dependencies
- ✅ Install Node.js dependencies for frontend

### Step 2: Verify .env File

Ensure `.env` file exists with required variables:
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_API_KEY`

### Step 3: Start Backend

```powershell
# Start the FastAPI backend server
.\start-backend.ps1
```

The backend will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Step 4: Start Frontend (in a new terminal)

```powershell
# Start the React frontend
.\start-frontend.ps1
```

The frontend will be available at:
- **Frontend**: http://localhost:3000

---

## Manual Setup

If you prefer manual setup:

### Backend Setup

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## Verification

### Test Backend

```powershell
# Test health endpoint
curl http://localhost:8000/health
# Or visit in browser: http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "adk-ide"
}
```

### Test Frontend

1. Open browser to http://localhost:3000
2. You should see the ADK IDE interface
3. Check browser console for any errors

### Test WebSocket Connection

1. Open browser developer tools (F12)
2. Go to Network tab → WS filter
3. The frontend should establish a WebSocket connection to `ws://localhost:8000/ws`

---

## Troubleshooting

### Python Not Found
- Ensure Python is installed and added to PATH
- Try: `python --version` or `py --version`
- See [SETUP_PREREQUISITES.md](SETUP_PREREQUISITES.md)

### Node.js Not Found
- Ensure Node.js is installed
- Try: `node --version`
- See [SETUP_PREREQUISITES.md](SETUP_PREREQUISITES.md)

### Port Already in Use
- Backend (port 8000): Change port in `start-backend.ps1`: `--port 8001`
- Frontend (port 3000): React will prompt to use another port

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Build Errors
- Clear node_modules: `rm -rf node_modules` then `npm install`
- Clear npm cache: `npm cache clean --force`

### WebSocket Connection Failed
- Ensure backend is running
- Check backend URL in frontend code
- Verify CORS settings in `main.py`

---

## Next Steps

Once everything is running:

1. **Run Tests**
   ```powershell
   pytest tests/ -v
   ```

2. **Check API Documentation**
   - Visit http://localhost:8000/docs

3. **Explore Features**
   - Agent orchestration
   - Code execution
   - WebSocket communication

4. **Read Documentation**
   - [ASSESSMENT_AND_PLAN.md](ASSESSMENT_AND_PLAN.md) - Project overview
   - [README.md](README.md) - Full documentation
   - [Context/](Context/) - Detailed guides

---

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review [ASSESSMENT_AND_PLAN.md](ASSESSMENT_AND_PLAN.md)
3. Check backend logs for errors
4. Check browser console for frontend errors






