# ADK Integration Reference

**⚠️ IMPORTANT: This system uses Google ADK (Agent Development Kit) integration. DO NOT create separate implementations for features already provided by ADK.**

## Current ADK Integration Status

### ✅ IMPLEMENTED ADK Features

This system already has complete ADK integration. Before implementing any voice, AI, or enterprise features, check this list first.

## 1. Core ADK Components

### 1.1 ADK Runner (`Runner.run_live()`)
- **Location**: `src/adk_mcp/enterprise_enhanced_server.py`
- **Purpose**: Bidirectional streaming for voice conversations
- **Features**:
  - Real-time audio processing
  - Speech-to-text transcription
  - Text-to-speech synthesis
  - Streaming response generation
- **Configuration**: BIDI streaming mode with AUDIO response modality

### 1.2 ADK LlmAgent
- **Location**: `src/adk_mcp/enterprise_enhanced_server.py`
- **Purpose**: AI conversation management
- **Model**: Gemini 2.5 Flash
- **Features**:
  - Context-aware responses
  - Tool integration
  - Conversation history management
  - Voice-optimized responses

### 1.3 ADK SessionService
- **Location**: `src/adk_mcp/enhanced_session_manager.py`
- **Purpose**: Session lifecycle management
- **Features**:
  - Automatic session cleanup
  - Context preservation
  - Memory management
  - Mobile lifecycle handling

## 2. ADK Tools Integration

### 2.1 BuiltInCodeExecutor
- **Location**: `src/adk_mcp/enterprise_enhanced_server.py`
- **Purpose**: Safe code execution
- **Features**:
  - Python code execution
  - Security sandboxing
  - Result formatting
  - Voice-friendly output

### 2.2 OpenAPIToolset
- **Location**: `src/adk_mcp/adk_enterprise_integration.py`
- **Purpose**: Automatic REST API tool generation
- **Features**:
  - Dynamic API discovery
  - Tool generation from OpenAPI specs
  - Enterprise system integration

### 2.3 ApplicationIntegrationToolset
- **Location**: `src/adk_mcp/adk_enterprise_integration.py`
- **Purpose**: Enterprise system connectors
- **Features**:
  - Database connections
  - External service integration
  - Workflow automation

## 3. ADK Production Services

### 3.1 VertexAiSessionService
- **Location**: `src/adk_mcp/adk_production_services.py`
- **Purpose**: Production session management
- **Features**:
  - Persistent session storage
  - Scalable session handling
  - Cloud-native architecture

### 3.2 GcsArtifactService
- **Location**: `src/adk_mcp/adk_production_services.py`
- **Purpose**: Binary data persistence
- **Features**:
  - File upload/download
  - Artifact management
  - Cloud storage integration

### 3.3 VertexAiRagMemoryService
- **Location**: `src/adk_mcp/adk_production_services.py`
- **Purpose**: External knowledge access
- **Features**:
  - Document retrieval
  - Knowledge base integration
  - RAG (Retrieval Augmented Generation)

## 4. ADK Safety & Security

### 4.1 Safety Callbacks
- **Location**: `src/adk_mcp/adk_safety_system.py`
- **Purpose**: Input/output validation and filtering
- **Features**:
  - `before_model_callback`: Input validation
  - `after_model_callback`: Output sanitization
  - `before_tool_callback`: Tool validation
  - `after_tool_callback`: Result filtering

### 4.2 Gemini Flash Lite for Safety
- **Location**: `src/adk_mcp/adk_safety_system.py`
- **Purpose**: Dedicated safety filtering
- **Features**:
  - Content moderation
  - Policy enforcement
  - Risk assessment

## 5. ADK Observability

### 5.1 OpenInference Integration
- **Location**: `src/adk_mcp/adk_observability_system.py`
- **Purpose**: Trace collection and monitoring
- **Features**:
  - Automatic agent run monitoring
  - Tool call tracking
  - Performance metrics
  - Dashboard integration

### 5.2 Performance Monitoring
- **Location**: `src/adk_mcp/adk_monitoring_system.py`
- **Purpose**: System performance tracking
- **Features**:
  - Latency measurement
  - Resource usage monitoring
  - Alerting capabilities

