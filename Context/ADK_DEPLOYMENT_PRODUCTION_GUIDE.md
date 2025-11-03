# ADK Deployment and Production Guide

## Overview

This guide covers deploying ADK agents to production environments, including containerization, cloud deployment, scaling, monitoring, and best practices for production-ready systems.

## Deployment Options

### 1. Vertex AI Agent Engine (Recommended)

The easiest way to deploy ADK agents with enterprise-grade scalability.

#### Basic Deployment

```python
from google.adk.deploy import VertexAiDeployment
from google.adk.agents import Agent

# Create your agent
agent = Agent(
    name="production_agent",
    model="gemini-2.5-flash",
    instruction="You are a production-ready assistant.",
    tools=[your_tools]
)

# Deploy to Vertex AI Agent Engine
deployment = VertexAiDeployment(
    project_id="your-project-id",
    region="us-central1",
    agent=agent,
    display_name="Production Agent"
)

# Deploy
deployment_info = await deployment.deploy()
print(f"Agent deployed: {deployment_info.endpoint}")
```

#### Advanced Configuration

```python
from google.adk.deploy import VertexAiDeployment, DeploymentConfig

# Configure deployment
config = DeploymentConfig(
    machine_type="n1-standard-4",
    min_replica_count=2,
    max_replica_count=10,
    cpu_utilization_target=70,
    memory_utilization_target=80,
    enable_auto_scaling=True,
    enable_logging=True,
    enable_monitoring=True
)

deployment = VertexAiDeployment(
    project_id="your-project-id",
    region="us-central1",
    agent=agent,
    config=config
)

# Deploy with custom configuration
deployment_info = await deployment.deploy()
```

### 2. Cloud Run Deployment

For serverless deployment with automatic scaling.

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE $PORT

# Run application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
```

#### FastAPI Application

```python
from fastapi import FastAPI, HTTPException
from google.adk.core import Runner
from google.adk.agents import Agent
import os

app = FastAPI(title="ADK Production Service")

# Initialize agent
agent = Agent(
    name="production_agent",
    model="gemini-2.5-flash",
    instruction="You are a production assistant."
)

runner = Runner(agent=agent)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "adk-agent"}

