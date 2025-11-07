# Theia Frontend Setup

**Date**: 2025-11-05  
**Status**: ✅ React Frontend Removed, Theia Ready

---

## ✅ Changes Made

1. ✅ **React Frontend Removed**
   - Removed `src/` directory
   - Removed `public/` directory
   - Removed `package.json` and `package-lock.json`
   - Removed `node_modules/`

2. ✅ **Theia IDE Ready**
   - Theia IDE base located at: `frontend/theia-ide-base`
   - Ready for setup and installation

---

## 🚀 Setting Up Theia Frontend

### Prerequisites

1. **Node.js** >= 20
   ```powershell
   node --version  # Should be >= 20
   ```

2. **Yarn** >= 1.7.0 < 2
   ```powershell
   yarn --version  # Install if needed: npm install -g yarn
   ```

### Setup Steps

1. **Navigate to Theia IDE Base**
   ```powershell
   cd frontend/theia-ide-base
   ```

2. **Install Dependencies**
   ```powershell
   yarn install
   ```
   ⚠️ This may take 10-15 minutes as it installs the entire Theia monorepo.

3. **Build Extensions**
   ```powershell
   yarn build:extensions
   ```

4. **Build Application (Development)**
   ```powershell
   yarn build:applications:dev
   ```

5. **Start the Browser Application**
   ```powershell
   cd applications/browser
   yarn start
   ```

   The application will be available at `http://localhost:3000`

---

## 📋 Project Structure

```
frontend/
├── README.md                    # Frontend overview
└── theia-ide-base/              # Theia IDE monorepo
    ├── applications/
    │   └── browser/             # Browser application
    ├── packages/                # Theia core packages
    ├── dev-packages/            # Development packages
    └── theia-extensions/
        └── adk-ide/             # ADK IDE Extension (if exists)
```

---

## 🔗 Integration with Backend

The Theia frontend connects to the FastAPI backend:

- **Backend URL**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws
- **REST API**: http://localhost:8000

Configuration can be set via environment variables:
- `ADK_BACKEND_URL` - Backend API URL
- `ADK_WS_URL` - WebSocket URL

---

## ⚙️ Development Workflow

### Watch Mode (Auto-rebuild)
```powershell
cd frontend/theia-ide-base
yarn watch
```

### Build Specific Extension
```powershell
cd frontend/theia-ide-base/theia-extensions/adk-ide
yarn build
```

### Clean Build
```powershell
cd frontend/theia-ide-base
yarn clean
yarn build:extensions
yarn build:applications:dev
```

---

## 🎯 Next Steps

1. **Install Yarn** (if not installed):
   ```powershell
   npm install -g yarn
   ```

2. **Follow Setup Steps** above to build and run Theia

3. **Verify Backend Connection**:
   - Make sure backend is running: `docker-compose up`
   - Check backend health: http://localhost:8000/health

---

## 📚 Documentation

- **Theia Setup Guide**: `THEIA_SETUP_GUIDE.md`
- **Theia Migration Summary**: `THEIA_MIGRATION_SUMMARY.md`
- **Backend Status**: `DOCKER_STATUS.md`

---

## ✅ Status

- **React Frontend**: ❌ Removed
- **Theia Frontend**: ✅ Ready for setup
- **Backend**: ✅ Running in Docker

---

**Last Updated**: 2025-11-05

