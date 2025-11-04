"""
Base Agent Classes and Communication Framework

Provides foundational classes for all ADK IDE agents with common functionality,
standardized communication protocols, and lifecycle management.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Type
from abc import ABC, abstractmethod

from google.adk.agents import BaseAgent, LlmAgent, AgentTool
from google.adk.core import AgentRequest, AgentResponse, InvocationContext
from google.adk.services import SessionService, ArtifactService, MemoryService
from google.adk.tools import google_search

from ..config import get_settings
from ..services import get_session_service, get_artifact_service, get_memory_service


class ADKIDEAgent(LlmAgent):
    """
    Base class for all ADK IDE agents with common functionality.
    
    Provides standardized initialization, service access, lifecycle management,
    and error handling for all agents in the system.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        instruction: str,
        tools: Optional[List] = None,
        **kwargs
    ):
        """
        Initialize ADK IDE agent with common configuration.
        
        Args:
            name: Agent name
            description: Agent description for delegation
            instruction: Agent instruction prompt
            tools: List of tools available to agent
            **kwargs: Additional LlmAgent parameters
        """
        settings = get_settings()
        
        # Initialize tools with google_search by default
        if tools is None:
            tools = []
        
        # Add google_search to all agents for research capabilities
        if google_search not in tools:
            tools.append(google_search)
        
        # Set default model and configuration
        kwargs.setdefault("model", settings.adk_model)
        kwargs.setdefault("generate_content_config", {
            "temperature": 0.1,
            "max_output_tokens": 8192
        })
        
        super().__init__(
            name=name,
            description=description,
            instruction=instruction,
            tools=tools,
            **kwargs
        )
        
        # Service references (initialized during execution)
        self.session_service: Optional[SessionService] = None
        self.artifact_service: Optional[ArtifactService] = None
        self.memory_service: Optional[MemoryService] = None
        
        # Agent metadata
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.execution_count = 0
        
    async def _setup_services(self, context: InvocationContext) -> None:
        """
        Set up service references from invocation context.
        
        Args:
            context: Invocation context containing services
        """
        self.session_service = get_session_service()
        self.artifact_service = get_artifact_service()
        self.memory_service = get_memory_service()
        
        # Store agent metadata in session state
        if context.session:
            agent_state = context.session.state.setdefault(f"{self.name}_metadata", {})
            agent_state.update({
                "agent_id": self.agent_id,
                "last_execution": datetime.utcnow().isoformat(),
                "execution_count": self.execution_count + 1
            })
    
    async def _cleanup_services(self, context: InvocationContext) -> None:
        """
        Clean up service references after execution.
        
        Args:
            context: Invocation context
        """
        self.execution_count += 1
        
        # Update execution metadata
        if context.session:
            agent_state = context.session.state.get(f"{self.name}_metadata", {})
            agent_state["execution_count"] = self.execution_count
            agent_state["last_cleanup"] = datetime.utcnow().isoformat()
    
    async def research_solution(self, problem: str, context: InvocationContext) -> str:
        """
        Research solutions for development problems using google_search.
        
        Args:
            problem: Problem description to research
            context: Invocation context
            
        Returns:
            Research results and recommendations
        """
        try:
            # Construct research query
            search_query = f"programming solution {problem} best practices"
            
            # Execute search
            search_results = await self._execute_tool(
                "google_search",
                {"query": search_query, "num_results": 5},
                context
            )
            
            # Analyze and summarize results
            if search_results and "results" in search_results:
                summaries = []
                for result in search_results["results"][:3]:  # Top 3 results
                    summaries.append(f"- {result.get('title', 'Unknown')}: {result.get('snippet', 'No description')}")
                
                return f"Research findings for '{problem}':\n" + "\n".join(summaries)
            
            return f"No specific research results found for: {problem}"
            
        except Exception as e:
            return f"Research failed for '{problem}': {str(e)}"
    
    async def _execute_tool(self, tool_name: str, args: Dict[str, Any], context: InvocationContext) -> Dict[str, Any]:
        """
        Execute a tool with error handling and logging.
        
        Args:
            tool_name: Name of tool to execute
            args: Tool arguments
            context: Invocation context
            
        Returns:
            Tool execution result
        """
        try:
            # Find tool by name
            tool = None
            for t in self.tools:
                if hasattr(t, 'name') and t.name == tool_name:
                    tool = t
                    break
            
            if not tool:
                return {"status": "error", "message": f"Tool '{tool_name}' not found"}
            
            # Execute tool
            result = await tool.execute(args, context)
            
            # Log successful execution
            if context.session:
                tool_log = context.session.state.setdefault("tool_executions", [])
                tool_log.append({
                    "agent": self.name,
                    "tool": tool_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success"
                })
            
            return result
            
        except Exception as e:
            # Log failed execution
            if context.session:
                tool_log = context.session.state.setdefault("tool_executions", [])
                tool_log.append({
                    "agent": self.name,
                    "tool": tool_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "error",
                    "error": str(e)
                })
            
            return {"status": "error", "message": str(e)}


