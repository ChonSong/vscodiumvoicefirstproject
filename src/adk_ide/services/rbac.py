"""Role-Based Access Control (RBAC) service for enterprise collaboration."""
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field


class Role(Enum):
    """User roles in the system."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(Enum):
    """System permissions."""
    READ_CODE = "read_code"
    WRITE_CODE = "write_code"
    EXECUTE_CODE = "execute_code"
    DEPLOY = "deploy"
    MANAGE_AGENTS = "manage_agents"
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    MANAGE_WORKSPACE = "manage_workspace"


@dataclass
class User:
    """User with role and permissions."""
    user_id: str
    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    workspace_ids: List[str] = field(default_factory=list)


class RBACService:
    """Role-Based Access Control service."""
    
    # Role to permissions mapping
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.ADMIN: {
            Permission.READ_CODE,
            Permission.WRITE_CODE,
            Permission.EXECUTE_CODE,
            Permission.DEPLOY,
            Permission.MANAGE_AGENTS,
            Permission.MANAGE_USERS,
            Permission.VIEW_LOGS,
            Permission.MANAGE_WORKSPACE,
        },
        Role.DEVELOPER: {
            Permission.READ_CODE,
            Permission.WRITE_CODE,
            Permission.EXECUTE_CODE,
            Permission.VIEW_LOGS,
        },
        Role.VIEWER: {
            Permission.READ_CODE,
            Permission.VIEW_LOGS,
        },
        Role.GUEST: {
            Permission.READ_CODE,
        },
    }
    
    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.workspace_members: Dict[str, List[str]] = {}  # workspace_id -> [user_ids]
    
    def create_user(self, user_id: str, role: Role = Role.DEVELOPER) -> User:
        """Create a new user with role."""
        permissions = self.ROLE_PERMISSIONS.get(role, set()).copy()
        user = User(user_id=user_id, role=role, permissions=permissions)
        self.users[user_id] = user
        return user
    
    def assign_role(self, user_id: str, role: Role) -> bool:
        """Assign role to user."""
        if user_id not in self.users:
            self.create_user(user_id, role)
        else:
            user = self.users[user_id]
            user.role = role
            user.permissions = self.ROLE_PERMISSIONS.get(role, set()).copy()
        return True
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission."""
        if user_id not in self.users:
            return False
        user = self.users[user_id]
        return permission in user.permissions
    
    def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """Grant additional permission to user."""
        if user_id not in self.users:
            return False
        self.users[user_id].permissions.add(permission)
        return True
    
    def revoke_permission(self, user_id: str, permission: Permission) -> bool:
        """Revoke permission from user."""
        if user_id not in self.users:
            return False
        self.users[user_id].permissions.discard(permission)
        return True
    
    def add_to_workspace(self, user_id: str, workspace_id: str) -> bool:
        """Add user to workspace."""
        if user_id not in self.users:
            return False
        if workspace_id not in self.workspace_members:
            self.workspace_members[workspace_id] = []
        if user_id not in self.workspace_members[workspace_id]:
            self.workspace_members[workspace_id].append(user_id)
        if workspace_id not in self.users[user_id].workspace_ids:
            self.users[user_id].workspace_ids.append(workspace_id)
        return True
    
    def get_workspace_members(self, workspace_id: str) -> List[str]:
        """Get list of user IDs in workspace."""
        return self.workspace_members.get(workspace_id, [])
    
    def can_access_workspace(self, user_id: str, workspace_id: str) -> bool:
        """Check if user can access workspace."""
        if user_id not in self.users:
            return False
        user = self.users[user_id]
        # Admins can access all workspaces
        if user.role == Role.ADMIN:
            return True
        return workspace_id in user.workspace_ids

