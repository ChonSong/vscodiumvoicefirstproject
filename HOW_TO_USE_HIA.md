# How to Use the Human Interaction Agent (HIA)

The Human Interaction Agent (HIA) is the **central orchestrator** of the ADK IDE system. It receives user requests and delegates tasks to specialized agents.

---

## Overview

The HIA:
- ✅ Acts as the central entry point for all development tasks
- ✅ Delegates complex tasks to the Developing Agent (DA) via `EventActions.transfer_to_agent`
- ✅ Handles simple code execution directly via the Code Execution Agent (CEA)
- ✅ Manages multi-agent workflows
- ✅ Saves responses to `session.state["hia_response"]` automatically

---

## Usage Methods

### 1. Via REST API (Recommended)

The easiest way to use HIA is through the FastAPI endpoint.

#### Start the Backend

```powershell
# Make sure dependencies are installed
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Basic Usage

**Endpoint**: `POST http://localhost:8000/orchestrate`

**Example Request**:
```python
import requests

# Simple request
response = requests.post(
    "http://localhost:8000/orchestrate",
    json={
        "message": "Create a Python function to calculate factorial",
        "user_id": "user123"
    }
)

print(response.json())
```

**Example with cURL**:
```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me write a Python function to sort a list",
    "user_id": "user123"
  }'
```

#### Request Format

```python
{
    "message": "Your task or question",
    "user_id": "optional_user_id",
    "session_id": "optional_session_id",  # For context persistence
    "task_type": "optional_task_type",     # "code_generation", "development", etc.
    "action": "execute_code"               # For direct code execution
}
```

#### Response Format

```python
{
    "status": "success",
    "agent": "human_interaction_agent",
    "llm_result": {
        # Response from the LLM agent
        "response": "The generated response...",
        "hia_response": "Saved to session.state"
    }
}
```

---

### 2. Via WebSocket (Real-time)

For real-time streaming and interactive communication:

**WebSocket Endpoint**: `ws://localhost:8000/ws`

**Python Example**:
```python
import asyncio
import websockets
import json

async def use_hia_websocket():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Send a request
        request = {
            "type": "orchestrate",
            "message": "Create a Python function to calculate fibonacci",
            "user_id": "user123"
        }
        
        await websocket.send(json.dumps(request))
        
        # Receive responses
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(data)
            
            if data.get("status") == "complete":
                break

# Run
asyncio.run(use_hia_websocket())
```

**JavaScript Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'orchestrate',
        message: 'Help me write a sorting algorithm',
        user_id: 'user123'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('HIA Response:', data);
};
```

---

### 3. Direct Python API

For programmatic use within Python:

```python
from src.adk_ide.agents.cea import CodeExecutionAgent
from src.adk_ide.agents.da import DevelopingAgent
from src.adk_ide.agents.hia import HumanInteractionAgent
import asyncio

# Initialize agents
code_executor = CodeExecutionAgent()
developing_agent = DevelopingAgent(code_executor=code_executor)
hia = HumanInteractionAgent(
    code_executor=code_executor,
    developing_agent=developing_agent
)

# Use HIA
async def main():
    # Simple request
    result = await hia.run({
        "message": "Create a Python function to calculate prime numbers",
        "user_id": "user123"
    })
    print(result)
    
    # Code execution request (directly delegates to CEA)
    result = await hia.run({
        "action": "execute_code",
        "code": "print('Hello, World!')"
    })
    print(result)

asyncio.run(main())
```

---

## Request Types

### 1. General Development Tasks

HIA will automatically delegate to the Developing Agent for complex tasks:

```python
{
    "message": "Create a REST API endpoint for user authentication",
    "user_id": "user123"
}
```

**What happens**:
1. HIA receives the request
2. Determines it's a complex development task
3. Uses `EventActions.transfer_to_agent` to delegate to DA
4. DA handles code generation
5. Response is returned through HIA

### 2. Direct Code Execution

For simple code execution, HIA delegates directly to CEA:

```python
{
    "action": "execute_code",
    "code": "print('Hello from HIA!')"
}
```

**What happens**:
1. HIA receives the request with `action: "execute_code"`
2. Directly delegates to CodeExecutionAgent
3. Code is executed in sandboxed environment
4. Results are returned

### 3. Code Generation Tasks

Explicit code generation requests:

```python
{
    "task_type": "code_generation",
    "message": "Write a Python class for handling database connections",
    "user_id": "user123"
}
```

---

## Configuration

### Environment Variables

The HIA uses ADK features when enabled:

```bash
# Enable ADK features (requires Google ADK installed)
ADK_ENABLED=true

