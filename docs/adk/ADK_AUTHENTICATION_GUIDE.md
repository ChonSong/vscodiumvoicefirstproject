# ADK Authentication and Security Guide

## Overview

This guide provides comprehensive information about authentication and security features in the Agent Development Kit (ADK) Voice IDE system. The authentication system provides enterprise-grade security with role-based access control, JWT tokens, and comprehensive audit logging.

## Authentication System Features

### 🔐 Core Security Features

- **Secure User Management**: Complete user lifecycle with password hashing (PBKDF2)
- **Role-Based Access Control (RBAC)**: 5 user roles with granular permissions
- **JWT Token Authentication**: Secure session tokens with expiration
- **Account Security**: Lockout protection after failed login attempts
- **Device Fingerprinting**: Track sessions by device characteristics
- **Security Event Logging**: Comprehensive audit trail

### 👥 User Roles and Permissions

The system supports 5 distinct user roles with escalating permissions:

#### Guest
- **Permissions**: `voice_interface`, `basic_code_execution`
- **Use Case**: Limited access for demonstration or trial users

#### User
- **Permissions**: `voice_interface`, `code_execution`, `file_operations`
- **Use Case**: Standard users with basic development capabilities

#### Developer
- **Permissions**: All User permissions + `advanced_features`, `debugging`, `monitoring`
- **Use Case**: Full development access with debugging and monitoring tools

#### Admin
- **Permissions**: All Developer permissions + `user_management`, `system_config`, `security_dashboard`
- **Use Case**: System administrators with user and configuration management

#### Super Admin
- **Permissions**: `*` (all permissions)
- **Use Case**: Full system access for system owners

## Authentication Methods

### 1. Password Authentication
```python
from src.adk_mcp.auth_security_system import get_auth_system

auth_system = get_auth_system()

# Authenticate user
session = await auth_system.authenticate(
    username="admin",
    password="admin123",
    ip_address="127.0.0.1"
)
```

### 2. JWT Token Authentication
```python
# Generate JWT token
token = auth_system._generate_jwt_token(user_id, session_id)

# Validate JWT token
session = await auth_system.validate_session(token)
```

### 3. API Key Authentication
```python
from src.adk_mcp.authentication_system import get_auth_system

auth_system = get_auth_system()

# Authenticate with API key
headers = {"X-API-Key": "your_api_key_here"}
auth_result = await auth_system.authenticate_request(headers, "/api/endpoint")
```

### 4. Session Token Authentication
```python
# Create session
session_token = await auth_system.create_session(
    user_id="user_123",
    websocket_id="ws_456",
    metadata={"client_type": "web"}
)

# Validate session
session_info = await auth_system.validate_session(session_token)
```

## Security Configuration

### Password Security
- **Hashing Algorithm**: PBKDF2 with 100,000 iterations
- **Salt**: Unique salt per user (16 bytes)
- **Storage**: Secure hash storage, never plain text

### Session Security
- **JWT Tokens**: HS256 algorithm with configurable secret
- **Session Timeout**: 24 hours (configurable)
- **Activity Tracking**: Last activity timestamps
- **Device Fingerprinting**: IP + User-Agent based tracking

### Account Protection
- **Failed Login Limit**: 5 attempts before lockout
- **Lockout Duration**: 30 minutes (configurable)
- **Automatic Unlock**: After lockout period expires

## Implementation Examples

### Basic Authentication Setup

```python
#!/usr/bin/env python3
"""
Basic authentication setup example
"""

from src.adk_mcp.auth_security_system import get_auth_system, UserRole

async def setup_authentication():
    auth_system = get_auth_system()
    
    # Create a new user
    user_id = auth_system.create_user(
        username="newuser",
        email="user@example.com",
        password="secure_password",
        role=UserRole.DEVELOPER
    )
    
    # Authenticate user
    session = await auth_system.authenticate(
        username="newuser",
        password="secure_password",
        ip_address="192.168.1.100"
    )
    
    if session:
        print(f"Authentication successful: {session.session_id}")
        return session
    else:
        print("Authentication failed")
        return None

# Run the setup
import asyncio
asyncio.run(setup_authentication())
```

### Web Server Integration

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from src.adk_mcp.auth_security_system import get_auth_system

app = FastAPI()
security = HTTPBearer()
auth_system = get_auth_system()

