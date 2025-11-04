from typing import Any, Dict, Optional
import re


async def before_model_callback(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Basic input guardrail scaffold.

    Return a dict to short-circuit model/tool calls; return None to proceed.
    """
    text = str(request)
    # Dangerous shell/actions
    if "rm -rf" in text or "format c:" in text:
        return {"blocked": True, "reason": "dangerous input detected"}
    # Crude prompt injection keywords
    injection_indicators = ["ignore previous", "disregard instructions", "override policy"]
    if any(ind in text.lower() for ind in injection_indicators):
        return {"blocked": True, "reason": "prompt injection indicators detected"}
    # Basic PII pattern detection (emails, API keys-like strings)
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        return {"blocked": True, "reason": "possible PII detected (email)"}
    if re.search(r"(?:api|secret|token|key)[^\n]{0,20}[A-Za-z0-9_\-]{16,}", text, re.IGNORECASE):
        return {"blocked": True, "reason": "possible secret detected"}
    # Size limit
    if len(text) > 200_000:
        return {"blocked": True, "reason": "request too large"}
    return None


async def after_model_callback(response: Dict[str, Any]) -> Dict[str, Any]:
    """Output sanitization scaffold."""
    return response


async def before_tool_callback(tool_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Tool policy validation scaffold."""
    if tool_name == "code_executor":
        code = str(args.get("code", ""))
        if len(code) > 100_000:
            return {"blocked": True, "reason": "code too large"}
        # Disallow network/process primitives explicitly here as an extra guard
        if re.search(r"\b(import\s+(socket|subprocess|pty|fcntl))\b", code):
            return {"blocked": True, "reason": "forbidden imports in code"}
    return None


async def after_tool_callback(result: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process tool results scaffold."""
    return result

