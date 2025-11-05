"""CodeWriterAgent for iterative refinement pattern."""
from typing import Any, Dict, Optional, Callable
import os

from .base import ADKIDEAgent
from .cea import CodeExecutionAgent


class CodeWriterAgent(ADKIDEAgent):
    """Specialized agent for writing and generating code."""

    def __init__(self, code_executor: Optional[CodeExecutionAgent] = None) -> None:
        super().__init__(name="code_writer_agent", description="Writes and generates code based on requirements")
        self.code_executor = code_executor
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                tools = []
                if code_executor:
                    try:
                        class CodeExecTool:
                            name = "code_executor"
                            description = "Execute code to test generated code"

                            async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                                return await code_executor.run({"code": payload.get("code", "")})

                        tools.append(CodeExecTool())
                    except Exception:
                        pass

                self._llm_agent = LlmAgent(
                    name="CodeWriterAgent",
                    description="Specialized agent for writing, generating, and modifying code based on requirements and specifications",
                    tools=tools if tools else None,  # type: ignore[arg-type]
                    instruction="You are a code generation specialist. Generate clean, well-documented code that follows best practices. Test your code when possible.",
                    output_key="generated_code",  # Save generated code to session.state["generated_code"]
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
        """Generate code based on requirements."""
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "code": result, "escalate": False}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc), "escalate": False}

        # Fallback scaffold
        return {
            "status": "received",
            "agent": self.name,
            "request": request,
            "code": "# Generated code placeholder",
            "escalate": False,
        }


class CodeReviewerAgent(ADKIDEAgent):
    """Specialized agent for reviewing and validating code."""

    def __init__(self) -> None:
        super().__init__(name="code_reviewer_agent", description="Reviews code for quality, correctness, and best practices")
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="CodeReviewerAgent",
                    description="Reviews code for quality, correctness, security, and adherence to best practices",
                    instruction="You are a code review specialist. Thoroughly review code for bugs, security issues, performance problems, and style violations. Set escalate=True if code meets acceptance criteria.",
                    output_key="code_review_result",  # Save review results to session.state["code_review_result"]
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
        """Review code and determine if it meets acceptance criteria.
        
        Returns EventActions.escalate=True when acceptance criteria are met,
        which signals LoopAgent to terminate the iterative refinement cycle.
        """
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                
                # Determine if code meets acceptance criteria
                # In a real implementation, this would analyze the review result
                meets_criteria = result.get("approved", False) if isinstance(result, dict) else False
                
                # Check if result already contains EventActions
                event_actions = result.get("event_actions", {}) if isinstance(result, dict) else {}
                
                # Set escalate flag in EventActions if criteria are met
                if meets_criteria:
                    event_actions["escalate"] = True
                
                return {
                    "status": "success",
                    "agent": self.name,
                    "review": result,
                    "approved": meets_criteria,
                    "escalate": meets_criteria,  # Legacy flag for backward compatibility
                    "event_actions": event_actions,  # ADK EventActions format
                }
            except Exception as exc:
                return {
                    "status": "error",
                    "agent": self.name,
                    "error": str(exc),
                    "escalate": False,
                    "event_actions": {},
                }

        # Fallback scaffold - approve after first iteration for demo
        code_to_review = request.get("code") or request.get("previous_result", {}).get("code", "")
        approved = bool(code_to_review and len(str(code_to_review)) > 10)
        
        return {
            "status": "success",
            "agent": self.name,
            "review": {"comments": ["Code review completed"], "approved": approved},
            "approved": approved,
            "escalate": approved,
            "event_actions": {"escalate": approved},  # ADK EventActions format
        }