## 6. ADK Enterprise Features

### 6.1 VertexAiSearchTool
- **Location**: `src/adk_mcp/adk_enterprise_integration.py`
- **Purpose**: Advanced document querying
- **Features**:
  - Semantic search
  - Document indexing
  - Enterprise search integration

### 6.2 Memory Service Integration
- **Location**: `src/adk_mcp/adk_enterprise_integration.py`
- **Purpose**: Long-term memory management
- **Features**:
  - Conversation persistence
  - Context retrieval
  - Memory optimization

## 7. Current Server Architecture

### Main Entry Point
- **File**: `run_enterprise_server.py`
- **Purpose**: Launches the complete ADK-integrated system
- **Port**: 8080
- **Features**: All ADK capabilities listed above

### Server Hierarchy
```
run_enterprise_server.py
└── EnterpriseEnhancedVoiceServer
    ├── SafetyEnhancedVoiceServer
    │   ├── ADK Safety Callbacks
    │   └── Security Controls
    ├── ADK Production Services
    │   ├── VertexAiSessionService
    │   ├── GcsArtifactService
    │   └── VertexAiRagMemoryService
    ├── ADK Enterprise Integration
    │   ├── OpenAPIToolset
    │   ├── ApplicationIntegrationToolset
    │   └── VertexAiSearchTool
    └── ADK Observability
        ├── OpenInference Instrumentation
        └── Performance Monitoring
```

## 8. Client-Side ADK Integration

### Voice Interface
- **File**: `static/voice_first_ui.html`
- **Features**:
  - WebSocket connection to ADK Runner
  - Audio capture optimized for ADK
  - Real-time transcription display
  - Voice response playback

### JavaScript Client
- **File**: `static/app.js`
- **Features**:
  - ADK-compatible audio format
  - WebSocket message handling
  - Session management
  - Error handling

## ⚠️ DO NOT IMPLEMENT

### These features are ALREADY provided by ADK:

❌ **Speech-to-Text**: Use ADK Runner.run_live()
❌ **Text-to-Speech**: Use ADK AUDIO response modality
❌ **AI Responses**: Use ADK LlmAgent with Gemini
❌ **Session Management**: Use ADK SessionService
❌ **Code Execution**: Use ADK BuiltInCodeExecutor
❌ **Enterprise Integration**: Use ADK enterprise toolsets
❌ **Safety Filtering**: Use ADK safety callbacks
❌ **Observability**: Use ADK OpenInference integration
❌ **Production Services**: Use ADK production services

## ✅ HOW TO EXTEND

### If you need to add functionality:

1. **Check ADK Documentation**: Verify the feature isn't already available
2. **Use ADK Tools**: Extend existing ADK tools rather than creating new ones
3. **Follow ADK Patterns**: Use ADK callbacks, services, and toolsets
4. **Integrate with Existing**: Add to the current server hierarchy
5. **Document Integration**: Update this reference document

## 🚀 Quick Start

### To run the complete ADK-integrated system:

```bash
# Set environment variables
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_CLOUD_PROJECT="your-project"

# Run the enterprise server
python run_enterprise_server.py

# Access the voice interface
open http://localhost:8080/voice
```

### To verify ADK integration:

```bash
# Check health endpoint
curl http://localhost:8080/health

# Check enterprise features
curl http://localhost:8080/enterprise/status

# Check safety systems
curl http://localhost:8080/safety/status
```

## 📋 Implementation Checklist

Before implementing any new feature, check:

- [ ] Is this already provided by ADK?
- [ ] Can I extend an existing ADK component?
- [ ] Am I following ADK patterns and conventions?
- [ ] Have I checked the current server implementation?
- [ ] Will this integrate with the existing ADK architecture?

## 🔄 Update Process

When ADK features are added or modified:

1. Update this reference document
2. Update the server implementation
3. Update client-side integration if needed
4. Update tests and documentation
5. Verify all ADK features still work together

---

**Remember: The goal is to maximize ADK usage, not duplicate its functionality!**