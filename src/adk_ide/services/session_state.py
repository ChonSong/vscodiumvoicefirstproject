"""
Session State Schema and Management

Defines standardized session state structure and management utilities
for the ADK IDE system with validation and sanitization.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class SecurityLevel(str, Enum):
    """Security level enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    HIGH_SECURITY = "high_security"


@dataclass
class UserPreferences:
    """User preferences for IDE configuration."""
    theme: str = "dark"
    font_size: int = 14
    auto_save: bool = True
    code_completion: bool = True
    syntax_highlighting: bool = True
    line_numbers: bool = True
    word_wrap: bool = False
    tab_size: int = 4
    language_defaults: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ExecutionResult:
    """Execution result record."""
    execution_id: str
    code: str
    language: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WorkflowState:
    """Workflow state tracking."""
    workflow_id: str
    workflow_type: str
    status: str
    steps_completed: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ADKIDESessionState:
    """
    Standardized session state structure for ADK IDE.
    
    Contains all session-specific data including user context,
    project state, execution history, and workflow tracking.
    """
    
    # Basic session information
    session_id: str
    user_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    security_level: SecurityLevel = SecurityLevel.STANDARD
    
    # Project and development context
    current_project: Optional[str] = None
    active_files: List[str] = field(default_factory=list)
    code_context: Dict[str, str] = field(default_factory=dict)
    
    # User preferences and configuration
    user_preferences: UserPreferences = field(default_factory=UserPreferences)
    
    # Execution and workflow tracking
    execution_history: List[ExecutionResult] = field(default_factory=list)
    workflow_state: Dict[str, WorkflowState] = field(default_factory=dict)
    
    # Agent-specific state
    developing_agent_state: Dict[str, Any] = field(default_factory=dict)
    code_execution_state: Dict[str, Any] = field(default_factory=dict)
    debug_session_state: Dict[str, Any] = field(default_factory=dict)
    
    # Security and permissions
    user_permissions: Dict[str, Any] = field(default_factory=dict)
    project_access: Dict[str, Any] = field(default_factory=dict)
    security_policies: Dict[str, Any] = field(default_factory=dict)
    
    # Activity tracking
    session_start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Communication and coordination
    active_agent: Optional[str] = None
    delegations: List[Dict[str, Any]] = field(default_factory=list)
    transfers: List[Dict[str, Any]] = field(default_factory=list)
    tool_executions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session state to dictionary.
        
        Returns:
            Session state as dictionary
        """
        data = asdict(self)
        
        # Convert enum values to strings
        data["status"] = self.status.value
        data["security_level"] = self.security_level.value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ADKIDESessionState":
        """
        Create session state from dictionary.
        
        Args:
            data: Session state dictionary
            
        Returns:
            ADKIDESessionState instance
        """
        # Handle enum conversions
        if "status" in data:
            data["status"] = SessionStatus(data["status"])
        if "security_level" in data:
            data["security_level"] = SecurityLevel(data["security_level"])
        
        # Handle nested objects
        if "user_preferences" in data and isinstance(data["user_preferences"], dict):
            data["user_preferences"] = UserPreferences.from_dict(data["user_preferences"])
        
        if "execution_history" in data:
            data["execution_history"] = [
                ExecutionResult.from_dict(item) if isinstance(item, dict) else item
                for item in data["execution_history"]
            ]
        
        if "workflow_state" in data:
            workflow_state = {}
            for key, value in data["workflow_state"].items():
                if isinstance(value, dict):
                    workflow_state[key] = WorkflowState.from_dict(value)
                else:
                    workflow_state[key] = value
            data["workflow_state"] = workflow_state
        
        return cls(**data)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow().isoformat()
    
    def add_execution_result(self, result: ExecutionResult) -> None:
        """
        Add execution result to history.
        
        Args:
            result: Execution result to add
        """
        self.execution_history.append(result)
        self.update_activity()
        
        # Keep only last 100 execution results
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def start_workflow(self, workflow: WorkflowState) -> None:
        """
        Start a new workflow.
        
        Args:
            workflow: Workflow to start
        """
        self.workflow_state[workflow.workflow_id] = workflow
        self.update_activity()
    
    def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> None:
        """
        Update workflow state.
        
        Args:
            workflow_id: Workflow identifier
            updates: Updates to apply
        """
        if workflow_id in self.workflow_state:
            workflow = self.workflow_state[workflow_id]
            
            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
            
            workflow.updated_at = datetime.utcnow().isoformat()
            self.update_activity()
    
    def complete_workflow(self, workflow_id: str) -> None:
        """
        Complete a workflow.
        
        Args:
            workflow_id: Workflow identifier
        """
        if workflow_id in self.workflow_state:
            self.workflow_state[workflow_id].status = "completed"
            self.workflow_state[workflow_id].updated_at = datetime.utcnow().isoformat()
            self.update_activity()
    
    def add_delegation(self, delegation: Dict[str, Any]) -> None:
        """
        Add delegation record.
        
        Args:
            delegation: Delegation information
        """
        self.delegations.append({
            **delegation,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.update_activity()
        
        # Keep only last 50 delegations
        if len(self.delegations) > 50:
            self.delegations = self.delegations[-50:]
    
    def add_transfer(self, transfer: Dict[str, Any]) -> None:
        """
        Add transfer record.
        
        Args:
            transfer: Transfer information
        """
        self.transfers.append({
            **transfer,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.active_agent = transfer.get("to_agent")
        self.update_activity()
        
        # Keep only last 20 transfers
        if len(self.transfers) > 20:
            self.transfers = self.transfers[-20:]
    
    def add_tool_execution(self, execution: Dict[str, Any]) -> None:
        """
        Add tool execution record.
        
        Args:
            execution: Tool execution information
        """
        self.tool_executions.append({
            **execution,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.update_activity()
        
        # Keep only last 100 tool executions
        if len(self.tool_executions) > 100:
            self.tool_executions = self.tool_executions[-100:]
    
    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """
        Get agent-specific state.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Agent state dictionary
        """
        state_key = f"{agent_name.lower()}_state"
        return getattr(self, state_key, {})
    
    def set_agent_state(self, agent_name: str, state: Dict[str, Any]) -> None:
        """
        Set agent-specific state.
        
        Args:
            agent_name: Agent name
            state: State to set
        """
        state_key = f"{agent_name.lower()}_state"
        if hasattr(self, state_key):
            setattr(self, state_key, state)
            self.update_activity()
    
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """
        Check if session is expired.
        
        Args:
            timeout_hours: Timeout in hours
            
        Returns:
            True if session is expired
        """
        try:
            last_activity_time = datetime.fromisoformat(self.last_activity)
            timeout_delta = datetime.utcnow() - last_activity_time
            return timeout_delta.total_seconds() > (timeout_hours * 3600)
        except (ValueError, TypeError):
            return True
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary.
        
        Returns:
            Session summary information
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "security_level": self.security_level.value,
            "current_project": self.current_project,
            "active_files_count": len(self.active_files),
            "execution_count": len(self.execution_history),
            "active_workflows": len([w for w in self.workflow_state.values() if w.status == "active"]),
            "active_agent": self.active_agent,
            "session_duration": self._calculate_session_duration(),
            "last_activity": self.last_activity
        }
    
    def _calculate_session_duration(self) -> str:
        """
        Calculate session duration.
        
        Returns:
            Session duration as string
        """
        try:
            start_time = datetime.fromisoformat(self.session_start_time)
            duration = datetime.utcnow() - start_time
            
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except (ValueError, TypeError):
            return "unknown"


class SessionStateManager:
    """
    Session state management utilities.
    
    Provides validation, sanitization, and manipulation utilities
    for session state objects.
    """
    
    @staticmethod
    def create_new_session_state(
        session_id: str,
        user_id: str,
        security_level: SecurityLevel = SecurityLevel.STANDARD
    ) -> ADKIDESessionState:
        """
        Create new session state with defaults.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            security_level: Security level
            
        Returns:
            New session state
        """
        return ADKIDESessionState(
            session_id=session_id,
            user_id=user_id,
            security_level=security_level
        )
    
    @staticmethod
    def validate_session_state(state: ADKIDESessionState) -> Dict[str, Any]:
        """
        Validate session state for consistency and security.
        
        Args:
            state: Session state to validate
            
        Returns:
            Validation result with issues
        """
        issues = []
        warnings = []
        
        # Required fields validation
        if not state.session_id:
            issues.append("Missing session_id")
        if not state.user_id:
            issues.append("Missing user_id")
        
        # Security validation
        if state.security_level == SecurityLevel.HIGH_SECURITY:
            if not state.security_policies:
                warnings.append("High security level but no security policies defined")
        
        # Data size validation
        if len(state.execution_history) > 1000:
            warnings.append("Execution history is very large, consider cleanup")
        
        if len(state.delegations) > 500:
            warnings.append("Delegation history is very large, consider cleanup")
        
        # Timestamp validation
        try:
            datetime.fromisoformat(state.session_start_time)
            datetime.fromisoformat(state.last_activity)
        except ValueError:
            issues.append("Invalid timestamp format")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @staticmethod
    def sanitize_session_state(state: ADKIDESessionState) -> ADKIDESessionState:
        """
        Sanitize session state by removing sensitive data and cleaning up.
        
        Args:
            state: Session state to sanitize
            
        Returns:
            Sanitized session state
        """
        # Create a copy
        sanitized_data = state.to_dict()
        
        # Remove sensitive information
        if "security_policies" in sanitized_data:
            # Keep only non-sensitive policy information
            policies = sanitized_data["security_policies"]
            sanitized_policies = {
                key: value for key, value in policies.items()
                if key not in ["encryption_keys", "api_keys", "tokens"]
            }
            sanitized_data["security_policies"] = sanitized_policies
        
        # Limit history sizes
        if len(sanitized_data.get("execution_history", [])) > 100:
            sanitized_data["execution_history"] = sanitized_data["execution_history"][-100:]
        
        if len(sanitized_data.get("delegations", [])) > 50:
            sanitized_data["delegations"] = sanitized_data["delegations"][-50:]
        
        if len(sanitized_data.get("tool_executions", [])) > 100:
            sanitized_data["tool_executions"] = sanitized_data["tool_executions"][-100:]
        
        return ADKIDESessionState.from_dict(sanitized_data)
    
    @staticmethod
    def merge_session_states(
        primary: ADKIDESessionState,
        secondary: ADKIDESessionState
    ) -> ADKIDESessionState:
        """
        Merge two session states, with primary taking precedence.
        
        Args:
            primary: Primary session state
            secondary: Secondary session state
            
        Returns:
            Merged session state
        """
        # Start with primary state
        merged_data = primary.to_dict()
        secondary_data = secondary.to_dict()
        
        # Merge execution histories
        all_executions = merged_data.get("execution_history", []) + secondary_data.get("execution_history", [])
        # Sort by timestamp and keep unique
        unique_executions = {}
        for exec_result in all_executions:
            if isinstance(exec_result, dict):
                exec_id = exec_result.get("execution_id")
                if exec_id and exec_id not in unique_executions:
                    unique_executions[exec_id] = exec_result
        
        merged_data["execution_history"] = list(unique_executions.values())[-100:]  # Keep last 100
        
        # Merge workflow states
        merged_workflows = merged_data.get("workflow_state", {})
        secondary_workflows = secondary_data.get("workflow_state", {})
        merged_workflows.update(secondary_workflows)
        merged_data["workflow_state"] = merged_workflows
        
        # Update activity timestamp to most recent
        primary_activity = datetime.fromisoformat(primary.last_activity)
        secondary_activity = datetime.fromisoformat(secondary.last_activity)
        
        if secondary_activity > primary_activity:
            merged_data["last_activity"] = secondary.last_activity
        
        return ADKIDESessionState.from_dict(merged_data)