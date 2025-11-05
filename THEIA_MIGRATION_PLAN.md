# Theia IDE Migration Plan

## Overview

Migrating from custom React frontend to Eclipse Theia IDE as the base platform, with ADK IDE features integrated as Theia extensions.

**Reference**: [Theia IDE GitHub](https://github.com/ChonSong/theia-ide.git)

## Why Theia IDE?

- **Professional IDE Platform**: Production-ready, battle-tested IDE framework
- **Extensible Architecture**: Built on Theia platform with excellent extension system
- **VS Code Compatible**: Supports VS Code extensions and language servers
- **Desktop & Browser**: Can run as desktop app (Electron) or browser app
- **Modern UI**: Professional, polished interface out of the box

## Migration Strategy

### Phase 1: Theia IDE Setup
1. Clone/initialize Theia IDE structure
2. Set up development environment
3. Configure build system

### Phase 2: Backend Integration
1. Create Theia backend service connecting to ADK IDE FastAPI
2. Implement WebSocket communication
3. Create service interfaces for agent operations

### Phase 3: ADK IDE Extensions
1. Agent Status View extension
2. Agent Chat Interface extension
3. Code Execution integration
4. File Explorer with ArtifactService
5. Agent Commands and Menus

### Phase 4: Feature Integration
1. Performance Profiler integration
2. Section Detection UI
3. Code Map visualization
4. Navigation Assistant
5. Smart Folding

## Architecture

```
Theia IDE (Base)
├── Theia Extensions (ADK IDE Features)
│   ├── adk-agent-view (Agent Status Panel)
│   ├── adk-chat-interface (Chat View)
│   ├── adk-code-executor (Code Execution Integration)
│   ├── adk-file-explorer (ArtifactService Integration)
│   ├── adk-commands (Agent Commands)
│   └── adk-backend (Backend Service)
└── FastAPI Backend (Existing)
    └── ADK Agents & Services
```

## Implementation Steps

### Step 1: Initialize Theia IDE Structure
- Set up Theia IDE monorepo structure
- Configure package.json and build scripts
- Install Theia dependencies

### Step 2: Create ADK IDE Theia Extension Package
- Create `theia-extensions/adk-ide` package
- Set up extension structure
- Configure extension manifest

### Step 3: Backend Service Integration
- Create Theia backend service
- Implement REST client for FastAPI endpoints
- Set up WebSocket connection

### Step 4: Create Views and Widgets
- Agent Status View (right sidebar)
- Chat Interface View (bottom panel)
- Code Execution Terminal integration
- File Explorer with ArtifactService

### Step 5: Commands and Menus
- Agent operation commands
- Context menus
- Keyboard shortcuts

### Step 6: Integration Testing
- Test all features
- Verify backend connectivity
- Validate agent operations

## File Structure

```
theia-ide/
├── applications/
│   └── browser/ (Browser app)
│   └── electron/ (Desktop app)
├── theia-extensions/
│   └── adk-ide/
│       ├── package.json
│       ├── src/
│       │   ├── browser/
│       │   │   ├── adk-agent-view.tsx
│       │   │   ├── adk-chat-view.tsx
│       │   │   ├── adk-commands.ts
│       │   │   └── adk-backend-service.ts
│       │   └── node/
│       │       └── adk-backend-service.ts
│       └── package.json
└── package.json
```

## Dependencies

Theia IDE uses:
- TypeScript
- Node.js
- Yarn (monorepo manager)
- Theia Platform packages

## Migration Checklist

- [ ] Clone/initialize Theia IDE structure
- [ ] Set up development environment
- [ ] Create ADK IDE extension package
- [ ] Implement backend service
- [ ] Create agent status view
- [ ] Create chat interface view
- [ ] Integrate code execution
- [ ] Integrate file explorer
- [ ] Create commands and menus
- [ ] Test all features
- [ ] Update documentation

