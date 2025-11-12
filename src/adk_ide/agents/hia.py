from typing import Any, Dict, Optional, Callable
import os
import logging
import time
import asyncio

from .base import ADKIDEAgent, AgentCommunication
from .cea import CodeExecutionAgent

logger = logging.getLogger(__name__)

try:  # pragma: no cover
    from prometheus_client import Counter, Histogram  # type: ignore
except Exception:  # pragma: no cover
    Counter = Histogram = None  # type: ignore

try:  # pragma: no cover
    from opentelemetry import trace  # type: ignore
    _delegation_tracer = trace.get_tracer(__name__)
except Exception:  # pragma: no cover
    _delegation_tracer = None

DELEGATION_COUNT: Any
DELEGATION_ESCALATIONS: Any
DELEGATION_DURATION: Any

if Counter is not None:  # pragma: no cover
    DELEGATION_COUNT = Counter(
        "adk_delegations_total",
        "Total number of ADK agent delegations triggered by the Human Interaction Agent",
        ["target"],
    )
    DELEGATION_ESCALATIONS = Counter(
        "adk_delegation_escalations_total",
        "Total number of escalation signals emitted by delegated agents",
        ["agent"],
    )
else:  # pragma: no cover
    DELEGATION_COUNT = None
    DELEGATION_ESCALATIONS = None

if Histogram is not None:  # pragma: no cover
    DELEGATION_DURATION = Histogram(
        "adk_delegation_duration_seconds",
        "Duration (seconds) of delegated agent execution handled by HIA",
        ["target"],
    )
else:  # pragma: no cover
    DELEGATION_DURATION = None


