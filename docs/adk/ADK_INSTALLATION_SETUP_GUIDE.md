# ADK Installation and Setup Guide

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space

### Required Accounts
- **Google Cloud Platform**: For Vertex AI and Gemini API access
- **Google API Key**: For Gemini model access

## Installation Methods

### Method 1: Stable Release (Recommended)

Install the latest stable version from PyPI:

```bash
pip install google-adk
```

### Method 2: Development Version

Install the latest development version from GitHub:

```bash
pip install git+https://github.com/google/adk-python.git@main
```

### Method 3: Local Development

For contributing or local development:

```bash
# Clone the repository
git clone https://github.com/google/adk-python.git
cd adk-python

# Install in development mode
pip install -e .
```

## Environment Setup

### 1. Google Cloud Configuration

#### Set up Google Cloud Project
```bash
# Install Google Cloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# Initialize gcloud
gcloud init

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

#### Authentication Setup
```bash
# Application Default Credentials (recommended for development)
gcloud auth application-default login

# Or use service account key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 2. Environment Variables

Create a `.env` file in your project root:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# ADK Configuration
ADK_LOG_LEVEL=INFO
ADK_SESSION_TIMEOUT=3600
ADK_MAX_CONCURRENT_SESSIONS=100

# Optional: Custom model configuration
ADK_DEFAULT_MODEL=gemini-2.5-flash
ADK_TEMPERATURE=0.7
ADK_MAX_OUTPUT_TOKENS=2048
```

### 3. Verify Installation

Test your ADK installation:

```python
#!/usr/bin/env python3
"""
ADK Installation Verification Script
"""

import asyncio
from google.adk.agents import Agent
from google.adk.core import Runner

async def test_adk_installation():
    """Test basic ADK functionality."""
    
    try:
        # Create a simple agent
        agent = Agent(
            name="test_agent",
            model="gemini-2.5-flash",
            instruction="You are a helpful assistant. Respond briefly to test the installation."
        )
        
        # Create runner
        runner = Runner(agent=agent)
        
        # Test basic functionality
        result = await runner.run("Hello, ADK!")
        
        print("✅ ADK Installation Successful!")
        print(f"Test Response: {result.response}")
        
        return True
        
    except Exception as e:
        print(f"❌ ADK Installation Failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_adk_installation())
```

## Quick Start Examples

### 1. Basic Agent

```python
from google.adk.agents import Agent

# Create a simple agent
agent = Agent(
    name="hello_agent",
    model="gemini-2.5-flash",
    instruction="You are a friendly assistant."
)

# Use the agent
from google.adk.core import Runner
runner = Runner(agent=agent)

# Run synchronously
result = runner.run_sync("What is ADK?")
print(result.response)
```

### 2. Agent with Tools

```python
from google.adk.agents import Agent
from google.adk.tools import google_search, FunctionTool

# Define a custom tool
@FunctionTool
def calculate_sum(a: int, b: int) -> dict:
    """Calculate the sum of two numbers."""
    return {"result": a + b, "status": "success"}

# Create agent with tools
agent = Agent(
    name="assistant_with_tools",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant with access to search and calculation tools.",
    tools=[google_search, calculate_sum]
)
```

### 3. Multi-Agent System

```python
from google.adk.agents import LlmAgent

# Create specialized agents
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="You are a research specialist. Find and analyze information.",
    tools=[google_search]
)

writer = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="You are a content writer. Create well-structured content."
)

# Create coordinator agent
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction="You coordinate research and writing tasks.",
    sub_agents=[researcher, writer]
)
```

## Development Environment Setup

### 1. Development Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or install specific dev tools
pip install pytest pytest-asyncio black flake8 mypy
```

### 2. IDE Configuration

#### VS Code Setup
Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm Setup
1. Set Python interpreter to your virtual environment
2. Enable pytest as test runner
3. Configure code style to use Black formatter

### 3. Testing Setup

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=google.adk

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

## Production Deployment

### 1. Docker Setup

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
```

### 2. Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
gcloud run deploy adk-service \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. Vertex AI Agent Engine

```python
# Deploy to Vertex AI Agent Engine
from google.adk.deploy import VertexAiDeployment

deployment = VertexAiDeployment(
    project_id="your-project-id",
    region="us-central1",
    agent=your_agent
)

# Deploy
deployment_info = await deployment.deploy()
print(f"Agent deployed: {deployment_info.endpoint}")
```

## Configuration Options

### 1. Model Configuration

```python
from google.adk.agents import Agent
from google.adk.core import GenerateContentConfig

# Configure model parameters
config = GenerateContentConfig(
    temperature=0.7,
    max_output_tokens=2048,
    top_p=0.9,
    top_k=40
)

agent = Agent(
    name="configured_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    generate_content_config=config
)
```

### 2. Session Configuration

```python
from google.adk.core import SessionService, InMemorySessionService

# Configure session service
session_service = InMemorySessionService(
    max_sessions=1000,
    session_timeout_seconds=3600
)
```

### 3. Streaming Configuration

```python
from google.adk.core import RunConfig, StreamingMode

# Configure streaming
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["TEXT", "AUDIO"],
    max_llm_calls=100
)
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Check authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth application-default login
```

#### 2. API Quota Issues
```bash
# Check quota usage
gcloud logging read "resource.type=consumed_api" --limit=10

# Request quota increase if needed
```

#### 3. Model Access Issues
```bash
# Verify model access
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     "https://generativelanguage.googleapis.com/v1beta/models"
```

#### 4. Import Errors
```python
# Check ADK installation
import google.adk
print(google.adk.__version__)

# Reinstall if needed
pip uninstall google-adk
pip install google-adk
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
import os
os.environ["ADK_LOG_LEVEL"] = "DEBUG"
```

### Performance Optimization

```python
# Optimize for production
from google.adk.core import RunConfig

config = RunConfig(
    max_llm_calls=50,  # Limit calls per session
    streaming_mode=StreamingMode.SSE,  # Use server-sent events
    save_input_blobs_as_artifacts=False  # Disable for performance
)
```

## Next Steps

1. **Read the Documentation**: Explore the full ADK documentation
2. **Try Examples**: Run the provided example projects
3. **Build Your Agent**: Start with a simple agent and gradually add complexity
4. **Join the Community**: Participate in discussions and contribute
5. **Deploy to Production**: Use the deployment guides for your platform

## Resources

- **Documentation**: [ADK Documentation](https://github.com/google/adk-docs)
- **Examples**: [ADK Examples](https://github.com/google/adk-python/tree/main/examples)
- **Community**: [GitHub Discussions](https://github.com/google/adk-python/discussions)
- **Issues**: [GitHub Issues](https://github.com/google/adk-python/issues)

## Support

For help with ADK:

1. Check the [troubleshooting guide](https://github.com/google/adk-docs/blob/main/docs/troubleshooting.md)
2. Search [existing issues](https://github.com/google/adk-python/issues)
3. Ask in [GitHub Discussions](https://github.com/google/adk-python/discussions)
4. Create a [new issue](https://github.com/google/adk-python/issues/new) if needed

Happy building with ADK! 🚀