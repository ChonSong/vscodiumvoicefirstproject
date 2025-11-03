# Agent Development Kit (ADK) - Comprehensive Documentation

## Overview

The Agent Development Kit (ADK) is an open-source, **code-first Python toolkit** designed for building, evaluating, and deploying sophisticated AI agents with enhanced flexibility and control. It is built on the philosophy of making agent development feel more like traditional software development, providing modularity and scalability for architectures ranging from simple tasks to complex workflows.

ADK offers a modular and flexible framework that is **model-agnostic** and **deployment-agnostic**, although it is highly optimised for integration with the Google ecosystem and Gemini models.

## I. Agent Architecture and Core Categories

The foundation for all components within ADK is the concept of the **Agent**, defined as a self-contained execution unit derived from the `BaseAgent` class, designed to act autonomously to achieve specific goals. ADK categorizes agents into three primary types, which can be composed into powerful Multi-Agent Systems (MAS):

### 1. LLM Agents (`LlmAgent` or `Agent`)
These agents rely on **Large Language Models (LLMs)** as their core engine for reasoning, planning, generation, and dynamically deciding which tools to use. They are ideal for flexible, language-centric tasks and can be configured with detailed instructions, tools, and constraints.

Key configuration parameters for an `LlmAgent` include:
*   **`model`**: Specifies the underlying LLM (e.g., `"gemini-2.5-flash"`). ADK supports using different models by passing the model name string or by wrapping models from external providers (like GPT or Claude) using the **`LiteLlm`** object, enabling multi-LLM flexibility.
*   **`instruction`**: Provides guidance on the agent's core task, persona, constraints, and how and when to use its `tools`. Effective instructions should be clear, specific, and guide tool usage precisely.
*   **`tools`**: A list of capabilities the agent can invoke, ranging from pre-built functions to custom APIs.
*   **`output_key`**: A powerful feature that automatically saves the agent's final textual response into the session state under the specified key, aiding in conversational context and state management.
*   **`generate_content_config`**: Allows fine-tuning of the underlying LLM's generation parameters, such as `temperature` (randomness) or `max_output_tokens`.

### 2. Workflow Agents
These are specialized agents that control the execution flow of their sub-agents in **predefined, deterministic patterns**, without relying on an LLM for flow control. They are perfect for structured processes requiring predictable execution. The main types are:
*   **`SequentialAgent`**: Executes sub-agents one after another, in a strict, dependable sequence. This is used for pipelines where output from one agent must feed directly as input (via session state) to the next.
*   **`ParallelAgent`**: Executes multiple sub-agents concurrently, significantly reducing latency for independent tasks like parallel web research.
*   **`LoopAgent`**: Repeatedly runs a sequence of sub-agents until a maximum number of iterations (`max_iterations`) is reached, or until a termination condition is met, typically signalled by a sub-agent setting the `escalate=True` flag in its `Event Actions`. This is essential for iterative refinement patterns.

### 3. Custom Agents
Custom Agents offer the ultimate flexibility by allowing developers to define **arbitrary orchestration logic**. They are created by inheriting directly from `BaseAgent` and implementing the core execution logic within the asynchronous method, `_run_async_impl` (in Python). This approach is recommended after understanding the predefined agent types and allows for use cases like:
*   Implementing **unique workflow patterns** that don't fit sequential, parallel, or loop structures.
*   Incorporating calls to external APIs or databases directly within the orchestration flow control.
*   **Dynamic Agent Selection**, choosing which sub-agent(s) to run next based on the evaluation of the current situation or input.

## II. Multi-Agent Systems and Delegation

The true power of ADK lies in composing these different agent types into **hierarchical Multi-Agent Systems (MAS)**. Agents collaborate or coordinate to achieve a larger goal.

### Agent Hierarchy and Communication
Agents are connected through `parent_agent`/`sub_agents` relationships. Key interaction mechanisms include:

1.  **LLM-Driven Delegation (Auto Flow)**: A central agent (Coordinator) delegates requests to specialised `sub_agents` listed in its configuration based on their descriptive `description` and the Coordinator's `instruction`. This dynamic routing requires the LLM to interpret the user's intent.
2.  **Explicit Invocation (`AgentTool`)**: An agent can call another specialised agent as a tool by wrapping it using the `AgentTool` class. The called agent's result is passed back to the calling agent (the parent) for summarisation or integration into the final response, allowing the parent agent to maintain control.
3.  **Transfer (Sub-Agent)**: When Agent A lists Agent B as a `sub_agent`, control of the conversation can be **transferred completely** to Agent B using the `transfer_to_agent` signal in an `EventActions` object. Once transferred, the new agent handles all subsequent user input.

