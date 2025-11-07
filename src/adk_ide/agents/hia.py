from typing import Any, Dict, Optional, Callable
import os

from .base import ADKIDEAgent, AgentCommunication
from .cea import CodeExecutionAgent
from ..tools.file_operations import FileOperationsTool


class HumanInteractionAgent(ADKIDEAgent):
    """Central orchestrator with optional ADK LlmAgent integration.

    Controlled via environment flag `ADK_ENABLED` ("true" to enable). Falls back
    to scaffold behavior if ADK is unavailable or disabled.
    
    Supports multi-agent delegation via EventActions.transfer_to_agent when
    sub_agents are configured.
    """

    def __init__(self, code_executor: CodeExecutionAgent, developing_agent: Optional[ADKIDEAgent] = None) -> None:
        super().__init__(name="human_interaction_agent", description="Central orchestrator")
        self.code_executor = code_executor
        self.developing_agent = developing_agent
        self.file_ops = FileOperationsTool(base_path=os.getcwd())
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore
                # Tool wiring is best-effort; if Tool API unavailable, continue without tools
                tools = None
                try:
                    # Capture self reference for closures
                    file_ops_instance = self.file_ops
                    
                    # Minimal tool wrapper to expose code execution
                    class CodeExecTool:
                        name = "code_executor"
                        description = "Execute Python code in a sandboxed environment"

                        async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                            return await code_executor.run({"code": payload.get("code", "")})
                    
                    # File operations tool
                    class FileOpsTool:
                        name = "file_operations"
                        description = "Read, write, and list files in the repository. Actions: 'read' (file_path), 'write' (file_path, content), 'list' (file_path for directory)"

                        async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                            return await file_ops_instance(payload)

                    tools = [CodeExecTool(), FileOpsTool()]
                except Exception:
                    tools = None

                # Configure sub_agents for transfer_to_agent delegation
                sub_agents = None
                if developing_agent is not None and hasattr(developing_agent, "_llm_agent") and developing_agent._llm_agent is not None:
                    sub_agents = [developing_agent._llm_agent]

                self._llm_agent = LlmAgent(
                    name="HumanInteractionAgent",
                    description="Central orchestrator for development tasks. Delegate complex development tasks to the Developing Agent when needed.",
                    tools=tools,  # type: ignore[arg-type]
                    sub_agents=sub_agents,  # Enable transfer_to_agent delegation
                    instruction="You are the central orchestrator. When you receive complex development tasks that require code generation or modification, you should delegate to the Developing Agent using transfer_to_agent. For simple code execution requests, use the code_executor tool directly.",
                    output_key="hia_response",  # Save responses to session.state["hia_response"]
                )
                # Cache a unified run callable supporting sync/async implementations
                run_method = getattr(self._llm_agent, "run", None)
                run_async_method = getattr(self._llm_agent, "run_async", None)
                if run_async_method is not None:
                    self._llm_agent_run = run_async_method
                elif run_method is not None:
                    self._llm_agent_run = run_method
            except Exception:
                self._llm_agent = None
                self._llm_agent_run = None

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Delegate code execution requests to the CodeExecutionAgent
        if request.get("action") == "execute_code":
            return await AgentCommunication.delegate_to_agent(self, self.code_executor, request)

        # Handle file operations requests
        if request.get("action") == "file_operations":
            return await self.file_ops(request.get("payload", {}))

        # If an ADK LlmAgent is available, attempt to route the request through it
        # The LlmAgent will handle transfer_to_agent delegation automatically if configured
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                
                # Check if result contains transfer_to_agent event action
                if isinstance(result, dict):
                    # Handle EventActions.transfer_to_agent if present
                    if "event_actions" in result and result.get("event_actions", {}).get("transfer_to_agent"):
                        transfer_target = result["event_actions"]["transfer_to_agent"]
                        # If we have a developing agent configured, delegate to it
                        if self.developing_agent is not None:
                            return await AgentCommunication.delegate_to_agent(self, self.developing_agent, request)
                
                return {"status": "success", "agent": self.name, "llm_result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: delegate to developing agent if available
        if self.developing_agent is not None and request.get("task_type") in ["code_generation", "development"]:
            return await AgentCommunication.delegate_to_agent(self, self.developing_agent, request)

        # Enhanced fallback scaffold behavior with basic intelligence
        message = request.get("message", "").lower()
        query = request.get("query", "").lower()
        
        # Handle common queries
        if "list" in message and "file" in message:
            # Try to list files
            result = await self.file_ops.list_directory(".")
            return {
                "status": "success",
                "agent": self.name,
                "response": f"Found {len(result.get('items', []))} items in the root directory.",
                "data": result
            }
        
        if "agent" in message or "available" in message:
            agents_info = f"Available agents: {self.name} (Central Orchestrator)"
            if self.developing_agent:
                agents_info += f", {self.developing_agent.name} (Development)"
            agents_info += f", {self.code_executor.name} (Code Execution)"
            return {
                "status": "success",
                "agent": self.name,
                "response": agents_info
            }
        
        if "execute" in message or "run" in message:
            return {
                "status": "info",
                "agent": self.name,
                "response": "To execute code, please enable ADK_ENABLED=true in your .env file, or send a structured request with action='execute_code'."
            }

        # Fallback scaffold behavior
        return {
            "status": "received",
            "agent": self.name,
            "response": f"I received your message. ADK is currently disabled. Enable it by setting ADK_ENABLED=true in .env. Your message: {request.get('message', request.get('query', str(request)))}"
        }

