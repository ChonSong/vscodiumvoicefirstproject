"""
Artifact Management Service

Handles file management, versioning, and storage for the ADK IDE system
using ADK's ArtifactService with enterprise-grade features.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import lru_cache
from enum import Enum

from google.adk.services import ArtifactService, InMemoryArtifactService, GcsArtifactService

from ..config import get_settings


class ArtifactType(str, Enum):
    """Types of artifacts managed by the system."""
    CODE = "code"
    BINARY = "binary"
    CONFIG = "config"
    LOG = "log"
    DOCUMENTATION = "documentation"
    TEST = "test"
    BUILD_ARTIFACT = "build_artifact"


class ADKIDEArtifact:
    """
    Standardized artifact structure for file management.
    
    Represents files and binary data with metadata for IDE operations.
    """
    
    def __init__(
        self,
        artifact_id: str,
        artifact_type: ArtifactType,
        file_path: str,
        content_hash: str,
        version: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ADK IDE artifact.
        
        Args:
            artifact_id: Unique artifact identifier
            artifact_type: Type of artifact
            file_path: File path within project
            content_hash: Content hash for integrity
            version: Artifact version number
            metadata: Additional metadata
        """
        self.artifact_id = artifact_id
        self.artifact_type = artifact_type
        self.file_path = file_path
        self.content_hash = content_hash
        self.version = version
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
        
        # IDE-specific metadata
        self.language: Optional[str] = None
        self.syntax_tree: Optional[Dict] = None
        self.dependencies: List[str] = []
        self.test_coverage: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert artifact to dictionary representation.
        
        Returns:
            Artifact as dictionary
        """
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type.value,
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "language": self.language,
            "syntax_tree": self.syntax_tree,
            "dependencies": self.dependencies,
            "test_coverage": self.test_coverage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ADKIDEArtifact":
        """
        Create artifact from dictionary representation.
        
        Args:
            data: Artifact dictionary
            
        Returns:
            ADKIDEArtifact instance
        """
        artifact = cls(
            artifact_id=data["artifact_id"],
            artifact_type=ArtifactType(data["artifact_type"]),
            file_path=data["file_path"],
            content_hash=data["content_hash"],
            version=data.get("version", 1),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        if "created_at" in data:
            artifact.created_at = datetime.fromisoformat(data["created_at"])
        if "modified_at" in data:
            artifact.modified_at = datetime.fromisoformat(data["modified_at"])
        
        # Set IDE-specific metadata
        artifact.language = data.get("language")
        artifact.syntax_tree = data.get("syntax_tree")
        artifact.dependencies = data.get("dependencies", [])
        artifact.test_coverage = data.get("test_coverage")
        
        return artifact


class EnhancedArtifactManager:
    """
    Enhanced artifact management with IDE-specific features.
    
    Provides file management, versioning, and metadata handling
    for development artifacts.
    """
    
    def __init__(self, artifact_service: ArtifactService):
        """
        Initialize enhanced artifact manager.
        
        Args:
            artifact_service: Underlying ADK artifact service
        """
        self.artifact_service = artifact_service
        self.settings = get_settings()
    
    async def save_code_file(
        self,
        file_path: str,
        content: str,
        language: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ADKIDEArtifact:
        """
        Save code file with IDE-specific metadata.
        
        Args:
            file_path: File path within project
            content: File content
            language: Programming language
            session_id: Session identifier
            
        Returns:
            Created artifact
        """
        # Generate content hash
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Create artifact metadata
        metadata = {
            "file_type": "source_code",
            "encoding": "utf-8",
            "size_bytes": len(content.encode()),
            "line_count": len(content.splitlines())
        }
        
        if session_id:
            metadata["session_id"] = session_id
        
        # Save to artifact service
        artifact_id = await self.artifact_service.save_artifact(
            data=content.encode(),
            metadata=metadata,
            session_id=session_id
        )
        
        # Create ADK IDE artifact
        artifact = ADKIDEArtifact(
            artifact_id=artifact_id,
            artifact_type=ArtifactType.CODE,
            file_path=file_path,
            content_hash=content_hash,
            metadata=metadata
        )
        
        # Set language-specific metadata
        if language:
            artifact.language = language
            artifact.dependencies = await self._extract_dependencies(content, language)
        
        return artifact
    
    async def load_code_file(
        self,
        artifact_id: str,
        session_id: Optional[str] = None
    ) -> tuple[str, ADKIDEArtifact]:
        """
        Load code file with metadata.
        
        Args:
            artifact_id: Artifact identifier
            session_id: Session identifier
            
        Returns:
            Tuple of (content, artifact)
        """
        # Load from artifact service
        data, metadata = await self.artifact_service.load_artifact(
            artifact_id=artifact_id,
            session_id=session_id
        )
        
        # Decode content
        content = data.decode('utf-8')
        
        # Create artifact object
        artifact = ADKIDEArtifact(
            artifact_id=artifact_id,
            artifact_type=ArtifactType.CODE,
            file_path=metadata.get("file_path", ""),
            content_hash=metadata.get("content_hash", ""),
            metadata=metadata
        )
        
        return content, artifact
    
    async def save_build_artifact(
        self,
        file_path: str,
        data: bytes,
        build_info: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> ADKIDEArtifact:
        """
        Save build artifact with build metadata.
        
        Args:
            file_path: Artifact file path
            data: Binary data
            build_info: Build information
            session_id: Session identifier
            
        Returns:
            Created artifact
        """
        # Generate content hash
        import hashlib
        content_hash = hashlib.sha256(data).hexdigest()
        
        # Create metadata
        metadata = {
            "file_type": "build_artifact",
            "size_bytes": len(data),
            "build_info": build_info,
            "created_by": "build_system"
        }
        
        if session_id:
            metadata["session_id"] = session_id
        
        # Save to artifact service
        artifact_id = await self.artifact_service.save_artifact(
            data=data,
            metadata=metadata,
            session_id=session_id
        )
        
        # Create artifact
        artifact = ADKIDEArtifact(
            artifact_id=artifact_id,
            artifact_type=ArtifactType.BUILD_ARTIFACT,
            file_path=file_path,
            content_hash=content_hash,
            metadata=metadata
        )
        
        return artifact
    
    async def list_project_files(
        self,
        project_id: str,
        file_type: Optional[ArtifactType] = None
    ) -> List[ADKIDEArtifact]:
        """
        List all files in a project.
        
        Args:
            project_id: Project identifier
            file_type: Optional file type filter
            
        Returns:
            List of project artifacts
        """
        # This would integrate with the artifact service's listing capabilities
        # Placeholder implementation
        artifacts = []
        
        # In a real implementation, this would query the artifact service
        # for artifacts associated with the project
        
        return artifacts
    
    async def get_file_history(
        self,
        file_path: str,
        project_id: str
    ) -> List[ADKIDEArtifact]:
        """
        Get version history for a file.
        
        Args:
            file_path: File path
            project_id: Project identifier
            
        Returns:
            List of file versions
        """
        # Placeholder implementation for file history
        # Would integrate with artifact service versioning
        return []
    
    async def _extract_dependencies(
        self,
        content: str,
        language: str
    ) -> List[str]:
        """
        Extract dependencies from code content.
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        # Simple dependency extraction based on language
        if language.lower() == "python":
            import re
            # Extract import statements
            import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(\S+)'
            matches = re.findall(import_pattern, content, re.MULTILINE)
            
            for from_module, import_name in matches:
                if from_module:
                    dependencies.append(from_module)
                else:
                    dependencies.append(import_name)
        
        elif language.lower() in ["javascript", "typescript"]:
            import re
            # Extract require/import statements
            require_pattern = r'(?:require|import)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
            
            requires = re.findall(require_pattern, content)
            imports = re.findall(import_pattern, content)
            
            dependencies.extend(requires)
            dependencies.extend(imports)
        
        # Remove duplicates and system modules
        dependencies = list(set(dependencies))
        dependencies = [dep for dep in dependencies if not dep.startswith('.')]
        
        return dependencies


@lru_cache()
def get_artifact_service() -> ArtifactService:
    """
    Get cached artifact service instance.
    
    Returns:
        Configured artifact service
    """
    settings = get_settings()
    
    if settings.is_production:
        # Use GCS artifact service for production
        return GcsArtifactService(
            bucket_name=f"{settings.google_cloud_project}-adk-ide-artifacts",
            project_id=settings.google_cloud_project
        )
    else:
        # Use in-memory service for development
        return InMemoryArtifactService()


@lru_cache()
def get_enhanced_artifact_manager() -> EnhancedArtifactManager:
    """
    Get cached enhanced artifact manager.
    
    Returns:
        Enhanced artifact manager instance
    """
    artifact_service = get_artifact_service()
    return EnhancedArtifactManager(artifact_service)