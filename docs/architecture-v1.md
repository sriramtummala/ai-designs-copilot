## 1. Introduction

This document outlines the initial architecture for the AI DesignOps Copilot, a system designed to automate and govern the generation of digital content (e.g., web pages, blog posts) for brand, design-system, and CMS teams. The system provides structured, compliant, and on-brand content through an AI-assisted workflow with human approval gates.

## 2. System Overview

The AI DesignOps Copilot is structured as a monorepo, separating concerns into distinct applications and libraries. This modular approach facilitates maintainability, testability, and clear ownership boundaries.

### 2.1 High-Level Component Diagram

```mermaid
graph TD
    A["User - DesignOps / Marketing"]
    B["Frontend Web App"]
    C["FastAPI Backend API"]
    D["Compliance Library"]
    K["LLM Service - OpenAI"]
    TOOLS["Tool Functions\nget_brand_info"]

    subgraph RAG_System [RAG System]
        F["RAG Retrieve API"]
        G["Embedding Model"]
        H["Vector Store - FAISS"]
        I["Knowledge Base"]
        J["Chunking and Metadata"]

        F -->|"Query Embeddings"| G
        G -->|"Semantic Search"| H
        H -->|"Retrieves Chunks"| I
        I -->|"Processed by"| J
        J --> H
    end

    subgraph Orchestration_Layer [Orchestration Layer]
        subgraph Workflow_Engine [Workflow Engine]
            WE_STATE("State Machine")
            WE_AUDIT("History / Audit Log")
            WE_FAIL(["FAILED - Terminal"])
        end
        subgraph Agents ["Agents  BaseAgent with Tenacity Retry"]
            AGENT_PLAN("Planner Agent\nPLANNING state")
            AGENT_WRITE("Writer Agent\nDRAFTING + REVISION states")
            AGENT_REVIEW("Reviewer Agent\nREVIEW state")
            AGENT_RESEARCH("Researcher Agent\nplanned")
        end
        subgraph HITL [Human-in-the-Loop]
            HITL_REVIEW("Human Review\nPOST /workflows/{id}/human-review")
            HITL_FEEDBACK("Generation Feedback\nPOST /feedback")
        end
    end

    A -->|"Submits Request"| B
    B -->|"Structured Request"| C

    C -->|"POST /workflows\nInitiates Workflow"| WE_STATE
    WE_STATE -->|"Logs each transition"| WE_AUDIT

    WE_STATE -->|"PLANNING: dispatch"| AGENT_PLAN
    AGENT_PLAN -->|"Plan output → metadata"| WE_STATE

    WE_STATE -->|"DRAFTING / REVISION: dispatch"| AGENT_WRITE
    AGENT_WRITE -->|"Draft output → metadata"| WE_STATE

    WE_STATE -->|"REVIEW: dispatch"| AGENT_REVIEW
    AGENT_REVIEW -->|"Review feedback → metadata"| WE_STATE

    WE_STATE -->|"HUMAN_REVIEW: pause"| HITL_REVIEW
    HITL_REVIEW -->|"approved=true → COMPLETED"| WE_STATE
    HITL_REVIEW -->|"approved=false → REVISION"| WE_STATE

    WE_STATE -->|"Agent exception or no output"| WE_FAIL

    AGENT_PLAN & AGENT_WRITE & AGENT_REVIEW & AGENT_RESEARCH -->|"chat.completions + retry"| K
    K -->|"Message response"| AGENT_PLAN & AGENT_WRITE & AGENT_REVIEW & AGENT_RESEARCH

    AGENT_PLAN & AGENT_WRITE & AGENT_REVIEW -->|"tool_calls loop"| TOOLS
    TOOLS -->|"Brand info result"| AGENT_PLAN & AGENT_WRITE & AGENT_REVIEW

    AGENT_RESEARCH -.->|"planned: retrieves context"| F
    F -.->|"planned: returns context"| AGENT_RESEARCH

    C -->|"POST /generate\nRAG + prompt + tools"| K
    C -->|"Retrieves knowledge"| F
    C -->|"Validates request"| D
    C -->|"Applies design tokens"| L["Tokens Library"]
    C -->|"Formats output"| M["CMS Adapter Library"]
    M -->|"Publishes"| N["CMS Publishing System"]
    C -->|"Returns workflow state"| B
    B -->|"Displays status"| A
    A -->|"Submits star rating"| HITL_FEEDBACK

    style RAG_System fill:#f9f,stroke:#333,stroke-width:2px
    style Orchestration_Layer fill:#ccf,stroke:#333,stroke-width:2px
    style Workflow_Engine fill:#fff,stroke:#000,stroke-width:1px
    style Agents fill:#eee,stroke:#000,stroke-width:1px
    style HITL fill:#ffc,stroke:#000,stroke-width:1px
    style WE_FAIL fill:#fdd,stroke:#c00,stroke-width:1px
```

