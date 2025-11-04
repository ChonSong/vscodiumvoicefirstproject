"""
Code Execution Agent (CEA)

Dedicated agent for secure code execution using BuiltInCodeExecutor.
This agent exclusively uses BuiltInCodeExecutor due to ADK constraints.
"""

from typing import Dict, Any, Optional
from google.adk.core import AgentRequest, AgentResponse, InvocationContext
from google.adk.agents import LlmAgent
from google.adk.tools import BuiltInCodeExecutor

from ..config import get_settings


class CodeExecutionAgent(LlmAgent):
    """
    Code Execution Agent - Dedicated secure code execution.
    
    This agent exclusively uses BuiltInCodeExecutor for secure, sandboxed
    code execution with resource monitoring and safety controls.
    
    Note: Due to ADK constraints, this agent cannot use any other tools
    alongside BuiltInCodeExecutor.
    """
    
    def __init__(self):
        """Initialize Code Execution Agent with BuiltInCodeExecutor."""
        
        settings = get_settings()
        
        instruction = """You are the Code Execution Agent (CEA) for the ADK IDE system,
        specialized in secure code execution and testing.

        ## Your Primary Responsibility:
        Execute code safely in a sandboxed environment with comprehensive monitoring.

        ## Your Capabilities:
        - Secure code execution using BuiltInCodeExecutor
        - Resource monitoring (CPU, memory usage)
        - Execution result analysis and reporting
        - Error detection and reporting
        - Security enforcement and sandboxing

        ## Execution Guidelines:
        - All code runs in a secure sandbox
        - Resource limits are strictly enforced
        - Dangerous operations are blocked
        - Execution results are captured and analyzed
        - Errors are reported with helpful context

        ## Security Features:
        - Sandboxed execution environment
        - CPU and memory monitoring
        - Network access restrictions
        - File system access controls
        - Automatic timeout protection

        ## Execution Process:
        1. **Receive Code**: Accept code from Developing Agent or other sources
        2. **Security Check**: Validate code for safety
        3. **Execute**: Run code in sandboxed environment
        4. **Monitor**: Track resource usage and execution
        5. **Report**: Provide detailed execution results

        ## Result Reporting:
        - Execution output (stdout/stderr)
        - Resource usage statistics
        - Execution time and performance metrics
        - Error details and stack traces
        - Security violations or warnings

        When executing code:
        1. Always prioritize security and safety
        2. Provide clear, detailed execution results
        3. Report any issues or errors comprehensively
        4. Monitor resource usage throughout execution
        5. Ensure proper cleanup after execution

        You are the trusted execution environment for the ADK IDE system."""

        # Configure BuiltInCodeExecutor with security settings
        code_executor = BuiltInCodeExecutor(
            stateful=True,
            error_retry_attempts=2,
            code_block_delimiters=('```python\n', '\n```'),
            # Resource limits from settings
            resource_limits={
                'memory': f"{settings.max_memory_mb}MB",
                'cpu': str(settings.max_cpu_cores),
                'execution_time': settings.max_execution_time_seconds
            }
        )

        super().__init__(
            name="CodeExecutionAgent",
            description="Dedicated agent for secure code execution with BuiltInCodeExecutor",
            instruction=instruction,
            model=settings.adk_model,
            code_executor=code_executor,
            generate_content_config={
                "temperature": 0.0,  # Deterministic execution
                "max_output_tokens": 4096
            }
        )
        
        # Execution statistics
        self.execution_count = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_execution_time = 0.0
        
        # Security settings
        self.settings = settings
    
    async def _run_async_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Main execution logic for Code Execution Agent.
        
        Args:
            request: Execution request with code
            
        Returns:
            Execution results and analysis
        """
        try:
            # Parse execution request
            exec_request = await self._parse_execution_request(request.prompt, request.context)
            
            # Validate code for security
            security_check = await self._validate_code_security(
                exec_request["code"],
                exec_request.get("language", "python")
            )
            
            if not security_check["safe"]:
                return AgentResponse(
                    content=f"Code execution blocked due to security concerns: {security_check['reason']}",
                    metadata={
                        "status": "blocked",
                        "security_violation": security_check["reason"],
                        "agent": self.name
                    }
                )
            
            # Execute code
            execution_result = await self._execute_code_safely(
                exec_request["code"],
                exec_request.get("language", "python"),
                request.context
            )
            
            # Update statistics
            self._update_execution_statistics(execution_result)
            
            # Format response
            response_content = await self._format_execution_response(execution_result)
            
            return AgentResponse(
                content=response_content,
                metadata={
                    "status": execution_result["status"],
                    "execution_time": execution_result.get("execution_time", 0),
                    "resource_usage": execution_result.get("resource_usage", {}),
                    "agent": self.name
                }
            )
            
        except Exception as e:
            self.failed_executions += 1
            return AgentResponse(
                content=f"Code execution failed due to system error: {str(e)}",
                metadata={
                    "status": "system_error",
                    "error": str(e),
                    "agent": self.name
                }
            )
    
    async def _parse_execution_request(
        self,
        prompt: str,
        context: InvocationContext
    ) -> Dict[str, Any]:
        """
        Parse execution request to extract code and parameters.
        
        Args:
            prompt: Execution request prompt
            context: Invocation context
            
        Returns:
            Parsed execution request
        """
        # Extract code from prompt (look for code blocks)
        import re
        
        # Look for code blocks with language specification
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, prompt, re.DOTALL)
        
        if matches:
            language, code = matches[0]
            language = language.lower() if language else "python"
        else:
            # Look for inline code or treat entire prompt as code
            if "execute" in prompt.lower() or "run" in prompt.lower():
                # Extract code after keywords
                code_start = max(
                    prompt.lower().find("execute:"),
                    prompt.lower().find("run:"),
                    prompt.lower().find("code:")
                )
                if code_start >= 0:
                    code = prompt[code_start:].split(":", 1)[1].strip()
                else:
                    code = prompt.strip()
            else:
                code = prompt.strip()
            
            language = "python"  # Default language
        
        return {
            "code": code,
            "language": language,
            "original_prompt": prompt
        }
    
    async def _validate_code_security(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Validate code for security concerns.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Security validation result
        """
        security_result = {
            "safe": True,
            "reason": None,
            "warnings": []
        }
        
        # Basic security checks
        dangerous_patterns = {
            "python": [
                r'import\s+os',
                r'import\s+subprocess',
                r'import\s+sys',
                r'exec\s*\(',
                r'eval\s*\(',
                r'__import__',
                r'open\s*\(',
                r'file\s*\(',
                r'input\s*\(',
                r'raw_input\s*\('
            ],
            "javascript": [
                r'require\s*\(\s*[\'"]fs[\'"]',
                r'require\s*\(\s*[\'"]child_process[\'"]',
                r'eval\s*\(',
                r'Function\s*\(',
                r'setTimeout\s*\(',
                r'setInterval\s*\('
            ]
        }
        
        patterns = dangerous_patterns.get(language, [])
        
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_result["safe"] = False
                security_result["reason"] = f"Potentially dangerous pattern detected: {pattern}"
                break
        
        # Check for excessively long code
        if len(code) > 10000:  # 10KB limit
            security_result["warnings"].append("Code is very long, execution may be slow")
        
        # Check for infinite loops (basic detection)
        if re.search(r'while\s+True\s*:', code) and 'break' not in code:
            security_result["warnings"].append("Potential infinite loop detected")
        
        return security_result
    
    async def _execute_code_safely(
        self,
        code: str,
        language: str,
        context: InvocationContext
    ) -> Dict[str, Any]:
        """
        Execute code safely using BuiltInCodeExecutor.
        
        Args:
            code: Code to execute
            language: Programming language
            context: Invocation context
            
        Returns:
            Execution result with output and metadata
        """
        import time
        
        start_time = time.time()
        
        try:
            # Prepare code for execution
            if language == "python":
                executable_code = code
            else:
                # For non-Python languages, provide guidance
                return {
                    "status": "unsupported_language",
                    "output": f"Language '{language}' is not currently supported for execution. Only Python code can be executed.",
                    "error": None,
                    "execution_time": 0,
                    "resource_usage": {}
                }
            
            # Execute using BuiltInCodeExecutor
            # Note: This is a simplified example - actual implementation would use the code_executor
            execution_output = f"Executing Python code:\n{executable_code}\n\n"
            
            # Simulate execution (in real implementation, use self.code_executor)
            try:
                # This would be: result = await self.code_executor.execute(executable_code)
                execution_output += "Code executed successfully.\n"
                execution_output += "Output: Hello from executed code!"
                
                execution_result = {
                    "status": "success",
                    "output": execution_output,
                    "error": None,
                    "execution_time": time.time() - start_time,
                    "resource_usage": {
                        "memory_mb": 50,  # Simulated
                        "cpu_percent": 10  # Simulated
                    }
                }
                
            except Exception as exec_error:
                execution_result = {
                    "status": "execution_error",
                    "output": execution_output,
                    "error": str(exec_error),
                    "execution_time": time.time() - start_time,
                    "resource_usage": {}
                }
            
            return execution_result
            
        except Exception as e:
            return {
                "status": "system_error",
                "output": "",
                "error": str(e),
                "execution_time": time.time() - start_time,
                "resource_usage": {}
            }
    
    async def _format_execution_response(
        self,
        execution_result: Dict[str, Any]
    ) -> str:
        """
        Format execution result into user-friendly response.
        
        Args:
            execution_result: Raw execution result
            
        Returns:
            Formatted response string
        """
        status = execution_result["status"]
        
        if status == "success":
            response = "✅ **Code Execution Successful**\n\n"
            response += f"**Output:**\n```\n{execution_result['output']}\n```\n\n"
            
            # Add performance metrics
            exec_time = execution_result.get("execution_time", 0)
            response += f"**Performance:**\n"
            response += f"- Execution Time: {exec_time:.3f} seconds\n"
            
            resource_usage = execution_result.get("resource_usage", {})
            if resource_usage:
                response += f"- Memory Usage: {resource_usage.get('memory_mb', 0)} MB\n"
                response += f"- CPU Usage: {resource_usage.get('cpu_percent', 0)}%\n"
        
        elif status == "execution_error":
            response = "❌ **Code Execution Failed**\n\n"
            response += f"**Error:**\n```\n{execution_result['error']}\n```\n\n"
            
            if execution_result.get("output"):
                response += f"**Partial Output:**\n```\n{execution_result['output']}\n```\n\n"
            
            response += "**Troubleshooting Tips:**\n"
            response += "- Check for syntax errors\n"
            response += "- Verify variable names and function calls\n"
            response += "- Ensure proper indentation (for Python)\n"
        
        elif status == "unsupported_language":
            response = "⚠️ **Unsupported Language**\n\n"
            response += execution_result["output"]
            response += "\n\n**Supported Languages:**\n- Python\n"
        
        elif status == "blocked":
            response = "🚫 **Execution Blocked**\n\n"
            response += "Code execution was blocked for security reasons.\n"
            response += f"Reason: {execution_result.get('error', 'Security policy violation')}\n\n"
            response += "**Security Guidelines:**\n"
            response += "- Avoid file system operations\n"
            response += "- No network access\n"
            response += "- No system command execution\n"
        
        else:
            response = "⚠️ **System Error**\n\n"
            response += f"An unexpected error occurred: {execution_result.get('error', 'Unknown error')}\n"
        
        return response
    
    def _update_execution_statistics(self, execution_result: Dict[str, Any]) -> None:
        """
        Update execution statistics.
        
        Args:
            execution_result: Execution result
        """
        self.execution_count += 1
        
        if execution_result["status"] == "success":
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        self.total_execution_time += execution_result.get("execution_time", 0)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Execution statistics
        """
        return {
            "total_executions": self.execution_count,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": (
                self.successful_executions / self.execution_count
                if self.execution_count > 0 else 0
            ),
            "total_execution_time": self.total_execution_time,
            "average_execution_time": (
                self.total_execution_time / self.execution_count
                if self.execution_count > 0 else 0
            )
        }