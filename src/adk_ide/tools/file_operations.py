"""File system operation tools for ADK agents."""
from typing import Any, Dict, List, Optional
import os
import pathlib
import re


class FileOperationsTool:
    """File system operations tool for ADK agents."""

    def __init__(self, base_path: Optional[str] = None) -> None:
        self.name = "file_operations"
        self.description = "Read, write, list, and manage files in the project"
        self.base_path = pathlib.Path(base_path) if base_path else pathlib.Path(".")
        # Security: restrict to base_path and subdirectories
        self._allowed_patterns = [
            re.compile(r"^[a-zA-Z0-9_./-]+$"),  # Basic filename pattern
        ]

    def _validate_path(self, file_path: str) -> bool:
        """Validate that file path is safe and within base_path."""
        try:
            resolved = (self.base_path / file_path).resolve()
            base_resolved = self.base_path.resolve()
            # Ensure path is within base_path
            return str(resolved).startswith(str(base_resolved)) and all(
                pattern.match(file_path) for pattern in self._allowed_patterns
            )
        except Exception:
            return False

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file."""
        if not self._validate_path(file_path):
            return {"error": "Invalid or unsafe file path"}
        
        try:
            full_path = self.base_path / file_path
            if not full_path.exists():
                return {"error": "File not found"}
            if not full_path.is_file():
                return {"error": "Path is not a file"}
            
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"status": "success", "content": content, "file_path": file_path}
        except Exception as exc:
            return {"error": str(exc)}

    async def write_file(self, file_path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """Write to a file."""
        if not self._validate_path(file_path):
            return {"error": "Invalid or unsafe file path"}
        
        try:
            full_path = self.base_path / file_path
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, mode, encoding="utf-8") as f:
                f.write(content)
            return {"status": "success", "file_path": file_path, "bytes_written": len(content.encode("utf-8"))}
        except Exception as exc:
            return {"error": str(exc)}

    async def list_directory(self, dir_path: str = ".") -> Dict[str, Any]:
        """List directory contents."""
        if not self._validate_path(dir_path):
            return {"error": "Invalid or unsafe directory path"}
        
        try:
            full_path = self.base_path / dir_path
            if not full_path.exists():
                return {"error": "Directory not found"}
            if not full_path.is_dir():
                return {"error": "Path is not a directory"}
            
            items = []
            for item in full_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            return {"status": "success", "directory": dir_path, "items": items}
        except Exception as exc:
            return {"error": str(exc)}

    async def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operation based on action."""
        action = payload.get("action", "read")
        file_path = payload.get("file_path", "")
        
        if action == "read":
            return await self.read_file(file_path)
        elif action == "write":
            content = payload.get("content", "")
            mode = payload.get("mode", "w")
            return await self.write_file(file_path, content, mode)
        elif action == "list":
            return await self.list_directory(file_path)
        else:
            return {"error": f"Unknown action: {action}"}


def get_file_operations_tool(base_path: Optional[str] = None) -> FileOperationsTool:
    """Get file operations tool."""
    return FileOperationsTool(base_path=base_path)

