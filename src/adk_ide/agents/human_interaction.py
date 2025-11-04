"""
Human Interaction Agent (HIA)

Central orchestrator and primary user interface for the ADK IDE system.
Handles user requests, delegates to specialized agents, and coordinates workflows.
"""

from typing import Dict, Any, Optional, List
from google.adk.core import AgentRequest, AgentResponse, InvocationContext
from google.adk.tools import google_search, AgentTool

from .base import ADKIDEAgent, AgentCommunication
from ..config import get_settings


class HumanInteractionAgent(ADKIDEAgent):
    """
    Human Interaction Agent - Central orchestrator for the ADK IDE system.
    
    Serves as the primary interface between users and the multi-agent system,
    coordinating tasks and managing the overall development workflow.
    """
    
    def __init__(self):
        """Initialize Human Interaction Agent with coordination capabilities."""
        
        instruction = """You are the Human Interaction Agent (HIA) for the ADK IDE system, 
        a sophisticated AI-powered development environment. Your role is to:

        1. **Central Orchestration**: Receive and interpret user development requests
        2. **Task Delegation**: Delegate complex tasks to specialized agents
        3. **Workflow Coordination**: Manage multi-agent workflows and ensure coherent results
        4. **User Communication**: Provide clear, helpful responses and status updates

        ## Available Specialized Agents:
        - **Developing Agent**: Code generation, modification, and development workflows
        - **Code Execution Agent**: Secure code execution and testing
        - **Debug Agent**: Debugging assistance and error analysis
        - **IDE Component Agents**: Code editing, navigation, and organization

        ## Your Capabilities:
        - Research development topics and solutions using google_search
        - Delegate tasks to appropriate specialized agents
        - Coordinate multi-step development workflows
        - Provide comprehensive development assistance

        ## Guidelines:
        - Always understand the user's intent before delegating
        - Choose the most appropriate agent for each task
        - Provide clear explanations of what you're doing
        - Coordinate between agents when tasks require multiple specializations
        - Maintain context and continuity across interactions

        When users request development assistance, analyze their needs and either:
        1. Handle simple queries directly with research
        2. Delegate to appropriate specialized agents
        3. Coordinate multi-agent workflows for complex tasks

        Always be helpful, clear, and focused on enabling productive development."""

        super().__init__(
            name="HumanInteractionAgent",
            description="Central orchestrator for development tasks and user interaction",
            instruction=instruction,
            tools=[google_search]  # Will add AgentTools for sub-agents
        )
        
        # Sub-agent references (will be set during system initialization)
        self.developing_agent = None
        self.code_execution_agent = None
        self.debug_agent = None
        
        # Coordination state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.delegation_history: List[Dict[str, Any]] = []
    
    def add_sub_agent(self, agent: ADKIDEAgent, agent_type: str) -> None:
        """
        Add a sub-agent and create AgentTool wrapper.
        
        Args:
            agent: Sub-agent to add
            agent_type: Type of agent (developing, execution, debug, etc.)
        """
        # Store agent reference
        setattr(self, f"{agent_type}_agent", agent)
        
        # Create AgentTool wrapper and add to tools
        agent_tool = AgentTool(agent)
        self.tools.append(agent_tool)
    
    async def _run_async_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Main execution logic for Human Interaction Agent.
        
        Args:
            request: User request
            
        Returns:
            Agent response with coordination results
        """
        await self._setup_services(request.context)
        
        try:
            # Analyze user request
            analysis = await self._analyze_user_request(request.prompt, request.context)
            
            # Handle based on analysis
            if analysis["complexity"] == "simple":
                response = await self._handle_simple_request(request, analysis)
            elif analysis["complexity"] == "moderate":
                response = await self._handle_moderate_request(request, analysis)
            else:
                response = await self._handle_complex_request(request, analysis)
            
            # Update coordination state
            await self._update_coordination_state(request, response, request.context)
            
            return response
            
        except Exception as e:
            return AgentResponse(
                content=f"I encountered an error while processing your request: {str(e)}. Let me try a different approach.",
                metadata={"error": str(e), "agent": self.name}
            )
        
        finally:
            await self._cleanup_services(request.context)
    
    async def _analyze_user_request(
        self,
        prompt: str,
        context: InvocationContext
    ) -> Dict[str, Any]:
        """
        Analyze user request to determine appropriate handling strategy.
        
        Args:
            prompt: User prompt
            context: Invocation context
            
        Returns:
            Analysis results with complexity and required agents
        """
        # Simple keyword-based analysis (could be enhanced with LLM analysis)
        analysis = {
            "complexity": "simple",
            "required_agents": [],
            "task_type": "general",
            "needs_research": False,
            "needs_execution": False
        }
        
        prompt_lower = prompt.lower()
        
        # Determine complexity and required agents
        if any(keyword in prompt_lower for keyword in ["create", "generate", "write", "implement"]):
            analysis["complexity"] = "moderate"
            analysis["required_agents"].append("developing")
            analysis["task_type"] = "development"
        
        if any(keyword in prompt_lower for keyword in ["run", "execute", "test", "compile"]):
            analysis["needs_execution"] = True
            analysis["required_agents"].append("execution")
        
        if any(keyword in prompt_lower for keyword in ["debug", "error", "fix", "troubleshoot"]):
            analysis["required_agents"].append("debug")
            analysis["task_type"] = "debugging"
        
        if any(keyword in prompt_lower for keyword in ["research", "find", "learn", "how to"]):
            analysis["needs_research"] = True
        
        # Complex tasks require multiple agents or workflows
        if len(analysis["required_agents"]) > 1:
            analysis["complexity"] = "complex"
        
        return analysis
    
    async def _handle_simple_request(
        self,
        request: AgentRequest,
        analysis: Dict[str, Any]
    ) -> AgentResponse:
        """
        Handle simple requests that can be answered directly.
        
        Args:
            request: User request
            analysis: Request analysis
            
        Returns:
            Direct response
        """
        if analysis["needs_research"]:
            # Research the topic
            research_results = await self.research_solution(
                request.prompt,
                request.context
            )
            
            return AgentResponse(
                content=f"Based on my research:\n\n{research_results}",
                metadata={"handled_by": "HIA", "research_performed": True}
            )
        
        # Provide general guidance
        return AgentResponse(
            content="I'm here to help with your development needs. I can assist with code generation, debugging, research, and coordinating complex development tasks. What would you like to work on?",
            metadata={"handled_by": "HIA", "type": "guidance"}
        )
    
    async def _handle_moderate_request(
        self,
        request: AgentRequest,
        analysis: Dict[str, Any]
    ) -> AgentResponse:
        """
        Handle moderate complexity requests requiring single agent delegation.
        
        Args:
            request: User request
            analysis: Request analysis
            
        Returns:
            Delegated response
        """
        if "developing" in analysis["required_agents"] and self.developing_agent:
            # Delegate to Developing Agent
            delegation_result = await AgentCommunication.delegate_to_agent(
                parent_agent=self,
                target_agent=self.developing_agent,
                task={
                    "description": request.prompt,
                    "parameters": {
                        "task_type": analysis["task_type"],
                        "needs_execution": analysis["needs_execution"]
                    }
                },
                context=request.context
            )
            
            if delegation_result["status"] == "success":
                return AgentResponse(
                    content=f"I've worked with the Developing Agent to handle your request:\n\n{delegation_result['result']}",
                    metadata={
                        "handled_by": "HIA + DevelopingAgent",
                        "delegation_id": delegation_result["delegation_id"]
                    }
                )
            else:
                return AgentResponse(
                    content=f"I encountered an issue delegating to the Developing Agent: {delegation_result['message']}",
                    metadata={"error": delegation_result["message"]}
                )
        
        # Fallback to research if no appropriate agent
        research_results = await self.research_solution(request.prompt, request.context)
        return AgentResponse(
            content=f"I researched your request and found:\n\n{research_results}",
            metadata={"handled_by": "HIA", "fallback_research": True}
        )
    
    async def _handle_complex_request(
        self,
        request: AgentRequest,
        analysis: Dict[str, Any]
    ) -> AgentResponse:
        """
        Handle complex requests requiring multi-agent coordination.
        
        Args:
            request: User request
            analysis: Request analysis
            
        Returns:
            Coordinated multi-agent response
        """
        workflow_id = f"workflow_{len(self.active_workflows)}"
        workflow = {
            "id": workflow_id,
            "request": request.prompt,
            "required_agents": analysis["required_agents"],
            "steps": [],
            "results": {}
        }
        
        self.active_workflows[workflow_id] = workflow
        
        try:
            # Execute workflow steps
            if "developing" in analysis["required_agents"] and self.developing_agent:
                # Step 1: Code development
                dev_result = await AgentCommunication.delegate_to_agent(
                    parent_agent=self,
                    target_agent=self.developing_agent,
                    task={
                        "description": f"Development task: {request.prompt}",
                        "parameters": {"workflow_id": workflow_id}
                    },
                    context=request.context
                )
                
                workflow["steps"].append("development")
                workflow["results"]["development"] = dev_result
            
            if "execution" in analysis["required_agents"] and self.code_execution_agent:
                # Step 2: Code execution (if needed)
                exec_result = await AgentCommunication.delegate_to_agent(
                    parent_agent=self,
                    target_agent=self.code_execution_agent,
                    task={
                        "description": f"Execute code from workflow {workflow_id}",
                        "parameters": {"workflow_id": workflow_id}
                    },
                    context=request.context
                )
                
                workflow["steps"].append("execution")
                workflow["results"]["execution"] = exec_result
            
            # Compile results
            response_parts = []
            for step in workflow["steps"]:
                result = workflow["results"][step]
                if result["status"] == "success":
                    response_parts.append(f"**{step.title()}**: {result['result']}")
                else:
                    response_parts.append(f"**{step.title()}**: Error - {result['message']}")
            
            final_response = "I've coordinated multiple agents to handle your complex request:\n\n" + "\n\n".join(response_parts)
            
            return AgentResponse(
                content=final_response,
                metadata={
                    "handled_by": "HIA + MultiAgent",
                    "workflow_id": workflow_id,
                    "agents_used": analysis["required_agents"]
                }
            )
            
        except Exception as e:
            return AgentResponse(
                content=f"I encountered an error during the multi-agent workflow: {str(e)}",
                metadata={"workflow_error": str(e), "workflow_id": workflow_id}
            )
        
        finally:
            # Clean up workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def _update_coordination_state(
        self,
        request: AgentRequest,
        response: AgentResponse,
        context: InvocationContext
    ) -> None:
        """
        Update coordination state and history.
        
        Args:
            request: Original request
            response: Generated response
            context: Invocation context
        """
        # Update delegation history
        self.delegation_history.append({
            "timestamp": context.session.metadata.get("timestamp", ""),
            "request": request.prompt,
            "response_type": response.metadata.get("handled_by", "unknown"),
            "success": "error" not in response.metadata
        })
        
        # Store in session state
        if context.session:
            coordination_state = context.session.state.setdefault("hia_coordination", {})
            coordination_state.update({
                "last_request": request.prompt,
                "last_response_type": response.metadata.get("handled_by", "unknown"),
                "active_workflows": len(self.active_workflows),
                "total_delegations": len(self.delegation_history)
            })
    
    async def get_system_status(self, context: InvocationContext) -> Dict[str, Any]:
        """
        Get current system status and agent availability.
        
        Args:
            context: Invocation context
            
        Returns:
            System status information
        """
        status = {
            "hia_status": "active",
            "available_agents": [],
            "active_workflows": len(self.active_workflows),
            "total_delegations": len(self.delegation_history)
        }
        
        # Check agent availability
        if self.developing_agent:
            status["available_agents"].append("developing")
        if self.code_execution_agent:
            status["available_agents"].append("execution")
        if self.debug_agent:
            status["available_agents"].append("debug")
        
        return status