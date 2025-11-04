"""Workflow orchestration agents: LoopAgent, SequentialAgent, ParallelAgent."""
from typing import Any, Dict, List, Optional, Callable
import os
import asyncio

from .base import ADKIDEAgent


class LoopAgent(ADKIDEAgent):
    """Iterative refinement agent using ADK LoopAgent pattern.
    
    Executes sub-agents repeatedly until termination conditions are met.
    """

    def __init__(self, sub_agents: List[ADKIDEAgent], max_iterations: int = 5) -> None:
        super().__init__(name="loop_agent", description="Iterative refinement orchestrator")
        self.sub_agents = sub_agents
        self.max_iterations = max_iterations
        self._adk_loop_agent: Optional[object] = None
        self._adk_loop_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LoopAgent as ADKLoopAgent  # type: ignore

                # Convert our sub-agents to ADK agents if they're ADK-enabled
                adk_sub_agents = []
                for agent in sub_agents:
                    if hasattr(agent, "_llm_agent") and agent._llm_agent is not None:
                        adk_sub_agents.append(agent._llm_agent)
                    else:
                        # Wrap in a simple adapter
                        class AdapterAgent:
                            def __init__(self, base_agent: ADKIDEAgent):
                                self.name = base_agent.name
                                self.description = base_agent.description
                                self._base = base_agent

                            async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
                                return await self._base.run(request)

                        adk_sub_agents.append(AdapterAgent(agent))

                if adk_sub_agents:
                    self._adk_loop_agent = ADKLoopAgent(
                        name="LoopAgent",
                        description="Iterative refinement workflow",
                        sub_agents=adk_sub_agents,
                        max_iterations=max_iterations,
                    )
                    run_method = getattr(self._adk_loop_agent, "run", None)
                    run_async_method = getattr(self._adk_loop_agent, "run_async", None)
                    if run_async_method is not None:
                        self._adk_loop_run = run_async_method
                    elif run_method is not None:
                        self._adk_loop_run = run_method
            except Exception:
                self._adk_loop_agent = None
                self._adk_loop_run = None

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute loop pattern with sub-agents."""
        if self._adk_loop_agent is not None and self._adk_loop_run is not None:  # pragma: no cover
            try:
                result = self._adk_loop_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "result": result, "iterations": self.max_iterations}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: manual loop execution
        iteration_count = 0
        current_request = request
        results = []

        while iteration_count < self.max_iterations:
            iteration_count += 1
            for agent in self.sub_agents:
                result = await agent.run(current_request)
                results.append({"iteration": iteration_count, "agent": agent.name, "result": result})
                
                # Check for termination signal (escalate flag)
                if result.get("escalate") is True or result.get("terminate") is True:
                    return {
                        "status": "completed",
                        "agent": self.name,
                        "iterations": iteration_count,
                        "results": results,
                        "termination_reason": "escalate_signal",
                    }
                
                # Update request with result for next iteration
                current_request = {**current_request, "previous_result": result}

        return {
            "status": "completed",
            "agent": self.name,
            "iterations": iteration_count,
            "results": results,
            "termination_reason": "max_iterations_reached",
        }


class SequentialAgent(ADKIDEAgent):
    """Deterministic sequential execution agent using ADK SequentialAgent pattern."""

    def __init__(self, sub_agents: List[ADKIDEAgent]) -> None:
        super().__init__(name="sequential_agent", description="Sequential pipeline orchestrator")
        self.sub_agents = sub_agents
        self._adk_seq_agent: Optional[object] = None
        self._adk_seq_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import SequentialAgent as ADKSequentialAgent  # type: ignore

                adk_sub_agents = []
                for agent in sub_agents:
                    if hasattr(agent, "_llm_agent") and agent._llm_agent is not None:
                        adk_sub_agents.append(agent._llm_agent)
                    else:
                        class AdapterAgent:
                            def __init__(self, base_agent: ADKIDEAgent):
                                self.name = base_agent.name
                                self.description = base_agent.description
                                self._base = base_agent

                            async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
                                return await self._base.run(request)

                        adk_sub_agents.append(AdapterAgent(agent))

                if adk_sub_agents:
                    self._adk_seq_agent = ADKSequentialAgent(
                        name="SequentialAgent",
                        description="Deterministic sequential workflow",
                        sub_agents=adk_sub_agents,
                    )
                    run_method = getattr(self._adk_seq_agent, "run", None)
                    run_async_method = getattr(self._adk_seq_agent, "run_async", None)
                    if run_async_method is not None:
                        self._adk_seq_run = run_async_method
                    elif run_method is not None:
                        self._adk_seq_run = run_method
            except Exception:
                self._adk_seq_agent = None
                self._adk_seq_run = None

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents sequentially, passing state between them."""
        if self._adk_seq_agent is not None and self._adk_seq_run is not None:  # pragma: no cover
            try:
                result = self._adk_seq_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: manual sequential execution
        current_request = request
        results = []

        for agent in self.sub_agents:
            result = await agent.run(current_request)
            results.append({"agent": agent.name, "result": result})
            
            # If an agent fails, stop the pipeline
            if result.get("status") == "error":
                return {
                    "status": "error",
                    "agent": self.name,
                    "failed_at": agent.name,
                    "results": results,
                }
            
            # Pass result to next agent via state
            current_request = {**current_request, "previous_result": result, "state": result.get("state", {})}

        return {"status": "success", "agent": self.name, "results": results}


class ParallelAgent(ADKIDEAgent):
    """Concurrent execution agent using ADK ParallelAgent pattern."""

    def __init__(self, sub_agents: List[ADKIDEAgent]) -> None:
        super().__init__(name="parallel_agent", description="Parallel execution orchestrator")
        self.sub_agents = sub_agents
        self._adk_parallel_agent: Optional[object] = None
        self._adk_parallel_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import ParallelAgent as ADKParallelAgent  # type: ignore

                adk_sub_agents = []
                for agent in sub_agents:
                    if hasattr(agent, "_llm_agent") and agent._llm_agent is not None:
                        adk_sub_agents.append(agent._llm_agent)
                    else:
                        class AdapterAgent:
                            def __init__(self, base_agent: ADKIDEAgent):
                                self.name = base_agent.name
                                self.description = base_agent.description
                                self._base = base_agent

                            async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
                                return await self._base.run(request)

                        adk_sub_agents.append(AdapterAgent(agent))

                if adk_sub_agents:
                    self._adk_parallel_agent = ADKParallelAgent(
                        name="ParallelAgent",
                        description="Concurrent execution workflow",
                        sub_agents=adk_sub_agents,
                    )
                    run_method = getattr(self._adk_parallel_agent, "run", None)
                    run_async_method = getattr(self._adk_parallel_agent, "run_async", None)
                    if run_async_method is not None:
                        self._adk_parallel_run = run_async_method
                    elif run_method is not None:
                        self._adk_parallel_run = run_method
            except Exception:
                self._adk_parallel_agent = None
                self._adk_parallel_run = None

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents in parallel."""
        if self._adk_parallel_agent is not None and self._adk_parallel_run is not None:  # pragma: no cover
            try:
                result = self._adk_parallel_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: manual parallel execution using asyncio
        tasks = [agent.run(request) for agent in self.sub_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for agent, result in zip(self.sub_agents, results):
            if isinstance(result, Exception):
                processed_results.append({"agent": agent.name, "status": "error", "error": str(result)})
            else:
                processed_results.append({"agent": agent.name, "result": result})

        return {"status": "success", "agent": self.name, "results": processed_results}

