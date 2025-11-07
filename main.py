from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json
from typing import Dict
import time
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, Counter, Histogram
from fastapi.responses import Response
from dotenv import load_dotenv
from src.adk_ide.observability.tracing import initialize_tracing

from src.adk_ide.agents.cea import CodeExecutionAgent
from src.adk_ide.agents.hia import HumanInteractionAgent
from src.adk_ide.agents.da import DevelopingAgent
from src.adk_ide.services.session import ProductionSessionManager
from src.adk_ide.services.artifact import ArtifactService
from src.adk_ide.security import callbacks as sec_cb
from src.adk_ide.websocket.handler import WebSocketManager


load_dotenv()

app = FastAPI(title="ADK IDE Service", version="0.1.0")

# Add CORS middleware to allow browser connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for the web UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize core agents with proper delegation chain
code_executor = CodeExecutionAgent()
developing_agent = DevelopingAgent(code_executor=code_executor)
hia = HumanInteractionAgent(code_executor=code_executor, developing_agent=developing_agent)
session_manager = ProductionSessionManager(environment=os.environ.get("ENVIRONMENT", "development"))
artifact_service = ArtifactService(environment=os.environ.get("ENVIRONMENT", "development"))
base_path = os.environ.get("PROJECT_BASE_PATH", os.getcwd())
websocket_manager = WebSocketManager(hia=hia, code_executor=code_executor, base_path=base_path)

# Initialize tracing if configured
_trace_error = initialize_tracing(service_name="adk-ide-service")

# Basic Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration", ["path"])


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    try:
        REQUEST_COUNT.labels(method=request.method, path=request.url.path, status=response.status_code).inc()
        REQUEST_DURATION.labels(path=request.url.path).observe(duration)
    except Exception:  # pragma: no cover
        pass
    return response


@app.get("/")
async def root():
    """Serve the main web UI"""
    return FileResponse("static/index.html")


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "adk-ide"}


@app.post("/orchestrate")
async def orchestrate(request: dict) -> dict:
    # Security callbacks (scaffold): before_model
    blocked = await sec_cb.before_model_callback(request)
    if blocked:
        return blocked
    result = await hia.run(request)
    return await sec_cb.after_model_callback(result)


@app.post("/execute")
async def execute_code(request: dict) -> dict:
    # before_tool
    btool = await sec_cb.before_tool_callback("code_executor", request)
    if btool:
        return btool
    result = await code_executor.run(request)
    return await sec_cb.after_tool_callback(result)


@app.post("/session/new")
async def create_session(request: dict) -> dict:
    user_id = request.get("user_id", "anonymous")
    project_context = request.get("project", "default")
    return await session_manager.create_session(user_id=user_id, project_context=project_context)


@app.post("/auth/login")
async def auth_login(request: dict) -> dict:
    """Dev-only login that issues a JWT for a given user_id."""
    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    session = await session_manager.create_session(user_id=user_id, project_context=request.get("project", "default"))
    return {"token": session["token"], "session_id": session["session_id"]}


@app.post("/auth/validate")
async def auth_validate(request: dict) -> dict:
    token = request.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="token is required")
    return session_manager.validate_token(token)


def _check_google_cloud() -> Dict[str, object]:
    """Check for Google Cloud env readiness and try initializing a client."""
    status: Dict[str, object] = {
        "GOOGLE_CLOUD_PROJECT": os.environ.get("GOOGLE_CLOUD_PROJECT"),
        "GOOGLE_API_KEY": "set" if os.environ.get("GOOGLE_API_KEY") else None,
        "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        "adc_file_exists": None,
        "storage_client": None,
        "error": None,
    }

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        status["adc_file_exists"] = os.path.exists(creds_path)

    # Best-effort client init (will succeed only if credentials are valid)
    try:
        from google.cloud import storage  # type: ignore

        _ = storage.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        status["storage_client"] = "initialized"
    except Exception as e:  # pragma: no cover
        status["storage_client"] = None
        status["error"] = str(e)

    # Summarize readiness
    ready = bool(status["GOOGLE_CLOUD_PROJECT"]) and (
        bool(status["GOOGLE_API_KEY"]) or bool(status["adc_file_exists"]) or bool(status["storage_client"])  # noqa: E501
    )
    status["ready"] = ready
    return status


@app.get("/cloud/status")
async def cloud_status() -> dict:
    return json.loads(json.dumps(_check_google_cloud()))


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent interactions."""
    await websocket_manager.websocket_endpoint(websocket)