Common patterns implemented via these primitives include the Coordinator/Dispatcher pattern, the Fan-Out/Gather pattern (using `ParallelAgent`), Hierarchical Planning, and the Generator/Critic pattern (using `SequentialAgent`).

## III. Context, State, and Memory Management

ADK provides structured ways to manage conversational context, which is crucial for meaningful, multi-turn interactions.

### 1. Session and State
A **`Session`** represents a single, ongoing interaction thread between a user and the agent system. It contains the chronological sequence of messages and actions (`Events`) for that interaction.

**`State`** (`session.state`) is the working memory or scratchpad for the session, storing temporary data relevant only to that specific conversation. Agents and tools can read from and write to the state to pass data between steps in a workflow. The `SessionService` (e.g., `InMemorySessionService` for testing or `VertexAiSessionService`/`DatabaseSessionService` for persistence) manages the lifecycle of `Session` objects.

### 2. Artifacts
**Artifacts** provide a mechanism for managing named, versioned binary data associated with a session or persistently with a user. They are designed to handle non-textual or large data blobs, such as images, audio clips, PDFs, or generated reports.

The `ArtifactService` handles versioning automatically when data is saved. ADK provides the `InMemoryArtifactService` for rapid prototyping and the **`GcsArtifactService`** for production environments requiring persistent storage via Google Cloud Storage.

### 3. Long-Term Memory
Distinct from session state, the **`MemoryService`** handles long-term knowledge, allowing agents to recall information about a user across multiple sessions or access external knowledge bases.

In Python ADK, implementations include the basic `InMemoryMemoryService` for demonstration and the powerful **`VertexAiRagMemoryService`**, which utilizes Vertex AI Retrieval Augmented Generation (RAG) for scalable, persistent, and semantically relevant knowledge retrieval. Agents use a tool (like `load_memory`) that queries the `MemoryService` via `ToolContext.search_memory()`.

## IV. Tools and External Capabilities

ADK features a **Rich Tool Ecosystem** that allows agents to perform actions beyond the LLM's intrinsic knowledge.

### 1. Custom and Function Tools
Any standard Python function or method can be automatically wrapped as a **`FunctionTool`** simply by including it in the agent's `tools` list. Key principles for defining effective tools include:
*   Using clear, descriptive function names and parameter names, as the LLM relies heavily on these for understanding.
*   Providing clear Python type hints (essential for schema generation) and detailed docstrings, which serve as the primary source of information for the LLM.
*   Returning a dictionary result, preferably including a `"status"` key (`'success'`, `'error'`, `'pending'`) for clarity to the LLM.

For tasks requiring significant time without blocking execution, the **`LongRunningFunctionTool`** (a subclass of `FunctionTool`) is used. The function returns an initial status (e.g., `pending` status and a `ticket-id`), pausing the agent run until the client sends back an intermediate or final status update.

### 2. Built-in and Ecosystem Tools
ADK integrates several powerful, built-in capabilities:
*   **Google Search**: Provided via the `google_search` tool for grounding responses with real-time information.
*   **Code Execution**: Enabled via `code_executor` and tools like **`BuiltInCodeExecutor`** or **`VertexAiCodeExecutor`**, which uses the Vertex Code Interpreter Extension for safe, sandboxed execution.
*   **Third-Party Integration**: ADK allows seamless integration of tools from other popular frameworks like **LangChain** and **CrewAI** by wrapping them using classes like `LangchainTool`.
*   **OpenAPI/REST**: The `OpenAPIToolset` automatically generates functional tools (`RestApiTool`) directly from an OpenAPI specification (YAML/JSON), simplifying API integration.

## V. Extensibility and Control with Callbacks

**Callbacks** are custom code snippets that serve as powerful hooks, running at specific points in the agent's execution process to inspect, modify, log, or enforce policy.

### Types of Callbacks
`LlmAgent`s support several specific callback types:

| Callback Type | When Called | Primary Use Case |
| :--- | :--- | :--- |
| **`before_model_callback`** | Just before the request is sent to the LLM. | Implementing **input guardrails** (e.g., blocking keywords) or **caching**. If it returns an `LlmResponse`, the actual LLM call is **skipped**. |
| **`after_model_callback`** | Immediately after the LLM response is received. | Sanitizing, reformatting, censoring, or parsing structured data from the LLM output. |
| **`before_tool_callback`** | Just before a tool (or function) is executed. | **Policy enforcement** (e.g., blocking tool use based on parameters) or cache validation. If it returns a dictionary, the tool execution is **skipped**, and the dictionary is used as the result. |
| **`after_tool_callback`** | Immediately after a tool finishes execution. | Post-processing, standardization, or logging tool outputs before they are sent back to the LLM. |

These callbacks provide a robust mechanism to implement comprehensive safety and security features, often leveraging a fast, cheap LLM (like Gemini Flash Lite) within a callback function to act as a **safety guardrail** against unsafe user inputs or tool inputs.

