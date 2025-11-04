from typing import Any, Dict, List
import os
import re
import asyncio

from .base import ADKIDEAgent


class CodeExecutionAgent(ADKIDEAgent):
    """Dedicated secure code execution agent (BuiltInCodeExecutor only).

    Attempts to use ADK's BuiltInCodeExecutor if available; otherwise returns
    a not_implemented status.
    """

    def __init__(self) -> None:
        super().__init__(name="code_execution_agent", description="Executes code in a sandboxed environment")
        self._executor = None
        # Lazy init at first call to avoid import-time failures
        self.max_code_len: int = int(os.environ.get("ADK_EXECUTE_MAX_CODE_LEN", "100000"))
        self.timeout_seconds: float = float(os.environ.get("ADK_EXECUTE_TIMEOUT_SECONDS", "20"))
        self._stateful: bool = os.environ.get("ADK_EXECUTE_STATEFUL", "true").lower() == "true"
        self._retry_attempts: int = int(os.environ.get("ADK_EXECUTE_RETRY_ATTEMPTS", "2"))
        self._cpu_limit: str = os.environ.get("ADK_EXECUTE_CPU", "2")
        self._memory_limit: str = os.environ.get("ADK_EXECUTE_MEMORY", "4GB")
        default_denylist = [r"\bimport\s+os\b", r"\bsubprocess\b", r"\bsocket\b", r"\bshutil\.rmtree\b"]
        self.denylist_patterns: List[re.Pattern[str]] = [re.compile(p, re.IGNORECASE) for p in default_denylist]

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        code = request.get("code")
        if not code:
            return {"status": "error", "error": "missing 'code'", "agent": self.name}

        # Basic input validation
        if len(str(code)) > self.max_code_len:
            return {"status": "error", "error": "code too large", "agent": self.name}
        for pattern in self.denylist_patterns:
            if pattern.search(str(code)):
                return {"status": "error", "error": "forbidden code pattern detected", "agent": self.name}

        # Try initialize executor if not yet
        if self._executor is None:
            # Try VertexAiCodeExecutor first (commonly available), then BuiltInCodeExecutor
            init_errors = []
            try:  # pragma: no cover
                from google.adk.code_executors import VertexAiCodeExecutor  # type: ignore

                # Project/location inferred from env variables
                self._executor = VertexAiCodeExecutor()
            except Exception as exc:
                init_errors.append(f"VertexAiCodeExecutor: {exc}")
                try:
                    from google.adk.code_executors import BuiltInCodeExecutor  # type: ignore

                    # Pass resource limits if supported by the installed ADK version
                    kwargs = {"stateful": self._stateful, "error_retry_attempts": self._retry_attempts}
                    # Some versions accept resource_limits
                    try:
                        kwargs["resource_limits"] = {"cpu": self._cpu_limit, "memory": self._memory_limit}
                    except Exception:
                        pass
                    self._executor = BuiltInCodeExecutor(**kwargs)
                except Exception as exc2:
                    init_errors.append(f"BuiltInCodeExecutor: {exc2}")
                    return {
                        "status": "not_implemented",
                        "agent": self.name,
                        "reason": "No supported ADK code executor available",
                        "errors": init_errors,
                    }

        try:  # pragma: no cover
            # Execute code via ADK executor (support both async and sync interfaces)
            execute_method = getattr(self._executor, "execute", None)
            if execute_method is None:
                raise RuntimeError("Executor missing 'execute' method")

            result = execute_method({"code": code})
            if hasattr(result, "__await__"):
                # Enforce timeout for async executors
                result = await asyncio.wait_for(result, timeout=self.timeout_seconds)  # type: ignore[arg-type]
            return {"status": "success", "result": result}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "error": str(exc), "agent": self.name}

