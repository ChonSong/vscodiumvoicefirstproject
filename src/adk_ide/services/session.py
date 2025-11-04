from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import os
import jwt
from contextlib import suppress


@dataclass
class ADKIDESessionState:
    """Standardized session state structure (scaffold)."""

    current_project: Optional[str] = None
    active_files: List[str] = field(default_factory=list)
    code_context: Dict[str, str] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    workflow_state: Dict[str, Any] = field(default_factory=dict)
    developing_agent_state: Dict[str, Any] = field(default_factory=dict)
    code_execution_state: Dict[str, Any] = field(default_factory=dict)
    debug_session_state: Dict[str, Any] = field(default_factory=dict)


class ProductionSessionManager:
    """Production-grade session management scaffold.

    This will be wired to VertexAiSessionService/DatabaseSessionService later.
    """

    def __init__(self, environment: str = "development") -> None:
        self.environment = environment
        self.jwt_secret = os.environ.get("ADK_JWT_SECRET", "dev-secret")
        self.jwt_algorithm = "HS256"
        self._adk_service: Optional[object] = None
        # Best-effort ADK session service wiring (optional)
        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            with suppress(Exception):  # pragma: no cover
                # Prefer Vertex AI backed session service if available in ADK
                from google.adk import SessionService  # type: ignore

                # Many ADK installs auto-infer project/location from env
                self._adk_service = SessionService()

    async def create_session(self, user_id: str, project_context: str) -> Dict[str, Any]:
        """Create a new logical session with minimal metadata or via ADK if available."""
        # Try ADK first if wired
        if self._adk_service is not None:  # pragma: no cover
            try:
                # Create a session and attach initial state; shape may vary across ADK versions
                initial_state = ADKIDESessionState(current_project=project_context).__dict__
                create = getattr(self._adk_service, "create", None) or getattr(self._adk_service, "create_session", None)
                if create is not None:
                    adk_session = create(metadata={"user_id": user_id, "project_context": project_context}, state=initial_state)
                    if hasattr(adk_session, "__await__"):
                        adk_session = await adk_session  # type: ignore[func-returns-value]
                    # Normalize into our contract
                    session_id = adk_session.get("session_id") or adk_session.get("id") or f"{user_id}:{datetime.utcnow().timestamp()}"
                    token = self._issue_token(user_id=user_id, session_id=session_id)
                    return {
                        "session_id": session_id,
                        "metadata": adk_session.get("metadata", {"user_id": user_id, "project_context": project_context}),
                        "state": adk_session.get("state", initial_state),
                        "token": token,
                        "provider": "adk",
                    }
            except Exception:
                # Fall through to local implementation
                pass

        # Local scaffold fallback
        session_id = f"{user_id}:{datetime.utcnow().timestamp()}"
        token = self._issue_token(user_id=user_id, session_id=session_id)
        return {
            "session_id": session_id,
            "metadata": {
                "user_id": user_id,
                "project_context": project_context,
                "created_at": datetime.utcnow().isoformat(),
                "security_level": "enterprise" if self.environment != "development" else "dev"
            },
            "state": ADKIDESessionState().__dict__,
            "token": token,
            "provider": "local",
        }

    async def cleanup_expired_sessions(self, hours: int = 24) -> Dict[str, Any]:
        """Placeholder cleanup method."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return {"status": "ok", "cutoff": cutoff_time.isoformat()}

    def _issue_token(self, user_id: str, session_id: str) -> str:
        """Issue a simple JWT for client use."""
        payload = {
            "sub": user_id,
            "sid": session_id,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT and return decoded info or error."""
        try:
            decoded = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return {"valid": True, "claims": decoded}
        except Exception as exc:  # pragma: no cover
            return {"valid": False, "error": str(exc)}

