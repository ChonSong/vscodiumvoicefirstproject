"""
Security Middleware

Provides security middleware for request validation, session security,
and policy enforcement across the ADK IDE system.
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from google.adk.core import InvocationContext
from ..services.session_state import ADKIDESessionState
from .session_security import get_session_security_manager, SecurityViolationType


class SecurityMiddleware:
    """
    Security middleware for ADK IDE system.
    
    Provides comprehensive security validation and policy enforcement
    for all agent interactions and system operations.
    """
    
    def __init__(self):
        self.security_manager = get_session_security_manager()
        self.active_validations: Dict[str, Dict[str, Any]] = {}
    
    async def validate_request(
        self,
        context: InvocationContext,
        action: str,
        resource: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate incoming request for security compliance.
        
        Args:
            context: Invocation context
            action: Action being performed
            resource: Resource being accessed
            **kwargs: Additional validation parameters
            
        Returns:
            Validation result with security status
        """
        validation_id = f"{context.session.id}_{action}_{datetime.utcnow().timestamp()}"
        
        try:
            # Extract request metadata
            user_id = context.session.metadata.get("user_id")
            source_ip = kwargs.get("source_ip", "unknown")
            user_agent = kwargs.get("user_agent", "unknown")
            
            if not user_id:
                return {
                    "valid": False,
                    "error": "User ID not found in session",
                    "violation_type": SecurityViolationType.INVALID_SESSION
                }
            
            # Validate session security
            session_validation = await self.security_manager.validate_session_security(
                session_id=context.session.id,
                user_id=user_id,
                source_ip=source_ip,
                user_agent=user_agent
            )
            
            if not session_validation["valid"]:
                return {
                    "valid": False,
                    "error": "Session security validation failed",
                    "violations": session_validation["violations"]
                }
            
            # Validate user permissions
            has_permission = await self.security_manager.validate_user_permissions(
                user_id=user_id,
                resource_type=resource,
                action=action,
                resource_id=kwargs.get("resource_id")
            )
            
            if not has_permission:
                return {
                    "valid": False,
                    "error": "Insufficient permissions",
                    "violation_type": SecurityViolationType.PERMISSION_DENIED
                }
            
            # Store validation for audit
            self.active_validations[validation_id] = {
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "timestamp": datetime.utcnow().isoformat(),
                "source_ip": source_ip,
                "session_id": context.session.id
            }
            
            return {
                "valid": True,
                "validation_id": validation_id,
                "security_level": session_validation.get("security_level", "standard"),
                "warnings": session_validation.get("warnings", [])
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Security validation error: {str(e)}",
                "violation_type": SecurityViolationType.UNAUTHORIZED_ACCESS
            }
    
    async def enforce_policies(
        self,
        context: InvocationContext,
        action: str,
        action_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforce security policies for specific action.
        
        Args:
            context: Invocation context
            action: Action being performed
            action_context: Context specific to the action
            
        Returns:
            Policy enforcement result
        """
        try:
            # Get session state
            session_state = ADKIDESessionState.from_session(context.session)
            
            # Enforce security policies
            enforcement_result = await self.security_manager.enforce_security_policies(
                session_state=session_state,
                action=action,
                context=action_context
            )
            
            return enforcement_result
            
        except Exception as e:
            return {
                "allowed": False,
                "error": f"Policy enforcement error: {str(e)}"
            }
    
    async def create_audit_entry(
        self,
        validation_id: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create audit log entry for completed action.
        
        Args:
            validation_id: Validation ID from validate_request
            result: Action result (success/failure)
            details: Additional audit details
            
        Returns:
            Audit entry ID if successful
        """
        try:
            validation_info = self.active_validations.get(validation_id)
            
            if not validation_info:
                return None
            
            # Create audit entry
            audit_id = await self.security_manager.create_audit_log_entry(
                session_id=validation_info["session_id"],
                user_id=validation_info["user_id"],
                action=validation_info["action"],
                resource=validation_info["resource"],
                result=result,
                details={
                    **(details or {}),
                    "source_ip": validation_info["source_ip"],
                    "validation_timestamp": validation_info["timestamp"]
                }
            )
            
            # Clean up validation tracking
            del self.active_validations[validation_id]
            
            return audit_id
            
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Audit logging error: {str(e)}")
            return None
    
    def create_security_decorator(self, resource_type: str, action: str):
        """
        Create security decorator for agent methods.
        
        Args:
            resource_type: Type of resource being accessed
            action: Action being performed
            
        Returns:
            Security decorator function
        """
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                # Extract context from arguments
                context = None
                for arg in args:
                    if isinstance(arg, InvocationContext):
                        context = arg
                        break
                
                if not context:
                    # Look for context in kwargs
                    context = kwargs.get('context')
                
                if not context:
                    raise ValueError("InvocationContext not found in arguments")
                
                # Validate security
                validation_result = await self.validate_request(
                    context=context,
                    action=action,
                    resource=resource_type,
                    **kwargs
                )
                
                if not validation_result["valid"]:
                    raise PermissionError(f"Security validation failed: {validation_result.get('error')}")
                
                validation_id = validation_result.get("validation_id")
                
                try:
                    # Execute original function
                    result = await func(*args, **kwargs)
                    
                    # Create audit entry for success
                    if validation_id:
                        await self.create_audit_entry(
                            validation_id=validation_id,
                            result="success",
                            details={"function": func.__name__}
                        )
                    
                    return result
                    
                except Exception as e:
                    # Create audit entry for failure
                    if validation_id:
                        await self.create_audit_entry(
                            validation_id=validation_id,
                            result="failure",
                            details={
                                "function": func.__name__,
                                "error": str(e)
                            }
                        )
                    
                    raise
            
            return wrapper
        return decorator


# Global security middleware instance
_security_middleware = None


def get_security_middleware() -> SecurityMiddleware:
    """Get global security middleware instance."""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware()
    return _security_middleware


# Convenience decorators
def require_permission(resource_type: str, action: str):
    """Decorator to require specific permission for method execution."""
    return get_security_middleware().create_security_decorator(resource_type, action)


def require_project_access(action: str = "read"):
    """Decorator to require project access for method execution."""
    return require_permission("project", action)


def require_file_access(action: str = "read"):
    """Decorator to require file access for method execution."""
    return require_permission("file", action)


def require_agent_access(action: str = "execute"):
    """Decorator to require agent access for method execution."""
    return require_permission("agent", action)