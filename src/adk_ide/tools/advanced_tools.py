"""Advanced tool integrations: OpenAPI, Langchain, LiteLlm, FunctionTool."""
from typing import Any, Dict, Optional, Callable, List
import os
from functools import wraps
import asyncio


class OpenAPIToolset:
    """OpenAPI toolset for automatic REST API tool generation."""
    
    def __init__(self, openapi_spec: Dict[str, Any]) -> None:
        self.spec = openapi_spec
        self.tools: List[Any] = []
        self._generate_tools()
    
    def _generate_tools(self) -> None:
        """Generate tools from OpenAPI specification."""
        paths = self.spec.get("paths", {})
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    tool = self._create_tool_from_operation(path, method, operation)
                    if tool:
                        self.tools.append(tool)
    
    def _create_tool_from_operation(
        self, path: str, method: str, operation: Dict[str, Any]
    ) -> Optional[Any]:
        """Create a tool from an OpenAPI operation."""
        operation_id = operation.get("operationId") or f"{method}_{path.replace('/', '_')}"
        summary = operation.get("summary", operation_id)
        
        class APITool:
            name = operation_id
            description = summary or f"{method.upper()} {path}"
            
            def __init__(self, path: str, method: str, operation: Dict[str, Any]):
                self.path = path
                self.method = method.upper()
                self.operation = operation
            
            async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                # In a real implementation, this would make HTTP requests
                return {
                    "status": "success",
                    "path": self.path,
                    "method": self.method,
                    "payload": payload,
                }
        
        return APITool(path, method, operation)
    
    def get_tools(self) -> List[Any]:
        """Get list of generated tools."""
        return self.tools


class LangchainToolAdapter:
    """Adapter for Langchain tool compatibility."""
    
    def __init__(self, langchain_tool: Any) -> None:
        self.langchain_tool = langchain_tool
        self.name = getattr(langchain_tool, "name", "langchain_tool")
        self.description = getattr(langchain_tool, "description", "Langchain tool")
    
    async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Langchain tool."""
        try:
            # Try to call the tool
            if hasattr(self.langchain_tool, "run"):
                result = self.langchain_tool.run(payload.get("input", ""))
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "result": result}
            elif callable(self.langchain_tool):
                result = self.langchain_tool(payload.get("input", ""))
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "result": result}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
        return {"status": "error", "error": "Tool not callable"}


class LiteLlmWrapper:
    """LiteLlm wrapper for multi-model support."""
    
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model
        self._client = None
        
        if os.environ.get("LITELLM_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                import litellm  # type: ignore
                self._client = litellm
            except ImportError:
                pass
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using LiteLlm."""
        if self._client is None:
            return {"status": "error", "error": "LiteLlm not available"}
        
        try:  # pragma: no cover
            response = await self._client.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return {
                "status": "success",
                "content": response.choices[0].message.content,
                "model": self.model,
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}


def create_function_tool(func: Callable, name: Optional[str] = None, description: Optional[str] = None) -> Any:
    """Wrap a Python function as a tool."""
    func_name = name or func.__name__
    func_desc = description or (func.__doc__ or f"Function: {func_name}")
    
    class FunctionTool:
        name = func_name
        description = func_desc
        
        def __init__(self, wrapped_func: Callable):
            self._func = wrapped_func
        
        async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract arguments from payload
                args = payload.get("args", [])
                kwargs = payload.get("kwargs", {})
                
                # Call function
                if asyncio.iscoroutinefunction(self._func):
                    result = await self._func(*args, **kwargs)
                else:
                    result = self._func(*args, **kwargs)
                
                return {"status": "success", "result": result}
            except Exception as exc:
                return {"status": "error", "error": str(exc)}
    
    return FunctionTool(func)


class LongRunningFunctionTool:
    """Tool for long-running operations with status tracking."""
    
    def __init__(self, func: Callable, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self._func = func
        self._tasks: Dict[str, Any] = {}  # task_id -> task
    
    async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Start long-running operation."""
        import uuid
        task_id = str(uuid.uuid4())
        
        # Start task in background
        if asyncio.iscoroutinefunction(self._func):
            task = asyncio.create_task(self._func(**payload))
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, lambda: self._func(**payload))
        
        self._tasks[task_id] = {
            "task": task,
            "status": "running",
            "started_at": asyncio.get_event_loop().time(),
        }
        
        return {
            "status": "started",
            "task_id": task_id,
            "message": "Long-running operation started",
        }
    
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of long-running task."""
        if task_id not in self._tasks:
            return {"status": "error", "error": "Task not found"}
        
        task_info = self._tasks[task_id]
        task = task_info["task"]
        
        if task.done():
            try:
                result = await task
                task_info["status"] = "completed"
                task_info["result"] = result
                return {
                    "status": "completed",
                    "result": result,
                }
            except Exception as exc:
                task_info["status"] = "failed"
                task_info["error"] = str(exc)
                return {
                    "status": "failed",
                    "error": str(exc),
                }
        
        return {
            "status": "running",
            "elapsed": asyncio.get_event_loop().time() - task_info["started_at"],
        }

