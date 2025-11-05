"""Smart Folding Agent for context-aware code collapsing."""
from typing import Any, Dict, Optional, Callable, List
import os

from .base import ADKIDEAgent
from .section_detection import SectionDetectionAgent, CodeSection


class SmartFoldingAgent(ADKIDEAgent):
    """Smart folding agent with context-aware collapsing.
    
    Uses section detection to intelligently fold code sections based on context,
    user preferences, and code structure.
    """

    def __init__(self, section_detector: Optional[SectionDetectionAgent] = None) -> None:
        super().__init__(
            name="smart_folding_agent",
            description="Context-aware code folding and collapsing"
        )
        self.section_detector = section_detector or SectionDetectionAgent()
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None
        self.folding_rules: Dict[str, Any] = {
            "fold_by_default": ["imports", "comments", "docstrings"],
            "always_show": ["main", "entry_point", "if __name__"],
            "context_aware": True,
        }

        if os.environ.get("ADK_ENABLED", "false").lower() == "true":
            try:  # pragma: no cover
                from google.adk import LlmAgent  # type: ignore

                self._llm_agent = LlmAgent(
                    name="SmartFoldingAgent",
                    description="Context-aware code folding that intelligently collapses code sections based on user context, focus, and code structure",
                    instruction="You are a smart folding specialist. Analyze code structure and user context to determine which sections should be folded. Consider focus areas, recently modified sections, and code complexity.",
                    output_key="folding_config",  # Save folding configuration to session.state
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

    def determine_folding(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Determine which sections should be folded based on context."""
        if context is None:
            context = {}
        
        # Detect sections
        sections = self.section_detector.detect_sections(code, context.get("language", "python"))
        
        # Determine folding strategy
        folding_config = []
        focus_line = context.get("focus_line")
        recently_modified = context.get("recently_modified", [])
        
        for section in sections:
            should_fold = False
            fold_reason = None
            
            # Always show sections near focus
            if focus_line and section.start_line <= focus_line <= section.end_line:
                should_fold = False
            # Always show recently modified sections
            elif any(section.start_line <= line <= section.end_line for line in recently_modified):
                should_fold = False
            # Fold by type rules
            elif section.section_type in self.folding_rules["fold_by_default"]:
                should_fold = True
                fold_reason = "default_rule"
            # Fold long sections
            elif section.end_line - section.start_line > 50:
                should_fold = True
                fold_reason = "long_section"
            # Fold nested sections away from focus
            elif section.level > 2 and (focus_line is None or not (section.start_line <= focus_line <= section.end_line)):
                should_fold = True
                fold_reason = "nested_away_from_focus"
            
            folding_config.append({
                "section_name": section.name,
                "start_line": section.start_line,
                "end_line": section.end_line,
                "folded": should_fold,
                "reason": fold_reason,
                "level": section.level,
            })
        
        return {
            "folding_config": folding_config,
            "total_sections": len(sections),
            "folded_count": sum(1 for f in folding_config if f["folded"]),
        }

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process smart folding requests."""
        code = request.get("code", "")
        context = request.get("context", {})
        action = request.get("action", "determine_folding")
        
        if action == "determine_folding" and code:
            folding_result = self.determine_folding(code, context)
            return {
                "status": "success",
                "agent": self.name,
                **folding_result,
            }
        
        if action == "toggle_fold":
            section_name = request.get("section_name")
            folding_config = request.get("folding_config", [])
            
            # Toggle fold state for specific section
            for fold_item in folding_config:
                if fold_item.get("section_name") == section_name:
                    fold_item["folded"] = not fold_item.get("folded", False)
                    break
            
            return {
                "status": "success",
                "agent": self.name,
                "folding_config": folding_config,
            }
        
        # Use LLM agent for enhanced context-aware analysis
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
            "folding_config": [],
            "message": "Provide code to determine folding strategy",
        }

