from typing import Any, Dict, Optional, Callable
import os

from .base import ADKIDEAgent, AgentCommunication
from .cea import CodeExecutionAgent


class DevelopingAgent(ADKIDEAgent):
    """Primary code generation and modification agent with optional ADK LlmAgent.
    
    Uses AgentTool to wrap CodeExecutionAgent (CEA) for secure code execution operations.
    """

    def __init__(self, code_executor: CodeExecutionAgent) -> None:
        super().__init__(name="developing_agent", description="Code generation and modification")
        self.code_executor = code_executor
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None
        self._cea_adapter: Optional[object] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent, AgentTool  # type: ignore

                tools = []
                
                # Wrap CEA as AgentTool for explicit invocation
                try:
                    # Create an adapter for the CodeExecutionAgent to work as an ADK agent
                    class CEAAdapter:
                        """Adapter to make CodeExecutionAgent compatible with AgentTool."""
                        def __init__(self, cea: CodeExecutionAgent):
                            self.name = "code_execution_agent"
                            self.description = "Executes code in a sandboxed environment using BuiltInCodeExecutor"
                            self._cea = cea
                        
                        async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
                            return await self._cea.run(request)
                    
                    self._cea_adapter = CEAAdapter(code_executor)
                    
                    # Wrap as AgentTool - this allows DA to invoke CEA as a tool
                    agent_tool = AgentTool(agent=self._cea_adapter)
                    tools.append(agent_tool)
                except Exception as exc:
                    # Fallback to direct tool wrapper if AgentTool unavailable
                    try:
                        class CodeExecTool:
                            name = "code_executor"
                            description = "Execute code in a sandboxed environment"

                            async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                                return await code_executor.run({"code": payload.get("code", "")})

                        tools.append(CodeExecTool())
                    except Exception:
                        pass

                self._llm_agent = LlmAgent(
                    name="DevelopingAgent",
                    description="Specialized code generation and modification agent. Use the code_execution_agent tool to execute code securely.",
                    tools=tools if tools else None,  # type: ignore[arg-type]
                    instruction="You are a specialized code generation and modification agent. When you need to execute code, use the code_execution_agent tool which provides secure, sandboxed execution.",
                    output_key="developing_agent_response",  # Save responses to session.state["developing_agent_response"]
                )
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
        if request.get("action") == "execute_code":
            return await AgentCommunication.delegate_to_agent(self, self.code_executor, request)
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "llm_result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}
        return {"status": "received", "agent": self.name, "request": request}

