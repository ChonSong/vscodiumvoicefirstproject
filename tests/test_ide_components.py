"""Integration tests for IDE component agents."""
import pytest
from src.adk_ide.agents.ide_components import (
    CodeEditorAgent,
    NavigationAgent,
    DebugAgent,
    ErrorDetectionAgent,
)
from src.adk_ide.agents.cea import CodeExecutionAgent


@pytest.mark.asyncio
async def test_code_editor_agent_format():
    """Test CodeEditorAgent formatting."""
    agent = CodeEditorAgent()
    result = await agent.run({
        "action": "format",
        "code": "def hello():\n    print('world')  \n",
    })
    
    assert result["status"] == "success"
    assert "formatted_code" in result


@pytest.mark.asyncio
async def test_navigation_agent():
    """Test NavigationAgent."""
    agent = NavigationAgent()
    result = await agent.run({"query": "find function"})
    
    assert result["status"] == "success"
    assert "suggestions" in result


@pytest.mark.asyncio
async def test_debug_agent_breakpoints():
    """Test DebugAgent breakpoint management."""
    agent = DebugAgent()
    
    # Set breakpoint
    result = await agent.run({"action": "set_breakpoint", "line": 10, "file": "test.py"})
    assert result["status"] == "success"
    assert result["breakpoint_set"] is True
    assert len(result["breakpoints"]) == 1
    
    # Remove breakpoint
    result = await agent.run({"action": "remove_breakpoint", "line": 10})
    assert result["status"] == "success"
    assert len(result["breakpoints"]) == 0


@pytest.mark.asyncio
async def test_error_detection_agent():
    """Test ErrorDetectionAgent."""
    agent = ErrorDetectionAgent()
    
    # Valid code
    result = await agent.run({"code": "def hello():\n    print('world')\n"})
    assert result["status"] == "success"
    assert "errors" in result
    assert "warnings" in result
    
    # Code with potential issues
    result = await agent.run({"code": "def hello(\n    print('world')\n"})
    assert result["status"] == "success"
    assert "errors" in result

