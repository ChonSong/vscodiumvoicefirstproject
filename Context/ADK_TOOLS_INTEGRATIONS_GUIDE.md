# ADK Tools and Integrations Guide

## Overview

The Agent Development Kit (ADK) provides a rich ecosystem of tools and integrations that extend agent capabilities beyond basic language model interactions. This guide covers all available tools, how to use them, and how to create custom integrations.

## Built-in Tools

### 1. Google Search Tool

Provides real-time web search capabilities for grounding responses with current information.

```python
from google.adk.tools import google_search
from google.adk.agents import Agent

agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash",
    instruction="Use Google Search to find current information when needed.",
    tools=[google_search]
)
```

**Usage Example:**
```python
# The agent can now search the web
result = await runner.run("What's the latest news about AI?")
# Agent will automatically use google_search tool
```

### 2. Code Execution Tools

Note: Both `BuiltInCodeExecutor` and `VertexAiCodeExecutor` are defined in the `google.adk.code_executors` module, not in `google.adk.tools`. Import them from `google.adk.code_executors`.

#### BuiltInCodeExecutor
Safe, sandboxed Python code execution. This is ADK's secure execution environment that monitors resource usage (CPU, memory) and blocks dangerous system operations. Due to current ADK limitations on combining built-in tools, it is used as the dedicated Code Execution Agent (CEA)'s sole tool.

```python
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.agents import Agent

code_executor = BuiltInCodeExecutor()

agent = Agent(
    name="code_assistant",
    model="gemini-2.5-flash",
    instruction="You can execute Python code to solve problems.",
    tools=[code_executor]
)
```

#### VertexAiCodeExecutor
Cloud-based code execution using the Vertex Code Interpreter Extension. Developers can optionally configure it with a resource name to load an existing interpreter extension.

```python
from google.adk.code_executors import VertexAiCodeExecutor

# Requires Google Cloud setup
code_executor = VertexAiCodeExecutor(
    project_id="your-project-id",
    location="us-central1",
    # Optional: interpreter_resource_name="projects/.../locations/.../extensions/codeInterpreter"
)

agent = Agent(
    name="cloud_code_assistant",
    model="gemini-2.5-flash",
    tools=[code_executor]
)
```

### 3. Memory Tools

#### Load Memory Tool
Access long-term memory across sessions.

```python
from google.adk.tools import load_memory
from google.adk.agents import Agent

agent = Agent(
    name="memory_assistant",
    model="gemini-2.5-flash",
    instruction="Use memory to recall information from previous conversations.",
    tools=[load_memory]
)
```

## Custom Function Tools

### Creating Function Tools

Any Python function can become a tool by using the `@FunctionTool` decorator or including it in the agent's tools list.

#### Method 1: Decorator Approach

```python
from google.adk.tools import FunctionTool

@FunctionTool
def calculate_area(length: float, width: float) -> dict:
    """Calculate the area of a rectangle.
    
    Args:
        length: The length of the rectangle
        width: The width of the rectangle
        
    Returns:
        Dictionary with area calculation result
    """
    area = length * width
    return {
        "area": area,
        "unit": "square units",
        "status": "success"
    }

# Use in agent
agent = Agent(
    name="math_assistant",
    model="gemini-2.5-flash",
    tools=[calculate_area]
)
```

#### Method 2: Direct Function Inclusion

```python
def get_weather(city: str) -> dict:
    """Get weather information for a city.
    
    Args:
        city: Name of the city
        
    Returns:
        Weather information dictionary
    """
    # Simulate weather API call
    return {
        "city": city,
        "temperature": "22°C",
        "condition": "Sunny",
        "status": "success"
    }

# Include directly in tools list
agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash",
    tools=[get_weather]  # Function automatically wrapped as FunctionTool
)
```

### Best Practices for Function Tools

1. **Clear Function Names**: Use descriptive names that indicate the tool's purpose
2. **Type Hints**: Always include type hints for parameters and return values
3. **Docstrings**: Provide detailed docstrings explaining the function's purpose and parameters
4. **Return Dictionaries**: Return structured data with status indicators
5. **Error Handling**: Handle exceptions gracefully and return error information