# Optional: Configure other settings
ADK_EXECUTE_MAX_CODE_LEN=100000
ADK_EXECUTE_TIMEOUT_SECONDS=20
ADK_EXECUTE_STATEFUL=true
ADK_EXECUTE_RETRY_ATTEMPTS=2
```

### With ADK Enabled

When `ADK_ENABLED=true`:
- ✅ Uses Google ADK's LlmAgent for intelligent orchestration
- ✅ Supports `EventActions.transfer_to_agent` delegation
- ✅ Automatically saves responses to `session.state["hia_response"]`
- ✅ Has access to code execution tool
- ✅ Can delegate to Developing Agent automatically

### Without ADK (Fallback Mode)

When `ADK_ENABLED=false` or ADK unavailable:
- ✅ Falls back to scaffold behavior
- ✅ Still delegates to Developing Agent for code generation tasks
- ✅ Still delegates to CEA for code execution
- ⚠️ Limited LLM capabilities

---

## Agent Delegation Flow

```
User Request
    ↓
Human Interaction Agent (HIA)
    ↓
    ├─→ Simple Code Execution? → CodeExecutionAgent (CEA)
    │
    └─→ Complex Development Task? → Developing Agent (DA)
                                    ↓
                                    └─→ Needs Code Execution? → CEA
```

### Example Flow

**Request**: "Create a Python function to calculate fibonacci numbers"

1. **HIA receives**: `{"message": "Create a Python function..."}`
2. **HIA analyzes**: Determines it's a complex development task
3. **HIA delegates**: Uses `EventActions.transfer_to_agent` → DA
4. **DA processes**: Generates code using its tools
5. **DA may call**: CEA to test the generated code
6. **Response returns**: Through DA → HIA → User

---

## Session Management

HIA automatically manages session state:

```python
# Responses are saved to session.state
session.state["hia_response"] = "Response from HIA"

# You can access previous responses
previous_response = session.state.get("hia_response")
```

**Create a session**:
```python
POST http://localhost:8000/session/new
{
    "user_id": "user123",
    "project": "my_project"
}
```

---

## Examples

### Example 1: Simple Question

```python
import requests

response = requests.post(
    "http://localhost:8000/orchestrate",
    json={
        "message": "What is the best way to handle errors in Python?",
        "user_id": "user123"
    }
)

print(response.json()["llm_result"]["response"])
```

### Example 2: Code Generation

```python
response = requests.post(
    "http://localhost:8000/orchestrate",
    json={
        "message": "Create a Python class for a REST API client with retry logic",
        "user_id": "user123",
        "task_type": "code_generation"
    }
)

result = response.json()
print("Generated Code:", result)
```

### Example 3: Code Execution

```python
response = requests.post(
    "http://localhost:8000/orchestrate",
    json={
        "action": "execute_code",
        "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
        """
    }
)

print("Execution Result:", response.json())
```

### Example 4: With Session Context

```python
# Create session
session_response = requests.post(
    "http://localhost:8000/session/new",
    json={"user_id": "user123", "project": "my_project"}
)
session_id = session_response.json()["session_id"]

# Use HIA with session
response = requests.post(
    "http://localhost:8000/orchestrate",
    json={
        "message": "Remember: I prefer functional programming style",
        "user_id": "user123",
        "session_id": session_id
    }
)

# Follow-up request (HIA remembers context)
response2 = requests.post(
    "http://localhost:8000/orchestrate",
    json={
        "message": "Create a function to filter even numbers",
        "user_id": "user123",
        "session_id": session_id  # Same session
    }
)
```

---

## Error Handling

HIA returns error responses when something goes wrong:

```python
{
    "status": "error",
    "agent": "human_interaction_agent",
    "error": "Error message here"
}
```

**Common Errors**:
- `ADK_ENABLED=true` but ADK not installed → Falls back to scaffold
- Invalid request format → Returns error status
- Network issues → Connection error

---

## Testing

### Test HIA Endpoint

```bash
# Health check
curl http://localhost:8000/health

# Test orchestration
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, HIA!", "user_id": "test"}'
```

### Interactive API Docs

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Best Practices

1. **Use Sessions**: For context-aware conversations, create and reuse sessions
2. **Be Specific**: Clear, specific requests get better results
3. **Monitor Responses**: Check `status` field in responses
4. **Handle Errors**: Always check for error status before processing
5. **Use WebSocket**: For real-time streaming and interactive experiences

---

## Troubleshooting

### HIA not responding

1. Check backend is running: `curl http://localhost:8000/health`
2. Check environment variables: `ADK_ENABLED=true` (optional)
3. Check logs for errors

### Delegation not working

1. Ensure `developing_agent` is passed to HIA constructor
2. Check `ADK_ENABLED` is set if using ADK features
3. Verify agents are properly initialized in `main.py`

### Session not persisting

1. Ensure SessionService is properly configured
2. Check Google Cloud credentials if using Vertex AI
3. Verify session_id is included in requests

---

## Next Steps

- **Learn about DA**: See how the Developing Agent works
- **Learn about CEA**: Understand secure code execution
- **Explore Workflows**: Check out LoopAgent, SequentialAgent, etc.
- **Integration Guide**: See how to integrate with Theia frontend

---

**Quick Start**:
1. Start backend: `uvicorn main:app --reload --port 8000`
2. Test: `curl -X POST http://localhost:8000/orchestrate -H "Content-Type: application/json" -d '{"message": "Hello!"}'`
3. Check docs: http://localhost:8000/docs

---

**Last Updated**: 2025-11-05



