"""WebSocket handler for real-time agent interactions."""
from typing import Dict, Any, Optional
import json
import asyncio
import shlex
from fastapi import WebSocket, WebSocketDisconnect
import logging
import pathlib

from ..agents.hia import HumanInteractionAgent
from ..agents.cea import CodeExecutionAgent
from ..tools.file_operations import FileOperationsTool

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time agent communication."""

    def __init__(self, hia: HumanInteractionAgent, code_executor: CodeExecutionAgent, base_path: Optional[str] = None):
        self.hia = hia
        self.code_executor = code_executor
        self.file_operations = FileOperationsTool(base_path=base_path)
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket client."""
        try:
            await websocket.send_json(message)
        except Exception as exc:
            logger.error(f"Error sending message: {exc}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    async def handle_agent_request(self, websocket: WebSocket, request: Dict[str, Any]):
        """Handle an agent request via WebSocket with streaming responses."""
        request_type = request.get("type", "orchestrate")
        request_id = request.get("request_id", "unknown")
        
        try:
            # Handle simple user messages
            if request_type == "user_message":
                message = request.get("message", "")
                
                # Send acknowledgment
                await self.send_personal_message({
                    "type": "status",
                    "message": "Processing your message...",
                }, websocket)
                
                # Route to HIA for processing
                result = await self.hia.run({"message": message, "query": message})
                
                # Extract meaningful response from result
                if isinstance(result, dict):
                    # Try to extract the actual response text
                    response_text = (
                        result.get("response") or 
                        result.get("llm_result", {}).get("response") if isinstance(result.get("llm_result"), dict) else None or
                        result.get("message") or 
                        f"Agent {result.get('agent', 'HIA')} processed: {result.get('status', 'completed')}"
                    )
                    
                    # If we have a code execution result, format it specially
                    if "llm_result" in result or "result" in result:
                        llm_data = result.get("llm_result", result.get("result", {}))
                        if isinstance(llm_data, dict) and ("output" in llm_data or "stdout" in llm_data):
                            code_output = llm_data.get("output") or llm_data.get("stdout")
                            await self.send_personal_message({
                                "type": "code_result",
                                "result": code_output,
                                "agent": "Code Executor",
                            }, websocket)
                            return
                else:
                    response_text = str(result)
                
                # Send agent response
                await self.send_personal_message({
                    "type": "agent_response",
                    "agent": "HIA",
                    "message": response_text,
                    "timestamp": request.get("timestamp"),
                    "full_result": result,  # Include full result for debugging
                }, websocket)
                return
            
            # Send initial acknowledgment
            await self.send_personal_message({
                "type": "ack",
                "request_id": request_id,
                "status": "processing",
            }, websocket)

            # Process request based on type
            if request_type == "orchestrate":
                # Stream progress updates
                await self.send_personal_message({
                    "type": "progress",
                    "request_id": request_id,
                    "message": "Routing to Human Interaction Agent...",
                }, websocket)
                
                result = await self.hia.run(request.get("payload", {}))
                
                await self.send_personal_message({
                    "type": "progress",
                    "request_id": request_id,
                    "message": "Processing complete",
                }, websocket)
                
                await self.send_personal_message({
                    "type": "result",
                    "request_id": request_id,
                    "status": "success",
                    "data": result,
                }, websocket)

            elif request_type == "execute_code":
                await self.send_personal_message({
                    "type": "progress",
                    "request_id": request_id,
                    "message": "Executing code...",
                }, websocket)
                
                result = await self.code_executor.run(request.get("payload", {}))
                
                await self.send_personal_message({
                    "type": "result",
                    "request_id": request_id,
                    "status": "success",
                    "data": result,
                }, websocket)

            elif request_type == "file_explorer":
                await self.send_personal_message({
                    "type": "progress",
                    "request_id": request_id,
                    "message": "Loading directory...",
                }, websocket)
                
                payload = request.get("payload", {})
                action = payload.get("action", "list")
                path = payload.get("path", ".")
                
                if action == "list":
                    result = await self.file_operations.list_directory(path)
                elif action == "read":
                    file_path = payload.get("file_path", "")
                    result = await self.file_operations.read_file(file_path)
                else:
                    result = {"error": f"Unknown action: {action}"}
                
                await self.send_personal_message({
                    "type": "file_explorer_result",
                    "request_id": request_id,
                    "status": "success" if "error" not in result else "error",
                    "data": result,
                    "message": result.get("error"),
                }, websocket)

            elif request_type == "terminal_execute":
                await self.send_personal_message({
                    "type": "terminal_progress",
                    "request_id": request_id,
                    "message": "Executing command...",
                }, websocket)
                
                payload = request.get("payload", {})
                command = payload.get("command", "")
                
                # Convert command to Python code for BuiltInCodeExecutor
                # For simple commands, wrap in Python subprocess call
                # For Python code, execute directly
                python_code = self._convert_command_to_python(command)
                
                result = await self.code_executor.run({"code": python_code})
                
                # Format result for terminal display
                terminal_result = {
                    "stdout": "",
                    "stderr": "",
                    "output": "",
                    "error": "",
                }
                
                if result.get("status") == "success":
                    exec_result = result.get("result", {})
                    if isinstance(exec_result, dict):
                        terminal_result["stdout"] = exec_result.get("stdout", "")
                        terminal_result["stderr"] = exec_result.get("stderr", "")
                        terminal_result["output"] = exec_result.get("output", str(exec_result))
                    else:
                        terminal_result["output"] = str(exec_result)
                else:
                    terminal_result["error"] = result.get("error", "Execution failed")
                
                await self.send_personal_message({
                    "type": "terminal_result",
                    "request_id": request_id,
                    "status": result.get("status", "error"),
                    "data": terminal_result,
                }, websocket)

            else:
                await self.send_personal_message({
                    "type": "error",
                    "request_id": request_id,
                    "message": f"Unknown request type: {request_type}",
                }, websocket)

        except Exception as exc:
            logger.error(f"Error handling request: {exc}")
            await self.send_personal_message({
                "type": "error",
                "request_id": request_id,
                "message": str(exc),
            }, websocket)

    async def websocket_endpoint(self, websocket: WebSocket):
        """Main WebSocket endpoint handler."""
        await self.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    request = json.loads(data)
                    await self.handle_agent_request(websocket, request)
                except json.JSONDecodeError:
                    await self.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON",
                    }, websocket)
                except Exception as exc:
                    logger.error(f"Error processing message: {exc}")
                    await self.send_personal_message({
                        "type": "error",
                        "message": str(exc),
                    }, websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as exc:
            logger.error(f"WebSocket error: {exc}")
            self.disconnect(websocket)

    def _convert_command_to_python(self, command: str) -> str:
        """Convert a terminal command to Python code for BuiltInCodeExecutor.
        
        For shell-like commands, wrap in subprocess. For Python code, return as-is.
        """
        command = command.strip()
        
        # If it looks like Python code (contains Python keywords or is multi-line), execute directly
        python_keywords = ["def ", "import ", "class ", "if ", "for ", "while ", "print(", "="]
        is_python = any(keyword in command for keyword in python_keywords) or "\n" in command
        
        if is_python:
            return command
        
        # Otherwise, treat as shell command and execute via subprocess
        # Use shlex to safely parse the command
        try:
            parts = shlex.split(command)
            cmd = parts[0] if parts else command
            args = parts[1:] if len(parts) > 1 else []
            
            # Wrap in Python subprocess call
            python_code = f"""
import subprocess
import sys
try:
    result = subprocess.run(
        {repr(parts)},
        capture_output=True,
        text=True,
        timeout=30,
        cwd='.'
    )
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print("Command timed out after 30 seconds", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
            return python_code.strip()
        except Exception:
            # Fallback: try to execute as simple Python expression
            return f"import os; os.system({repr(command)})"

