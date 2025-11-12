from typing import Any, Dict, Optional, Callable, List
import os
import logging

from .base import ADKIDEAgent, AgentCommunication
from .cea import CodeExecutionAgent
from ..services.artifact import ArtifactService, ToolContextArtifactMethods

logger = logging.getLogger(__name__)


class DevelopingAgent(ADKIDEAgent):
    """Primary code generation and modification agent with optional ADK LlmAgent.

    When ADK is enabled, the Code Execution Agent (CEA) is wrapped as an AgentTool to enable native
    agent-to-agent delegation while still falling back to FunctionTool in legacy scenarios.
    """

    def __init__(self, code_executor: CodeExecutionAgent, artifact_service: Optional[ArtifactService] = None) -> None:
        super().__init__(name="developing_agent", description="Code generation and modification")
        self.code_executor = code_executor
        self.artifact_service = artifact_service or getattr(code_executor, "artifact_service", None)
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore
                from google.adk.tools import AgentTool, FunctionTool  # type: ignore

                tools = []
                artifact_service = self.artifact_service
                agent_tool_created = False

                # Preferred: wrap CEA as AgentTool for native delegation
                try:  # pragma: no cover
                    class CodeExecutionAgentAdapter:
                        name = "code_execution_agent"
                        description = "Execute Python code securely using the Code Execution Agent."

                        def __init__(self, base_agent: CodeExecutionAgent, artifact_service_ref: Optional[Any]) -> None:
                            self._base = base_agent
                            self._artifact_service = artifact_service_ref

                        async def run(
                            self,
                            request: Optional[Dict[str, Any]] = None,
                            invocation_context: Optional[Any] = None,
                            **kwargs: Any,
                        ) -> Dict[str, Any]:
                            payload: Dict[str, Any] = {}
                            if request and isinstance(request, dict):
                                payload.update(request)
                            # Merge additional kwargs (e.g., tool call arguments)
                            for key, value in kwargs.items():
                                if key not in payload:
                                    payload[key] = value

                            if "code" not in payload:
                                raise ValueError("Missing 'code' argument for code execution tool")

                            result = await self._base.run(payload)
                            await self._handle_artifacts(invocation_context, payload, result)
                            return result

                        async def _handle_artifacts(
                            self,
                            invocation_context: Optional[Any],
                            payload: Dict[str, Any],
                            result: Dict[str, Any],
                        ) -> None:
                            if self._artifact_service is None:
                                return

                            session_id: Optional[str] = payload.get("session_id")
                            tool_context = None

                            if invocation_context is not None:
                                tool_context = getattr(invocation_context, "tool_context", None)
                                session = getattr(invocation_context, "session", None)
                                if session is not None:
                                    session_id = getattr(session, "session_id", None) or getattr(session, "id", None) or session_id

                            if session_id is None:
                                return

                            helper = ToolContextArtifactMethods(self._artifact_service, session_id)

                            # Wire helper methods into tool_context for downstream usage
                            if tool_context is not None:
                                if not hasattr(tool_context, "save_artifact"):
                                    setattr(tool_context, "save_artifact", helper.save_artifact)
                                if not hasattr(tool_context, "load_artifact"):
                                    setattr(tool_context, "load_artifact", helper.load_artifact)

                            if result.get("status") != "success":
                                return

                            execution_output = self._extract_output(result)
                            if not execution_output:
                                return

                            try:
                                artifact_name = f"code-execution-output-{session_id}.txt"
                                await helper.save_artifact(
                                    artifact_name=artifact_name,
                                    content=execution_output.encode("utf-8"),
                                    metadata={
                                        "agent": self.name,
                                        "description": "Captured stdout/result from code execution",
                                    },
                                )
                            except Exception as artifact_exc:  # pragma: no cover
                                logger.debug(f"Failed to persist code execution artifact: {artifact_exc}", exc_info=True)

                        @staticmethod
                        def _extract_output(result: Dict[str, Any]) -> str:
                            exec_result = result.get("result")
                            if isinstance(exec_result, dict):
                                for key in ["output", "stdout", "text", "result"]:
                                    value = exec_result.get(key)
                                    if value:
                                        return str(value)
                            elif exec_result is not None:
                                return str(exec_result)
                            return ""

                    adapter_agent = CodeExecutionAgentAdapter(code_executor, artifact_service)
                    agent_tool = AgentTool(adapter_agent)
                    tools.append(agent_tool)
                    agent_tool_created = True
                    logger.info("Created AgentTool for code execution")
                except Exception as agent_tool_exc:  # pragma: no cover
                    logger.warning(
                        f"Could not create AgentTool for code execution: {agent_tool_exc}. Falling back to FunctionTool.",
                        exc_info=True,
                    )

                # Fallback: wrap CEA as FunctionTool for environments without AgentTool support
                if not agent_tool_created:
                    try:
                        async def execute_code(code: str) -> str:
                            """Execute Python code in a sandboxed environment.
                            
                            This tool executes Python code securely using BuiltInCodeExecutor.
                            Note: Graphical applications and interactive windows are not supported.
                            For simple scripts and calculations, use this tool.
                            
                            Args:
                                code: The Python code to execute (as a string)
                                
                            Returns:
                                String containing the execution result or error message
                            """
                            try:
                                logger.info(f"FunctionTool execute_code called with code length: {len(code)}")
                                
                                # Call the code executor
                                result = await code_executor.run({"code": code})
                                logger.info(f"Code execution result: status={result.get('status')}, keys={list(result.keys())}")
                                
                                # Handle different statuses
                                if result.get("status") == "success":
                                    # Extract result and format as string
                                    exec_result = result.get("result", "")
                                    output_text = ""
                                    
                                    # Handle different result formats from ADK executors
                                    if isinstance(exec_result, dict):
                                        # Try common keys for output
                                        output_text = str(
                                            exec_result.get(
                                                "output",
                                                exec_result.get(
                                                    "stdout",
                                                    exec_result.get(
                                                        "text",
                                                        exec_result.get("result", exec_result),
                                                    ),
                                                ),
                                            )
                                        )
                                    elif exec_result is not None:
                                        output_text = str(exec_result)
                                    
                                    if output_text:
                                        logger.info(f"Code execution successful, output length: {len(output_text)}")
                                        return f"Code executed successfully.\nOutput:\n{output_text}"
                                    else:
                                        logger.info("Code executed successfully with no output")
                                        return "Code executed successfully with no output."
                                        
                                elif result.get("status") == "error":
                                    error_msg = result.get("error", "Unknown error")
                                    logger.warning(f"Code execution error: {error_msg}")
                                    return f"Code execution failed with error: {error_msg}"
                                    
                                elif result.get("status") == "not_implemented":
                                    reason = result.get("reason", "Code execution not available")
                                    errors = result.get("errors", [])
                                    error_details = f"{reason}"
                                    if errors:
                                        error_details += f"\nDetails: {', '.join(str(e) for e in errors)}"
                                    logger.warning(f"Code execution not available: {error_details}")
                                    return (
                                        f"Code execution is not available: {error_details}. "
                                        "Please check that BuiltInCodeExecutor or VertexAiCodeExecutor is properly configured."
                                    )
                                else:
                                    reason = result.get("reason", result.get("error", "Unknown reason"))
                                    logger.warning(f"Code execution failed with status '{result.get('status')}': {reason}")
                                    return f"Code execution failed: {reason}"
                                    
                            except Exception as exc:
                                logger.error(f"Exception in execute_code FunctionTool: {exc}", exc_info=True)
                                error_msg = f"Exception during code execution: {str(exc)}"
                                return error_msg
                    
                        # Create FunctionTool from the async function
                        # FunctionTool automatically wraps the function and creates a tool
                        code_exec_tool = FunctionTool(execute_code)
                        tools.append(code_exec_tool)
                        logger.info("Created FunctionTool for code execution")
                    except Exception as exc:  # pragma: no cover
                        logger.warning(f"Could not create FunctionTool for code execution: {exc}", exc_info=True)
                        tools = []

                # Get model from environment or use default
                # Common models: "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"
                model = os.environ.get("ADK_MODEL", os.environ.get("GOOGLE_MODEL", "gemini-2.5-flash"))
                
                self._llm_agent = LlmAgent(
                    name="DevelopingAgent",
                    model=model,  # Required: specify the LLM model
                    description="Specialized code generation and modification agent. Use the execute_code tool to execute code securely.",
                    tools=tools if tools else [],  # type: ignore[arg-type] - Empty list if no tools
                    instruction="You are a specialized code generation and modification agent. When you need to execute code, use the execute_code tool which provides secure, sandboxed execution. The tool accepts a 'code' parameter with the Python code to execute. Important limitations: Graphical applications (pygame, tkinter, matplotlib with GUI backends) and interactive windows are NOT supported. The tool works well for: calculations, data processing, text manipulation, file operations (read/write), and CLI applications. If code execution fails, explain the limitations clearly to the user and suggest alternatives like generating the code for them to run locally.",
                    output_key="developing_agent_response",  # Save responses to session.state["developing_agent_response"]
                )
                logger.info(f"Created LlmAgent for DevelopingAgent with {len(tools)} tools")
                run_method = getattr(self._llm_agent, "run", None)
                run_async_method = getattr(self._llm_agent, "run_async", None)
                if run_async_method is not None:
                    self._llm_agent_run = run_async_method
                elif run_method is not None:
                    self._llm_agent_run = run_method
            except Exception as exc:
                logger.error(f"Failed to initialize ADK LlmAgent for DevelopingAgent: {exc}", exc_info=True)
                self._llm_agent = None
                self._llm_agent_run = None

    async def _save_web_assets(self, request: Dict[str, Any]) -> Dict[str, Any]:
        session_id = request.get("session_id")
        assets: Optional[List[Dict[str, Any]]] = request.get("assets")  # type: ignore[assignment]

        if not session_id:
            return {
                "status": "error",
                "agent": self.name,
                "error": "session_id is required to save web assets",
            }
        if not assets or not isinstance(assets, list):
            return {
                "status": "error",
                "agent": self.name,
                "error": "assets list is required to save web assets",
            }
        if self.artifact_service is None:
            return {
                "status": "error",
                "agent": self.name,
                "error": "ArtifactService is not available; cannot persist web assets",
            }

        saved: List[Dict[str, Any]] = []
        for asset in assets:
            name = asset.get("name")
            content = asset.get("content")
            content_type = asset.get("content_type", "text/plain")
            if not name or content is None:
                continue
            try:
                data_bytes = content.encode("utf-8") if isinstance(content, str) else bytes(content)
            except Exception as exc:  # pragma: no cover
                logger.warning(f"Could not encode asset '{name}' for session '{session_id}': {exc}")
                continue

            try:
                result = await self.artifact_service.save_artifact(
                    session_id=session_id,
                    artifact_name=name,
                    content=data_bytes,
                    metadata={
                        "content_type": content_type,
                        "agent": self.name,
                    },
                )
                saved.append(
                    {
                        "name": name,
                        "content_type": content_type,
                        "artifact": result,
                    }
                )
            except Exception as exc:  # pragma: no cover
                logger.error(f"Failed to save asset '{name}' for session '{session_id}': {exc}", exc_info=True)
                return {
                    "status": "error",
                    "agent": self.name,
                    "error": f"Failed to save asset '{name}': {exc}",
                }

        return {
            "status": "success",
            "agent": self.name,
            "artifacts": saved,
        }

    async def save_web_assets(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Public helper for REST endpoints to persist web assets."""
        return await self._save_web_assets(request)

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if request.get("action") == "execute_code":
            return await AgentCommunication.delegate_to_agent(self, self.code_executor, request)
        if request.get("action") == "save_web_assets":
            return await self._save_web_assets(request)
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "llm_result": result}
            except Exception as exc:
                logger.error(f"Error in DevelopingAgent.run: {exc}", exc_info=True)
                return {"status": "error", "agent": self.name, "error": str(exc)}
        return {"status": "received", "agent": self.name, "request": request}
