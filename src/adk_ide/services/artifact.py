"""Artifact service wrapper for ADK IDE system.

Provides persistent storage for non-textual data (files, logs, build reports, etc.)
using ADK's ArtifactService with GCS backend for production.
"""
from typing import Any, Dict, Optional, BinaryIO
import os
from contextlib import suppress


class ArtifactService:
    """Wrapper for ADK ArtifactService with GCS backend support.
    
    Manages versioned artifacts (files, binaries, logs) associated with sessions.
    Provides tool_context.save_artifact and tool_context.load_artifact methods.
    """

    def __init__(self, environment: str = "development") -> None:
        self.environment = environment
        self._adk_service: Optional[object] = None
        self._local_store: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            with suppress(Exception):  # pragma: no cover
                # Prefer GcsArtifactService for production, InMemoryArtifactService for dev
                if environment == "production":
                    try:
                        from google.adk.artifact_services import GcsArtifactService  # type: ignore
                        self._adk_service = GcsArtifactService()
                    except Exception:
                        # Fallback to InMemory if GCS unavailable
                        from google.adk.artifact_services import InMemoryArtifactService  # type: ignore
                        self._adk_service = InMemoryArtifactService()
                else:
                    from google.adk.artifact_services import InMemoryArtifactService  # type: ignore
                    self._adk_service = InMemoryArtifactService()

    async def save_artifact(
        self,
        session_id: str,
        artifact_name: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Save an artifact (file/binary data) associated with a session.
        
        Args:
            session_id: Session identifier
            artifact_name: Name/identifier for the artifact
            content: Binary content to save
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary with artifact_id, version, and other metadata
        """
        if self._adk_service is not None:  # pragma: no cover
            try:
                save_method = getattr(self._adk_service, "save", None) or getattr(self._adk_service, "save_artifact", None)
                if save_method is not None:
                    result = save_method(
                        session_id=session_id,
                        artifact_name=artifact_name,
                        content=content,
                        metadata=metadata or {},
                    )
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    return {
                        "status": "success",
                        "artifact_id": result.get("artifact_id") or result.get("id"),
                        "version": result.get("version", 1),
                        "metadata": result.get("metadata", {}),
                    }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        # Fallback: local in-memory storage
        session_store = self._local_store.setdefault(session_id, {})
        session_store[artifact_name] = {
            "content": content,
            "metadata": metadata or {},
            "version": 1,
        }
        artifact_id = f"{session_id}/{artifact_name}"
        return {
            "status": "success",
            "artifact_id": artifact_id,
            "version": 1,
            "metadata": metadata or {},
            "provider": "local",
        }

    async def load_artifact(
        self,
        session_id: str,
        artifact_name: str,
        version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Load an artifact by name and optional version.
        
        Args:
            session_id: Session identifier
            artifact_name: Name/identifier for the artifact
            version: Optional version number (defaults to latest)
            
        Returns:
            Dictionary with content (bytes) and metadata
        """
        if self._adk_service is not None:  # pragma: no cover
            try:
                load_method = getattr(self._adk_service, "load", None) or getattr(self._adk_service, "load_artifact", None)
                if load_method is not None:
                    kwargs = {"session_id": session_id, "artifact_name": artifact_name}
                    if version is not None:
                        kwargs["version"] = version
                    
                    result = load_method(**kwargs)
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    
                    return {
                        "status": "success",
                        "content": result.get("content") or result.get("data"),
                        "metadata": result.get("metadata", {}),
                        "version": result.get("version", 1),
                    }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        # Fallback: return from in-memory store
        session_store = self._local_store.get(session_id, {})
        artifact = session_store.get(artifact_name)
        if artifact:
            return {
                "status": "success",
                "content": artifact.get("content", b""),
                "metadata": artifact.get("metadata", {}),
                "version": artifact.get("version", 1),
                "provider": "local",
            }
        return {
            "status": "not_found",
            "content": b"",
            "metadata": {},
            "version": None,
            "provider": "local",
        }

    async def list_artifacts(self, session_id: str) -> Dict[str, Any]:
        """List all artifacts for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with list of artifact names and metadata
        """
        if self._adk_service is not None:  # pragma: no cover
            try:
                list_method = getattr(self._adk_service, "list", None) or getattr(self._adk_service, "list_artifacts", None)
                if list_method is not None:
                    result = list_method(session_id=session_id)
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    return {
                        "status": "success",
                        "artifacts": result.get("artifacts") or result.get("items", []),
                    }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        session_store = self._local_store.get(session_id, {})
        artifacts = [
            {
                "name": name,
                "metadata": data.get("metadata", {}),
                "version": data.get("version", 1),
            }
            for name, data in session_store.items()
        ]
        return {"status": "success", "artifacts": artifacts, "provider": "local"}


class ToolContextArtifactMethods:
    """Mixin class providing save_artifact and load_artifact methods for tool context.
    
    This can be used to extend tool context objects with artifact management capabilities.
    """
    
    def __init__(self, artifact_service: ArtifactService, session_id: str):
        self.artifact_service = artifact_service
        self.session_id = session_id
    
    async def save_artifact(
        self,
        artifact_name: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Save an artifact using the current session context.
        
        This method is intended to be called from tool implementations.
        """
        return await self.artifact_service.save_artifact(
            session_id=self.session_id,
            artifact_name=artifact_name,
            content=content,
            metadata=metadata,
        )
    
    async def load_artifact(
        self,
        artifact_name: str,
        version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Load an artifact using the current session context.
        
        This method is intended to be called from tool implementations.
        """
        return await self.artifact_service.load_artifact(
            session_id=self.session_id,
            artifact_name=artifact_name,
            version=version,
        )

