"""Enterprise agents for collaboration, security, and compliance."""
from typing import Any, Dict, Optional, Callable, List
import os
import re
from datetime import datetime

from .base import ADKIDEAgent


class MultiDeveloperAgent(ADKIDEAgent):
    """Multi-developer agent for simultaneous editing with conflict resolution."""

    def __init__(self) -> None:
        super().__init__(
            name="multi_developer_agent",
            description="Simultaneous editing with conflict resolution and real-time collaboration"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None
        self.active_editors: Dict[str, List[str]] = {}  # file -> [user_ids]
        self.conflicts: List[Dict[str, Any]] = []

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="MultiDeveloperAgent",
                    description="Manages simultaneous editing with conflict detection, resolution, and real-time collaboration",
                    instruction="You are a collaboration specialist. Manage multiple developers editing the same files, detect conflicts, suggest resolutions, and coordinate changes.",
                    output_key="collaboration_result",
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

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process collaboration requests."""
        action = request.get("action", "edit")
        user_id = request.get("user_id")
        file_path = request.get("file_path")
        
        if action == "start_edit" and user_id and file_path:
            if file_path not in self.active_editors:
                self.active_editors[file_path] = []
            if user_id not in self.active_editors[file_path]:
                self.active_editors[file_path].append(user_id)
            return {
                "status": "success",
                "agent": self.name,
                "active_editors": self.active_editors[file_path],
                "file": file_path,
            }
        
        if action == "detect_conflict" and file_path:
            editors = self.active_editors.get(file_path, [])
            has_conflict = len(editors) > 1
            if has_conflict:
                conflict = {
                    "file": file_path,
                    "editors": editors,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.conflicts.append(conflict)
            return {
                "status": "success",
                "agent": self.name,
                "has_conflict": has_conflict,
                "editors": editors,
            }
        
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        return {
            "status": "success",
            "agent": self.name,
            "action": action,
            "message": "Multi-developer collaboration available",
        }


class SecurityScannerAgent(ADKIDEAgent):
    """Security scanning agent with continuous vulnerability assessment."""

    def __init__(self) -> None:
        super().__init__(
            name="security_scanner_agent",
            description="Continuous vulnerability assessment and security scanning"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="SecurityScannerAgent",
                    description="Scans code for security vulnerabilities, common vulnerabilities, and security best practices",
                    instruction="You are a security scanning specialist. Analyze code for vulnerabilities, injection risks, insecure dependencies, and security misconfigurations. Provide actionable security recommendations.",
                    output_key="security_scan_result",
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

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process security scanning requests."""
        code = request.get("code", "")
        
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: basic pattern detection
        vulnerabilities = []
        if re.search(r"eval\s*\(", code):
            vulnerabilities.append({"type": "code_injection", "severity": "high", "message": "eval() usage detected"})
        if re.search(r"password\s*=\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            vulnerabilities.append({"type": "hardcoded_secret", "severity": "critical", "message": "Hardcoded password detected"})
        if "sql" in code.lower() and "execute" in code.lower() and "%s" not in code and "?" not in code:
            vulnerabilities.append({"type": "sql_injection", "severity": "high", "message": "Potential SQL injection risk"})
        
        return {
            "status": "success",
            "agent": self.name,
            "vulnerabilities": vulnerabilities,
            "scan_complete": True,
        }


class ComplianceMonitorAgent(ADKIDEAgent):
    """Compliance monitor agent against industry standards."""

    def __init__(self) -> None:
        super().__init__(
            name="compliance_monitor_agent",
            description="Compliance monitoring against industry standards (GDPR, HIPAA, SOC2, etc.)"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="ComplianceMonitorAgent",
                    description="Monitors code and practices for compliance with industry standards like GDPR, HIPAA, SOC2, PCI-DSS",
                    instruction="You are a compliance monitoring specialist. Analyze code, configurations, and practices for compliance with various industry standards. Provide compliance reports and recommendations.",
                    output_key="compliance_result",
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

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process compliance monitoring requests."""
        standard = request.get("standard", "GDPR")
        
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        return {
            "status": "success",
            "agent": self.name,
            "standard": standard,
            "compliance_status": "pending_review",
            "message": "Compliance monitoring available",
        }

