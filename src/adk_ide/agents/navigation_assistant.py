"""Navigation Assistant Agent for voice-controlled section jumping."""
from typing import Any, Dict, Optional, Callable, List
import os
import re

from .base import ADKIDEAgent
from .section_detection import SectionDetectionAgent


class NavigationAssistantAgent(ADKIDEAgent):
    """Navigation assistant agent with voice-controlled section jumping.
    
    Enables natural language navigation commands to jump between code sections,
    functions, classes, and regions.
    """

    def __init__(self, section_detector: Optional[SectionDetectionAgent] = None) -> None:
        super().__init__(
            name="navigation_assistant_agent",
            description="Voice-controlled navigation and section jumping"
        )
        self.section_detector = section_detector or SectionDetectionAgent()
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="NavigationAssistantAgent",
                    description="Assists with natural language navigation commands to jump between code sections, functions, classes, and regions",
                    instruction="You are a navigation assistant. Interpret natural language commands like 'go to function X', 'jump to class Y', 'show me the region Z', and translate them into precise code navigation actions.",
                    output_key="navigation_result",  # Save navigation results to session.state
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

    def parse_navigation_command(self, command: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse natural language navigation command and find matching section."""
        command_lower = command.lower()
        
        # Pattern matching for common commands
        patterns = {
            "go_to": [
                r"go to (.+)",
                r"jump to (.+)",
                r"show me (.+)",
                r"navigate to (.+)",
                r"open (.+)",
            ],
            "find": [
                r"find (.+)",
                r"search for (.+)",
                r"locate (.+)",
            ],
            "next": [
                r"next (.+)",
                r"go to next (.+)",
            ],
            "previous": [
                r"previous (.+)",
                r"go to previous (.+)",
            ],
        }
        
        target_name = None
        action = "go_to"
        
        # Extract target from command
        for action_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, command_lower)
                if match:
                    target_name = match.group(1).strip()
                    action = action_type
                    break
            if target_name:
                break
        
        # If no pattern matched, try to extract any quoted or capitalized words
        if not target_name:
            # Try to find function/class names in command
            words = command.split()
            for word in words:
                # Look for capitalized words (likely class/function names)
                if word and word[0].isupper() and word.isalnum():
                    target_name = word
                    break
                # Look for quoted strings
                if word.startswith('"') or word.startswith("'"):
                    target_name = word.strip('"\'')
                    break
        
        # Find matching section
        matched_sections = []
        if target_name:
            # Fuzzy matching
            target_lower = target_name.lower()
            for section in sections:
                section_name_lower = section.get("name", "").lower()
                if target_lower in section_name_lower or section_name_lower in target_lower:
                    matched_sections.append(section)
                # Also check for partial matches
                elif any(word in section_name_lower for word in target_lower.split() if len(word) > 3):
                    matched_sections.append(section)
        
        return {
            "action": action,
            "target": target_name,
            "matched_sections": matched_sections,
            "command": command,
        }

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process navigation requests."""
        code = request.get("code", "")
        command = request.get("command", "")
        current_line = request.get("current_line", 1)
        language = request.get("language", "python")
        
        if command and code:
            # Detect sections first
            sections = self.section_detector.detect_sections(code, language)
            sections_data = [
                {
                    "name": s.name,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "level": s.level,
                    "section_type": s.section_type,
                }
                for s in sections
            ]
            
            # Parse navigation command
            nav_result = self.parse_navigation_command(command, sections_data)
            
            # Determine target location
            target_line = current_line
            target_section = None
            
            if nav_result["matched_sections"]:
                # Use first match
                target_section = nav_result["matched_sections"][0]
                target_line = target_section["start_line"]
            elif nav_result["action"] == "next":
                # Find next section after current line
                next_sections = [s for s in sections_data if s["start_line"] > current_line]
                if next_sections:
                    target_section = next_sections[0]
                    target_line = target_section["start_line"]
            elif nav_result["action"] == "previous":
                # Find previous section before current line
                prev_sections = [s for s in sections_data if s["start_line"] < current_line]
                if prev_sections:
                    target_section = prev_sections[-1]
                    target_line = target_section["start_line"]
            
            return {
                "status": "success",
                "agent": self.name,
                "target_line": target_line,
                "target_section": target_section,
                "navigation_result": nav_result,
                "all_sections": sections_data,
            }
        
        # Use LLM agent for enhanced natural language understanding
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
            "target_line": current_line,
            "message": "Provide command and code for navigation",
        }

