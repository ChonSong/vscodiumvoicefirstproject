"""Memory tools for ADK agents - load_memory tool implementation."""
from typing import Any, Dict, Optional
import os

from ..services.memory import MemoryService


def create_load_memory_tool(memory_service: MemoryService, user_id: str):
    """Create a load_memory tool for use in agents.
    
    Args:
        memory_service: MemoryService instance
        user_id: Current user ID
        
    Returns:
        Tool object that can be added to agent tools list
    """
    class LoadMemoryTool:
        name = "load_memory"
        description = "Query long-term memory to recall information about the user, project, or previous sessions. Use this to access knowledge that persists across sessions."

        def __init__(self, service: MemoryService, uid: str):
            self.memory_service = service
            self.user_id = uid

        async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
            """Execute memory search/load.
            
            Args in payload:
                - query: Search query string (required for search)
                - memory_id: Optional specific memory ID to load
                - limit: Maximum results (default 5)
            """
            query = payload.get("query", "")
            memory_id = payload.get("memory_id")
            limit = payload.get("limit", 5)
            
            if memory_id:
                # Load specific memory
                result = await self.memory_service.load_memory(
                    user_id=self.user_id,
                    memory_id=memory_id,
                )
                return result
            elif query:
                # Search memory
                result = await self.memory_service.search(
                    user_id=self.user_id,
                    query=query,
                    limit=limit,
                )
                return result
            else:
                return {
                    "status": "error",
                    "error": "Either 'query' or 'memory_id' must be provided",
                }
    
    return LoadMemoryTool(memory_service, user_id)

