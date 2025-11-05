"""Code Map Agent for visual structure overview."""
from typing import Any, Dict, Optional, Callable, List
import os

from .base import ADKIDEAgent
from .section_detection import SectionDetectionAgent


class CodeMapAgent(ADKIDEAgent):
    """Code map agent with visual structure overview.
    
    Generates visual representations of code structure including:
    - Hierarchical section tree
    - Function/class relationships
    - Code flow visualization
    - Dependency graphs
    """

    def __init__(self, section_detector: Optional[SectionDetectionAgent] = None) -> None:
        super().__init__(
            name="code_map_agent",
            description="Visual structure overview and code mapping"
        )
        self.section_detector = section_detector or SectionDetectionAgent()
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="CodeMapAgent",
                    description="Generates visual representations of code structure including hierarchical trees, function relationships, code flow, and dependency graphs",
                    instruction="You are a code mapping specialist. Analyze code structure and create comprehensive visual overviews showing hierarchy, relationships, dependencies, and flow. Provide both textual and structured representations suitable for visualization.",
                    output_key="code_map",  # Save code map to session.state
                )
                run_method = getattr(self._llm_agent, "run", None)
                run_async_method = getattr(self._llm_agent, "run_async", None)
                if run_async_method is not None:
                    self._llm_agent_run = run_async_method
                elif run_method is not None:
                    self._llm_agent_run = run_method
            except Exception:
                self._llm_agent = None
                self._llm_agent_run = None

    def generate_code_map(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate visual code map structure."""
        sections = self.section_detector.detect_sections(code, language)
        
        # Build tree structure
        tree = self._build_tree(sections)
        
        # Calculate statistics
        stats = {
            "total_sections": len(sections),
            "functions": len([s for s in sections if s.section_type == "function"]),
            "classes": len([s for s in sections if s.section_type == "class"]),
            "regions": len([s for s in sections if s.section_type == "region"]),
            "max_depth": max([s.level for s in sections], default=0),
            "total_lines": len(code.split("\n")),
        }
        
        # Generate text representation
        text_map = self._generate_text_map(tree, sections)
        
        # Generate graph data (for visualization)
        graph_data = self._generate_graph_data(sections)
        
        return {
            "tree": tree,
            "stats": stats,
            "text_map": text_map,
            "graph_data": graph_data,
            "sections": [
                {
                    "name": s.name,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "level": s.level,
                    "section_type": s.section_type,
                    "parent": s.parent,
                }
                for s in sections
            ],
        }

    def _build_tree(self, sections: List) -> Dict[str, Any]:
        """Build hierarchical tree structure."""
        tree = {}
        root_sections = [s for s in sections if s.parent is None]
        
        for section in root_sections:
            children = [s for s in sections if s.parent == section.name]
            tree[section.name] = {
                "section": {
                    "name": section.name,
                    "type": section.section_type,
                    "lines": (section.start_line, section.end_line),
                    "level": section.level,
                },
                "children": self._build_tree(children) if children else {},
            }
        
        return tree

    def _generate_text_map(self, tree: Dict[str, Any], sections: List) -> str:
        """Generate text representation of code map."""
        lines = []
        lines.append("Code Structure Map")
        lines.append("=" * 50)
        
        def add_node(node_dict: Dict[str, Any], prefix: str = "", is_last: bool = True):
            for i, (name, data) in enumerate(node_dict.items()):
                is_last_item = i == len(node_dict) - 1
                connector = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{connector}{name} ({data['section']['type']})")
                
                if data["children"]:
                    next_prefix = prefix + ("    " if is_last_item else "│   ")
                    add_node(data["children"], next_prefix, is_last_item)
        
        add_node(tree)
        return "\n".join(lines)

    def _generate_graph_data(self, sections: List) -> Dict[str, Any]:
        """Generate graph data for visualization."""
        nodes = []
        edges = []
        
        for section in sections:
            nodes.append({
                "id": section.name,
                "label": section.name,
                "type": section.section_type,
                "level": section.level,
                "lines": (section.start_line, section.end_line),
            })
            
            if section.parent:
                edges.append({
                    "from": section.parent,
                    "to": section.name,
                    "type": "parent",
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
        }

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process code map generation requests."""
        code = request.get("code", "")
        language = request.get("language", "python")
        format_type = request.get("format", "full")
        
        if code:
            code_map = self.generate_code_map(code, language)
            
            # Return requested format
            if format_type == "tree":
                return {
                    "status": "success",
                    "agent": self.name,
                    "tree": code_map["tree"],
                }
            elif format_type == "stats":
                return {
                    "status": "success",
                    "agent": self.name,
                    "stats": code_map["stats"],
                }
            elif format_type == "graph":
                return {
                    "status": "success",
                    "agent": self.name,
                    "graph_data": code_map["graph_data"],
                }
            elif format_type == "text":
                return {
                    "status": "success",
                    "agent": self.name,
                    "text_map": code_map["text_map"],
                }
            else:
                return {
                    "status": "success",
                    "agent": self.name,
                    **code_map,
                }
        
        # Use LLM agent for enhanced analysis
        if self._llm_agent is not None and self._llm_agent_run is not None:  # pragma: no cover
            try:
                result = self._llm_agent_run(request)
                if hasattr(result, "__await__"):
                    result = await result  # type: ignore[func-returns-value]
                return {"status": "success", "agent": self.name, "result": result}
            except Exception as exc:
                return {"status": "error", "agent": self.name, "error": str(exc)}

        # Fallback
        return {
            "status": "success",
            "agent": self.name,
            "message": "Provide code to generate code map",
        }