async def get_current_session(token: str = Depends(security)):
    """Dependency to get current authenticated session."""
    session = await auth_system.validate_session(token.credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return session

@app.post("/login")
async def login(username: str, password: str):
    """Login endpoint."""
    session = await auth_system.authenticate(username, password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "token": session.token,
        "session_id": session.session_id,
        "expires_at": session.expires_at.isoformat()
    }

@app.get("/protected")
async def protected_endpoint(session = Depends(get_current_session)):
    """Protected endpoint requiring authentication."""
    user = auth_system.get_user(session.user_id)
    return {
        "message": "Access granted",
        "user": user.username,
        "role": user.role.value
    }
```

### Permission Checking

```python
def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        async def wrapper(session, *args, **kwargs):
            if not auth_system.check_permission(session, permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(session, *args, **kwargs)
        return wrapper
    return decorator

@require_permission("code_execution")
async def execute_code(session, code: str):
    """Execute code with permission check."""
    # Code execution logic here
    pass
```

## Security Monitoring

### Security Events
The system logs comprehensive security events:

- **Login Events**: Success/failure, IP tracking
- **Session Events**: Creation, validation, revocation
- **Permission Events**: Access granted/denied
- **Account Events**: Lockouts, unlocks, password changes

### Getting Security Statistics

```python
# Get comprehensive security stats
stats = auth_system.get_security_stats()
print(f"Total users: {stats['total_users']}")
print(f"Active sessions: {stats['active_sessions']}")

# Get recent security events
events = auth_system.get_recent_security_events(limit=20)
for event in events:
    print(f"{event['timestamp']}: {event['event_type']} - {event['details']}")
```

### Security Dashboard Data

```python
async def get_security_dashboard_data():
    """Get data for security dashboard."""
    auth_system = get_auth_system()
    
    return {
        "stats": auth_system.get_security_stats(),
        "recent_events": auth_system.get_recent_security_events(50),
        "active_sessions": [
            {
                "session_id": s.session_id[:8] + "...",
                "user_id": s.user_id,
                "created_at": s.created_at.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "ip_address": s.ip_address
            }
            for s in auth_system.sessions.values()
            if s.status.value == "active"
        ]
    }
```

## Rate Limiting

The authentication system includes built-in rate limiting:

### Default Rate Limits
- **Voice Requests**: 100 per minute
- **Code Execution**: 20 per minute  
- **API Requests**: 1000 per hour
- **WebSocket Connections**: 10 per minute

### Custom Rate Limiting

```python
from src.adk_mcp.authentication_system import RateLimitRule

# Add custom rate limit
custom_rule = RateLimitRule(
    name="custom_endpoint",
    max_requests=50,
    time_window_seconds=300,  # 5 minutes
    endpoint_pattern="/api/custom/*"
)

auth_system.rate_limits["custom_endpoint"] = custom_rule
```

## Default Demo Accounts

For development and testing, the system creates default accounts:

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| admin | admin123 | Admin | All admin permissions |
| developer | dev123 | Developer | Development tools access |
| guest | guest123 | Guest | Basic voice interface |

## Best Practices

### Security Best Practices

1. **Change Default Passwords**: Always change default passwords in production
2. **Use Strong Secrets**: Generate strong JWT secrets for production
3. **Enable HTTPS**: Always use HTTPS in production environments
4. **Monitor Events**: Regularly review security event logs
5. **Update Permissions**: Regularly audit and update user permissions

### Development Best Practices

1. **Test Authentication**: Always test authentication flows thoroughly
2. **Handle Errors**: Implement proper error handling for auth failures
3. **Log Security Events**: Log all security-related events
4. **Validate Inputs**: Always validate authentication inputs
5. **Use Middleware**: Implement authentication as middleware for consistency

## Troubleshooting

### Common Issues

#### Authentication Fails
- Check username/password combination
- Verify account is not locked
- Check if user exists and is active

#### Session Expired
- Check token expiration time
- Verify session hasn't been revoked
- Ensure system time is synchronized

#### Permission Denied
- Verify user has required permissions
- Check role assignments
- Review permission mappings

### Debug Commands

```python
# Check user status
user = auth_system.get_user(user_id)
print(f"User active: {user.is_active}")
print(f"Failed attempts: {user.failed_login_attempts}")
print(f"Locked until: {user.locked_until}")

# Check session status
session = auth_system.get_session(session_id)
print(f"Session status: {session.status}")
print(f"Expires at: {session.expires_at}")

# View recent events
events = auth_system.get_recent_security_events(10)
for event in events:
    if event['severity'] in ['warning', 'error']:
        print(f"Issue: {event['event_type']} - {event['details']}")
```

## Integration with ADK

The authentication system integrates seamlessly with ADK components:

### Voice Interface Integration
```python
# Authenticate voice session
async def start_voice_session(username: str, password: str):
    session = await auth_system.authenticate(username, password)
    if session and auth_system.check_permission(session, "voice_interface"):
        # Start voice session
        return session
    return None
```

### Agent Tool Integration
```python
from google.adk.tools import FunctionTool

@FunctionTool
async def secure_code_execution(code: str, session_token: str):
    """Execute code with authentication."""
    session = await auth_system.validate_session(session_token)
    if not session:
        return {"error": "Authentication required"}
    
    if not auth_system.check_permission(session, "code_execution"):
        return {"error": "Insufficient permissions"}
    
    # Execute code securely
    return {"result": "Code executed successfully"}
```

This authentication system provides enterprise-grade security while maintaining ease of use for development and integration with ADK components.