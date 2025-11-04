"""
Memory Management Service

Handles long-term knowledge persistence and retrieval for the ADK IDE system
using ADK's MemoryService with enhanced learning capabilities.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import lru_cache
from enum import Enum

from google.adk.services import MemoryService, InMemoryMemoryService, VertexAiRagMemoryService

from ..config import get_settings


class MemoryType(str, Enum):
    """Types of memory entries in the system."""
    CODE_PATTERN = "code_pattern"
    ERROR_SOLUTION = "error_solution"
    BEST_PRACTICE = "best_practice"
    USER_PREFERENCE = "user_preference"
    PROJECT_CONTEXT = "project_context"
    DEBUGGING_SOLUTION = "debugging_solution"
    PERFORMANCE_TIP = "performance_tip"


class ADKIDEMemoryEntry:
    """
    Long-term memory structure for knowledge persistence.
    
    Represents learned knowledge that can be retrieved and applied
    across development sessions.
    """
    
    def __init__(
        self,
        entry_id: str,
        entry_type: MemoryType,
        content: str,
        relevance_score: float = 1.0,
        usage_count: int = 0,
        project_context: Optional[str] = None,
        language_context: Optional[str] = None,
        framework_context: Optional[str] = None
    ):
        """
        Initialize memory entry.
        
        Args:
            entry_id: Unique entry identifier
            entry_type: Type of memory entry
            content: Memory content
            relevance_score: Relevance score (0.0 to 1.0)
            usage_count: Number of times used
            project_context: Associated project context
            language_context: Programming language context
            framework_context: Framework context
        """
        self.entry_id = entry_id
        self.entry_type = entry_type
        self.content = content
        self.relevance_score = relevance_score
        self.usage_count = usage_count
        
        # Contextual information
        self.project_context = project_context
        self.language_context = language_context
        self.framework_context = framework_context
        
        # Temporal information
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.success_rate = 1.0  # Success rate when applied
        
        # Embeddings (set by memory service)
        self.embeddings: List[float] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert memory entry to dictionary.
        
        Returns:
            Memory entry as dictionary
        """
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type.value,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "usage_count": self.usage_count,
            "project_context": self.project_context,
            "language_context": self.language_context,
            "framework_context": self.framework_context,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "success_rate": self.success_rate,
            "embeddings": self.embeddings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ADKIDEMemoryEntry":
        """
        Create memory entry from dictionary.
        
        Args:
            data: Memory entry dictionary
            
        Returns:
            ADKIDEMemoryEntry instance
        """
        entry = cls(
            entry_id=data["entry_id"],
            entry_type=MemoryType(data["entry_type"]),
            content=data["content"],
            relevance_score=data.get("relevance_score", 1.0),
            usage_count=data.get("usage_count", 0),
            project_context=data.get("project_context"),
            language_context=data.get("language_context"),
            framework_context=data.get("framework_context")
        )
        
        # Set temporal information
        if "created_at" in data:
            entry.created_at = datetime.fromisoformat(data["created_at"])
        if "last_accessed" in data:
            entry.last_accessed = datetime.fromisoformat(data["last_accessed"])
        
        entry.success_rate = data.get("success_rate", 1.0)
        entry.embeddings = data.get("embeddings", [])
        
        return entry
    
    def update_usage(self, success: bool = True) -> None:
        """
        Update usage statistics.
        
        Args:
            success: Whether the memory was successfully applied
        """
        self.usage_count += 1
        self.last_accessed = datetime.utcnow()
        
        # Update success rate using exponential moving average
        alpha = 0.1  # Learning rate
        if success:
            self.success_rate = (1 - alpha) * self.success_rate + alpha * 1.0
        else:
            self.success_rate = (1 - alpha) * self.success_rate + alpha * 0.0
        
        # Update relevance score based on usage and success
        usage_factor = min(self.usage_count / 10.0, 1.0)  # Cap at 10 uses
        self.relevance_score = 0.5 * self.success_rate + 0.3 * usage_factor + 0.2 * self.relevance_score


