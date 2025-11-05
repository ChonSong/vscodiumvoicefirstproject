"""Section Detection Agent for automatic code section identification."""
from typing import Any, Dict, Optional, Callable, List
import os
import re
from dataclasses import dataclass

from .base import ADKIDEAgent


@dataclass
class CodeSection:
    """Represents a detected code section."""
    name: str
    start_line: int
    end_line: int
    level: int  # Hierarchical level (0 = top level)
    section_type: str  # "function", "class", "comment_block", "region"
    parent: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SectionDetectionAgent(ADKIDEAgent):
    """Agent for automatic code section identification.
    
    Detects code sections using:
    - Comment-based patterns (standardized syntax)
    - Semantic analysis (functions, classes, blocks)
    - Hierarchical structure with parent-child relationships
    """

    def __init__(self) -> None:
        super().__init__(
            name="section_detection_agent",
            description="Automatic code section identification using comment patterns and semantic analysis"
        )
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None
        
        # Standardized comment patterns for section detection
        self.section_patterns = {
            "region": [
                r"#\s*region\s+(.+)$",  # # region SectionName
                r"#\s*<region\s+(.+)>$",  # # <region SectionName>
                r"//\s*region\s+(.+)$",  # // region SectionName (JS/TS)
            ],
            "end_region": [
                r"#\s*endregion",
                r"#\s*</region>",
                r"//\s*endregion",
            ],
            "section": [
                r"#\s*===\s*(.+)\s*===$",  # # === Section Name ===
                r"#\s*---\s*(.+)\s*---$",  # # --- Section Name ---
                r"#\s*###\s*(.+)$",  # # ### Section Name
            ],
        }

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="SectionDetectionAgent",
                    description="Detects code sections automatically using comment patterns and semantic analysis. Identifies functions, classes, comment-based regions, and hierarchical structures.",
                    instruction="You are a code section detection specialist. Analyze code to identify logical sections, functions, classes, and comment-based regions. Provide hierarchical structure with parent-child relationships.",
                    output_key="detected_sections",  # Save sections to session.state
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

    def detect_sections(self, code: str, language: str = "python") -> List[CodeSection]:
        """Detect code sections from source code."""
        lines = code.split("\n")
        sections: List[CodeSection] = []
        region_stack: List[CodeSection] = []  # Track nested regions
        
        current_function = None
        current_class = None
        function_start = None
        class_start = None
        level = 0

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Check for region markers
            for pattern in self.section_patterns["region"]:
                match = re.match(pattern, stripped, re.IGNORECASE)
                if match:
                    section_name = match.group(1).strip()
                    section = CodeSection(
                        name=section_name,
                        start_line=line_num,
                        end_line=line_num,  # Will be updated when end_region found
                        level=len(region_stack),
                        section_type="region",
                        parent=region_stack[-1].name if region_stack else None,
                    )
                    region_stack.append(section)
                    sections.append(section)
                    continue
            
            # Check for end region markers
            for pattern in self.section_patterns["end_region"]:
                if re.match(pattern, stripped, re.IGNORECASE):
                    if region_stack:
                        region_stack[-1].end_line = line_num
                        region_stack.pop()
                    continue
            
            # Check for section markers (single-line sections)
            for pattern in self.section_patterns["section"]:
                match = re.match(pattern, stripped, re.IGNORECASE)
                if match:
                    section_name = match.group(1).strip()
                    sections.append(CodeSection(
                        name=section_name,
                        start_line=line_num,
                        end_line=line_num,
                        level=len(region_stack),
                        section_type="section",
                        parent=region_stack[-1].name if region_stack else None,
                    ))
                    continue
            
            # Detect functions (Python)
            if language == "python":
                func_match = re.match(r"^def\s+(\w+)\s*\(", stripped)
                if func_match:
                    if current_function:
                        # End previous function
                        sections.append(CodeSection(
                            name=current_function,
                            start_line=function_start,
                            end_line=line_num - 1,
                            level=1 if current_class else 0,
                            section_type="function",
                            parent=current_class,
                        ))
                    current_function = func_match.group(1)
                    function_start = line_num
                    continue
                
                # Detect classes
                class_match = re.match(r"^class\s+(\w+)", stripped)
                if class_match:
                    if current_class:
                        # End previous class
                        sections.append(CodeSection(
                            name=current_class,
                            start_line=class_start,
                            end_line=line_num - 1,
                            level=0,
                            section_type="class",
                            parent=None,
                        ))
                    current_class = class_match.group(1)
                    class_start = line_num
                    current_function = None  # Reset function
                    continue
            
            # Detect functions (JavaScript/TypeScript)
            elif language in ["javascript", "typescript"]:
                func_match = re.match(r"^(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)", stripped)
                if func_match:
                    func_name = func_match.group(1) or func_match.group(2)
                    if current_function:
                        sections.append(CodeSection(
                            name=current_function,
                            start_line=function_start,
                            end_line=line_num - 1,
                            level=0,
                            section_type="function",
                            parent=None,
                        ))
                    current_function = func_name
                    function_start = line_num
                    continue
        
        # Close any remaining sections
        if current_function and function_start:
            sections.append(CodeSection(
                name=current_function,
                start_line=function_start,
                end_line=len(lines),
                level=1 if current_class else 0,
                section_type="function",
                parent=current_class,
            ))
        
        if current_class and class_start:
            sections.append(CodeSection(
                name=current_class,
                start_line=class_start,
                end_line=len(lines),
                level=0,
                section_type="class",
                parent=None,
            ))
        
        return sections

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process section detection requests."""
        code = request.get("code", "")
        language = request.get("language", "python")
        action = request.get("action", "detect")
        
        if action == "detect" and code:
            sections = self.detect_sections(code, language)
            
            # Convert to serializable format
            sections_data = [
                {
                    "name": s.name,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "level": s.level,
                    "section_type": s.section_type,
                    "parent": s.parent,
                    "metadata": s.metadata,
                }
                for s in sections
            ]
            
            return {
                "status": "success",
                "agent": self.name,
                "sections": sections_data,
                "section_count": len(sections),
                "hierarchy": self._build_hierarchy(sections_data),
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
            "sections": [],
            "message": "Provide code to detect sections",
        }

    def _build_hierarchy(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build hierarchical structure from sections."""
        hierarchy = {}
        root_sections = [s for s in sections if s["parent"] is None]
        
        for section in root_sections:
            children = [s for s in sections if s.get("parent") == section["name"]]
            hierarchy[section["name"]] = {
                "section": section,
                "children": {s["name"]: {} for s in children},
            }
        
        return hierarchy