@app.post("/chat")
async def chat(message: str):
    """Chat endpoint."""
    try:
        result = await runner.run(message)
        return {
            "response": result.response,
            "session_id": result.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(message: str):
    """Streaming chat endpoint."""
    from fastapi.responses import StreamingResponse
    
    async def generate():
        async for event in runner.run_stream(message):
            yield f"data: {event.json()}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy adk-agent \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --concurrency 100 \
    --max-instances 10 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. Google Kubernetes Engine (GKE)

For full control and advanced orchestration.

#### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
  labels:
    app: adk-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      containers:
      - name: adk-agent
        image: gcr.io/your-project/adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
        - name: PORT
          value: "8080"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: adk-agent-service
spec:
  selector:
    app: adk-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: adk-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: adk-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### Deploy to GKE

```bash
# Create GKE cluster
gcloud container clusters create adk-cluster \
    --zone us-central1-a \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10

# Build and push image
docker build -t gcr.io/your-project/adk-agent:latest .
docker push gcr.io/your-project/adk-agent:latest

# Deploy to cluster
kubectl apply -f deployment.yaml
```

## Production Configuration

### 1. Environment Variables

```bash
# Core ADK Configuration
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_API_KEY="your-api-key"
export ADK_LOG_LEVEL="INFO"

# Production Settings
export ADK_MAX_CONCURRENT_SESSIONS=1000
export ADK_SESSION_TIMEOUT=3600
export ADK_MAX_LLM_CALLS=100

# Security Settings
export ADK_JWT_SECRET="your-jwt-secret"
export ADK_ENABLE_AUTH=true
export ADK_RATE_LIMIT_ENABLED=true

# Monitoring Settings
export ADK_ENABLE_TRACING=true
export ADK_METRICS_ENDPOINT="/metrics"
export ADK_HEALTH_CHECK_ENDPOINT="/health"

# Database Configuration (if using persistent storage)
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export REDIS_URL="redis://host:6379/0"
```

### 2. Production Agent Configuration

```python
from google.adk.agents import Agent
from google.adk.core import GenerateContentConfig, RunConfig, StreamingMode
from google.adk.services import VertexAiSessionService, GcsArtifactService

# Production-optimized model configuration
model_config = GenerateContentConfig(
    temperature=0.3,  # Lower temperature for consistency
    max_output_tokens=1024,  # Reasonable limit
    top_p=0.8,
    top_k=40
)

# Production agent
production_agent = Agent(
    name="production_assistant",
    model="gemini-2.5-flash",
    instruction="""You are a production assistant. 
    Be helpful, accurate, and concise. 
    Always validate inputs and handle errors gracefully.""",
    generate_content_config=model_config,
    tools=production_tools
)

# Production services
session_service = VertexAiSessionService(
    project_id="your-project-id",
    location="us-central1"
)

artifact_service = GcsArtifactService(
    project_id="your-project-id",
    bucket_name="your-artifacts-bucket"
)

# Production run configuration
run_config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=50,  # Prevent runaway costs
    save_input_blobs_as_artifacts=False,  # Optimize performance
    response_modalities=["TEXT"]
)
```

### 3. Production Services Setup

```python
from google.adk.services import (
    VertexAiSessionService,
    GcsArtifactService,
    VertexAiRagMemoryService
)

class ProductionServices:
    """Production service configuration."""
    
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        
        # Session service for persistent sessions
        self.session_service = VertexAiSessionService(
            project_id=project_id,
            location=region
        )
        
        # Artifact service for file storage
        self.artifact_service = GcsArtifactService(
            project_id=project_id,
            bucket_name=f"{project_id}-adk-artifacts"
        )
        
        # Memory service for RAG
        self.memory_service = VertexAiRagMemoryService(
            project_id=project_id,
            location=region,
            corpus_id="production-corpus"
        )
    
    async def initialize(self):
        """Initialize all services."""
        # Create GCS bucket if it doesn't exist
        await self._ensure_bucket_exists()
        
        # Initialize memory corpus
        await self._ensure_corpus_exists()
    
    async def _ensure_bucket_exists(self):
        """Ensure GCS bucket exists."""
        from google.cloud import storage
        
        client = storage.Client(project=self.project_id)
        bucket_name = f"{self.project_id}-adk-artifacts"
        
        try:
            client.get_bucket(bucket_name)
        except Exception:
            # Create bucket
            bucket = client.create_bucket(bucket_name, location="US")
            print(f"Created bucket: {bucket_name}")
    
    async def _ensure_corpus_exists(self):
        """Ensure RAG corpus exists."""
        # Implementation depends on your RAG setup
        pass

# Initialize production services
services = ProductionServices("your-project-id", "us-central1")
await services.initialize()
```

## Monitoring and Observability

### 1. OpenInference Integration

```python
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(trace_sdk.TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter (for services like Arize, Phoenix, etc.)
otlp_exporter = OTLPSpanExporter(
    endpoint="https://your-observability-endpoint/v1/traces",
    headers={"api-key": "your-api-key"}
)

# Add span processor
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument ADK
GoogleADKInstrumentor().instrument()
```

### 2. Custom Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
REQUEST_COUNT = Counter('adk_requests_total', 'Total ADK requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('adk_request_duration_seconds', 'Request duration')
ACTIVE_SESSIONS = Gauge('adk_active_sessions', 'Number of active sessions')
LLM_CALLS = Counter('adk_llm_calls_total', 'Total LLM calls', ['model'])

class MetricsMiddleware:
    """Middleware for collecting metrics."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Increment request counter
            REQUEST_COUNT.labels(
                method=scope["method"],
                endpoint=scope["path"]
            ).inc()
            
            # Process request
            await self.app(scope, receive, send)
            
            # Record duration
            duration = time.time() - start_time
            REQUEST_DURATION.observe(duration)
        else:
            await self.app(scope, receive, send)

# Start metrics server
start_http_server(9090)
```

### 3. Health Checks

```python
from fastapi import FastAPI
from google.adk.core import Runner
import asyncio

app = FastAPI()

class HealthChecker:
    """Comprehensive health checking."""
    
    def __init__(self, runner: Runner):
        self.runner = runner
        self.last_check = None
        self.is_healthy = True
    
    async def check_health(self) -> dict:
        """Perform health check."""
        checks = {}
        overall_healthy = True
        
        # Check ADK agent
        try:
            test_result = await asyncio.wait_for(
                self.runner.run("Health check"),
                timeout=5.0
            )
            checks["adk_agent"] = {"status": "healthy", "response_time": "< 5s"}
        except asyncio.TimeoutError:
            checks["adk_agent"] = {"status": "unhealthy", "error": "timeout"}
            overall_healthy = False
        except Exception as e:
            checks["adk_agent"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False
        
        # Check external dependencies
        checks["database"] = await self._check_database()
        checks["storage"] = await self._check_storage()
        checks["memory_service"] = await self._check_memory_service()
        
        # Update overall health
        for check in checks.values():
            if check["status"] != "healthy":
                overall_healthy = False
        
        self.is_healthy = overall_healthy
        self.last_check = time.time()
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": self.last_check,
            "checks": checks
        }
    
    async def _check_database(self) -> dict:
        """Check database connectivity."""
        try:
            # Implement database check
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_storage(self) -> dict:
        """Check storage service."""
        try:
            # Implement storage check
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_memory_service(self) -> dict:
        """Check memory service."""
        try:
            # Implement memory service check
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Initialize health checker
health_checker = HealthChecker(runner)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return await health_checker.check_health()

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe."""
    health_status = await health_checker.check_health()
    if health_status["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Not ready")
```

## Security Best Practices

### 1. Authentication and Authorization

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

app = FastAPI()
security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token.credentials, "your-secret", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/chat")
async def protected_chat(message: str, user=Depends(verify_token)):
    """Protected chat endpoint."""
    # Process with user context
    result = await runner.run(message, user_context=user)
    return {"response": result.response}
```

### 2. Input Validation and Sanitization

```python
from pydantic import BaseModel, validator
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 10000:
            raise ValueError('Message too long')
        return v.strip()
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if v and not v.isalnum():
            raise ValueError('Invalid session ID format')
        return v

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with input validation."""
    result = await runner.run(
        request.message,
        session_id=request.session_id
    )
    return {"response": result.response}
```

### 3. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def rate_limited_chat(request: Request, message: str):
    """Rate-limited chat endpoint."""
    result = await runner.run(message)
    return {"response": result.response}
```

## Scaling and Performance

### 1. Connection Pooling

```python
import asyncio
from typing import Dict, Any

class ConnectionPool:
    """Connection pool for external services."""
    
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.connections = asyncio.Queue(maxsize=max_connections)
        self.active_connections = 0
    
    async def get_connection(self):
        """Get connection from pool."""
        if self.connections.empty() and self.active_connections < self.max_connections:
            # Create new connection
            connection = await self._create_connection()
            self.active_connections += 1
            return connection
        else:
            # Wait for available connection
            return await self.connections.get()
    
    async def return_connection(self, connection):
        """Return connection to pool."""
        await self.connections.put(connection)
    
    async def _create_connection(self):
        """Create new connection."""
        # Implement connection creation logic
        pass

# Use connection pool
pool = ConnectionPool(max_connections=50)
```

### 2. Caching Strategy

```python
import redis
import json
from typing import Optional

class CacheManager:
    """Redis-based caching for ADK responses."""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
    
    def _cache_key(self, message: str, user_id: str) -> str:
        """Generate cache key."""
        import hashlib
        key_data = f"{message}:{user_id}"
        return f"adk:cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def get_cached_response(self, message: str, user_id: str) -> Optional[dict]:
        """Get cached response."""
        key = self._cache_key(message, user_id)
        cached = self.redis_client.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_response(self, message: str, user_id: str, response: dict, ttl: int = None):
        """Cache response."""
        key = self._cache_key(message, user_id)
        ttl = ttl or self.default_ttl
        
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(response)
        )

# Use caching
cache_manager = CacheManager("redis://localhost:6379")

@app.post("/chat")
async def cached_chat(message: str, user_id: str):
    """Chat with caching."""
    # Check cache first
    cached_response = await cache_manager.get_cached_response(message, user_id)
    if cached_response:
        return cached_response
    
    # Generate new response
    result = await runner.run(message)
    response = {"response": result.response}
    
    # Cache response
    await cache_manager.cache_response(message, user_id, response)
    
    return response
```

### 3. Load Balancing

```yaml
# nginx.conf for load balancing
upstream adk_backend {
    least_conn;
    server adk-instance-1:8080 max_fails=3 fail_timeout=30s;
    server adk-instance-2:8080 max_fails=3 fail_timeout=30s;
    server adk-instance-3:8080 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://adk_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        access_log off;
        proxy_pass http://adk_backend;
    }
}
```

## Disaster Recovery

### 1. Backup Strategy

```python
import asyncio
import json
from datetime import datetime
from google.cloud import storage

