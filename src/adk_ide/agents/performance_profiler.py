"""Performance Profiler Agent for runtime analysis and bottleneck identification."""
from typing import Any, Dict, Optional, Callable, List
import os
import time
import cProfile
import pstats
import io
from contextlib import contextmanager

from .base import ADKIDEAgent
from .cea import CodeExecutionAgent


class PerformanceProfilerAgent(ADKIDEAgent):
    """Performance profiler agent with bottleneck identification and optimization recommendations.
    
    Integrates with CodeExecutionAgent to profile running code and identify performance bottlenecks.
    """

    def __init__(self, code_executor: Optional[CodeExecutionAgent] = None) -> None:
        super().__init__(
            name="performance_profiler_agent",
            description="Runtime analysis, bottleneck identification, and optimization recommendations"
        )
        self.code_executor = code_executor
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None
        self.profile_results: Dict[str, Any] = {}

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                tools = []
                if code_executor:
                    try:
                        class ProfilerTool:
                            name = "profile_code"
                            description = "Profile code execution to identify performance bottlenecks"

                            async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                                return await self._parent._profile_code(payload)

                        profiler_tool = ProfilerTool()
                        profiler_tool._parent = self
                        tools.append(profiler_tool)
                    except Exception:
                        pass

                self._llm_agent = LlmAgent(
                    name="PerformanceProfilerAgent",
                    description="Runtime analysis, bottleneck identification, and optimization recommendations. Use profile_code tool to analyze code performance.",
                    tools=tools if tools else None,  # type: ignore[arg-type]
                    instruction="You are a performance profiling specialist. Analyze code execution to identify bottlenecks, memory leaks, CPU-intensive operations, and provide optimization recommendations. Use the profile_code tool to gather performance metrics.",
                    output_key="performance_analysis",  # Save analysis to session.state
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

    async def _profile_code(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Profile code execution and return performance metrics."""
        code = payload.get("code", "")
        if not code:
            return {"error": "No code provided for profiling"}

        try:
            # Use cProfile for Python code profiling
            profiler = cProfile.Profile()
            profiler.enable()
            
            # Execute code via code executor
            start_time = time.time()
            execution_result = None
            if self.code_executor:
                execution_result = await self.code_executor.run({"code": code})
            else:
                # Fallback: direct execution (limited security)
                exec_globals = {}
                exec(code, exec_globals)
                execution_result = {"status": "success", "result": "Executed"}
            
            profiler.disable()
            end_time = time.time()
            
            # Extract profiling statistics
            stats_stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
            stats_output = stats_stream.getvalue()
            
            # Analyze for bottlenecks
            bottlenecks = self._identify_bottlenecks(stats)
            
            execution_time = end_time - start_time
            
            profile_id = f"profile_{int(time.time())}"
            self.profile_results[profile_id] = {
                "execution_time": execution_time,
                "stats": stats_output,
                "bottlenecks": bottlenecks,
                "execution_result": execution_result,
            }
            
            return {
                "status": "success",
                "profile_id": profile_id,
                "execution_time_seconds": execution_time,
                "bottlenecks": bottlenecks,
                "top_functions": self._extract_top_functions(stats_output),
                "stats_summary": stats_output[:1000],  # First 1000 chars
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def _identify_bottlenecks(self, stats: pstats.Stats) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks from profiling stats."""
        bottlenecks = []
        
        # Get top time-consuming functions
        stats.sort_stats('cumulative')
        
        # Analyze stats for common bottlenecks
        total_time = sum(stat[3] for stat in stats.stats.values())  # cumulative time is index 3
        
        for func_name, stat_tuple in stats.stats.items():
            # stat_tuple format: (call_count, primitive_call_count, total_time, cumulative_time, callers)
            if len(stat_tuple) >= 4:
                cumulative_time = stat_tuple[3]
                call_count = stat_tuple[0]
                
                if total_time > 0 and cumulative_time > total_time * 0.1:  # More than 10% of total time
                    bottlenecks.append({
                        "function": f"{func_name[0]}:{func_name[1]}({func_name[2]})",
                        "cumulative_time": cumulative_time,
                        "percentage": (cumulative_time / total_time * 100) if total_time > 0 else 0,
                        "call_count": call_count,
                        "type": "high_cpu" if cumulative_time > total_time * 0.2 else "moderate",
                    })
        
        # Sort by cumulative time and return top 5
        bottlenecks.sort(key=lambda x: x["cumulative_time"], reverse=True)
        return bottlenecks[:5]

    def _extract_top_functions(self, stats_output: str) -> List[Dict[str, Any]]:
        """Extract top functions from stats output."""
        lines = stats_output.split("\n")
        top_functions = []
        
        for line in lines[5:15]:  # Skip header, get top 10
            if line.strip() and "ncalls" not in line:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        top_functions.append({
                            "ncalls": parts[0],
                            "tottime": parts[1],
                            "percall": parts[2],
                            "cumtime": parts[3],
                            "function": " ".join(parts[4:]) if len(parts) > 4 else "",
                        })
                    except (ValueError, IndexError):
                        continue
        
        return top_functions

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance profiling requests."""
        action = request.get("action", "analyze")
        code = request.get("code", "")
        
        if action == "profile" and code:
            # Direct profiling request
            profile_result = await self._profile_code({"code": code})
            return {
                "status": "success",
                "agent": self.name,
                "profile_result": profile_result,
            }
        
        if action == "get_profile" and request.get("profile_id"):
            # Retrieve previous profile result
            profile_id = request.get("profile_id")
            if profile_id in self.profile_results:
                return {
                    "status": "success",
                    "agent": self.name,
                    "profile": self.profile_results[profile_id],
                }
            return {"status": "error", "error": f"Profile {profile_id} not found"}
        
        # Use LLM agent for analysis
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: basic analysis
        if code:
            # Simple heuristics for performance issues
            warnings = []
            if "for " in code and "range(" in code and code.count("for ") > 3:
                warnings.append("Multiple nested loops detected - potential O(n²) or worse complexity")
            if "time.sleep" in code:
                warnings.append("Blocking sleep detected - consider async alternatives")
            if code.count("import ") > 10:
                warnings.append("Many imports detected - check for unused imports")
            
            return {
                "status": "success",
                "agent": self.name,
                "warnings": warnings,
                "recommendations": [
                    "Profile code execution to identify bottlenecks",
                    "Consider caching for repeated computations",
                    "Use async/await for I/O operations",
                ],
            }
        
        return {"status": "received", "agent": self.name, "request": request}