```python
@FunctionTool
def database_query(query: str, table: str) -> dict:
    """Execute a database query safely.
    
    Args:
        query: SQL query to execute (SELECT only)
        table: Target table name
        
    Returns:
        Query results or error information
    """
    try:
        # Validate query is SELECT only
        if not query.strip().upper().startswith('SELECT'):
            return {
                "error": "Only SELECT queries are allowed",
                "status": "error"
            }
        
        # Execute query (implement your database logic)
        results = execute_safe_query(query, table)
        
        return {
            "results": results,
            "row_count": len(results),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
```

## Long-Running Function Tools

For operations that take significant time, use `LongRunningFunctionTool`.

```python
from google.adk.tools import LongRunningFunctionTool
import asyncio
import uuid

class DataProcessingTool(LongRunningFunctionTool):
    """Tool for long-running data processing tasks."""
    
    def __init__(self):
        super().__init__()
        self.active_jobs = {}
    
    async def start_processing(self, dataset_url: str) -> dict:
        """Start processing a large dataset.
        
        Args:
            dataset_url: URL of the dataset to process
            
        Returns:
            Job ticket for tracking progress
        """
        job_id = str(uuid.uuid4())
        
        # Start background processing
        self.active_jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "dataset_url": dataset_url
        }
        
        # Start async processing
        asyncio.create_task(self._process_dataset(job_id, dataset_url))
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Processing started"
        }
    
    async def _process_dataset(self, job_id: str, dataset_url: str):
        """Background processing logic."""
        try:
            # Simulate long processing
            for i in range(10):
                await asyncio.sleep(1)  # Simulate work
                self.active_jobs[job_id]["progress"] = (i + 1) * 10
            
            # Complete processing
            self.active_jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "result": "Processing completed successfully"
            })
            
        except Exception as e:
            self.active_jobs[job_id].update({
                "status": "error",
                "error": str(e)
            })
    
    async def check_job_status(self, job_id: str) -> dict:
        """Check the status of a processing job."""
        job = self.active_jobs.get(job_id)
        if not job:
            return {"error": "Job not found", "status": "error"}
        
        return job

# Use the long-running tool
processing_tool = DataProcessingTool()

agent = Agent(
    name="data_processor",
    model="gemini-2.5-flash",
    tools=[processing_tool.start_processing, processing_tool.check_job_status]
)
```

## OpenAPI Integration

ADK can automatically generate tools from OpenAPI specifications.

### Basic OpenAPI Integration

```python
from google.adk.tools import OpenAPIToolset

# Create toolset from OpenAPI spec
api_toolset = OpenAPIToolset(
    openapi_spec_url="https://api.example.com/openapi.json",
    # Or from local file
    # openapi_spec_path="./api_spec.yaml"
)

# Get generated tools
api_tools = api_toolset.get_tools()

agent = Agent(
    name="api_assistant",
    model="gemini-2.5-flash",
    instruction="Use the API tools to interact with external services.",
    tools=api_tools
)
```

### Custom OpenAPI Configuration

```python
from google.adk.tools import OpenAPIToolset, RestApiTool

# Configure authentication
auth_config = {
    "type": "bearer",
    "token": "your-api-token"
}

# Create toolset with authentication
api_toolset = OpenAPIToolset(
    openapi_spec_url="https://api.example.com/openapi.json",
    auth_config=auth_config,
    base_url="https://api.example.com/v1"  # Override base URL
)

# Filter specific operations
filtered_tools = api_toolset.get_tools(
    include_operations=["getUserById", "createUser", "updateUser"]
)

agent = Agent(
    name="user_management_assistant",
    model="gemini-2.5-flash",
    tools=filtered_tools
)
```

### Manual REST API Tool Creation

```python
from google.adk.tools import RestApiTool

# Create individual REST API tool
user_api_tool = RestApiTool(
    name="get_user_profile",
    description="Get user profile information",
    method="GET",
    url="https://api.example.com/users/{user_id}",
    parameters={
        "user_id": {
            "type": "string",
            "description": "User ID to retrieve",
            "required": True
        }
    },
    headers={
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    }
)

agent = Agent(
    name="user_assistant",
    model="gemini-2.5-flash",
    tools=[user_api_tool]
)
```