class BackupManager:
    """Backup manager for ADK data."""
    
    def __init__(self, project_id: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(project=project_id)
    
    async def backup_sessions(self):
        """Backup active sessions."""
        # Get all active sessions
        sessions = await self._get_active_sessions()
        
        # Create backup
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "sessions": sessions,
            "version": "1.0"
        }
        
        # Upload to GCS
        backup_name = f"sessions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        await self._upload_backup(backup_name, backup_data)
    
    async def backup_artifacts(self):
        """Backup artifacts."""
        # Implementation for artifact backup
        pass
    
    async def restore_sessions(self, backup_name: str):
        """Restore sessions from backup."""
        backup_data = await self._download_backup(backup_name)
        
        # Restore sessions
        for session_data in backup_data["sessions"]:
            await self._restore_session(session_data)
    
    async def _get_active_sessions(self):
        """Get all active sessions."""
        # Implementation depends on your session storage
        pass
    
    async def _upload_backup(self, name: str, data: dict):
        """Upload backup to GCS."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(f"backups/{name}")
        blob.upload_from_string(json.dumps(data))
    
    async def _download_backup(self, name: str) -> dict:
        """Download backup from GCS."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(f"backups/{name}")
        return json.loads(blob.download_as_text())
    
    async def _restore_session(self, session_data: dict):
        """Restore individual session."""
        # Implementation depends on your session storage
        pass

