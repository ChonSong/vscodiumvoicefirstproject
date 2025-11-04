"""
Session Security and Isolation

Implements comprehensive session security including user permission validation,
project access controls, and security policy enforcement.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from enum import Enum
import ipaddress
import re

from ..config import get_settings
from ..services.session_state import ADKIDESessionState, SecurityLevel


class AccessLevel(str, Enum):
    """Access level enumeration."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class SecurityViolationType(str, Enum):
    """Security violation types."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    INVALID_SESSION = "invalid_session"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_VIOLATION = "ip_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DATA_EXFILTRATION_ATTEMPT = "data_exfiltration_attempt"


class SessionSecurityManager:
    """
    Comprehensive session security and isolation manager.
    
    Handles user permission validation, project access controls,
    security policy enforcement, and audit logging.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.security_violations: List[Dict[str, Any]] = []
        self.rate_limits: Dict[str, List[datetime]] = {}
        
    async def validate_user_permissions(
        self,
        user_id: str,
        resource_type: str,
        action: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Validate user permissions for specific resource and action.
        
        Args:
            user_id: User identifier
            resource_type: Type of resource (project, file, agent, etc.)
            action: Action being attempted (read, write, execute, etc.)
            resource_id: Specific resource identifier
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Get user permissions from database/cache
            user_permissions = await self._get_user_permissions(user_id)
            
            if not user_permissions:
                await self._log_security_violation(
                    user_id=user_id,
                    violation_type=SecurityViolationType.UNAUTHORIZED_ACCESS,
                    details=f"No permissions found for user {user_id}"
                )
                return False
            
            # Check global permissions
            global_access = user_permissions.get("global_access", AccessLevel.NONE)
            if global_access == AccessLevel.OWNER:
                return True
            
            # Check resource-specific permissions
            resource_permissions = user_permissions.get("resources", {})
            resource_access = resource_permissions.get(resource_type, {})
            
            if resource_id:
                # Check specific resource permission
                specific_access = resource_access.get(resource_id, AccessLevel.NONE)
            else:
                # Check general resource type permission
                specific_access = resource_access.get("default", AccessLevel.NONE)
            
            # Validate action against access level
            required_level = self._get_required_access_level(action)
            has_permission = self._check_access_level(specific_access, required_level)
            
            if not has_permission:
                await self._log_security_violation(
                    user_id=user_id,
                    violation_type=SecurityViolationType.PERMISSION_DENIED,
                    details=f"Insufficient permissions for {action} on {resource_type}:{resource_id}"
                )
            
            return has_permission
            
        except Exception as e:
            await self._log_security_violation(
                user_id=user_id,
                violation_type=SecurityViolationType.UNAUTHORIZED_ACCESS,
                details=f"Permission validation error: {str(e)}"
            )
            return False
    
    async def validate_project_access(
        self,
        user_id: str,
        project_id: str,
        access_type: str = "read"
    ) -> bool:
        """
        Validate user access to specific project.
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            access_type: Type of access requested
            
        Returns:
            True if user has project access, False otherwise
        """
        try:
            # Check project-specific permissions
            project_permissions = await self._get_project_permissions(user_id, project_id)
            
            if not project_permissions:
                return False
            
            # Validate access type
            user_access_level = project_permissions.get("access_level", AccessLevel.NONE)
            required_level = self._get_required_access_level(access_type)
            
            return self._check_access_level(user_access_level, required_level)
            
        except Exception as e:
            await self._log_security_violation(
                user_id=user_id,
                violation_type=SecurityViolationType.UNAUTHORIZED_ACCESS,
                details=f"Project access validation error: {str(e)}"
            )
            return False
    
    async def validate_session_security(
        self,
        session_id: str,
        user_id: str,
        source_ip: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """
        Comprehensive session security validation.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            source_ip: Source IP address
            user_agent: User agent string
            
        Returns:
            Security validation result
        """
        validation_result = {
            "valid": True,
            "violations": [],
            "warnings": [],
            "security_level": SecurityLevel.STANDARD
        }
        
        try:
            # Validate IP address
            if not await self._validate_ip_address(source_ip, user_id):
                validation_result["valid"] = False
                validation_result["violations"].append({
                    "type": SecurityViolationType.IP_VIOLATION,
                    "message": f"IP address {source_ip} not allowed for user {user_id}"
                })
            
            # Check rate limiting
            if not await self._check_rate_limits(user_id):
                validation_result["valid"] = False
                validation_result["violations"].append({
                    "type": SecurityViolationType.RATE_LIMIT_EXCEEDED,
                    "message": f"Rate limit exceeded for user {user_id}"
                })
            
            # Validate session integrity
            session_valid = await self._validate_session_integrity(session_id, user_id)
            if not session_valid:
                validation_result["valid"] = False
                validation_result["violations"].append({
                    "type": SecurityViolationType.INVALID_SESSION,
                    "message": f"Session integrity check failed for {session_id}"
                })
            
            # Check for suspicious activity
            suspicious_activity = await self._detect_suspicious_activity(
                user_id, source_ip, user_agent
            )
            if suspicious_activity:
                validation_result["warnings"].append({
                    "type": SecurityViolationType.SUSPICIOUS_ACTIVITY,
                    "message": "Suspicious activity detected",
                    "details": suspicious_activity
                })
                validation_result["security_level"] = SecurityLevel.HIGH
            
            # Update session tracking
            await self._update_session_tracking(session_id, user_id, source_ip, user_agent)
            
            return validation_result
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["violations"].append({
                "type": SecurityViolationType.UNAUTHORIZED_ACCESS,
                "message": f"Session validation error: {str(e)}"
            })
            return validation_result
    
    async def enforce_security_policies(
        self,
        session_state: ADKIDESessionState,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforce security policies for session actions.
        
        Args:
            session_state: Current session state
            action: Action being performed
            context: Action context
            
        Returns:
            Policy enforcement result
        """
        enforcement_result = {
            "allowed": True,
            "modifications": [],
            "warnings": []
        }
        
        try:
            # Get security policies for user
            security_policies = await self._get_security_policies(
                session_state.user_permissions.user_id
            )
            
            # Check data access policies
            if action in ["read_file", "write_file", "execute_code"]:
                data_policy_result = await self._enforce_data_access_policy(
                    session_state, action, context, security_policies
                )
                enforcement_result.update(data_policy_result)
            
            # Check execution policies
            if action in ["execute_code", "run_agent"]:
                execution_policy_result = await self._enforce_execution_policy(
                    session_state, action, context, security_policies
                )
                if not execution_policy_result["allowed"]:
                    enforcement_result["allowed"] = False
                enforcement_result["warnings"].extend(execution_policy_result.get("warnings", []))
            
            # Check collaboration policies
            if action in ["share_session", "invite_collaborator"]:
                collaboration_policy_result = await self._enforce_collaboration_policy(
                    session_state, action, context, security_policies
                )
                if not collaboration_policy_result["allowed"]:
                    enforcement_result["allowed"] = False
                enforcement_result["modifications"].extend(
                    collaboration_policy_result.get("modifications", [])
                )
            
            return enforcement_result
            
        except Exception as e:
            return {
                "allowed": False,
                "error": f"Policy enforcement error: {str(e)}"
            }
    
    async def create_audit_log_entry(
        self,
        session_id: str,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create comprehensive audit log entry.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            action: Action performed
            resource: Resource accessed
            result: Action result (success/failure)
            details: Additional details
            
        Returns:
            Audit log entry ID
        """
        audit_entry = {
            "id": secrets.token_hex(16),
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "details": details or {},
            "ip_address": details.get("ip_address") if details else None,
            "user_agent": details.get("user_agent") if details else None
        }
        
        # Store audit entry (implement based on your storage backend)
        await self._store_audit_entry(audit_entry)
        
        return audit_entry["id"]
    
    # Private helper methods
    
    async def _get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get user permissions from storage."""
        # Implement based on your user management system
        # This is a placeholder implementation
        return {
            "global_access": AccessLevel.READ,
            "resources": {
                "project": {"default": AccessLevel.READ},
                "file": {"default": AccessLevel.WRITE},
                "agent": {"default": AccessLevel.READ}
            }
        }
    
    async def _get_project_permissions(self, user_id: str, project_id: str) -> Dict[str, Any]:
        """Get project-specific permissions."""
        # Implement based on your project management system
        return {
            "access_level": AccessLevel.WRITE,
            "permissions": ["read", "write", "execute"]
        }
    
    def _get_required_access_level(self, action: str) -> AccessLevel:
        """Map action to required access level."""
        action_mappings = {
            "read": AccessLevel.READ,
            "write": AccessLevel.WRITE,
            "execute": AccessLevel.WRITE,
            "delete": AccessLevel.ADMIN,
            "admin": AccessLevel.ADMIN,
            "owner": AccessLevel.OWNER
        }
        return action_mappings.get(action, AccessLevel.READ)
    
    def _check_access_level(self, user_level: AccessLevel, required_level: AccessLevel) -> bool:
        """Check if user access level meets requirement."""
        level_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        
        user_level_value = level_hierarchy.get(user_level, 0)
        required_level_value = level_hierarchy.get(required_level, 0)
        
        return user_level_value >= required_level_value
    
    async def _validate_ip_address(self, source_ip: str, user_id: str) -> bool:
        """Validate source IP against allowlist."""
        try:
            source_ip_obj = ipaddress.ip_address(source_ip)
            
            # Check against configured allowed IP ranges
            for ip_range in self.settings.allowed_ip_list:
                if source_ip_obj in ipaddress.ip_network(ip_range, strict=False):
                    return True
            
            # Check user-specific IP allowlist
            user_allowed_ips = await self._get_user_allowed_ips(user_id)
            for ip_range in user_allowed_ips:
                if source_ip_obj in ipaddress.ip_network(ip_range, strict=False):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _check_rate_limits(self, user_id: str) -> bool:
        """Check rate limits for user."""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=5)  # 5-minute window
        
        # Get recent requests for user
        user_requests = self.rate_limits.get(user_id, [])
        
        # Filter to requests within window
        recent_requests = [req for req in user_requests if req > window_start]
        
        # Update rate limit tracking
        recent_requests.append(current_time)
        self.rate_limits[user_id] = recent_requests[-100:]  # Keep last 100 requests
        
        # Check against limit (e.g., 60 requests per 5 minutes)
        return len(recent_requests) <= 60
    
    async def _validate_session_integrity(self, session_id: str, user_id: str) -> bool:
        """Validate session integrity and authenticity."""
        try:
            # Check if session exists and is valid
            session_info = self.active_sessions.get(session_id)
            
            if not session_info:
                return False
            
            # Validate session belongs to user
            if session_info.get("user_id") != user_id:
                return False
            
            # Check session expiration
            expires_at = session_info.get("expires_at")
            if expires_at and datetime.fromisoformat(expires_at) < datetime.utcnow():
                return False
            
            # Validate session token integrity
            expected_hash = self._generate_session_hash(session_id, user_id)
            actual_hash = session_info.get("integrity_hash")
            
            return expected_hash == actual_hash
            
        except Exception:
            return False
    
    async def _detect_suspicious_activity(
        self,
        user_id: str,
        source_ip: str,
        user_agent: str
    ) -> Optional[Dict[str, Any]]:
        """Detect suspicious activity patterns."""
        suspicious_indicators = []
        
        # Check for unusual IP patterns
        user_ip_history = await self._get_user_ip_history(user_id)
        if source_ip not in user_ip_history and len(user_ip_history) > 0:
            suspicious_indicators.append("new_ip_address")
        
        # Check for unusual user agent
        user_agent_history = await self._get_user_agent_history(user_id)
        if user_agent not in user_agent_history and len(user_agent_history) > 0:
            suspicious_indicators.append("new_user_agent")
        
        # Check for rapid session creation
        recent_sessions = await self._get_recent_sessions(user_id, minutes=10)
        if len(recent_sessions) > 5:
            suspicious_indicators.append("rapid_session_creation")
        
        if suspicious_indicators:
            return {
                "indicators": suspicious_indicators,
                "risk_level": "medium" if len(suspicious_indicators) < 3 else "high"
            }
        
        return None
    
    async def _update_session_tracking(
        self,
        session_id: str,
        user_id: str,
        source_ip: str,
        user_agent: str
    ) -> None:
        """Update session tracking information."""
        session_info = {
            "user_id": user_id,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=self.settings.session_timeout_hours)).isoformat(),
            "integrity_hash": self._generate_session_hash(session_id, user_id)
        }
        
        self.active_sessions[session_id] = session_info
    
    def _generate_session_hash(self, session_id: str, user_id: str) -> str:
        """Generate session integrity hash."""
        hash_input = f"{session_id}:{user_id}:{self.settings.secret_key}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    async def _log_security_violation(
        self,
        user_id: str,
        violation_type: SecurityViolationType,
        details: str
    ) -> None:
        """Log security violation."""
        violation = {
            "id": secrets.token_hex(16),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "violation_type": violation_type.value,
            "details": details
        }
        
        self.security_violations.append(violation)
        
        # Store violation in persistent storage
        await self._store_security_violation(violation)
    
    async def _get_security_policies(self, user_id: str) -> Dict[str, Any]:
        """Get security policies for user."""
        # Implement based on your policy management system
        return {
            "data_access": {
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "allowed_file_types": [".py", ".js", ".ts", ".java", ".cpp", ".go", ".rs"],
                "restricted_paths": ["/etc", "/root", "/sys"]
            },
            "execution": {
                "max_execution_time": 300,  # 5 minutes
                "max_memory_usage": 1024 * 1024 * 1024,  # 1GB
                "allowed_commands": ["python", "node", "javac", "gcc"]
            },
            "collaboration": {
                "max_collaborators": 10,
                "require_approval": True,
                "allowed_domains": ["company.com"]
            }
        }
    
    async def _enforce_data_access_policy(
        self,
        session_state: ADKIDESessionState,
        action: str,
        context: Dict[str, Any],
        policies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce data access policies."""
        result = {"allowed": True, "modifications": [], "warnings": []}
        
        data_policies = policies.get("data_access", {})
        
        # Check file size limits
        if "file_size" in context:
            max_size = data_policies.get("max_file_size", float('inf'))
            if context["file_size"] > max_size:
                result["allowed"] = False
                result["warnings"].append(f"File size exceeds limit: {max_size} bytes")
        
        # Check file type restrictions
        if "file_path" in context:
            file_path = context["file_path"]
            allowed_types = data_policies.get("allowed_file_types", [])
            
            if allowed_types:
                file_ext = "." + file_path.split(".")[-1] if "." in file_path else ""
                if file_ext not in allowed_types:
                    result["allowed"] = False
                    result["warnings"].append(f"File type not allowed: {file_ext}")
            
            # Check restricted paths
            restricted_paths = data_policies.get("restricted_paths", [])
            for restricted_path in restricted_paths:
                if file_path.startswith(restricted_path):
                    result["allowed"] = False
                    result["warnings"].append(f"Access to restricted path: {restricted_path}")
        
        return result
    
    async def _enforce_execution_policy(
        self,
        session_state: ADKIDESessionState,
        action: str,
        context: Dict[str, Any],
        policies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce execution policies."""
        result = {"allowed": True, "warnings": []}
        
        execution_policies = policies.get("execution", {})
        
        # Check execution time limits
        max_time = execution_policies.get("max_execution_time", 300)
        if context.get("estimated_time", 0) > max_time:
            result["warnings"].append(f"Execution may exceed time limit: {max_time}s")
        
        # Check memory usage limits
        max_memory = execution_policies.get("max_memory_usage", float('inf'))
        if context.get("estimated_memory", 0) > max_memory:
            result["allowed"] = False
            result["warnings"].append(f"Memory usage exceeds limit: {max_memory} bytes")
        
        return result
    
    async def _enforce_collaboration_policy(
        self,
        session_state: ADKIDESessionState,
        action: str,
        context: Dict[str, Any],
        policies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce collaboration policies."""
        result = {"allowed": True, "modifications": []}
        
        collaboration_policies = policies.get("collaboration", {})
        
        # Check collaborator limits
        max_collaborators = collaboration_policies.get("max_collaborators", 10)
        current_collaborators = len(session_state.collaboration_state.get("collaborators", []))
        
        if current_collaborators >= max_collaborators:
            result["allowed"] = False
            result["modifications"].append(f"Maximum collaborators reached: {max_collaborators}")
        
        return result
    
    # Placeholder methods for external integrations
    async def _get_user_allowed_ips(self, user_id: str) -> List[str]:
        """Get user-specific allowed IP ranges."""
        return []
    
    async def _get_user_ip_history(self, user_id: str) -> List[str]:
        """Get user IP address history."""
        return []
    
    async def _get_user_agent_history(self, user_id: str) -> List[str]:
        """Get user agent history."""
        return []
    
    async def _get_recent_sessions(self, user_id: str, minutes: int) -> List[str]:
        """Get recent sessions for user."""
        return []
    
    async def _store_audit_entry(self, audit_entry: Dict[str, Any]) -> None:
        """Store audit entry in persistent storage."""
        pass
    
    async def _store_security_violation(self, violation: Dict[str, Any]) -> None:
        """Store security violation in persistent storage."""
        pass


# Global session security manager instance
_session_security_manager = None


def get_session_security_manager() -> SessionSecurityManager:
    """Get global session security manager instance."""
    global _session_security_manager
    if _session_security_manager is None:
        _session_security_manager = SessionSecurityManager()
    return _session_security_manager