class EnhancedMemoryManager:
    """
    Enhanced memory management with learning capabilities.
    
    Provides intelligent knowledge storage, retrieval, and learning
    from development sessions and user interactions.
    """
    
    def __init__(self, memory_service: MemoryService):
        """
        Initialize enhanced memory manager.
        
        Args:
            memory_service: Underlying ADK memory service
        """
        self.memory_service = memory_service
        self.settings = get_settings()
    
    async def store_code_pattern(
        self,
        pattern_description: str,
        code_example: str,
        language: str,
        framework: Optional[str] = None,
        project_context: Optional[str] = None
    ) -> ADKIDEMemoryEntry:
        """
        Store a code pattern for future reference.
        
        Args:
            pattern_description: Description of the pattern
            code_example: Code example demonstrating the pattern
            language: Programming language
            framework: Optional framework context
            project_context: Optional project context
            
        Returns:
            Created memory entry
        """
        # Create memory content
        content = f"Pattern: {pattern_description}\n\nExample:\n```{language}\n{code_example}\n```"
        
        # Generate entry ID
        import hashlib
        entry_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create memory entry
        entry = ADKIDEMemoryEntry(
            entry_id=entry_id,
            entry_type=MemoryType.CODE_PATTERN,
            content=content,
            language_context=language,
            framework_context=framework,
            project_context=project_context
        )
        
        # Store in memory service
        await self._store_memory_entry(entry)
        
        return entry
    
    async def store_error_solution(
        self,
        error_message: str,
        solution: str,
        language: Optional[str] = None,
        context: Optional[str] = None
    ) -> ADKIDEMemoryEntry:
        """
        Store an error solution for future reference.
        
        Args:
            error_message: Error message or description
            solution: Solution or fix for the error
            language: Programming language context
            context: Additional context
            
        Returns:
            Created memory entry
        """
        # Create memory content
        content = f"Error: {error_message}\n\nSolution: {solution}"
        if context:
            content += f"\n\nContext: {context}"
        
        # Generate entry ID
        import hashlib
        entry_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create memory entry
        entry = ADKIDEMemoryEntry(
            entry_id=entry_id,
            entry_type=MemoryType.ERROR_SOLUTION,
            content=content,
            language_context=language
        )
        
        # Store in memory service
        await self._store_memory_entry(entry)
        
        return entry
    
    async def store_best_practice(
        self,
        practice_description: str,
        example: Optional[str] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> ADKIDEMemoryEntry:
        """
        Store a best practice for future reference.
        
        Args:
            practice_description: Description of the best practice
            example: Optional example demonstrating the practice
            language: Programming language context
            framework: Framework context
            
        Returns:
            Created memory entry
        """
        # Create memory content
        content = f"Best Practice: {practice_description}"
        if example:
            content += f"\n\nExample: {example}"
        
        # Generate entry ID
        import hashlib
        entry_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create memory entry
        entry = ADKIDEMemoryEntry(
            entry_id=entry_id,
            entry_type=MemoryType.BEST_PRACTICE,
            content=content,
            language_context=language,
            framework_context=framework
        )
        
        # Store in memory service
        await self._store_memory_entry(entry)
        
        return entry
    
    async def search_relevant_knowledge(
        self,
        query: str,
        entry_type: Optional[MemoryType] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        max_results: int = 5
    ) -> List[ADKIDEMemoryEntry]:
        """
        Search for relevant knowledge entries.
        
        Args:
            query: Search query
            entry_type: Optional entry type filter
            language: Optional language filter
            framework: Optional framework filter
            max_results: Maximum number of results
            
        Returns:
            List of relevant memory entries
        """
        # Use memory service search capabilities
        search_results = await self.memory_service.search_memory(
            query=query,
            max_results=max_results
        )
        
        # Convert results to ADKIDEMemoryEntry objects
        entries = []
        for result in search_results:
            # This would need to be adapted based on the actual MemoryService API
            # Placeholder implementation
            entry = ADKIDEMemoryEntry(
                entry_id=result.get("id", ""),
                entry_type=MemoryType.CODE_PATTERN,  # Default type
                content=result.get("content", ""),
                relevance_score=result.get("score", 0.0)
            )
            entries.append(entry)
        
        # Apply filters
        if entry_type:
            entries = [e for e in entries if e.entry_type == entry_type]
        
        if language:
            entries = [e for e in entries if e.language_context == language]
        
        if framework:
            entries = [e for e in entries if e.framework_context == framework]
        
        return entries[:max_results]
    
    async def get_error_solutions(
        self,
        error_message: str,
        language: Optional[str] = None
    ) -> List[ADKIDEMemoryEntry]:
        """
        Get solutions for a specific error.
        
        Args:
            error_message: Error message to search for
            language: Optional language context
            
        Returns:
            List of relevant error solutions
        """
        return await self.search_relevant_knowledge(
            query=f"error {error_message}",
            entry_type=MemoryType.ERROR_SOLUTION,
            language=language,
            max_results=3
        )
    
    async def get_code_patterns(
        self,
        pattern_query: str,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> List[ADKIDEMemoryEntry]:
        """
        Get code patterns matching a query.
        
        Args:
            pattern_query: Pattern search query
            language: Optional language context
            framework: Optional framework context
            
        Returns:
            List of relevant code patterns
        """
        return await self.search_relevant_knowledge(
            query=pattern_query,
            entry_type=MemoryType.CODE_PATTERN,
            language=language,
            framework=framework,
            max_results=5
        )
    
    async def learn_from_correction(
        self,
        original_code: str,
        corrected_code: str,
        error_type: str,
        language: str
    ) -> ADKIDEMemoryEntry:
        """
        Learn from code corrections to improve future suggestions.
        
        Args:
            original_code: Original code with error
            corrected_code: Corrected code
            error_type: Type of error that was corrected
            language: Programming language
            
        Returns:
            Created memory entry
        """
        # Create learning content
        content = f"Error Type: {error_type}\n\nOriginal Code:\n{original_code}\n\nCorrected Code:\n{corrected_code}"
        
        # Generate entry ID
        import hashlib
        entry_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create memory entry
        entry = ADKIDEMemoryEntry(
            entry_id=entry_id,
            entry_type=MemoryType.ERROR_SOLUTION,
            content=content,
            language_context=language,
            relevance_score=0.8  # High relevance for learned corrections
        )
        
        # Store in memory service
        await self._store_memory_entry(entry)
        
        return entry
    
    async def _store_memory_entry(self, entry: ADKIDEMemoryEntry) -> None:
        """
        Store memory entry in the underlying memory service.
        
        Args:
            entry: Memory entry to store
        """
        # This would integrate with the actual MemoryService API
        # Placeholder implementation
        await self.memory_service.store_memory(
            content=entry.content,
            metadata=entry.to_dict()
        )
    
    async def update_entry_usage(
        self,
        entry_id: str,
        success: bool = True
    ) -> None:
        """
        Update usage statistics for a memory entry.
        
        Args:
            entry_id: Entry identifier
            success: Whether the entry was successfully applied
        """
        # This would retrieve, update, and store the entry
        # Placeholder implementation
        pass


@lru_cache()
def get_memory_service() -> MemoryService:
    """
    Get cached memory service instance.
    
    Returns:
        Configured memory service
    """
    settings = get_settings()
    
    if settings.is_production:
        # Use Vertex AI RAG memory service for production
        return VertexAiRagMemoryService(
            project_id=settings.google_cloud_project,
            location=settings.google_cloud_region
        )
    else:
        # Use in-memory service for development
        return InMemoryMemoryService()


@lru_cache()
def get_enhanced_memory_manager() -> EnhancedMemoryManager:
    """
    Get cached enhanced memory manager.
    
    Returns:
        Enhanced memory manager instance
    """
    memory_service = get_memory_service()
    return EnhancedMemoryManager(memory_service)