### 2.2 Workflow State Machine

The `WorkflowEngine` enforces an explicit transition allowlist. Every call to `transition()` is validated before it commits; invalid moves raise `ValueError`.

```mermaid
stateDiagram-v2
    [*] --> INITIALIZED

    INITIALIZED --> PLANNING
    INITIALIZED --> FAILED

    PLANNING --> DRAFTING
    PLANNING --> FAILED

    DRAFTING --> REVIEW
    DRAFTING --> REVISION
    DRAFTING --> FAILED

    REVIEW --> HUMAN_REVIEW
    REVIEW --> REVISION
    REVIEW --> FAILED

    HUMAN_REVIEW --> COMPLETED : approved = true
    HUMAN_REVIEW --> REVISION  : approved = false
    HUMAN_REVIEW --> FAILED

    REVISION --> DRAFTING
    REVISION --> REVIEW
    REVISION --> FAILED

    COMPLETED --> [*]
    FAILED --> [*]
```

| State | Agent Dispatched | Notes |
|---|---|---|
| `PLANNING` | `PlannerAgent` | Produces outline, audience analysis, keywords |
| `DRAFTING` | `WriterAgent` | Writes Markdown draft using plan as context |
| `REVIEW` | `ReviewerAgent` | Evaluates draft against brand and compliance rules |
| `HUMAN_REVIEW` | — | **Workflow pauses.** No LLM call. Resumes via `POST /workflows/{id}/human-review` |
| `REVISION` | `WriterAgent` | Rewrites using `human_review_feedback` from metadata |
| `COMPLETED` | — | Terminal — content approved |
| `FAILED` | — | Terminal — agent exception or retry exhaustion recorded in `metadata.error` |

### 2.3 Agent Architecture

All agents extend `BaseAgent` (`libs/llm/agents/core.py`). Each agent:

- Maintains a `conversation_history` seeded with its role-specific system prompt (`libs/llm/agents/roles.py`).
- Passes `AVAILABLE_TOOLS` on every LLM call, enabling multi-turn tool-call loops (the loop runs until `finish_reason != "tool_calls"`).
- Uses **tenacity** in `_call_llm` for automatic exponential-backoff retry (up to 3 attempts, 1 s → 10 s) on `RateLimitError`, `APIConnectionError`, `APITimeoutError`, and `InternalServerError`. Non-retryable errors (auth, bad request) fail immediately and return `None`.
- On `None` return or an unhandled exception, `WorkflowEngine.execute_agent_action()` calls `fail()`, recording `failed_at_state` and `reason` in `metadata.error` before transitioning to `FAILED`.

## 3. Repository Structure

```text
apps/api              FastAPI backend — RAG, LLM, workflow, and feedback endpoints
apps/web              Frontend application shell
libs/ai-workflows     WorkflowEngine, ContentWorkflowState, STATE_TRANSITIONS
libs/llm              BaseAgent, agent roles, prompts, tool schemas, tool functions
libs/rag              Embedding pipeline, FAISS index, retrieval helpers
libs/ui               Shared UI components
libs/tokens           Design-token source and generated artifacts
libs/compliance       Brand, accessibility, and design-system validation rules
libs/cms-adapter      CMS-style YAML model and publishing adapter
docs                  Architecture, learning log, decisions, and interview notes
scripts               Utility scripts for setup and validation
```

## 4. Key Design Decisions

| Decision | Rationale |
|---|---|
| State machine with explicit transition allowlist | Prevents illegal state jumps; every transition is auditable in `history` |
| `HUMAN_REVIEW` as a first-class pause state | Keeps approval gates in the state machine rather than a side-channel |
| Agents call OpenAI directly (not proxied through the API layer) | Avoids an extra hop; `openai_client` is injected into `WorkflowEngine` at creation |
| `sys.path.append("./libs/ai-workflows")` workaround | Hyphenated directory name `libs/ai-workflows` is not a valid Python package path; direct path append lets `from states import …` resolve |
| `load_dotenv(override=True)` | Ensures `.env` values win over any inherited shell env vars, avoiding stale key issues |
| Tenacity inside `_call_llm` (not as a method decorator) | Allows `self` and `kwargs` to be in scope for the retry closure |
| In-memory `workflow_store` | Sufficient for portfolio/demo scope; replace with a database-backed store for production |
