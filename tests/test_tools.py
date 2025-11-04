"""Integration tests for tools."""
import pytest
import os
import tempfile
import pathlib
from src.adk_ide.tools.file_operations import FileOperationsTool, get_file_operations_tool
from src.adk_ide.tools.google_search import GoogleSearchTool, get_google_search_tool


@pytest.mark.asyncio
async def test_file_operations_read_write():
    """Test file operations read and write."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileOperationsTool(base_path=tmpdir)
        
        # Write file
        write_result = await tool.write_file("test.txt", "Hello, World!")
        assert write_result["status"] == "success"
        assert write_result["file_path"] == "test.txt"
        
        # Read file
        read_result = await tool.read_file("test.txt")
        assert read_result["status"] == "success"
        assert read_result["content"] == "Hello, World!"


@pytest.mark.asyncio
async def test_file_operations_list():
    """Test file operations list directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileOperationsTool(base_path=tmpdir)
        
        # Create test files
        await tool.write_file("file1.txt", "content1")
        await tool.write_file("file2.txt", "content2")
        
        # List directory
        list_result = await tool.list_directory(".")
        assert list_result["status"] == "success"
        assert len(list_result["items"]) >= 2


@pytest.mark.asyncio
async def test_file_operations_tool_call():
    """Test FileOperationsTool __call__ interface."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileOperationsTool(base_path=tmpdir)
        
        # Write via __call__
        result = await tool({
            "action": "write",
            "file_path": "test.txt",
            "content": "Test content",
        })
        assert result["status"] == "success"
        
        # Read via __call__
        result = await tool({
            "action": "read",
            "file_path": "test.txt",
        })
        assert result["status"] == "success"
        assert result["content"] == "Test content"


@pytest.mark.asyncio
async def test_google_search_tool():
    """Test GoogleSearchTool."""
    tool = GoogleSearchTool()
    
    result = await tool({"query": "Python programming"})
    assert "status" in result
    assert "query" in result
    assert result["query"] == "Python programming"
    # Should have results (even if mock)
    assert "results" in result


def test_get_file_operations_tool():
    """Test get_file_operations_tool factory."""
    tool = get_file_operations_tool()
    assert isinstance(tool, FileOperationsTool)


def test_get_google_search_tool():
    """Test get_google_search_tool factory."""
    # May return None if API key not configured
    tool = get_google_search_tool()
    assert tool is None or isinstance(tool, GoogleSearchTool)

