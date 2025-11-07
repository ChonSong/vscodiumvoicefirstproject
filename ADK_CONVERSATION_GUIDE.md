# ADK Bidirectional Conversation Guide

## Overview

This document answers your questions about the ADK integration and demonstrates how to use bidirectional conversation with repository access.

---

## ❓ Is the ADK Integration an Extension?

**No, the ADK integration is NOT a browser extension or IDE extension.**

The ADK (Agent Development Kit) integration is the **core architecture** of this system:

### What ADK Is:
- **Server-side framework** from Google for building AI agent systems
- **Multi-agent orchestration** platform (HIA, DA, CEA agents)
- **Python SDK** integrated directly into the FastAPI backend
- **Runtime environment** for secure code execution and AI interactions

### Key Components:
```
Backend (Python FastAPI)
├── google.adk.LlmAgent         # AI conversation agent
├── google.adk.BuiltInCodeExecutor  # Secure code execution
├── google.adk.SessionService   # Session management
└── Custom agents (HIA, DA, CEA)   # Multi-agent system
```

### Not an Extension Because:
- It runs on the **server-side**, not in the browser
- It's **built into** the application architecture
- It provides the **core functionality**, not adds to it
- It's a **framework**, not a plugin

---

## ✅ Can It Provide Bidirectional Conversation with Repository Access?

**YES!** The system is specifically designed for this. Here's how:

### 1. Bidirectional Communication

The system uses **WebSocket** for real-time, bidirectional communication:

```javascript
// Client sends message
ws.send({
  type: "user_message",
  message: "List files in the src directory"
})

// Server responds in real-time
ws.onmessage = (event) => {
  // Receives agent responses instantly
}
```

### 2. Repository Access

The HIA (Human Interaction Agent) has **three tools** for repository interaction:

#### a) **File Operations Tool**
```python
# List files
{"action": "list", "file_path": "src"}

# Read files
{"action": "read", "file_path": "main.py"}

# Write files
{"action": "write", "file_path": "test.py", "content": "..."}
```

#### b) **Code Execution Tool**
```python
# Execute Python code with repository context
{"action": "execute_code", "code": "import os; print(os.listdir('src'))"}
```

#### c) **ADK LlmAgent** (when enabled)
- Natural language understanding
- Intelligent tool selection
- Context-aware responses

### 3. How It Works

```
┌─────────────┐                  ┌──────────────┐
│   Browser   │  ←──WebSocket──→ │   Backend    │
│  (Client)   │                  │   (FastAPI)  │
└─────────────┘                  └──────┬───────┘
                                        │
                                 ┌──────▼────────┐
                                 │      HIA      │
                                 │  (ADK Agent)  │
                                 └──┬────────┬───┘
                                    │        │
                    ┌───────────────┘        └────────────┐
                    │                                     │
            ┌───────▼────────┐                   ┌────────▼────────┐
            │ File Operations│                   │ Code Executor   │
            │     Tool       │                   │      Tool       │
            └───────┬────────┘                   └────────┬────────┘
                    │                                     │
                    └─────────────┬───────────────────────┘
                                  │
                         ┌────────▼────────┐
                         │   Repository    │
                         │   /workspaces/  │
                         │   vscodium...   │
                         └─────────────────┘
```

---

## 🚀 Current Status: System Running

### ✅ Backend Running
- **URL**: http://localhost:8000
- **Status**: Active and accepting connections
- **WebSocket**: ws://localhost:8000/ws

### ✅ Frontend Available
- **URL**: http://localhost:8000
- **Interface**: Web-based chat UI
- **Features**: Real-time messaging with agents

### 🔧 ADK Status
- **Mode**: Fallback (ADK_ENABLED=false)
- **Agents**: HIA, DA, CEA initialized
- **Tools**: File operations, code execution available

---

## 💡 How to Use Bidirectional Conversation

### Option 1: Web UI (Easiest)

1. **Open in browser**: http://localhost:8000
2. **Click "Connect"** to establish WebSocket connection
3. **Type messages** like:
   - "List files in the src directory"
   - "What agents are available?"
   - "Show me the main.py file"
   - "Execute: print(2+2)"

### Option 2: Enable Full ADK (Advanced)

To enable full AI-powered conversations:

1. **Update .env file**:
   ```bash
   ADK_ENABLED=true
   ```

2. **Restart the backend**:
   ```bash
   # The server will auto-reload if still running with --reload flag
   ```

3. **Now you can use natural language**:
   - "Can you analyze the code in src/adk_ide/agents/hia.py?"
   - "List all Python files and summarize their purpose"
   - "Execute code to count lines in each file"
   - "Read the README and explain the architecture"

### Option 3: API Calls (Programmatic)

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "user_message",
            "message": "List files in src"
        }))
        
        # Receive response
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(chat())
```

---

## 📊 Example Conversations

### Example 1: File Listing
```
You: "List files in the src directory"

HIA: "Found 4 items in the root directory."
     [Shows: src/, static/, tests/, main.py, ...]
```

### Example 2: Code Execution
```
You: "Execute: print(2+2)"

Code Executor: "4"
```

### Example 3: Agent Info
```
You: "What agents are available?"

HIA: "Available agents: human_interaction_agent (Central Orchestrator),
      developing_agent (Development), code_execution_agent (Code Execution)"
```

### Example 4: With ADK Enabled (Full AI)
```
You: "Analyze the architecture and suggest improvements"

HIA: [Uses LlmAgent with Gemini]
     "Based on analyzing your repository structure, I can see you have
      a multi-agent system with HIA, DA, and CEA. Here are some suggestions:
      1. Add caching for file operations...
      2. Implement retry logic for code execution...
      [detailed analysis]"
```

---

## 🔐 Repository Access Security

The system has **security controls** to protect your repository:

### Path Validation
```python
# Only allows access within base_path
# Blocks: ../../../etc/passwd
# Allows: src/agents/hia.py
```

### Sandboxed Execution
```python
# Code execution is isolated
# Resource limits enforced
# Timeout protection
```

### Safety Callbacks
```python
# Before model: Input validation
# Before tool: Permission checks
# After tool: Output sanitization
```

---

## 🎯 Next Steps

### 1. Try the Web Interface
```bash
# Open in browser
http://localhost:8000

# Click "Connect"
# Start chatting with the agents
```

### 2. Enable Full ADK (Optional)
```bash
# Edit .env
echo "ADK_ENABLED=true" >> .env

# Restart (auto-reloads if running with --reload)
```

### 3. Explore Advanced Features
- Multi-agent delegation
- Complex code analysis
- Automated refactoring
- Testing and validation

---

## 📚 Summary

### Your Questions Answered:

1. **Is ADK an extension?**
   - No, it's the core server-side framework

2. **Can it do bidirectional conversation with repository?**
   - Yes! Through WebSocket + File Operations + Code Execution

3. **How to get frontend and backend running?**
   - ✅ **DONE!** Both are running now:
     - Backend: http://localhost:8000
     - Frontend: http://localhost:8000 (same URL)
     - WebSocket: ws://localhost:8000/ws

### What You Can Do Now:

✅ Chat with AI agents in real-time  
✅ Access and analyze repository files  
✅ Execute code in a sandboxed environment  
✅ Get intelligent responses about your codebase  
✅ Delegate complex tasks to specialized agents  

**Start exploring at: http://localhost:8000** 🚀
