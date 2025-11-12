# ADK IDE Project Structure

This repository contains the clean, organized implementation of the ADK IDE after overhaul.

## Directory Structure

```
adk-ide/
├── src/                          # Backend Python code
│   └── adk_ide/                  # Core ADK IDE implementation
│       ├── agents/               # Multi-agent system
│       ├── services/             # Session, artifact, etc.
│       ├── tools/                # ADK tools
│       ├── security/             # Security callbacks
│       ├── websocket/            # WebSocket handlers
│       └── observability/        # Tracing and metrics
├── theia-fresh/                  # Frontend: Eclipse Theia IDE with ADK integration
│   ├── packages/adk-ide/         # ADK-specific Theia extensions
│   ├── packages/core/            # Theia core
│   └── ...                       # Other Theia packages and configs
├── docs/                         # Documentation
│   ├── adk/                      # ADK-specific guides and references
│   │   ├── adk implementation requirements.txt
│   │   ├── ADK_*.md              # Various ADK guides
│   │   └── API_REFERENCE.md
│   └── development/              # Development process docs
│       ├── DEVELOPMENT_PROCESS.md
│       ├── MILESTONES.md
│       └── PROJECT_TRANSFORMATION_ANALYSIS.md
├── tests/                        # Test suite
│   ├── test_api.py
│   ├── test_ide_components.py
│   ├── test_tools.py
│   └── test_workflow_agents.py
├── main.py                       # FastAPI entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose setup
├── .env                          # Environment variables (untracked)
├── README.md                     # Project overview
├── LICENSE                       # MIT License
└── PROJECT_STRUCTURE.md          # This file
```

## Key Components

### 1. Backend (src/adk_ide/)
- Multi-agent architecture using Google ADK
- FastAPI-based API with WebSocket support
- Secure code execution and session management
- Observability with OpenTelemetry and Prometheus

### 2. Frontend (theia-fresh/)
- Eclipse Theia IDE framework
- Integrated ADK agents for AI-assisted development
- VS Code extension compatibility
- Modern web-based IDE with voice-first capabilities via ADK

### 3. Documentation (docs/)
- **docs/adk/**: Comprehensive ADK guides, API reference, implementation requirements
- **docs/development/**: Development workflows, milestones, transformation analysis

### 4. Testing (tests/)
- Unit and integration tests for API, agents, tools, and workflows

## Removed Components
- Temporary setup scripts and fix guides (PS1 files)
- Redundant documentation and progress reports
- Duplicate frontend directories
- __pycache__ artifacts

## Next Steps
1. **Review Requirements**: Start with `docs/adk/adk implementation requirements.txt`
2. **Environment Setup**: Ensure `.env` has Google Cloud credentials
3. **Backend**: `pip install -r requirements.txt` then `uvicorn main:app --reload`
4. **Docker**: `docker-compose up --build` for full stack
5. **Frontend (Theia)**: `cd theia-fresh; yarn install; yarn start` for IDE
6. **Voice Integration**: Access via ADK audio modalities in the running service
7. **Testing**: `pytest tests/`

This structure focuses on the core ADK IDE functionality with clean separation of backend, frontend, docs, and tests.