# Schedule regular backups
backup_manager = BackupManager("your-project-id", "your-backup-bucket")

async def scheduled_backup():
    """Scheduled backup task."""
    while True:
        try:
            await backup_manager.backup_sessions()
            await backup_manager.backup_artifacts()
            print(f"Backup completed at {datetime.now()}")
        except Exception as e:
            print(f"Backup failed: {e}")
        
        # Wait 6 hours
        await asyncio.sleep(6 * 3600)

# Start backup task
asyncio.create_task(scheduled_backup())
```

### 2. Circuit Breaker Pattern

```python
import asyncio
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Use circuit breaker
llm_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

async def protected_llm_call(message: str):
    """LLM call with circuit breaker protection."""
    return await llm_circuit_breaker.call(runner.run, message)
```

## Cost Optimization

### 1. Model Selection Strategy

```python
from google.adk.agents import Agent

class ModelSelector:
    """Intelligent model selection for cost optimization."""
    
    def __init__(self):
        self.models = {
            "simple": {
                "name": "gemini-1.5-flash-8b",
                "cost_per_token": 0.000001,
                "max_complexity": 3
            },
            "standard": {
                "name": "gemini-2.5-flash",
                "cost_per_token": 0.000005,
                "max_complexity": 7
            },
            "advanced": {
                "name": "gemini-2.5-pro",
                "cost_per_token": 0.00002,
                "max_complexity": 10
            }
        }
    
    def select_model(self, message: str, complexity_score: int = None) -> str:
        """Select appropriate model based on complexity."""
        if complexity_score is None:
            complexity_score = self._calculate_complexity(message)
        
        for tier, config in self.models.items():
            if complexity_score <= config["max_complexity"]:
                return config["name"]
        
        return self.models["advanced"]["name"]
    
    def _calculate_complexity(self, message: str) -> int:
        """Calculate message complexity score."""
        score = 0
        
        # Length factor
        score += min(len(message) // 100, 3)
        
        # Complexity keywords
        complex_keywords = ["analyze", "compare", "explain", "code", "algorithm"]
        score += sum(1 for keyword in complex_keywords if keyword in message.lower())
        
        # Question complexity
        if "?" in message:
            score += message.count("?")
        
        return min(score, 10)

# Use model selector
model_selector = ModelSelector()

async def optimized_chat(message: str):
    """Chat with cost-optimized model selection."""
    selected_model = model_selector.select_model(message)
    
    # Create agent with selected model
    agent = Agent(
        name="cost_optimized_agent",
        model=selected_model,
        instruction="You are a helpful assistant."
    )
    
    runner = Runner(agent=agent)
    return await runner.run(message)
```

### 2. Token Usage Monitoring

```python
class TokenUsageMonitor:
    """Monitor and control token usage."""
    
    def __init__(self, daily_limit: int = 1000000):
        self.daily_limit = daily_limit
        self.usage_today = 0
        self.last_reset = datetime.now().date()
    
    def check_usage(self, estimated_tokens: int) -> bool:
        """Check if usage is within limits."""
        self._reset_if_new_day()
        
        if self.usage_today + estimated_tokens > self.daily_limit:
            return False
        
        return True
    
    def record_usage(self, tokens_used: int):
        """Record token usage."""
        self._reset_if_new_day()
        self.usage_today += tokens_used
    
    def _reset_if_new_day(self):
        """Reset usage counter for new day."""
        today = datetime.now().date()
        if today > self.last_reset:
            self.usage_today = 0
            self.last_reset = today
    
    def get_usage_stats(self) -> dict:
        """Get usage statistics."""
        self._reset_if_new_day()
        
        return {
            "usage_today": self.usage_today,
            "daily_limit": self.daily_limit,
            "remaining": self.daily_limit - self.usage_today,
            "percentage_used": (self.usage_today / self.daily_limit) * 100
        }

# Use token monitor
token_monitor = TokenUsageMonitor(daily_limit=500000)

async def monitored_chat(message: str):
    """Chat with token usage monitoring."""
    estimated_tokens = len(message.split()) * 1.3  # Rough estimation
    
    if not token_monitor.check_usage(estimated_tokens):
        raise HTTPException(status_code=429, detail="Daily token limit exceeded")
    
    result = await runner.run(message)
    
    # Record actual usage (would need to get from ADK response)
    actual_tokens = result.usage.total_tokens if hasattr(result, 'usage') else estimated_tokens
    token_monitor.record_usage(actual_tokens)
    
    return {"response": result.response, "usage": token_monitor.get_usage_stats()}
```

This comprehensive deployment and production guide covers all aspects of running ADK agents in production environments, from basic deployment to advanced scaling, monitoring, and cost optimization strategies.