class HumanInteractionAgent(ADKIDEAgent):
    """Central orchestrator with optional ADK LlmAgent integration.

    Controlled via environment flag `ADK_ENABLED` ("true" to enable). Falls back
    to scaffold behavior if ADK is unavailable or disabled.
    
    Supports multi-agent delegation via EventActions.transfer_to_agent when
    sub_agents are configured.
    """

    def __init__(self, code_executor: CodeExecutionAgent, developing_agent: Optional[ADKIDEAgent] = None, session_service: Optional[object] = None) -> None:
        super().__init__(name="human_interaction_agent", description="Central orchestrator")
        self.code_executor = code_executor
        self.developing_agent = developing_agent
        self._llm_agent: Optional[object] = None
        self._llm_agent_run: Optional[Callable[..., Any]] = None
        self._session_service = session_service
        self._adk_session_service: Optional[object] = None

        adk_enabled = os.environ.get("ADK_ENABLED", "false").lower() == "true"
        logger.info(f"ADK_ENABLED: {adk_enabled}")
        
        if adk_enabled:
            # Create ADK session service for Runner if not provided
            if self._session_service is None:
                try:
                    from google.adk.sessions import InMemorySessionService  # type: ignore
                    self._adk_session_service = InMemorySessionService()
                    logger.info("Created InMemorySessionService for ADK Runner")
                except Exception as e:
                    logger.warning(f"Could not create InMemorySessionService: {e}")
                    # Will try to create on-demand in run method
            else:
                self._adk_session_service = self._session_service
                
            # Initialize LlmAgent
            try:  # pragma: no cover
                from google.adk.agents import LlmAgent  # type: ignore
                logger.info("Successfully imported ADK LlmAgent")
                # Tool wiring: HIA doesn't need direct tools since it can delegate to Developing Agent
                # The Developing Agent has code execution tools properly configured
                # This avoids tool compatibility issues with ADK's FunctionTool
                # LlmAgent requires tools to be a list, not None, so use empty list
                tools = []
                logger.debug("HIA agent running without direct tools - will delegate to Developing Agent for code execution")

                # Configure sub_agents for transfer_to_agent delegation
                # LlmAgent requires sub_agents to be a list, not None
                sub_agents = []
                if developing_agent is not None and hasattr(developing_agent, "_llm_agent") and developing_agent._llm_agent is not None:
                    sub_agents = [developing_agent._llm_agent]
                    logger.debug(f"Configured sub_agents for delegation: {len(sub_agents)} agent(s)")
                else:
                    logger.debug("No sub_agents configured - delegation not available")

                # Get model from environment or use default
                # Common models: "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"
                model = os.environ.get("ADK_MODEL", os.environ.get("GOOGLE_MODEL", "gemini-2.5-flash"))
                logger.info(f"Using model: {model}")

                self._llm_agent = LlmAgent(
                    name="HumanInteractionAgent",
                    model=model,  # Required: specify the LLM model
                    description="Central orchestrator for development tasks. Delegate complex development tasks to the Developing Agent when needed.",
                    tools=tools,  # Empty list - no direct tools, will delegate to Developing Agent
                    sub_agents=sub_agents,  # Enable transfer_to_agent delegation if Developing Agent is available
                    instruction="You are the central orchestrator. When you receive complex development tasks that require code generation or modification, you should delegate to the Developing Agent using transfer_to_agent. The Developing Agent has access to code execution capabilities. Always delegate development and code-related tasks to the Developing Agent.",
                    output_key="hia_response",  # Save responses to session.state["hia_response"]
                )
                logger.info("ADK LlmAgent initialized successfully")
                
                # Note: We'll create Runner on-demand in the run method
                # Runner may need to be created per request or per agent
                logger.info("ADK LlmAgent ready for Runner execution")
            except Exception as exc:
                logger.error(f"Failed to initialize ADK LlmAgent: {exc}", exc_info=True)
                self._llm_agent = None
                self._llm_agent_run = None
        else:
            logger.info("ADK not enabled, HIA will use fallback behavior")

    def _extract_response_text(self, result: Any, request: Dict[str, Any]) -> str:
        """Extract response text from ADK LlmAgent result in various formats.
        
        ADK LlmAgent with output_key="hia_response" saves responses to session.state["hia_response"].
        The result might be the session object, a response object containing the session, or the response text directly.
        Also handles Content objects from google.genai.types.
        """
        if result is None:
            return ""
        
        # Handle Content objects from google.genai.types
        try:
            from google.genai.types import Content, Part  # type: ignore
            if isinstance(result, Content):
                # Extract text from Content object
                text_parts = []
                if hasattr(result, "parts"):
                    for part in result.parts:
                        # Handle Part objects
                        if hasattr(part, "text") and part.text:
                            text_parts.append(str(part.text))
                        # Handle dict parts
                        elif isinstance(part, dict):
                            if "text" in part and part["text"]:
                                text_parts.append(str(part["text"]))
                            # Also check for inline_data or other content types
                            elif "inline_data" in part:
                                # Skip binary data
                                continue
                        # Handle string parts
                        elif isinstance(part, str):
                            text_parts.append(part)
                
                if text_parts:
                    combined = "".join(text_parts)
                    logger.debug(f"Extracted text from Content object: {len(combined)} chars")
                    return combined
                
                # Fallback: try to get text directly
                if hasattr(result, "text") and result.text:
                    return str(result.text)
                
                # Try role and parts if available
                if hasattr(result, "role"):
                    logger.debug(f"Content object has role: {result.role}")
        except (ImportError, AttributeError) as e:
            logger.debug(f"Could not handle Content object: {e}")
            pass
        
        # If result is a string, return it directly
        if isinstance(result, str):
            return result
        
        # If result is a dict, try multiple possible keys
        if isinstance(result, dict):
            # First, try to get from session.state (ADK saves to output_key)
            # Check if result itself is a session-like object
            if hasattr(result, "state") and hasattr(result.state, "get"):
                session_state = result.state
                if isinstance(session_state, dict):
                    for key in ["hia_response", "developing_agent_response", "delegated_response"]:
                        stored_value = session_state.get(key)
                        if stored_value:
                            if isinstance(stored_value, str):
                                return stored_value
                            elif isinstance(stored_value, dict):
                                # Recursively extract from nested response
                                return self._extract_response_text(stored_value, request)
                            else:
                                # Handle Content objects or other types stored in session state
                                extracted = self._extract_response_text(stored_value, request)
                                if extracted:
                                    return extracted
            
            # Check if result contains a session object
            if "session" in result:
                session = result["session"]
                # Try different ways to access session state
                if hasattr(session, "state"):
                    session_state = session.state
                    if isinstance(session_state, Dict):
                        for key in ["hia_response", "developing_agent_response", "delegated_response", "web_preview_message"]:
                            stored_value = session_state.get(key)
                            if stored_value:
                                if isinstance(stored_value, str):
                                    return stored_value
                                elif isinstance(stored_value, dict):
                                    return self._extract_response_text(stored_value, request)
                elif isinstance(session, dict) and "state" in session:
                    session_state = session["state"]
                    if isinstance(session_state, Dict):
                        for key in ["hia_response", "developing_agent_response", "delegated_response", "web_preview_message"]:
                            stored_value = session_state.get(key)
                            if stored_value:
                                if isinstance(stored_value, str):
                                    return stored_value
                                elif isinstance(stored_value, dict):
                                    return self._extract_response_text(stored_value, request)
            
            # Try common ADK response keys directly
            for key in ["response", "text", "content", "message", "output", "result", "data", "developing_agent_response", "delegated_response", "web_preview_message"]:
                if key in result:
                    value = result[key]
                    if isinstance(value, str) and value.strip():
                        return value
                    elif isinstance(value, dict):
                        # Recursively check nested structures
                        nested = self._extract_response_text(value, request)
                        if nested:
                            return nested
                    else:
                        # Try to extract from non-string values (e.g., Content objects, other types)
                        extracted = self._extract_response_text(value, request)
                        if extracted:
                            return extracted
            
            # Check for event_actions or other nested structures
            if "event_actions" in result:
                event_actions = result["event_actions"]
                if isinstance(event_actions, dict):
                    for key in ["response", "text", "message", "output"]:
                        if key in event_actions:
                            value = event_actions[key]
                            if isinstance(value, str) and value.strip():
                                return value
            
            # Check for nested response structures
            if "llm_response" in result:
                return self._extract_response_text(result["llm_response"], request)
            
            # If result has a string representation, try that
            if "status" in result and "message" in result:
                msg = result["message"]
                if isinstance(msg, str) and msg.strip():
                    return msg
        
        # Try to get string representation, but filter out empty or generic messages
        try:
            result_str = str(result)
            # Don't return generic object representations
            if result_str and not result_str.startswith("<") and len(result_str) > 10:
                return result_str
        except Exception:
            pass
        
        return ""

    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Delegate code execution requests to the CodeExecutionAgent
        if request.get("action") == "execute_code":
            return await AgentCommunication.delegate_to_agent(self, self.code_executor, request)

        # Handle interactive web preview capability questions in fallback mode
        message_text = request.get("message") or request.get("text") or ""
        if isinstance(message_text, str):
            lowered = message_text.lower()
            if any(keyword in lowered for keyword in [
                "view html",
                "preview html",
                "render html",
                "view css",
                "render css",
                "preview css",
                "view javascript",
                "render javascript",
                "preview javascript",
                "web preview",
                "view web",
                "snake game",
                "html preview",
                "run html",
                "execute html",
            ]):
                instructions = (
                    "Yes — the ADK IDE can render HTML, CSS, and JavaScript directly inside the built-in Web Preview pane. "
                    "Open the Web Preview widget (View → ADK IDE → Web Preview or press Ctrl+Shift+W), select or paste your session ID, "
                    "and use the pane to save or load HTML/CSS/JS artifacts. The preview runs inside a sandboxed iframe so you can interact "
                    "with experiences like a snake game without leaving the IDE."
                )
                return {
                    "status": "success",
                    "agent": self.name,
                    "response": instructions,
                    "web_preview_message": instructions,
                }

        # If an ADK LlmAgent is available, use Runner to execute it properly
        if self._llm_agent is not None:  # pragma: no cover
            try:
                # Use ADK Runner to run the agent - this is the proper way
                # Runner handles InvocationContext creation and Event processing
                # Runner is available directly from google.adk or from google.adk.runners
                try:
                    from google.adk import Runner  # type: ignore
                except ImportError:
                    from google.adk.runners import Runner  # type: ignore
                
                # Get session service for Runner (created in __init__ or use provided one)
                # Runner requires a session_service parameter
                session_service = self._adk_session_service
                if session_service is None:
                    # Fallback: create on-demand if not already created
                    try:
                        from google.adk.sessions import InMemorySessionService  # type: ignore
                        session_service = InMemorySessionService()
                        self._adk_session_service = session_service
                        logger.debug("Created InMemorySessionService for Runner (on-demand)")
                    except Exception as e:
                        logger.error(f"Failed to create session service: {e}")
                        raise ValueError("Session service is required for ADK Runner but could not be created")
                
                message = request.get("message", request.get("text", ""))
                if not message:
                    message = str(request)
                
                # Get user_id and session_id from request
                user_id = request.get("user_id", "theia-user")
                session_id = request.get("session_id")
                
                # CRITICAL: Runner.run() requires the session to exist in the session service
                # We must create the session BEFORE calling Runner.run()
                # If session_id is provided, check if it exists; if not, create it
                # If no session_id, create a new session
                session_created = False
                if session_id:
                    # Check if session exists
                    # get_session signature: get_session(*, app_name: str, user_id: str, session_id: str) -> Session
                    try:
                        get_method = getattr(session_service, "get_session", None)
                        if get_method:
                            existing_session = get_method(
                                app_name="agents",  # Must match Runner's app_name
                                user_id=user_id,
                                session_id=session_id
                            )
                            if hasattr(existing_session, "__await__"):
                                existing_session = await existing_session  # type: ignore
                            if existing_session:
                                logger.debug(f"Session {session_id} already exists")
                                session_created = True
                    except Exception as e:
                        logger.debug(f"Session {session_id} not found, will create: {e}")
                        session_created = False
                
                # Create session if it doesn't exist
                if not session_created:
                    try:
                        # Use create_session method
                        # Signature: create_session(*, app_name: str, user_id: str, state: Optional[dict] = None, session_id: Optional[str] = None) -> Session
                        create_method = getattr(session_service, "create_session", None)
                        if create_method:
                            # Create session with app_name, user_id, and optional session_id
                            # app_name must match what we use in Runner ("agents")
                            create_kwargs = {
                                "app_name": "agents",  # Must match Runner's app_name
                                "user_id": user_id,
                                "state": {}  # Initial empty state
                            }
                            if session_id:
                                create_kwargs["session_id"] = session_id
                            
                            session = create_method(**create_kwargs)
                            if hasattr(session, "__await__"):
                                session = await session  # type: ignore
                            
                            # Extract session_id from created session
                            if isinstance(session, dict):
                                session_id = session.get("session_id") or session.get("id") or session_id
                            elif hasattr(session, "session_id"):
                                session_id = session.session_id
                            elif hasattr(session, "id"):
                                session_id = session.id
                            
                            logger.debug(f"Created session: {session_id} with app_name=agents, user_id={user_id}")
                            session_created = True
                    except Exception as e:
                        logger.error(f"Could not create session via create_session: {e}", exc_info=True)
                        # Fallback: generate session_id and try to create with sync method
                        if not session_id:
                            session_id = f"{user_id}-{int(time.time() * 1000)}"
                        try:
                            # Try sync method as fallback
                            create_sync_method = getattr(session_service, "create_session_sync", None)
                            if create_sync_method:
                                session = create_sync_method(
                                    app_name="agents",
                                    user_id=user_id,
                                    session_id=session_id,
                                    state={}
                                )
                                logger.debug(f"Created session via sync method: {session_id}")
                                session_created = True
                        except Exception as e2:
                            logger.error(f"Could not create session via sync method either: {e2}", exc_info=True)
                
                if not session_id:
                    raise ValueError("Failed to create or get session_id for Runner")
                
                logger.debug(f"Running LlmAgent with Runner, user_id={user_id}, session_id={session_id}, message: {message[:100]}...")
                
                # Create Runner with the agent and session service
                # Runner requires either 'app' OR both 'app_name' and 'agent'
                # Since our agent is from google.adk.agents, we need app_name="agents"
                # to match the agent's module location (otherwise we get a mismatch warning)
                runner = Runner(
                    app_name="agents",  # Must match where the agent was loaded from (google.adk.agents)
                    agent=self._llm_agent,
                    session_service=session_service
                )  # type: ignore
                
                # Runner.run() requires: user_id, session_id, new_message (Content type)
                # Content type from google.genai.types
                # Create Content object from message string
                try:
                    from google.genai.types import Content, Part  # type: ignore
                    # Create Content with Part containing the text
                    new_message = Content(parts=[Part(text=message)])  # type: ignore
                    logger.debug("Created Content object from google.genai.types")
                except (ImportError, AttributeError, TypeError) as e:
                    # Fallback: try dict format
                    logger.debug(f"Could not create Content object: {e}. Trying dict format...")
                    try:
                        new_message = {"parts": [{"text": message}]}
                    except Exception:
                        # Last resort: use string (ADK might handle conversion)
                        new_message = message
                        logger.warning("Using string for new_message - ADK may need to convert it")
                
                logger.debug(f"Calling Runner.run with user_id={user_id}, session_id={session_id}, new_message type={type(new_message).__name__}")
                
                # Runner.run() returns an async generator of Events
                # It requires keyword-only arguments: user_id, session_id, new_message
                # All parameters MUST be keyword-only (no positional arguments)
                runner_result = runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=new_message  # type: ignore
                )
                
                # Check what type of result we got
                import inspect
                events = []
                final_session = None
                result = None
                delegated_agent: Optional[str] = None
                delegation_trace: list[Dict[str, Any]] = []
                delegation_start_time: Optional[float] = None
                delegation_span: Optional[Any] = None
                
                if inspect.isasyncgen(runner_result):
                    logger.info("Runner.run() returned async generator, consuming Events...")
                    # Consume the async generator - process Events
                    try:
                        async for event in runner_result:  # type: ignore
                            events.append(event)
                            event_type = type(event).__name__
                            logger.info(f"Received Event: {event_type}")
                            
                            # Log event attributes for debugging
                            if hasattr(event, "__dict__"):
                                event_attrs = list(event.__dict__.keys())
                                logger.debug(f"Event attributes: {event_attrs}")
                            
                            # Try to extract session from event
                            if hasattr(event, "session"):
                                final_session = event.session
                                logger.debug("Found session in event.session")
                            elif hasattr(event, "context"):
                                if hasattr(event.context, "session"):
                                    final_session = event.context.session
                                    logger.debug("Found session in event.context.session")
                            
                            # Try to extract response from event
                            # Check multiple possible attributes
                            if hasattr(event, "response") and event.response:
                                result = event.response
                                logger.info(f"Found response in event.response: {type(result)}")
                            elif hasattr(event, "text") and event.text:
                                result = event.text
                                logger.info(f"Found response in event.text: {type(result)}")
                            elif hasattr(event, "content") and event.content:
                                result = event.content
                                logger.info(f"Found response in event.content: {type(result)}")
                            elif hasattr(event, "data") and event.data:
                                result = event.data
                                logger.info(f"Found response in event.data: {type(result)}")
                            elif hasattr(event, "message") and event.message:
                                result = event.message
                                logger.info(f"Found response in event.message: {type(result)}")
                            
                            # Also check for candidates (LLM responses often in candidates)
                            if hasattr(event, "candidates") and event.candidates:
                                logger.debug(f"Event has candidates: {len(event.candidates) if hasattr(event.candidates, '__len__') else 'unknown'}")
                                try:
                                    candidates = event.candidates
                                    if candidates and len(candidates) > 0:
                                        first_candidate = candidates[0]
                                        if hasattr(first_candidate, "content"):
                                            result = first_candidate.content
                                            logger.info(f"Found response in event.candidates[0].content: {type(result)}")
                                        elif hasattr(first_candidate, "text"):
                                            result = first_candidate.text
                                            logger.info(f"Found response in event.candidates[0].text: {type(result)}")
                                except Exception as e:
                                    logger.debug(f"Could not extract from candidates: {e}")
                            
                            # Check for EventActions.transfer_to_agent in events
                            # ADK Runner automatically handles transfer_to_agent when sub_agents are configured
                            # But we should log when transfers occur for debugging
                            if hasattr(event, "event_actions") or hasattr(event, "actions"):
                                event_actions = getattr(event, "event_actions", None) or getattr(event, "actions", None)
                                if event_actions:
                                    if hasattr(event_actions, "transfer_to_agent"):
                                        transfer_target = event_actions.transfer_to_agent
                                        delegated_agent = transfer_target or delegated_agent
                                        delegation_trace.append({
                                            "type": "transfer_to_agent",
                                            "target": transfer_target,
                                            "event": event_type
                                        })
                                        if delegation_start_time is None:
                                            delegation_start_time = time.perf_counter()
                                        if DELEGATION_COUNT is not None:
                                            try:  # pragma: no cover
                                                DELEGATION_COUNT.labels(target=transfer_target or "unknown").inc()
                                            except Exception:
                                                logger.debug("Could not record delegation metric", exc_info=True)
                                        if _delegation_tracer and delegation_span is None:
                                            try:  # pragma: no cover
                                                delegation_span = _delegation_tracer.start_span(
                                                    "adk.delegation",
                                                    attributes={
                                                        "adk.delegated.to": transfer_target or "unknown",
                                                        "adk.session.id": session_id or "unknown",
                                                    },
                                                )
                                            except Exception:
                                                logger.debug("Failed to start delegation span", exc_info=True)
                                                delegation_span = None
                                        elif delegation_span is not None:
                                            try:  # pragma: no cover
                                                delegation_span.set_attribute("adk.delegated.to", transfer_target or "unknown")
                                            except Exception:
                                                logger.debug("Failed to set delegation span attribute", exc_info=True)
                                        logger.info(f"EventActions.transfer_to_agent detected: {transfer_target}")
                                    elif isinstance(event_actions, dict) and "transfer_to_agent" in event_actions:
                                        transfer_target = event_actions["transfer_to_agent"]
                                        delegated_agent = transfer_target or delegated_agent
                                        delegation_trace.append({
                                            "type": "transfer_to_agent",
                                            "target": transfer_target,
                                            "event": event_type
                                        })
                                        if delegation_start_time is None:
                                            delegation_start_time = time.perf_counter()
                                        if DELEGATION_COUNT is not None:
                                            try:  # pragma: no cover
                                                DELEGATION_COUNT.labels(target=transfer_target or "unknown").inc()
                                            except Exception:
                                                logger.debug("Could not record delegation metric", exc_info=True)
                                        if _delegation_tracer and delegation_span is None:
                                            try:  # pragma: no cover
                                                delegation_span = _delegation_tracer.start_span(
                                                    "adk.delegation",
                                                    attributes={
                                                        "adk.delegated.to": transfer_target or "unknown",
                                                        "adk.session.id": session_id or "unknown",
                                                    },
                                                )
                                            except Exception:
                                                logger.debug("Failed to start delegation span", exc_info=True)
                                                delegation_span = None
                                        elif delegation_span is not None:
                                            try:  # pragma: no cover
                                                delegation_span.set_attribute("adk.delegated.to", transfer_target or "unknown")
                                            except Exception:
                                                logger.debug("Failed to set delegation span attribute", exc_info=True)
                                        logger.info(f"EventActions.transfer_to_agent detected (dict): {transfer_target}")
                                    if hasattr(event_actions, "escalate") and event_actions.escalate:
                                        delegation_trace.append({
                                            "type": "escalate",
                                            "event": event_type
                                        })
                                        target_label = delegated_agent or "unknown"
                                        if DELEGATION_ESCALATIONS is not None:
                                            try:  # pragma: no cover
                                                DELEGATION_ESCALATIONS.labels(agent=target_label).inc()
                                            except Exception:
                                                logger.debug("Could not record escalation metric", exc_info=True)
                                        if delegation_span is not None:
                                            try:  # pragma: no cover
                                                delegation_span.set_attribute("adk.delegation.escalated", True)
                                            except Exception:
                                                logger.debug("Failed to annotate delegation span escalation", exc_info=True)
                                        logger.info("EventActions.escalate detected: terminating delegated loop")
                                    elif isinstance(event_actions, dict) and event_actions.get("escalate"):
                                        delegation_trace.append({
                                            "type": "escalate",
                                            "event": event_type
                                        })
                                        target_label = delegated_agent or "unknown"
                                        if DELEGATION_ESCALATIONS is not None:
                                            try:  # pragma: no cover
                                                DELEGATION_ESCALATIONS.labels(agent=target_label).inc()
                                            except Exception:
                                                logger.debug("Could not record escalation metric", exc_info=True)
                                        if delegation_span is not None:
                                            try:  # pragma: no cover
                                                delegation_span.set_attribute("adk.delegation.escalated", True)
                                            except Exception:
                                                logger.debug("Failed to annotate delegation span escalation", exc_info=True)
                                        logger.info("EventActions.escalate detected (dict): terminating delegated loop")
                            
                            # Also check event data/attributes for event_actions
                            if hasattr(event, "__dict__"):
                                event_dict = event.__dict__
                                if "event_actions" in event_dict:
                                    event_actions = event_dict["event_actions"]
                                    if hasattr(event_actions, "transfer_to_agent"):
                                        transfer_target = event_actions.transfer_to_agent
                                        delegated_agent = transfer_target or delegated_agent
                                        delegation_trace.append({
                                            "type": "transfer_to_agent",
                                            "target": transfer_target,
                                            "event": event_type
                                        })
                                        logger.info(f"EventActions.transfer_to_agent found in event.__dict__: {transfer_target}")
                                    elif isinstance(event_actions, dict) and "transfer_to_agent" in event_actions:
                                        transfer_target = event_actions["transfer_to_agent"]
                                        delegated_agent = transfer_target or delegated_agent
                                        delegation_trace.append({
                                            "type": "transfer_to_agent",
                                            "target": transfer_target,
                                            "event": event_type
                                        })
                                        logger.info(f"EventActions.transfer_to_agent found in event.__dict__ (dict): {transfer_target}")
                                    if isinstance(event_actions, dict) and event_actions.get("escalate"):
                                        delegation_trace.append({
                                            "type": "escalate",
                                            "event": event_type
                                        })
                                        logger.info("EventActions.escalate found in event.__dict__ (dict)")
                    except asyncio.CancelledError:
                        logger.warning("Async generator consumption was cancelled (likely during shutdown)")
                        # Re-raise to allow proper cleanup
                        raise
                    except Exception as async_exc:
                        logger.error(f"Error consuming async generator: {async_exc}", exc_info=True)
                        raise
                elif inspect.isgenerator(runner_result):
                    logger.debug("Runner.run() returned regular generator, consuming Events...")
                    # Consume the regular generator - process Events
                    # Note: This is a regular generator, not async, so use regular for loop
                    # However, the generator may yield events that contain async operations
                    # We need to consume it in a way that doesn't block the event loop
                    try:
                        for event in runner_result:  # type: ignore
                            # Check for cancellation before processing each event
                            # This allows graceful shutdown if the request is cancelled
                            try:
                                # Yield control periodically to check for cancellation
                                if len(events) % 10 == 0:  # Every 10 events
                                    await asyncio.sleep(0)  # Yield to event loop and check for cancellation
                            except asyncio.CancelledError:
                                logger.warning("Generator consumption was cancelled (likely during shutdown)")
                                # Close the generator if possible
                                try:
                                    runner_result.close()  # type: ignore
                                except Exception:
                                    pass
                                raise
                            
                            events.append(event)
                            event_type = type(event).__name__
                            logger.debug(f"Received Event: {event_type}")
                            
                            # Try to extract session from event
                            if hasattr(event, "session"):
                                final_session = event.session
                            elif hasattr(event, "context") and hasattr(event.context, "session"):
                                final_session = event.context.session
                            
                            # Try to extract response from event
                            if hasattr(event, "response"):
                                result = event.response
                            elif hasattr(event, "text"):
                                result = event.text
                            elif hasattr(event, "content"):
                                result = event.content
                            elif hasattr(event, "data"):
                                result = event.data
                            elif hasattr(event, "message"):
                                result = event.message

                            # Detect delegation in regular generator events
                            event_actions = getattr(event, "event_actions", None) or getattr(event, "actions", None)
                            if event_actions:
                                if hasattr(event_actions, "transfer_to_agent"):
                                    transfer_target = event_actions.transfer_to_agent
                                    delegated_agent = transfer_target or delegated_agent
                                    delegation_trace.append({
                                        "type": "transfer_to_agent",
                                        "target": transfer_target,
                                        "event": event_type
                                    })
                                    if delegation_start_time is None:
                                        delegation_start_time = time.perf_counter()
                                    if DELEGATION_COUNT is not None:
                                        try:  # pragma: no cover
                                            DELEGATION_COUNT.labels(target=transfer_target or "unknown").inc()
                                        except Exception:
                                            logger.debug("Could not record delegation metric", exc_info=True)
                                    if _delegation_tracer and delegation_span is None:
                                        try:  # pragma: no cover
                                            delegation_span = _delegation_tracer.start_span(
                                                "adk.delegation",
                                                attributes={
                                                    "adk.delegated.to": transfer_target or "unknown",
                                                    "adk.session.id": session_id or "unknown",
                                                },
                                            )
                                        except Exception:
                                            logger.debug("Failed to start delegation span", exc_info=True)
                                            delegation_span = None
                                    elif delegation_span is not None:
                                        try:  # pragma: no cover
                                            delegation_span.set_attribute("adk.delegated.to", transfer_target or "unknown")
                                        except Exception:
                                            logger.debug("Failed to set delegation span attribute", exc_info=True)
                                    logger.info(f"(sync) EventActions.transfer_to_agent detected: {transfer_target}")
                                elif isinstance(event_actions, dict) and "transfer_to_agent" in event_actions:
                                    transfer_target = event_actions["transfer_to_agent"]
                                    delegated_agent = transfer_target or delegated_agent
                                    delegation_trace.append({
                                        "type": "transfer_to_agent",
                                        "target": transfer_target,
                                        "event": event_type
                                    })
                                    if delegation_start_time is None:
                                        delegation_start_time = time.perf_counter()
                                    if DELEGATION_COUNT is not None:
                                        try:  # pragma: no cover
                                            DELEGATION_COUNT.labels(target=transfer_target or "unknown").inc()
                                        except Exception:
                                            logger.debug("Could not record delegation metric", exc_info=True)
                                    if _delegation_tracer and delegation_span is None:
                                        try:  # pragma: no cover
                                            delegation_span = _delegation_tracer.start_span(
                                                "adk.delegation",
                                                attributes={
                                                    "adk.delegated.to": transfer_target or "unknown",
                                                    "adk.session.id": session_id or "unknown",
                                                },
                                            )
                                        except Exception:
                                            logger.debug("Failed to start delegation span", exc_info=True)
                                            delegation_span = None
                                    elif delegation_span is not None:
                                        try:  # pragma: no cover
                                            delegation_span.set_attribute("adk.delegated.to", transfer_target or "unknown")
                                        except Exception:
                                            logger.debug("Failed to set delegation span attribute", exc_info=True)
                                    logger.info(f"(sync) EventActions.transfer_to_agent detected (dict): {transfer_target}")
                                if hasattr(event_actions, "escalate") and event_actions.escalate:
                                    delegation_trace.append({
                                        "type": "escalate",
                                        "event": event_type
                                    })
                                    target_label = delegated_agent or "unknown"
                                    if DELEGATION_ESCALATIONS is not None:
                                        try:  # pragma: no cover
                                            DELEGATION_ESCALATIONS.labels(agent=target_label).inc()
                                        except Exception:
                                            logger.debug("Could not record escalation metric", exc_info=True)
                                    if delegation_span is not None:
                                        try:  # pragma: no cover
                                            delegation_span.set_attribute("adk.delegation.escalated", True)
                                        except Exception:
                                            logger.debug("Failed to annotate delegation span escalation", exc_info=True)
                                    logger.info("(sync) EventActions.escalate detected")
                                elif isinstance(event_actions, dict) and event_actions.get("escalate"):
                                    delegation_trace.append({
                                        "type": "escalate",
                                        "event": event_type
                                    })
                                    target_label = delegated_agent or "unknown"
                                    if DELEGATION_ESCALATIONS is not None:
                                        try:  # pragma: no cover
                                            DELEGATION_ESCALATIONS.labels(agent=target_label).inc()
                                        except Exception:
                                            logger.debug("Could not record escalation metric", exc_info=True)
                                    if delegation_span is not None:
                                        try:  # pragma: no cover
                                            delegation_span.set_attribute("adk.delegation.escalated", True)
                                        except Exception:
                                            logger.debug("Failed to annotate delegation span escalation", exc_info=True)
                                    logger.info("(sync) EventActions.escalate detected (dict)")
                    except StopIteration:
                        logger.debug("Generator exhausted")
                    except asyncio.CancelledError:
                        logger.warning("Generator consumption was cancelled")
                        raise
                    except Exception as gen_exc:
                        logger.error(f"Error consuming generator: {gen_exc}", exc_info=True)
                        raise
                elif hasattr(runner_result, "__await__"):
                    # It's a coroutine, await it
                    logger.debug("Runner.run() returned coroutine, awaiting...")
                    result = await runner_result  # type: ignore
                    # Check if result has a response attribute
                    if hasattr(result, "response"):
                        result = result.response
                else:
                    # Direct result
                    logger.debug(f"Runner.run() returned direct result: {type(runner_result)}")
                    result = runner_result
                    if hasattr(result, "response"):
                        result = result.response
                
                # After processing events (if any), ALWAYS check session state for response
                # ADK Runner saves responses to session.state["hia_response"] after processing
                logger.info(f"Processed {len(events)} events from Runner. Checking session state for response...")
                
                # Always try to get session from session service to check state
                # The session state is the authoritative source for the response
                try:
                    get_method = getattr(session_service, "get_session", None)
                    if get_method:
                        logger.info(f"Retrieving session from session service: app_name=agents, user_id={user_id}, session_id={session_id}")
                        retrieved_session = get_method(
                            app_name="agents",
                            user_id=user_id,
                            session_id=session_id
                        )
                        if hasattr(retrieved_session, "__await__"):
                            retrieved_session = await retrieved_session  # type: ignore
                        
                        if retrieved_session:
                            # Use retrieved session (most up-to-date)
                            final_session = retrieved_session
                            logger.info("Successfully retrieved session from session service")
                        elif final_session is None:
                            logger.warning("Could not retrieve session from session service and no session from events")
                    else:
                        logger.warning("Session service does not have get_session method")
                except Exception as e:
                    logger.warning(f"Error retrieving session from session service: {e}", exc_info=True)
                
                # Now check session state for response (this is the most reliable source)
                if final_session is not None:
                    try:
                        session_state = None
                        if hasattr(final_session, "state"):
                            session_state = final_session.state
                            logger.debug(f"Accessing session.state as attribute: {type(session_state)}")
                        elif isinstance(final_session, dict) and "state" in final_session:
                            session_state = final_session["state"]
                            logger.debug(f"Accessing session.state as dict key: {type(session_state)}")
                        elif hasattr(final_session, "get"):
                            # Try as a dict-like object
                            session_state = final_session.get("state")
                            logger.debug(f"Accessing session.state via get() method: {type(session_state)}")
                        
                        if session_state is not None:
                            logger.info(f"Session state retrieved: type={type(session_state)}")
                            if isinstance(session_state, dict):
                                state_keys = list(session_state.keys())
                                logger.info(f"Session state keys: {state_keys}")
                                
                                # ADK saves response to output_key ("hia_response")
                                hia_response = session_state.get("hia_response")
                                if hia_response:
                                    logger.info(f"Found 'hia_response' in session.state: type={type(hia_response)}")
                                    if result is None or not self._extract_response_text(result, request):
                                        result = hia_response
                                        logger.info(f"Using session.state['hia_response'] as result (type: {type(result)})")
                                    else:
                                        logger.debug(f"Response already found in events, but also found in session.state['hia_response']")
                                else:
                                    logger.warning("No 'hia_response' key in session.state")
                                    if delegated_agent:
                                        delegated_keys = {
                                            "developing_agent": ["developing_agent_response", "da_response"],
                                            delegated_agent: [
                                                f"{delegated_agent}_response",
                                                f"{delegated_agent.lower()}_response",
                                                f"{delegated_agent.replace(' ', '_').lower()}_response",
                                            ],
                                        }
                                        for key_list in delegated_keys.values():
                                            for key in key_list:
                                                if key in session_state:
                                                    value = session_state[key]
                                                    logger.info(f"Found delegated response '{key}' in session.state: type={type(value)}")
                                                    result = value
                                                    break
                                            if result is not None:
                                                break
                                    if result is None:
                                        # Try other common keys
                                        for key in ["response", "text", "message", "content", "output", "result", "llm_response"]:
                                            if key in session_state:
                                                value = session_state[key]
                                                logger.info(f"Found '{key}' in session.state: type={type(value)}")
                                                if result is None or not self._extract_response_text(result, request):
                                                    result = value
                                                    logger.info(f"Using session.state['{key}'] as result")
                                                    break
                            else:
                                logger.warning(f"Session state is not a dict: {type(session_state)}")
                                # Try to access it as an object with attributes
                                if hasattr(session_state, "hia_response"):
                                    hia_response = getattr(session_state, "hia_response")
                                    if hia_response:
                                        logger.info(f"Found hia_response as attribute: type={type(hia_response)}")
                                        if result is None:
                                            result = hia_response
                        else:
                            logger.warning("Session state is None - cannot retrieve response")
                    except Exception as e:
                        logger.error(f"Error accessing session state: {e}", exc_info=True)
                else:
                    logger.warning("No session available to check state")
                
                # If we still don't have a result, try to extract from events
                if result is None and events:
                    logger.info("No result from session state, trying to extract from events...")
                    # Check all events for response data, not just the last one
                    for event in reversed(events):  # Check from last to first
                        # Try to extract from event attributes
                        if hasattr(event, "__dict__"):
                            event_dict = event.__dict__
                            for key in ["response", "text", "content", "message", "output", "result", "data"]:
                                if key in event_dict:
                                    value = event_dict[key]
                                    if value and (isinstance(value, str) or (isinstance(value, dict) and value)):
                                        result = value
                                        logger.info(f"Found response in event.{key}: {type(value)}")
                                        break
                            if result:
                                break
                        
                        # Also try direct attribute access
                        for attr_name in ["response", "text", "content", "message", "output", "result"]:
                            if hasattr(event, attr_name):
                                value = getattr(event, attr_name)
                                if value and (isinstance(value, str) or (isinstance(value, dict) and value)):
                                    result = value
                                    logger.info(f"Found response in event.{attr_name}: {type(value)}")
                                    break
                        if result:
                            break
                    
                    # If still no result, use last event
                    if result is None and events:
                        last_event = events[-1]
                        result = last_event
                        logger.info(f"Using last event as result: {type(last_event)}")
                elif result is None:
                    # No events processed, but we might still have a result
                    # Try to get session and check state
                    try:
                        # get_session signature: get_session(*, app_name: str, user_id: str, session_id: str) -> Session
                        get_method = getattr(session_service, "get_session", None)
                        if get_method:
                            retrieved_session = get_method(
                                app_name="agents",  # Must match Runner's app_name
                                user_id=user_id,
                                session_id=session_id
                            )
                            if hasattr(retrieved_session, "__await__"):
                                retrieved_session = await retrieved_session  # type: ignore
                            
                            if hasattr(retrieved_session, "state"):
                                session_state = retrieved_session.state
                                if isinstance(session_state, dict):
                                    hia_response = session_state.get("hia_response")
                                    if hia_response:
                                        result = hia_response
                                        logger.debug("Found response in session.state['hia_response'] (no events)")
                    except Exception as e:
                        logger.debug(f"Could not retrieve session after processing: {e}")
                
                # Note: ADK Runner automatically handles EventActions.transfer_to_agent when sub_agents are configured
                # The Runner will automatically transfer control to the sub-agent, and the sub-agent's response
                # will be in the events or session.state. We don't need to manually handle transfer_to_agent here.
                # However, we should check if the response indicates a transfer occurred (for logging/debugging)
                if isinstance(result, dict):
                    # Check if result indicates a transfer occurred (for logging)
                    if "event_actions" in result and result.get("event_actions", {}).get("transfer_to_agent"):
                        transfer_target = result["event_actions"]["transfer_to_agent"]
                        delegated_agent = transfer_target or delegated_agent
                        logger.info(f"Transfer to agent '{transfer_target}' was handled by ADK Runner. Response should be from the delegated agent.")
                    elif "delegated_to" in result or "transfer_to_agent" in result:
                        delegated_agent = result.get("delegated_to") or result.get("transfer_to_agent") or delegated_agent
                        logger.debug(f"Response indicates delegation occurred: {delegated_agent}")
                
                # Extract response text from result
                # ADK LlmAgent with output_key="hia_response" saves to session.state["hia_response"]
                response_text = self._extract_response_text(result, request)
                
                # Log for debugging
                logger.info(f"HIA agent result type: {type(result)}")
                if result is not None:
                    logger.info(f"HIA agent result repr (first 500 chars): {str(result)[:500]}")
                if response_text:
                    logger.info(f"HIA agent response_text extracted (first 200 chars): {response_text[:200]}")
                    logger.info(f"HIA agent response_text length: {len(response_text)}")
                else:
                    logger.warning(f"HIA agent could not extract response text from result")
                    logger.warning(f"Result type: {type(result)}")
                    logger.warning(f"Result repr (first 1000 chars): {str(result)[:1000] if result is not None else 'None'}")
                    
                    # Log result structure for debugging
                    if isinstance(result, dict):
                        logger.warning(f"Result keys: {list(result.keys())}")
                        for key in result.keys():
                            logger.warning(f"  {key}: {type(result[key])} = {str(result[key])[:200]}")
                        if "session" in result:
                            logger.warning(f"Result contains session: {type(result['session'])}")
                            if hasattr(result["session"], "state"):
                                logger.warning(f"Session state type: {type(result['session'].state)}")
                                if isinstance(result["session"].state, dict):
                                    logger.warning(f"Session state keys: {list(result['session'].state.keys())}")
                                    for key in result["session"].state.keys():
                                        logger.warning(f"  session.state['{key}']: {type(result['session'].state[key])} = {str(result['session'].state[key])[:200]}")
                    
                    # Try one more time to get session and extract response
                    if final_session is None:
                        try:
                            get_method = getattr(session_service, "get_session", None)
                            if get_method:
                                retrieved_session = get_method(
                                    app_name="agents",
                                    user_id=user_id,
                                    session_id=session_id
                                )
                                if hasattr(retrieved_session, "__await__"):
                                    retrieved_session = await retrieved_session  # type: ignore
                                if retrieved_session:
                                    final_session = retrieved_session
                                    logger.info("Retrieved session one more time for final extraction attempt")
                                    if hasattr(final_session, "state"):
                                        session_state = final_session.state
                                        if isinstance(session_state, dict):
                                            logger.info(f"Final session state keys: {list(session_state.keys())}")
                                            for key in ["hia_response", "response", "text", "message", "content"]:
                                                if key in session_state:
                                                    value = session_state[key]
                                                    logger.info(f"Found {key} in final session state: {type(value)}")
                                                    extracted = self._extract_response_text(value, request)
                                                    if extracted:
                                                        response_text = extracted
                                                        logger.info(f"Successfully extracted response from session.state['{key}']")
                                                        break
                        except Exception as e:
                            logger.warning(f"Final session retrieval failed: {e}", exc_info=True)
                
                def finalize_metrics_and_return(payload: Dict[str, Any]) -> Dict[str, Any]:
                    if delegated_agent:
                        payload.setdefault("delegated_to", delegated_agent)
                    if delegation_trace:
                        payload.setdefault("delegation_trace", delegation_trace)
                    if delegation_start_time is not None and delegated_agent and DELEGATION_DURATION is not None:
                        try:  # pragma: no cover
                            duration_value = max(time.perf_counter() - delegation_start_time, 0.0)
                            DELEGATION_DURATION.labels(target=delegated_agent).observe(duration_value)
                            if delegation_span is not None:
                                delegation_span.set_attribute("adk.delegation.duration", duration_value)
                        except Exception:
                            logger.debug("Could not record delegation duration metric", exc_info=True)
                    if delegation_span is not None:
                        try:  # pragma: no cover
                            delegation_span.end()
                        except Exception:
                            logger.debug("Failed to end delegation span", exc_info=True)
                    return payload

                # Return structured response with extracted text
                # Don't include raw result as it may contain non-serializable Content objects
                # Ensure response_text is a string (not a Content object)
                if response_text:
                    # Convert to string if not already
                    if not isinstance(response_text, str):
                        response_text = str(response_text)
                    if response_text.strip():
                        response_payload: Dict[str, Any] = {
                            "status": "success",
                            "agent": self.name,
                            "response": response_text,
                        }
                        return finalize_metrics_and_return(response_payload)
                else:
                    # If we can't extract text, try to provide a helpful message
                    # Check if result indicates success but no text was extracted
                    if isinstance(result, dict):
                        if result.get("status") == "success":
                            response_payload = {
                                "status": "success",
                                "agent": self.name,
                                "response": "Request processed successfully. The agent has completed your request.",
                            }
                            return finalize_metrics_and_return(response_payload)
                        elif "error" in result:
                            error_payload = {
                                "status": "error",
                                "agent": self.name,
                                "error": result.get("error", "Unknown error"),
                                "response": f"Error: {result.get('error', 'Unknown error')}",
                            }
                            return finalize_metrics_and_return(error_payload)
                    
                    # Last resort: return a message indicating processing
                    fallback_response = {
                        "status": "success",
                        "agent": self.name,
                        "response": "I received your message. Please check if ADK is properly configured and the session state is accessible.",
                    }
                    return finalize_metrics_and_return(fallback_response)
            except Exception as exc:
                logger.error(f"HIA agent error: {exc}", exc_info=True)
                error_payload = {
                    "status": "error",
                    "agent": self.name,
                    "error": str(exc),
                    "response": f"Error processing request: {str(exc)}",
                }
                return finalize_metrics_and_return(error_payload)

        # Fallback: delegate to developing agent if available
        if self.developing_agent is not None and request.get("task_type") in ["code_generation", "development"]:
            return await AgentCommunication.delegate_to_agent(self, self.developing_agent, request)

        # Fallback scaffold behavior
        return {
            "status": "received", 
            "agent": self.name, 
            "request": request,
            "response": "I received your message. ADK features are not enabled. Please set ADK_ENABLED=true to use full functionality."
        }

