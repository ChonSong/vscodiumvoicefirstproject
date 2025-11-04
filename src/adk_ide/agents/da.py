from typing import Any, Dict, Optional, Callable
import os

from .base import ADKIDEAgent, AgentCommunication
from .cea import CodeExecutionAgent


class DevelopingAgent(ADKIDEAgent):
    """Primary code generation and modification agent with optional ADK LlmAgent."""

    def __init__(self, code_executor: CodeExecutionAgent) -> None:
        super().__init__(name="developing_agent", description="Code generation and modification")
        self.code_executor = code_executor
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                tools = None
                try:
                    class CodeExecTool:
                        name = "code_executor"
                        description = "Execute code in a sandboxed environment"

                        async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                            return await code_executor.run({"code": payload.get("code", "")})

                    tools = [CodeExecTool()]
                except Exception:
                    tools = None

                self._llm_agent = LlmAgent(
                    name="DevelopingAgent",
                    description="Specialized code generation and modification agent",
                    tools=tools,  # type: ignore[arg-type]
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