## Third-Party Framework Integration

### LangChain Integration

```python
from google.adk.tools import LangchainTool
from langchain.tools import DuckDuckGoSearchRun

# Wrap LangChain tool
ddg_search = DuckDuckGoSearchRun()
adk_search_tool = LangchainTool(ddg_search)

agent = Agent(
    name="langchain_assistant",
    model="gemini-2.5-flash",
    tools=[adk_search_tool]
)
```

### CrewAI Integration

```python
from google.adk.tools import CrewAiTool
from crewai.tools import SerperDevTool

# Wrap CrewAI tool
serper_tool = SerperDevTool()
adk_serper_tool = CrewAiTool(serper_tool)

agent = Agent(
    name="crewai_assistant",
    model="gemini-2.5-flash",
    tools=[adk_serper_tool]
)
```

## Google Cloud Tools

### Vertex AI Search Tool

```python
from google.adk.tools import VertexAiSearchTool

# Configure Vertex AI Search
search_tool = VertexAiSearchTool(
    project_id="your-project-id",
    location="global",
    data_store_id="your-datastore-id"
)

agent = Agent(
    name="enterprise_search_assistant",
    model="gemini-2.5-flash",
    instruction="Use Vertex AI Search to find information in enterprise documents.",
    tools=[search_tool]
)
```

### Cloud Storage Tools

```python
from google.adk.tools import FunctionTool
from google.cloud import storage

@FunctionTool
def upload_to_gcs(file_content: str, bucket_name: str, file_name: str) -> dict:
    """Upload content to Google Cloud Storage.
    
    Args:
        file_content: Content to upload
        bucket_name: GCS bucket name
        file_name: Name for the uploaded file
        
    Returns:
        Upload result information
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        blob.upload_from_string(file_content)
        
        return {
            "status": "success",
            "file_url": f"gs://{bucket_name}/{file_name}",
            "size": len(file_content)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@FunctionTool
def download_from_gcs(bucket_name: str, file_name: str) -> dict:
    """Download content from Google Cloud Storage."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        content = blob.download_as_text()
        
        return {
            "status": "success",
            "content": content,
            "size": blob.size
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Use in agent
agent = Agent(
    name="storage_assistant",
    model="gemini-2.5-flash",
    tools=[upload_to_gcs, download_from_gcs]
)
```

## Model Context Protocol (MCP) Tools

ADK supports MCP tools for extended functionality.

### Using MCP Tools

```python
from google.adk.tools import McpTool

# Connect to MCP server
mcp_tool = McpTool(
    server_url="http://localhost:3000/mcp",
    tool_name="file_operations"
)

agent = Agent(
    name="mcp_assistant",
    model="gemini-2.5-flash",
    tools=[mcp_tool]
)
```

## Agent Tools (Sub-Agent Integration)

Use other agents as tools for complex workflows.

```python
from google.adk.tools import AgentTool
from google.adk.agents import LlmAgent

# Create specialized agents
research_agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="You are a research specialist. Find and analyze information.",
    tools=[google_search]
)

analysis_agent = LlmAgent(
    name="analyzer",
    model="gemini-2.5-flash",
    instruction="You analyze data and provide insights."
)

# Wrap agents as tools
research_tool = AgentTool(research_agent)
analysis_tool = AgentTool(analysis_agent)

# Create coordinator agent
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction="Coordinate research and analysis tasks.",
    tools=[research_tool, analysis_tool]
)
```

## Tool Authentication

### API Key Authentication

```python
@FunctionTool
def authenticated_api_call(query: str, api_key: str) -> dict:
    """Make authenticated API call.
    
    Args:
        query: Search query
        api_key: API key for authentication
        
    Returns:
        API response data
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make API call with authentication
    response = make_api_request(query, headers)
    return response
```

### OAuth Authentication

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