## VI. Streaming and Real-Time Interaction

ADK offers native support for streaming, culminating in **Bidirectional Streaming (Bidi-streaming or "live" mode)**, which brings low-latency voice and video interaction capability from the Gemini Live API to agents.

### Bidi-streaming Concepts
Bidi-streaming enables **real-time, two-way communication** that supports interruption, making conversations fluid and human-like. This is distinct from token-level streaming (which lacks interruption capability) or server-side streaming (which is one-way).

The streaming architecture involves:
*   The **`Runner.run_live()`** method, which starts a streaming session.
*   The **`LiveRequestQueue`**, which buffers and sequences incoming user messages (text, audio blobs, control signals) for orderly processing by the agent.
*   Events streamed back to the client via a transport layer like **WebSockets** or **Server-Sent Events (SSE)**.

### Runtime Configuration (`RunConfig`)
Streaming behaviour and modalities are configured using the `RunConfig` class. Key parameters include:
*   **`streaming_mode`**: Sets the behavior to `NONE`, `SSE` (one-way server-to-client streaming), or `BIDI` (bidirectional streaming).
*   **`response_modalities`**: Defines desired outputs (e.g., `["TEXT", "AUDIO"]`).
*   **`speech_config`**: Configures speech synthesis details (voice, language code) for audio responses.
*   **`save_input_blobs_as_artifacts`**: If `true`, input blobs (like uploaded files/video) are saved as run artifacts for debugging.
*   **`max_llm_calls`**: Limits the total number of LLM calls per run (default 500), preventing runaway processes and excessive costs.

## VII. Developer Lifecycle and Deployment

ADK provides tooling across the entire agent development lifecycle.

### Development and Evaluation
ADK supports a fast iteration loop through several tools:
*   **Development UI**: A built-in web interface (`adk web`) helps developers test, evaluate, debug, and showcase their agents locally.
*   **Event Inspection**: The Dev UI allows developers to inspect individual function calls, responses, model responses, and trace latency logs for each event.
*   **Evaluation**: The `adk eval` command line utility supports **systematic evaluation** against predefined datasets. Evaluation datasets, known as **Evalsets**, contain multiple conversational sessions (`eval_cases`) including user queries, expected tool use, intermediate responses, and a final reference response.

### Deployment
Agents can be containerised and deployed virtually anywhere. Core deployment targets supported by the documentation include:
*   **Vertex AI Agent Engine**: The easiest way to deploy ADK agents to a managed service in Vertex AI for enterprise-grade scalability and reliability.
*   **Cloud Run / GKE**: For full control, agents can be deployed to serverless Cloud Run or Kubernetes Engine (GKE), often integrated via a FastAPI application using ADK utilities.

### Contribution and Community
ADK welcomes community contributions for bug reports, feature requests, documentation improvements, and code contributions. Contributors must sign a **Contributor License Agreement (CLA)**.

## Installation

### Stable Release (Recommended)
```bash
pip install google-adk
```

### Development Version
```bash
pip install git+https://github.com/google/adk-python.git@main
```

## Quick Start Examples

### Define a Single Agent
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash", # Or your preferred Gemini model
    instruction="You are a helpful assistant. Answer user questions using Google Search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

### Define a Multi-Agent System
```python
from google.adk.agents import LlmAgent, BaseAgent

# Define individual agents
greeter = LlmAgent(name="greeter", model="gemini-2.5-flash", ...)
task_executor = LlmAgent(name="task_executor", model="gemini-2.5-flash", ...)

# Create parent agent and assign children via sub_agents
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.5-flash",
    description="I coordinate greetings and tasks.",
    sub_agents=[ # Assign sub_agents here
        greeter,
        task_executor
    ]
)
```

## Key Features

✨ **Rich Tool Ecosystem**: Utilize pre-built tools, custom functions, OpenAPI specs, or integrate existing tools to give agents diverse capabilities, all for tight integration with the Google ecosystem.

✨ **Code-First Development**: Define agent logic, tools, and orchestration directly in Python for ultimate flexibility, testability, and versioning.

✨ **Modular Multi-Agent Systems**: Design scalable applications by composing multiple specialized agents into flexible hierarchies.

✨ **Deploy Anywhere**: Easily containerize and deploy agents on Cloud Run or scale seamlessly with Vertex AI Agent Engine.

## 🤖 Agent2Agent (A2A) Protocol and ADK Integration

For remote agent-to-agent communication, ADK integrates with the A2A protocol.

## Development UI

A built-in development UI to help you test, evaluate, debug, and showcase your agent(s).

## Evaluate Agents

```bash
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

## License

This project is licensed under the Apache 2.0 License.

**Source:** [adk-python repository](https://github.com/google/adk-python)