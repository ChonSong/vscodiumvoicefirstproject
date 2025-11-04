"""
Developing Agent (DA)

Specialized agent for code generation, modification, and development workflows.
Coordinates with Code Execution Agent and manages development tasks.
"""

from typing import Dict, Any, Optional, List
from google.adk.core import AgentRequest, AgentResponse, InvocationContext
from google.adk.tools import google_search, AgentTool

from .base import ResearchEnabledAgent, AgentCommunication
from ..config import get_settings


class DevelopingAgent(ResearchEnabledAgent):
    """
    Developing Agent - Specialized for code generation and modification.
    
    Handles all aspects of code development including generation, modification,
    refactoring, and coordination with execution and testing agents.
    """
    
    def __init__(self):
        """Initialize Developing Agent with development capabilities."""
        
        instruction = """You are the Developing Agent (DA) for the ADK IDE system, 
        specialized in code generation, modification, and development workflows.

        ## Your Primary Responsibilities:
        1. **Code Generation**: Create new code based on user requirements
        2. **Code Modification**: Edit, refactor, and improve existing code
        3. **Development Workflows**: Manage complex development tasks
        4. **Quality Assurance**: Ensure code quality and best practices
        5. **Integration**: Coordinate with Code Execution Agent for testing

        ## Your Capabilities:
        - Generate code in multiple programming languages (Python, JavaScript, TypeScript, Java, C++, Go, Rust)
        - Research coding solutions and best practices using google_search
        - Delegate code execution to the Code Execution Agent
        - Apply software engineering best practices
        - Handle complex development workflows

        ## Development Guidelines:
        - Always write clean, readable, and well-documented code
        - Follow language-specific conventions and best practices
        - Include appropriate error handling and validation
        - Consider performance and security implications
        - Provide clear explanations of your code decisions

        ## Workflow Process:
        1. **Understand Requirements**: Analyze user needs and constraints
        2. **Research Solutions**: Use google_search for best practices and patterns
        3. **Generate Code**: Create high-quality code solutions
        4. **Coordinate Testing**: Work with Code Execution Agent when needed
        5. **Iterate and Improve**: Refine based on feedback and results

        ## Code Quality Standards:
        - Use meaningful variable and function names
        - Include docstrings and comments for complex logic
        - Implement proper error handling
        - Follow SOLID principles and design patterns
        - Ensure code is testable and maintainable

        When handling development requests:
        1. First understand the full scope and requirements
        2. Research relevant patterns and best practices if needed
        3. Generate clean, well-structured code
        4. Explain your approach and design decisions
        5. Suggest testing strategies or coordinate with execution agent

        Always prioritize code quality, maintainability, and user requirements."""

        super().__init__(
            name="DevelopingAgent",
            description="Specialized agent for code generation, modification, and development workflows",
            instruction=instruction,
            tools=[google_search]  # Will add AgentTool for Code Execution Agent
        )
        
        # Code Execution Agent reference
        self.code_execution_agent = None
        
        # Development state
        self.current_projects: Dict[str, Dict[str, Any]] = {}
        self.code_history: List[Dict[str, Any]] = []
        
        # Supported languages and their configurations
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "comment_style": "#",
                "best_practices": ["PEP 8", "type hints", "docstrings"]
            },
            "javascript": {
                "extension": ".js",
                "comment_style": "//",
                "best_practices": ["ES6+", "JSDoc", "error handling"]
            },
            "typescript": {
                "extension": ".ts",
                "comment_style": "//",
                "best_practices": ["strict types", "interfaces", "JSDoc"]
            },
            "java": {
                "extension": ".java",
                "comment_style": "//",
                "best_practices": ["JavaDoc", "SOLID principles", "exception handling"]
            },
            "cpp": {
                "extension": ".cpp",
                "comment_style": "//",
                "best_practices": ["RAII", "const correctness", "smart pointers"]
            },
            "go": {
                "extension": ".go",
                "comment_style": "//",
                "best_practices": ["gofmt", "error handling", "interfaces"]
            },
            "rust": {
                "extension": ".rs",
                "comment_style": "//",
                "best_practices": ["ownership", "error handling", "documentation"]
            }
        }
    
    def set_code_execution_agent(self, execution_agent) -> None:
        """
        Set Code Execution Agent reference and add as tool.
        
        Args:
            execution_agent: Code Execution Agent instance
        """
        self.code_execution_agent = execution_agent
        
        # Create AgentTool wrapper and add to tools
        execution_tool = AgentTool(execution_agent)
        self.tools.append(execution_tool)
    
    async def _run_async_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Main execution logic for Developing Agent.
        
        Args:
            request: Development request
            
        Returns:
            Development response with generated code or modifications
        """
        await self._setup_services(request.context)
        
        try:
            # Parse development request
            dev_request = await self._parse_development_request(request.prompt, request.context)
            
            # Handle based on request type
            if dev_request["type"] == "code_generation":
                response = await self._handle_code_generation(dev_request, request.context)
            elif dev_request["type"] == "code_modification":
                response = await self._handle_code_modification(dev_request, request.context)
            elif dev_request["type"] == "code_review":
                response = await self._handle_code_review(dev_request, request.context)
            elif dev_request["type"] == "refactoring":
                response = await self._handle_refactoring(dev_request, request.context)
            else:
                response = await self._handle_general_development(dev_request, request.context)
            
            # Store in development history
            await self._update_development_history(dev_request, response, request.context)
            
            return response
            
        except Exception as e:
            return AgentResponse(
                content=f"I encountered an error during development: {str(e)}. Let me try a different approach.",
                metadata={"error": str(e), "agent": self.name}
            )
        
        finally:
            await self._cleanup_services(request.context)
    
    async def _parse_development_request(
        self,
        prompt: str,
        context: InvocationContext
    ) -> Dict[str, Any]:
        """
        Parse development request to determine type and parameters.
        
        Args:
            prompt: User prompt
            context: Invocation context
            
        Returns:
            Parsed request with type and parameters
        """
        request_info = {
            "type": "general_development",
            "language": None,
            "framework": None,
            "requirements": prompt,
            "needs_execution": False,
            "complexity": "medium"
        }
        
        prompt_lower = prompt.lower()
        
        # Determine request type
        if any(keyword in prompt_lower for keyword in ["create", "generate", "write", "implement"]):
            request_info["type"] = "code_generation"
        elif any(keyword in prompt_lower for keyword in ["modify", "change", "update", "edit"]):
            request_info["type"] = "code_modification"
        elif any(keyword in prompt_lower for keyword in ["review", "check", "analyze", "evaluate"]):
            request_info["type"] = "code_review"
        elif any(keyword in prompt_lower for keyword in ["refactor", "restructure", "optimize", "improve"]):
            request_info["type"] = "refactoring"
        
        # Detect language
        for lang in self.supported_languages:
            if lang in prompt_lower:
                request_info["language"] = lang
                break
        
        # Detect if execution is needed
        if any(keyword in prompt_lower for keyword in ["test", "run", "execute", "verify"]):
            request_info["needs_execution"] = True
        
        # Detect complexity
        if any(keyword in prompt_lower for keyword in ["simple", "basic", "quick"]):
            request_info["complexity"] = "low"
        elif any(keyword in prompt_lower for keyword in ["complex", "advanced", "comprehensive"]):
            request_info["complexity"] = "high"
        
        return request_info
    
    async def _handle_code_generation(
        self,
        dev_request: Dict[str, Any],
        context: InvocationContext
    ) -> AgentResponse:
        """
        Handle code generation requests.
        
        Args:
            dev_request: Parsed development request
            context: Invocation context
            
        Returns:
            Response with generated code
        """
        language = dev_request.get("language", "python")
        requirements = dev_request["requirements"]
        
        # Research best practices if needed
        if dev_request["complexity"] == "high":
            research_query = f"{language} {requirements} best practices implementation"
            research_results = await self.research_coding_solution(
                research_query,
                language,
                context=context
            )
        
        # Generate code based on requirements
        code_content = await self._generate_code(
            requirements=requirements,
            language=language,
            context=context
        )
        
        # Test code if execution is needed and agent is available
        execution_result = None
        if dev_request["needs_execution"] and self.code_execution_agent:
            execution_result = await self._execute_code(code_content, language, context)
        
        # Prepare response
        response_content = f"I've generated {language} code for your requirements:\n\n```{language}\n{code_content}\n```"
        
        if execution_result:
            response_content += f"\n\n**Execution Result:**\n{execution_result}"
        
        # Add explanation
        response_content += f"\n\n**Code Explanation:**\n{await self._explain_code(code_content, language)}"
        
        return AgentResponse(
            content=response_content,
            metadata={
                "type": "code_generation",
                "language": language,
                "executed": execution_result is not None,
                "lines_of_code": len(code_content.splitlines())
            }
        )
    
    async def _handle_code_modification(
        self,
        dev_request: Dict[str, Any],
        context: InvocationContext
    ) -> AgentResponse:
        """
        Handle code modification requests.
        
        Args:
            dev_request: Parsed development request
            context: Invocation context
            
        Returns:
            Response with modified code
        """
        # This would integrate with artifact service to get existing code
        # For now, provide guidance on modification approach
        
        language = dev_request.get("language", "python")
        requirements = dev_request["requirements"]
        
        response_content = f"""I can help you modify your {language} code. To provide the best assistance, I need:

1. **Current Code**: The existing code you want to modify
2. **Specific Changes**: What modifications you want to make
3. **Context**: How this code fits into your larger project

**Modification Approach:**
- I'll analyze your existing code structure
- Research best practices for the requested changes
- Implement modifications while maintaining code quality
- Test changes if needed using the Code Execution Agent
- Provide clear explanations of what was changed and why

Please share your current code and I'll help you modify it according to your requirements: {requirements}"""
        
        return AgentResponse(
            content=response_content,
            metadata={
                "type": "code_modification",
                "language": language,
                "awaiting_code": True
            }
        )
    
    async def _handle_code_review(
        self,
        dev_request: Dict[str, Any],
        context: InvocationContext
    ) -> AgentResponse:
        """
        Handle code review requests.
        
        Args:
            dev_request: Parsed development request
            context: Invocation context
            
        Returns:
            Response with code review
        """
        language = dev_request.get("language", "python")
        
        response_content = f"""I'm ready to perform a comprehensive code review for your {language} code. 

**My Review Process:**
1. **Code Quality Analysis**: Check for readability, maintainability, and best practices
2. **Security Review**: Identify potential security vulnerabilities
3. **Performance Assessment**: Look for optimization opportunities
4. **Best Practices Compliance**: Ensure adherence to {language} conventions
5. **Documentation Review**: Check for adequate comments and documentation

**Review Criteria:**
- Code structure and organization
- Error handling and edge cases
- Performance and efficiency
- Security considerations
- Maintainability and readability
- Test coverage and testability

Please share the code you'd like me to review, and I'll provide detailed feedback with specific recommendations for improvement."""
        
        return AgentResponse(
            content=response_content,
            metadata={
                "type": "code_review",
                "language": language,
                "awaiting_code": True
            }
        )
    
    async def _handle_refactoring(
        self,
        dev_request: Dict[str, Any],
        context: InvocationContext
    ) -> AgentResponse:
        """
        Handle code refactoring requests.
        
        Args:
            dev_request: Parsed development request
            context: Invocation context
            
        Returns:
            Response with refactoring plan
        """
        language = dev_request.get("language", "python")
        
        response_content = f"""I'll help you refactor your {language} code to improve its structure and maintainability.

**Refactoring Approach:**
1. **Code Analysis**: Understand current structure and identify improvement areas
2. **Design Pattern Application**: Apply appropriate design patterns
3. **Code Organization**: Improve modularity and separation of concerns
4. **Performance Optimization**: Enhance efficiency where possible
5. **Maintainability Enhancement**: Make code easier to understand and modify

**Common Refactoring Techniques:**
- Extract methods/functions for better modularity
- Eliminate code duplication (DRY principle)
- Improve naming conventions
- Simplify complex conditional logic
- Apply SOLID principles
- Optimize data structures and algorithms

**Quality Assurance:**
- Maintain existing functionality (behavior preservation)
- Improve code readability and documentation
- Ensure backward compatibility where needed
- Test refactored code to verify correctness

Please share your code and specific refactoring goals, and I'll create a detailed refactoring plan with step-by-step improvements."""
        
        return AgentResponse(
            content=response_content,
            metadata={
                "type": "refactoring",
                "language": language,
                "awaiting_code": True
            }
        )
    
    async def _handle_general_development(
        self,
        dev_request: Dict[str, Any],
        context: InvocationContext
    ) -> AgentResponse:
        """
        Handle general development requests.
        
        Args:
            dev_request: Parsed development request
            context: Invocation context
            
        Returns:
            Response with development guidance
        """
        requirements = dev_request["requirements"]
        
        # Research the topic
        research_results = await self.research_solution(requirements, context)
        
        response_content = f"""I'm here to help with your development needs. Based on your request: "{requirements}"

**Research Findings:**
{research_results}

**How I Can Assist:**
- **Code Generation**: Create new code from scratch
- **Code Modification**: Edit and improve existing code
- **Code Review**: Analyze code quality and provide feedback
- **Refactoring**: Restructure code for better maintainability
- **Best Practices**: Provide guidance on coding standards
- **Testing**: Coordinate with Code Execution Agent for testing

**Supported Languages:**
{', '.join(self.supported_languages.keys())}

**Next Steps:**
Please provide more specific details about what you'd like to develop, including:
- Programming language preference
- Specific functionality requirements
- Any constraints or preferences
- Whether you need the code tested

I'll then provide tailored assistance for your development needs."""
        
        return AgentResponse(
            content=response_content,
            metadata={
                "type": "general_development",
                "research_performed": True
            }
        )
    
    async def _generate_code(
        self,
        requirements: str,
        language: str,
        context: InvocationContext
    ) -> str:
        """
        Generate code based on requirements.
        
        Args:
            requirements: Code requirements
            language: Programming language
            context: Invocation context
            
        Returns:
            Generated code
        """
        # This is a simplified code generation example
        # In a real implementation, this would use more sophisticated generation logic
        
        if language == "python":
            return f'''"""
{requirements}

This module implements the requested functionality.
"""

def main():
    """Main function implementing the requirements."""
    # TODO: Implement {requirements}
    print("Hello from generated code!")
    return True

if __name__ == "__main__":
    result = main()
    print(f"Execution result: {{result}}")'''
        
        elif language == "javascript":
            return f'''/**
 * {requirements}
 * 
 * This module implements the requested functionality.
 */

function main() {{
    // TODO: Implement {requirements}
    console.log("Hello from generated code!");
    return true;
}}

// Execute if running directly
if (require.main === module) {{
    const result = main();
    console.log(`Execution result: ${{result}}`);
}}

module.exports = {{ main }};'''
        
        else:
            return f"// {requirements}\n// TODO: Implement functionality for {language}"
    
    async def _execute_code(
        self,
        code: str,
        language: str,
        context: InvocationContext
    ) -> Optional[str]:
        """
        Execute code using Code Execution Agent.
        
        Args:
            code: Code to execute
            language: Programming language
            context: Invocation context
            
        Returns:
            Execution result or None if execution failed
        """
        if not self.code_execution_agent:
            return None
        
        try:
            execution_result = await AgentCommunication.delegate_to_agent(
                parent_agent=self,
                target_agent=self.code_execution_agent,
                task={
                    "description": f"Execute {language} code",
                    "parameters": {
                        "code": code,
                        "language": language
                    }
                },
                context=context
            )
            
            if execution_result["status"] == "success":
                return execution_result["result"]
            else:
                return f"Execution failed: {execution_result['message']}"
        
        except Exception as e:
            return f"Execution error: {str(e)}"
    
    async def _explain_code(self, code: str, language: str) -> str:
        """
        Generate explanation for code.
        
        Args:
            code: Code to explain
            language: Programming language
            
        Returns:
            Code explanation
        """
        lines = len(code.splitlines())
        lang_config = self.supported_languages.get(language, {})
        
        explanation = f"This {language} code consists of {lines} lines and follows {language} best practices"
        
        if "best_practices" in lang_config:
            practices = ", ".join(lang_config["best_practices"])
            explanation += f" including {practices}"
        
        explanation += ". The code is structured for readability and maintainability."
        
        return explanation
    
    async def _update_development_history(
        self,
        dev_request: Dict[str, Any],
        response: AgentResponse,
        context: InvocationContext
    ) -> None:
        """
        Update development history.
        
        Args:
            dev_request: Development request
            response: Generated response
            context: Invocation context
        """
        self.code_history.append({
            "timestamp": context.session.metadata.get("timestamp", ""),
            "type": dev_request["type"],
            "language": dev_request.get("language"),
            "requirements": dev_request["requirements"],
            "success": "error" not in response.metadata
        })
        
        # Store in session state
        if context.session:
            dev_state = context.session.state.setdefault("developing_agent_state", {})
            dev_state.update({
                "last_request_type": dev_request["type"],
                "last_language": dev_request.get("language"),
                "total_requests": len(self.code_history)
            })