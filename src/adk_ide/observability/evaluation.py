"""Evaluation and observability capabilities for ADK IDE."""
from typing import Any, Dict, Optional, List, Callable
import os
import json
from datetime import datetime


class OpenInferenceTracing:
    """OpenInference tracing for automated trace collection."""
    
    def __init__(self) -> None:
        self.traces: List[Dict[str, Any]] = []
        self._enabled = os.environ.get("OPENINFERENCE_ENABLED", "false").lower() == "true"
    
    def start_trace(self, trace_id: str, operation: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a new trace."""
        if not self._enabled:
            return {}
        
        trace = {
            "trace_id": trace_id,
            "operation": operation,
            "start_time": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "spans": [],
        }
        self.traces.append(trace)
        return trace
    
    def add_span(self, trace_id: str, span: Dict[str, Any]) -> None:
        """Add span to trace."""
        for trace in self.traces:
            if trace["trace_id"] == trace_id:
                trace["spans"].append(span)
                break
    
    def end_trace(self, trace_id: str, result: Optional[Any] = None) -> Dict[str, Any]:
        """End a trace."""
        for trace in self.traces:
            if trace["trace_id"] == trace_id:
                trace["end_time"] = datetime.utcnow().isoformat()
                trace["result"] = result
                return trace
        return {}
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID."""
        for trace in self.traces:
            if trace["trace_id"] == trace_id:
                return trace
        return None


class EvaluationService:
    """Evaluation service for systematic agent testing."""
    
    def __init__(self) -> None:
        self.evaluations: List[Dict[str, Any]] = []
        self.evalsets: List[Dict[str, Any]] = []
    
    def create_evalset(self, name: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an evaluation dataset."""
        evalset = {
            "name": name,
            "test_cases": test_cases,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.evalsets.append(evalset)
        return evalset
    
    def run_evaluation(
        self,
        agent_name: str,
        evalset_name: str,
        test_function: Callable,
    ) -> Dict[str, Any]:
        """Run evaluation on agent."""
        evalset = next((e for e in self.evalsets if e["name"] == evalset_name), None)
        if not evalset:
            return {"status": "error", "error": f"Evalset '{evalset_name}' not found"}
        
        results = []
        for test_case in evalset["test_cases"]:
            try:
                result = test_function(test_case)
                results.append({
                    "test_case": test_case,
                    "result": result,
                    "passed": result.get("status") == "success",
                })
            except Exception as exc:
                results.append({
                    "test_case": test_case,
                    "result": {"status": "error", "error": str(exc)},
                    "passed": False,
                })
        
        evaluation = {
            "agent_name": agent_name,
            "evalset_name": evalset_name,
            "results": results,
            "passed_count": sum(1 for r in results if r["passed"]),
            "total_count": len(results),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.evaluations.append(evaluation)
        return evaluation
    
    def get_trajectory(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trajectory analysis for a trace."""
        # This would analyze the trace to extract step-by-step reasoning
        return {
            "trace_id": trace_id,
            "steps": [],
            "reasoning_path": [],
        }


class TrajectoryAnalysis:
    """Trajectory analysis for step-by-step reasoning visualization."""
    
    def __init__(self, tracing: OpenInferenceTracing) -> None:
        self.tracing = tracing
    
    def analyze(self, trace_id: str) -> Dict[str, Any]:
        """Analyze trajectory from trace."""
        trace = self.tracing.get_trace(trace_id)
        if not trace:
            return {"status": "error", "error": "Trace not found"}
        
        steps = []
        for span in trace.get("spans", []):
            steps.append({
                "step": len(steps) + 1,
                "operation": span.get("operation", ""),
                "input": span.get("input", {}),
                "output": span.get("output", {}),
                "duration": span.get("duration", 0),
            })
        
        return {
            "trace_id": trace_id,
            "steps": steps,
            "total_steps": len(steps),
            "reasoning_path": [s["operation"] for s in steps],
        }

