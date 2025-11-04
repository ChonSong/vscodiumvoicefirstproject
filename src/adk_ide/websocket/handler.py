"""WebSocket handler for real-time agent interactions."""
from typing import Dict, Any, Optional
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import logging

from ..agents.hia import HumanInteractionAgent
from ..agents.cea import CodeExecutionAgent

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time agent communication."""

    def __init__(self, hia: HumanInteractionAgent, code_executor: CodeExecutionAgent):
        self.hia = hia
        self.code_executor = code_executor
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

