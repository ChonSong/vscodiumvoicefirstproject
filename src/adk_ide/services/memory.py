"""Memory Service wrapper for ADK IDE system.

Provides long-term knowledge persistence using ADK's MemoryService with
VertexAiRagMemoryService for production and scalable knowledge retrieval.
"""
from typing import Any, Dict, Optional, List
import os
from contextlib import suppress


class MemoryService:
    """Wrapper for ADK MemoryService with VertexAiRagMemoryService support.
    
    Manages long-term knowledge that persists across sessions, allowing agents
    to recall information about users and access external knowledge bases.
    """

    def __init__(self, environment: str = "development") -> None:
        self.environment = environment
        self._adk_service: Optional[object] = None
        
        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            with suppress(Exception):  # pragma: no cover
                # Prefer VertexAiRagMemoryService for production
                if environment == "production":
                    try:
                        from google.adk.memory_services import VertexAiRagMemoryService  # type: ignore
                        self._adk_service = VertexAiRagMemoryService()
                    except Exception:
                        # Fallback to InMemory if Vertex AI unavailable
                        from google.adk.memory_services import InMemoryMemoryService  # type: ignore
                        self._adk_service = InMemoryMemoryService()
                else:
                    from google.adk.memory_services import InMemoryMemoryService  # type: ignore
                    self._adk_service = InMemoryMemoryService()

    async def save(
        self,
        user_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Save knowledge to memory service.
        
        Args:
            user_id: User identifier for user-specific knowledge
            content: Content to store in memory
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary with memory_id and status
        """
        if self._adk_service is not None:  # pragma: no cover
            try:
                save_method = getattr(self._adk_service, "save", None) or getattr(self._adk_service, "save_memory", None)
                if save_method is not None:
                    result = save_method(
                        user_id=user_id,
                        content=content,
                        metadata=metadata or {},
                    )
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    return {
                        "status": "success",
                        "memory_id": result.get("memory_id") or result.get("id"),
                        "metadata": result.get("metadata", {}),
                    }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        # Fallback: local storage simulation
        memory_id = f"{user_id}:{hash(content)}"
        return {
            "status": "success",
            "memory_id": memory_id,
            "metadata": metadata or {},
            "provider": "local",
        }

    async def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Search memory using semantic search.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results
        """
        if self._adk_service is not None:  # pragma: no cover
            try:
                search_method = getattr(self._adk_service, "search", None) or getattr(self._adk_service, "search_memory", None)
                if search_method is not None:
                    result = search_method(
                        user_id=user_id,
                        query=query,
                        limit=limit,
                    )
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    
                    return {
                        "status": "success",
                        "results": result.get("results") or result.get("items", []),
                        "count": len(result.get("results") or result.get("items", [])),
                    }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        # Fallback: return empty results
        return {
            "status": "success",
            "results": [],
            "count": 0,
            "provider": "local",
        }

    async def load_memory(
        self,
        user_id: str,
        memory_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Load memory by ID or all memories for user.
        
        Args:
            user_id: User identifier
            memory_id: Optional specific memory ID
            
        Returns:
            Dictionary with memory content
        """
        if memory_id and self._adk_service is not None:  # pragma: no cover
            try:
                load_method = getattr(self._adk_service, "load", None) or getattr(self._adk_service, "load_memory", None)
                if load_method is not None:
                    result = load_method(user_id=user_id, memory_id=memory_id)
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    return {
                        "status": "success",
                        "content": result.get("content") or result.get("data"),
                        "metadata": result.get("metadata", {}),
                    }
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        # Fallback: use search to get all memories
        return await self.search(user_id=user_id, query="", limit=100)

    async def delete(
        self,
        user_id: str,
        memory_id: str,
    ) -> Dict[str, Any]:
        """Delete a memory entry.
        
        Args:
            user_id: User identifier
            memory_id: Memory ID to delete
            
        Returns:
            Dictionary with deletion status
        """
        if self._adk_service is not None:  # pragma: no cover
            try:
                delete_method = getattr(self._adk_service, "delete", None) or getattr(self._adk_service, "delete_memory", None)
                if delete_method is not None:
                    result = delete_method(user_id=user_id, memory_id=memory_id)
                    if hasattr(result, "__await__"):
                        result = await result  # type: ignore[func-returns-value]
                    return {"status": "success", "deleted": True}
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

        return {"status": "success", "deleted": True, "provider": "local"}


class ToolContextMemoryMethods:
    """Mixin class providing search_memory and load_memory methods for tool context.
    
    This can be used to extend tool context objects with memory management capabilities.
    """
    
    def __init__(self, memory_service: MemoryService, user_id: str):
        self.memory_service = memory_service
        self.user_id = user_id
    
    async def search_memory(
        self,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Search memory using the current user context.
        
        This method is intended to be called from tool implementations.
        """
        return await self.memory_service.search(
            user_id=self.user_id,
            query=query,
            limit=limit,
        )
    
    async def load_memory(
        self,
        memory_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Load memory using the current user context.
        
        This method is intended to be called from tool implementations.
        """
        return await self.memory_service.load_memory(
            user_id=self.user_id,
            memory_id=memory_id,
        )