@FunctionTool
def oauth_api_call(resource_id: str, credentials_json: str) -> dict:
    """Make OAuth-authenticated API call."""
    try:
        # Load credentials
        creds = Credentials.from_authorized_user_info(
            json.loads(credentials_json)
        )
        
        # Refresh if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Make authenticated request
        headers = {"Authorization": f"Bearer {creds.token}"}
        response = make_api_request(resource_id, headers)
        
        return {
            "status": "success",
            "data": response
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

## Tool Error Handling

### Robust Error Handling Pattern

```python
@FunctionTool
def robust_api_tool(endpoint: str, params: dict) -> dict:
    """Robust API tool with comprehensive error handling."""
    try:
        # Validate inputs
        if not endpoint:
            return {
                "status": "error",
                "error": "Endpoint is required",
                "error_type": "validation_error"
            }
        
        # Make API call with retries
        for attempt in range(3):
            try:
                response = make_api_call(endpoint, params)
                return {
                    "status": "success",
                    "data": response,
                    "attempt": attempt + 1
                }
            except requests.exceptions.Timeout:
                if attempt == 2:  # Last attempt
                    return {
                        "status": "error",
                        "error": "Request timeout after 3 attempts",
                        "error_type": "timeout_error"
                    }
                time.sleep(2 ** attempt)  # Exponential backoff
                
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error": "Connection error - service unavailable",
            "error_type": "connection_error"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown_error"
        }
```

## Tool Performance Optimization

### Caching Tool Results

```python
from functools import lru_cache
import hashlib
import json

class CachedTool:
    """Base class for tools with caching."""
    
    def __init__(self, cache_size: int = 128):
        self.cache = {}
        self.cache_size = cache_size
    
    def _cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {"args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str):
        """Get cached result."""
        return self.cache.get(cache_key)
    
    def _set_cache(self, cache_key: str, result: dict):
        """Set cached result."""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = result

@FunctionTool
def cached_expensive_operation(data: str) -> dict:
    """Expensive operation with caching."""
    cache_key = hashlib.md5(data.encode()).hexdigest()
    
    # Check cache
    cached_result = tool_cache.get(cache_key)
    if cached_result:
        return {
            "status": "success",
            "result": cached_result,
            "cached": True
        }
    
    # Perform expensive operation
    result = perform_expensive_computation(data)
    
    # Cache result
    tool_cache[cache_key] = result
    
    return {
        "status": "success",
        "result": result,
        "cached": False
    }

# Global cache
tool_cache = {}
```

## Tool Testing

### Unit Testing Tools

```python
import pytest
from unittest.mock import patch, MagicMock

def test_calculate_area_tool():
    """Test the calculate_area function tool."""
    result = calculate_area(5.0, 3.0)
    
    assert result["status"] == "success"
    assert result["area"] == 15.0
    assert result["unit"] == "square units"

@pytest.mark.asyncio
async def test_api_tool_success():
    """Test API tool with mocked response."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = await api_tool("test_endpoint")
        
        assert result["status"] == "success"
        assert result["data"] == {"data": "test"}

@pytest.mark.asyncio
async def test_api_tool_error():
    """Test API tool error handling."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = await api_tool("test_endpoint")
        
        assert result["status"] == "error"
        assert "connection_error" in result["error_type"]
```

## Best Practices Summary

1. **Tool Design**:
   - Use clear, descriptive names
   - Provide comprehensive docstrings
   - Return structured data with status indicators
   - Handle errors gracefully

2. **Performance**:
   - Implement caching for expensive operations
   - Use async/await for I/O operations
   - Add timeouts for external API calls
   - Implement retry logic with exponential backoff

3. **Security**:
   - Validate all inputs
   - Use secure authentication methods
   - Never expose sensitive data in responses
   - Implement rate limiting for external APIs

4. **Testing**:
   - Write unit tests for all tools
   - Mock external dependencies
   - Test error conditions
   - Validate tool integration with agents

5. **Documentation**:
   - Document tool parameters and return values
   - Provide usage examples
   - Explain authentication requirements
   - Document error conditions and responses

This comprehensive guide covers the full spectrum of ADK tools and integrations, from built-in tools to custom implementations and third-party integrations.