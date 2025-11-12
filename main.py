from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import Dict, List
import time
import asyncio
import logging
from urllib.parse import unquote
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, Counter, Histogram
from fastapi.responses import Response
import httpx
from dotenv import load_dotenv
from src.adk_ide.observability.tracing import initialize_tracing

logger = logging.getLogger(__name__)

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

# Initialize services and core agents with proper delegation chain
artifact_service = ArtifactService(environment=os.environ.get("ENVIRONMENT", "development"))
code_executor = CodeExecutionAgent(artifact_service=artifact_service)
developing_agent = DevelopingAgent(code_executor=code_executor, artifact_service=artifact_service)
hia = HumanInteractionAgent(code_executor=code_executor, developing_agent=developing_agent)
session_manager = ProductionSessionManager(environment=os.environ.get("ENVIRONMENT", "development"))
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


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "adk-ide"}


@app.post("/orchestrate")
async def orchestrate(request: dict) -> dict:
    # Security callbacks (scaffold): before_model
    blocked = await sec_cb.before_model_callback(request)
    if blocked:
        return blocked
    try:
        result = await hia.run(request)
        return await sec_cb.after_model_callback(result)
    except asyncio.CancelledError:
        # Handle graceful shutdown - request was cancelled
        logger.info("Orchestration request was cancelled (likely during server shutdown)")
        raise  # Re-raise to allow proper cleanup
    except Exception as exc:
        # Log other errors but don't expose internal details
        logger.error(f"Error in orchestration: {exc}", exc_info=True)
        return {
            "status": "error",
            "agent": "human_interaction_agent",
            "error": "An error occurred while processing your request. Please try again.",
        }


@app.post("/execute")
async def execute_code(request: dict) -> dict:
    # before_tool
    btool = await sec_cb.before_tool_callback("code_executor", request)
    if btool:
        return btool
    try:
        result = await code_executor.run(request)
        return await sec_cb.after_tool_callback(result)
    except asyncio.CancelledError:
        logger.info("Code execution request was cancelled (likely during server shutdown)")
        raise
    except Exception as exc:
        logger.error(f"Error in code execution: {exc}", exc_info=True)
        return {
            "status": "error",
            "agent": "code_execution_agent",
            "error": "An error occurred while executing code. Please try again.",
        }


@app.post("/web/assets")
async def save_web_assets(payload: dict) -> dict:
    """Persist web assets (HTML/CSS/JS) via DevelopingAgent."""
    return await developing_agent.save_web_assets(payload)


