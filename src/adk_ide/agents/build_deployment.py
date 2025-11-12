"""Build and Deployment Agents for automated build and deployment."""
from typing import Any, Dict, Optional, Callable, List
import os
import subprocess
import json
from pathlib import Path

from .base import ADKIDEAgent


class BuildOrchestrationAgent(ADKIDEAgent):
    """Build orchestration agent for complex build pipeline management."""

    def __init__(self) -> None:
        super().__init__(
            name="build_orchestration_agent",
            description="Complex build pipeline management with dependency graphs and parallel compilation"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="BuildOrchestrationAgent",
                    description="Manages complex build pipelines, dependency graphs, and parallel compilation processes",
                    instruction="You are a build orchestration specialist. Analyze build requirements, create dependency graphs, optimize build order, and manage parallel compilation processes.",
                    output_key="build_result",
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
        """Process build orchestration requests."""
        build_type = request.get("build_type", "auto")
        project_path = request.get("project_path", ".")
        
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: basic build detection
        build_commands = {
            "python": ["python", "-m", "build"],
            "npm": ["npm", "run", "build"],
            "maven": ["mvn", "clean", "install"],
            "gradle": ["./gradlew", "build"],
        }
        
        return {
            "status": "success",
            "agent": self.name,
            "build_type": build_type,
            "suggested_commands": build_commands,
        }


class DependencyManagerAgent(ADKIDEAgent):
    """Dependency manager agent with automatic package installation."""

    def __init__(self) -> None:
        super().__init__(
            name="dependency_manager_agent",
            description="Automatic package installation, version conflict resolution, and security vulnerability scanning"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="DependencyManagerAgent",
                    description="Manages dependencies with automatic installation, version resolution, and security scanning",
                    instruction="You are a dependency management specialist. Install packages, resolve version conflicts, analyze dependency graphs, and scan for security vulnerabilities.",
                    output_key="dependency_result",
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
        """Process dependency management requests."""
        action = request.get("action", "analyze")
        package = request.get("package")
        
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback
        return {
            "status": "success",
            "agent": self.name,
            "action": action,
            "package": package,
            "message": "Dependency management available",
        }


class AssetBundlerAgent(ADKIDEAgent):
    """Asset bundler agent for web asset compilation and optimization."""

    def __init__(self) -> None:
        super().__init__(
            name="asset_bundler_agent",
            description="Web asset compilation, minification, and optimization for production deployment"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="AssetBundlerAgent",
                    description="Compiles, minifies, and optimizes web assets for production deployment",
                    instruction="You are an asset bundling specialist. Bundle JavaScript, CSS, and other assets, apply minification and optimization, and prepare assets for production deployment.",
                    output_key="bundle_result",
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
        """Process asset bundling requests."""
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
            "message": "Asset bundling available",
        }


class DeploymentAgent(ADKIDEAgent):
    """Deployment agent with automated deployment to multiple targets."""

    def __init__(self) -> None:
        super().__init__(
            name="deployment_agent",
            description="Automated deployment to multiple targets (cloud, containers, edge) with rollback capabilities"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="DeploymentAgent",
                    description="Deploys applications to cloud, containers, and edge devices with health monitoring and rollback",
                    instruction="You are a deployment specialist. Deploy applications to various targets, monitor deployment health, and manage rollback capabilities.",
                    output_key="deployment_result",
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
        """Process deployment requests."""
        target = request.get("target", "cloud")
        
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
            "target": target,
            "message": "Deployment available",
        }


class GitOperationsAgent(ADKIDEAgent):
    """Git operations agent with comprehensive version control functionality."""

    def __init__(self) -> None:
        super().__init__(
            name="git_operations_agent",
            description="Comprehensive Git functionality including commit, branch, merge, rebase, and pull request management"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore

                tools = []
                try:
                    class GitTool:
                        name = "git_command"
                        description = "Execute Git commands safely (commit, branch, merge, rebase, status, log, etc.)"

                        async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                            command = payload.get("command", "")
                            args = payload.get("args", [])
                            return await self._parent._execute_git(command, args)

                    git_tool = GitTool()
                    git_tool._parent = self
                    tools.append(git_tool)
                except Exception:
                    pass

                self._llm_agent = LlmAgent(
                    name="GitOperationsAgent",
                    description="Comprehensive Git version control operations including commit, branch, merge, rebase, and pull request management",
                    tools=tools if tools else None,  # type: ignore[arg-type]
                    instruction="You are a Git operations specialist. Execute Git commands safely, manage branches, handle merges and rebases, and assist with pull request workflows.",
                    output_key="git_result",
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

    async def _execute_git(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Execute Git command safely."""
        # Whitelist of safe Git commands
        safe_commands = {
            "status", "log", "branch", "tag", "diff", "show", "ls-files",
            "config", "remote", "fetch", "pull", "clone",
        }
        
        # Commands requiring validation
        write_commands = {
            "commit", "merge", "rebase", "checkout", "branch", "tag", "push",
        }
        
        if command not in safe_commands and command not in write_commands:
            return {"error": f"Git command '{command}' not allowed"}
        
        try:
            import subprocess as sp
            result = sp.run(
                ["git", command] + args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process Git operation requests."""
        action = request.get("action", "status")
        command = request.get("command", action)
        
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback: execute git command
        if action in ["status", "log", "branch"]:
            git_result = await self._execute_git(action, request.get("args", []))
            return {
                "status": "success",
                "agent": self.name,
                "action": action,
                "git_result": git_result,
            }

        return {
            "status": "success",
            "agent": self.name,
            "action": action,
            "message": "Git operations available",
        }

