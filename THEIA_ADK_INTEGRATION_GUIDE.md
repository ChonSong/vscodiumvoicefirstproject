# Theia ADK Integration Guide

Complete guide for integrating all Google ADK features into Theia IDE.

---

## ✅ What's Been Created

### 1. ADK IDE Extension Package

**Location**: `theia-fresh/packages/adk-ide/`

**Structure**:
```
packages/adk-ide/
├── src/
│   ├── browser/              # Frontend code
│   │   ├── adk-hia-chat-widget.tsx       # HIA Chat interface
│   │   ├── adk-agent-status-widget.tsx   # Agent status monitoring
│   │   ├── adk-ide-frontend-service.ts   # Frontend service
│   │   ├── adk-ide-contribution.ts       # Commands & menus
│   │   ├── adk-ide-frontend-module.ts    # DI module
│   │   └── style/
│   │       └── adk-ide.css               # Styles
│   ├── node/                 # Backend code
│   │   ├── adk-ide-backend-service.ts    # Backend service
│   │   └── adk-ide-backend-module.ts     # Backend DI module
│   └── common/               # Shared types
│       ├── adk-ide-protocol.ts           # Protocol definitions
│       └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

---

## Features Implemented

### ✅ 1. HIA Chat Interface
- Real-time chat with Human Interaction Agent
- WebSocket and REST API support
- Session management
- Message history
- Auto-connect on widget open

### ✅ 2. Agent Status Monitoring
- Real-time agent status display
- Auto-refresh (every 5 seconds)
- Manual refresh button
- Status indicators (idle, running, error)
- Agent descriptions

### ✅ 3. Backend Integration
- REST API client for FastAPI backend
- WebSocket client for real-time communication
- Automatic reconnection
- Error handling and fallbacks

### ✅ 4. Commands & Menus
- View menu integration
- Command palette commands
- Keyboard shortcuts
- Quick access to all features

---

## Installation Steps

### Step 1: Rebuild Theia with ADK Extension

```powershell
cd d:\vscodiumvoicefirstproject\theia-fresh

# Install dependencies (if needed)
npm install

# Build the ADK IDE extension
cd packages/adk-ide
npm run build

# Build the browser application
cd ../../examples/browser
npm run build
```

### Step 2: Start ADK Backend

```powershell
cd d:\vscodiumvoicefirstproject

# Install Python dependencies (if needed)
pip install -r requirements.txt

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Theia

```powershell
cd d:\vscodiumvoicefirstproject\theia-fresh\examples\browser
npm run start
```

Theia will be available at: **http://localhost:3000**

---

## Using ADK Features in Theia

### Opening HIA Chat

1. **Via Menu**: View → ADK IDE → HIA Chat
2. **Via Keyboard**: Press `Ctrl+Shift+A`
3. **Via Command Palette**: 
   - Press `Ctrl+Shift+P`
   - Type "ADK IDE: Open HIA Chat"
   - Press Enter

### Opening Agent Status

1. **Via Menu**: View → ADK IDE → Agent Status
2. **Via Keyboard**: Press `Ctrl+Shift+S`
3. **Via Command Palette**: "ADK IDE: Open Agent Status"

### Chatting with HIA

1. Open the HIA Chat widget
2. Type your message in the input box
3. Press `Enter` to send (or `Shift+Enter` for new line)
4. View responses in real-time

**Example Messages**:
- "Create a Python function to calculate factorial"
- "Help me write a REST API endpoint"
- "Explain how to use async/await in JavaScript"

### Monitoring Agent Status

1. Open the Agent Status widget
2. View real-time status of all agents:
   - Human Interaction Agent (HIA)
   - Developing Agent (DA)
   - Code Execution Agent (CEA)
3. Status updates automatically every 5 seconds
4. Use refresh button for manual updates

---

## Configuration

### Backend URL

Set environment variables to configure the backend:

**Windows PowerShell**:
```powershell
$env:ADK_BACKEND_URL="http://localhost:8000"
$env:ADK_WS_URL="ws://localhost:8000/ws"
```

**Linux/Mac**:
```bash
export ADK_BACKEND_URL=http://localhost:8000
export ADK_WS_URL=ws://localhost:8000/ws
```

Or modify in Theia's configuration files.

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Theia IDE (Browser)             │
│  ┌───────────────────────────────────┐  │
│  │   ADK IDE Extension (Frontend)    │  │
│  │  - HIA Chat Widget                │  │
│  │  - Agent Status Widget            │  │
│  │  - Frontend Service               │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│  ┌──────────────▼────────────────────┐  │
│  │   ADK IDE Extension (Backend)     │  │
│  │   - Backend Service               │  │
│  └──────────────┬────────────────────┘  │
└─────────────────┼───────────────────────┘
                  │
         ┌────────▼────────┐
         │  FastAPI Backend│
         │  (Port 8000)    │
         │  ┌────────────┐ │
         │  │ HIA Agent  │ │
         │  │ DA Agent   │ │
         │  │ CEA Agent  │ │
         │  └────────────┘ │
         └─────────────────┘
```

---

## Available Commands

All commands are accessible via Command Palette (`Ctrl+Shift+P`):

- `ADK IDE: Open HIA Chat` - Open chat interface
- `ADK IDE: Open Agent Status` - Open agent status panel
- `ADK IDE: Orchestrate` - Open chat for orchestration
- `ADK IDE: Execute Code` - Execute code with ADK

---

## Keyboard Shortcuts

- `Ctrl+Shift+A` - Open HIA Chat
- `Ctrl+Shift+S` - Open Agent Status

---

## WebSocket vs REST API

The extension uses **WebSocket** for real-time communication when available, with automatic fallback to **REST API**:

- **WebSocket**: Real-time, bidirectional communication
- **REST API**: Reliable fallback, request/response pattern

Both are configured automatically.

---

## Troubleshooting

### Backend Not Connecting

1. **Check backend is running**:
   ```powershell
   curl http://localhost:8000/health
   ```

2. **Check environment variables**:
   ```powershell
   echo $env:ADK_BACKEND_URL
   ```

3. **Check browser console** for connection errors

### Widgets Not Appearing

1. **Check extension is built**:
   ```powershell
   cd theia-fresh/packages/adk-ide
   npm run build
   ```

2. **Rebuild browser application**:
   ```powershell
   cd theia-fresh/examples/browser
   npm run build
   ```

3. **Check Theia console** for errors

### WebSocket Connection Issues

1. Check backend WebSocket endpoint: `ws://localhost:8000/ws`
2. Check firewall settings
3. The extension will automatically fall back to REST API

---

## Next Steps

### Adding More Features

You can extend the extension with:

1. **Code Execution Integration**: Add terminal integration
2. **File Explorer Integration**: Connect to ArtifactService
3. **Performance Profiler UI**: Visualize profiling results
4. **Code Map Visualization**: Show code structure
5. **Session Management UI**: Manage multiple sessions

### Customization

- Modify `adk-ide.css` for styling
- Add new widgets in `src/browser/`
- Add new commands in `adk-ide-contribution.ts`
- Extend protocol in `adk-ide-protocol.ts`

---

## Development

### Watch Mode

```powershell
cd theia-fresh/packages/adk-ide
npm run watch
```

### Testing

```powershell
cd theia-fresh/packages/adk-ide
npm run test
```

---

## Summary

✅ **ADK IDE Extension Created**  
✅ **HIA Chat Interface** - Chat with agents  
✅ **Agent Status Monitoring** - Real-time status  
✅ **Backend Integration** - REST + WebSocket  
✅ **Commands & Menus** - Easy access  
✅ **Integrated into Theia** - Ready to use  

**Status**: ✅ **COMPLETE** - All Google ADK features integrated into Theia!

---

**Last Updated**: 2025-11-05