@app.get("/web/assets/{session_id}")
async def list_web_assets(session_id: str) -> dict:
    """List artifacts saved for a session (used by the web preview)."""
    try:
        return await artifact_service.list_artifacts(session_id=session_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/web/assets/{session_id}/{artifact_name}")
async def get_web_asset(session_id: str, artifact_name: str) -> Response:
    """Fetch a specific artifact (HTML/CSS/JS) for preview rendering."""
    decoded_name = unquote(artifact_name)
    try:
        artifact = await artifact_service.load_artifact(session_id=session_id, artifact_name=decoded_name)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))

    if artifact.get("status") != "success":
        raise HTTPException(status_code=404, detail="Artifact not found")

    content = artifact.get("content", b"")
    if isinstance(content, str):
        content_bytes = content.encode("utf-8")
    else:
        content_bytes = content or b""

    metadata = artifact.get("metadata", {}) or {}
    media_type = metadata.get("content_type") or "text/plain"

    return Response(content=content_bytes, media_type=media_type)


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
    """Check for Google Cloud env readiness and try initializing a client.
    
    Note: GOOGLE_API_KEY is used for ADK/LLM APIs.
    GOOGLE_APPLICATION_CREDENTIALS is used for GCS storage (optional).
    System is ready if API key is set (storage is optional).
    """
    status: Dict[str, object] = {
        "GOOGLE_CLOUD_PROJECT": os.environ.get("GOOGLE_CLOUD_PROJECT"),
        "GOOGLE_API_KEY": "set" if os.environ.get("GOOGLE_API_KEY") else None,
        "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        "adc_file_exists": None,
        "storage_client": None,
        "warnings": [],
    }

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    api_key = os.environ.get("GOOGLE_API_KEY")
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # Check credentials file status
    creds_file_exists = False
    if creds_path:
        creds_file_exists = os.path.exists(creds_path)
        status["adc_file_exists"] = creds_file_exists

    # Try to initialize storage client only if we have valid credentials
    # Storage client requires service account credentials, not API key
    if project:
        # Only try storage client if credentials file exists, or no credentials path is set (try ADC)
        should_try_storage = creds_file_exists or (not creds_path)
        
        if should_try_storage:
            try:
                from google.cloud import storage  # type: ignore
                # Try to initialize storage client
                # This will use the credentials file if set, or ADC otherwise
                storage.Client(project=project)
                # Just creating the client validates credentials
                status["storage_client"] = "initialized"
            except ImportError:
                status["storage_client"] = None
                status["warnings"].append(
                    "google-cloud-storage package not installed. Storage features will use in-memory fallback."
                )
            except Exception as e:  # pragma: no cover
                status["storage_client"] = None
                # Storage failure is not critical if API key is available
                if api_key:
                    status["warnings"].append(
                        f"Storage client unavailable: {str(e)}. "
                        "Storage features will use in-memory fallback. ADK/LLM APIs will work with API key."
                    )
                else:
                    status["warnings"].append(f"Storage client initialization failed: {str(e)}")
        else:
            # Credentials file path is set but file doesn't exist
            # Don't try to initialize storage client (it will fail)
            status["storage_client"] = None
            if api_key:
                # Only add warning if API key is set (system will work without storage)
                status["warnings"].append(
                    "Storage features unavailable (credentials file not found). "
                    "Using in-memory fallback. ADK/LLM APIs will work with API key."
                )
            else:
                # No API key and no credentials - this is a problem
                status["warnings"].append(
                    f"Credentials file not found: {creds_path}. "
                    "Either set GOOGLE_API_KEY or provide valid GOOGLE_APPLICATION_CREDENTIALS."
                )

    # Summarize readiness
    # Ready if we have project and API key (storage is optional)
    has_project = bool(project)
    has_api_key = bool(api_key)
    
    # System is ready if API key is set (ADK/LLM APIs will work)
    # Storage is optional and can use in-memory fallback
    ready = has_project and has_api_key
    status["ready"] = ready
    
    # Add helpful message if not ready
    if not ready:
        if not has_project:
            status["warnings"].append("GOOGLE_CLOUD_PROJECT not set")
        if not has_api_key:
            status["warnings"].append("GOOGLE_API_KEY not set (required for ADK/LLM APIs)")
    
    # Clean up warnings if empty
    if not status["warnings"]:
        del status["warnings"]
    elif len(status["warnings"]) == 1 and not ready:
        # If only one warning and not ready, promote it to error message
        status["error"] = status["warnings"][0]
        del status["warnings"]
    
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


@app.get("/proxy/schemastore/{path:path}")
async def proxy_schemastore(path: str, request: Request) -> Response:
    """Proxy requests to schemastore.org to avoid browser CORS.
    Example: /proxy/schemastore/api/json/catalog.json
    """
    target_url = f"https://schemastore.org/{path}"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(target_url)
            headers = {"Content-Type": resp.headers.get("content-type", "application/json")}
            # Optional caching to be polite to the upstream
            cache_control = resp.headers.get("cache-control") or "public, max-age=3600"
            headers["Cache-Control"] = cache_control
            return Response(content=resp.content, media_type=headers["Content-Type"], status_code=resp.status_code, headers=headers)
    except Exception as e:
        return Response(content=str(e).encode(), media_type="text/plain", status_code=502)