class AgentCommunication:
    """
    Standardized communication protocol between agents.
    
    Handles agent delegation, result passing, and state management
    for multi-agent workflows.
    """
    
    @staticmethod
    async def delegate_to_agent(
        parent_agent: BaseAgent,
        target_agent: BaseAgent,
        task: Dict[str, Any],
        context: InvocationContext
    ) -> Dict[str, Any]:
        """
        Delegate task to specialized agent via AgentTool.
        
        Args:
            parent_agent: Agent making the delegation
            target_agent: Agent receiving the task
            task: Task description and parameters
            context: Invocation context
            
        Returns:
            Task execution result
        """
        try:
            # Create AgentTool wrapper for target agent
            agent_tool = AgentTool(target_agent)
            
            # Prepare delegation request
            delegation_request = {
                "task_description": task.get("description", ""),
                "task_parameters": task.get("parameters", {}),
                "parent_agent": parent_agent.name,
                "delegation_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Execute delegation
            result = await agent_tool.execute(delegation_request, context)
            
            # Store result in session state for continuity
            if context.session:
                delegation_key = f"{target_agent.name}_result"
                context.session.state[delegation_key] = {
                    "result": result,
                    "delegation_id": delegation_request["delegation_id"],
                    "completed_at": datetime.utcnow().isoformat()
                }
                
                # Update delegation history
                delegation_history = context.session.state.setdefault("delegations", [])
                delegation_history.append({
                    "from": parent_agent.name,
                    "to": target_agent.name,
                    "task": task.get("description", ""),
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "status": "success",
                "result": result,
                "delegation_id": delegation_request["delegation_id"],
                "target_agent": target_agent.name
            }
            
        except Exception as e:
            # Log delegation failure
            if context.session:
                delegation_history = context.session.state.setdefault("delegations", [])
                delegation_history.append({
                    "from": parent_agent.name,
                    "to": target_agent.name,
                    "task": task.get("description", ""),
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "status": "error",
                "message": f"Delegation to {target_agent.name} failed: {str(e)}",
                "target_agent": target_agent.name
            }
    
    @staticmethod
    async def transfer_to_agent(
        source_agent: BaseAgent,
        target_agent: BaseAgent,
        context: InvocationContext,
        transfer_reason: str = "Complex task delegation"
    ) -> Dict[str, Any]:
        """
        Transfer conversation control to another agent.
        
        Args:
            source_agent: Agent transferring control
            target_agent: Agent receiving control
            context: Invocation context
            transfer_reason: Reason for transfer
            
        Returns:
            Transfer confirmation
        """
        try:
            # Record transfer in session state
            if context.session:
                transfer_log = context.session.state.setdefault("transfers", [])
                transfer_log.append({
                    "from": source_agent.name,
                    "to": target_agent.name,
                    "reason": transfer_reason,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Set active agent
                context.session.state["active_agent"] = target_agent.name
            
            return {
                "status": "transferred",
                "from_agent": source_agent.name,
                "to_agent": target_agent.name,
                "reason": transfer_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "transfer_failed",
                "error": str(e),
                "from_agent": source_agent.name,
                "to_agent": target_agent.name
            }
    
    @staticmethod
    def get_agent_state(agent_name: str, context: InvocationContext) -> Dict[str, Any]:
        """
        Get agent state from session.
        
        Args:
            agent_name: Name of agent
            context: Invocation context
            
        Returns:
            Agent state dictionary
        """
        if not context.session:
            return {}
        
        return context.session.state.get(f"{agent_name}_state", {})
    
    @staticmethod
    def set_agent_state(
        agent_name: str,
        state: Dict[str, Any],
        context: InvocationContext
    ) -> None:
        """
        Set agent state in session.
        
        Args:
            agent_name: Name of agent
            state: State dictionary to store
            context: Invocation context
        """
        if context.session:
            context.session.state[f"{agent_name}_state"] = state
    
    @staticmethod
    def get_delegation_history(context: InvocationContext) -> List[Dict[str, Any]]:
        """
        Get delegation history from session.
        
        Args:
            context: Invocation context
            
        Returns:
            List of delegation records
        """
        if not context.session:
            return []
        
        return context.session.state.get("delegations", [])


class ResearchEnabledAgent(ADKIDEAgent):
    """
    Base class for agents with enhanced research capabilities.
    
    Provides specialized research methods for development-related queries
    and solution discovery.
    """
    
    async def research_coding_solution(
        self,
        problem: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        context: Optional[InvocationContext] = None
    ) -> str:
        """
        Research coding solutions with language and framework context.
        
        Args:
            problem: Coding problem to research
            language: Programming language context
            framework: Framework context
            context: Invocation context
            
        Returns:
            Research results with coding solutions
        """
        # Build specific search query
        query_parts = ["programming", problem]
        
        if language:
            query_parts.append(language)
        if framework:
            query_parts.append(framework)
        
        query_parts.extend(["best practices", "solution", "example"])
        search_query = " ".join(query_parts)
        
        return await self.research_solution(search_query, context)
    
    async def research_error_solution(
        self,
        error_message: str,
        context: Optional[InvocationContext] = None
    ) -> str:
        """
        Research solutions for specific error messages.
        
        Args:
            error_message: Error message to research
            context: Invocation context
            
        Returns:
            Error resolution suggestions
        """
        search_query = f"fix error {error_message} solution programming"
        return await self.research_solution(search_query, context)
    
    async def research_best_practices(
        self,
        topic: str,
        language: Optional[str] = None,
        context: Optional[InvocationContext] = None
    ) -> str:
        """
        Research best practices for development topics.
        
        Args:
            topic: Development topic
            language: Programming language context
            context: Invocation context
            
        Returns:
            Best practices research results
        """
        query_parts = [topic, "best practices", "programming"]
        
        if language:
            query_parts.append(language)
        
        search_query = " ".join(query_parts)
        return await self.research_solution(search_query, context)