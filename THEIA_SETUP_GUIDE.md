# Theia IDE Setup Guide for ADK IDE

## Overview

This guide explains how to set up and build Theia IDE with ADK IDE extensions integrated.

## Prerequisites

- **Node.js** >= 20
- **Yarn** >= 1.7.0 < 2
- **Git**

## Setup Steps

### 1. Navigate to Theia IDE Base

```bash
cd frontend/theia-ide-base
```

### 2. Install Dependencies

```bash
yarn install
```

This will install all dependencies for the monorepo, including:
- Theia platform packages
- Browser application
- All extensions (including ADK IDE extension)

### 3. Build Extensions

```bash
yarn build:extensions
```

This builds all extensions including the ADK IDE extension.

### 4. Build Applications

For development build (faster, unminified):
```bash
yarn build:applications:dev
```

For production build (minified):
```bash
yarn build:applications
```

### 5. Download VS Code Plugins (Optional)

```bash
yarn download:plugins
```

### 6. Start the Browser Application

```bash
cd applications/browser
yarn start
```

The application will be available at `http://localhost:3000`

## Development Workflow

### Watch Mode (Auto-rebuild on changes)

From the root:
```bash
yarn watch
```

Or for specific extension:
```bash
cd theia-extensions/adk-ide
yarn watch
```

### Building ADK IDE Extension Only

```bash
cd theia-extensions/adk-ide
yarn build
```

## Project Structure

```
theia-ide-base/
├── applications/
│   └── browser/          # Browser application
│       └── package.json  # Includes adk-ide-ext dependency
├── theia-extensions/
│   └── adk-ide/          # ADK IDE Extension
│       ├── src/
│       │   ├── browser/     # Frontend code
│       │   ├── node/       # Backend code
│       │   └── common/     # Shared code
│       └── package.json
└── package.json          # Root monorepo config
```

## ADK IDE Extension Features

The ADK IDE extension adds:

1. **Agent Status View** - Monitor agent status and activity
2. **Chat Interface** - Communicate with ADK agents
3. **Backend Service** - Connects to FastAPI backend
4. **Commands** - Agent operations via command palette

## Configuration

### Backend URL

The ADK backend service connects to the FastAPI backend. Configure via environment variables:

```bash
export ADK_BACKEND_URL=http://localhost:8000
export ADK_WS_URL=ws://localhost:8000/ws
```

Or set in the backend service code (defaults to localhost:8000).

## Troubleshooting

### Build Errors

1. **Type errors**: Run `yarn build` from root to ensure all dependencies are built
2. **Missing dependencies**: Run `yarn install` again
3. **Version conflicts**: Check that all packages use Theia version 1.66.0

### Runtime Errors

1. **WebSocket connection fails**: Ensure FastAPI backend is running on port 8000
2. **Views not appearing**: Check browser console for errors
3. **Commands not working**: Verify extension is loaded in browser DevTools

## Next Steps

1. Start FastAPI backend: `uvicorn main:app --reload`
2. Start Theia IDE: `cd applications/browser && yarn start`
3. Open views: View menu → ADK Agent Status / ADK Chat
4. Test agent communication via chat interface

## Integration with Existing Frontend

The old React frontend (`frontend/src`) can be kept as reference, but Theia IDE replaces it. The ADK IDE extension provides:

- Better IDE experience (Theia platform)
- Professional UI
- VS Code extension support
- Better code editing (Monaco Editor built-in)
- Terminal integration
- File explorer integration

