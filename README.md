# AI DesignOps Copilot

AI DesignOps Copilot is a portfolio project that demonstrates a governed, enterprise-style AI workflow for page generation, brand alignment, design-system compliance, CMS-style publishing, and workflow automation.

The project models how an enterprise team could use retrieval-augmented generation, agentic workflow orchestration, design-token governance, CMS integration patterns, and ticket automation to reduce manual effort while maintaining approval gates and traceability.

## Implemented Capabilities

| Capability | Status | Details |
|---|---|---|
| Governed page request intake | Done | Typed FastAPI request model with enum-validated fields |
| Knowledge retrieval (RAG) | Done | FAISS vector store + sentence-transformers over brand, CMS, and token docs |
| LLM content generation | Done | OpenAI integration with configurable temperature, top_p, penalties |
| Tool calling | Done | `get_brand_info` tool with multi-turn loop and tenacity retry |
| Agentic workflow engine | Done | State-machine workflow with Planner, Writer, and Reviewer agents |
| Human-in-the-loop approval | Done | `HUMAN_REVIEW` pause state with approve/reject endpoint |
| Feedback logging | Done | JSONL feedback log per generated response |
| Design-system governance | Planned | Token pipeline, Storybook components, DS versioning |
| CMS-style publishing | Planned | YAML page model and CMS adapter abstraction |
| Workflow automation | Planned | GitHub Issues / Jira ticket generation |

## Repository Structure

```text
apps/api              Python FastAPI backend — RAG, LLM, workflow, and feedback endpoints.
apps/web              Frontend application shell.
libs/ai-workflows     Workflow state machine and engine.
libs/llm              Prompts, tool definitions, tool functions, and agent classes.
libs/rag              Embedding pipeline, FAISS index, and retrieval helpers.
libs/ui               Shared UI components.
libs/tokens           Design-token source and generated artifacts.
libs/compliance       Brand, accessibility, and design-system validation rules.
libs/cms-adapter      CMS-style YAML and publishing adapter logic.
docs                  Architecture, learning log, decisions, and interview notes.
scripts               Utility scripts for setup, validation, and automation.
```

## Running the API

**Prerequisites:** Python 3.10+, `.env` file at repo root with `OPENAI_API_KEY` and `OPENAI_MODEL`.

```bash
# From repo root — always launch from here so monorepo imports resolve
apps/api/.venv/Scripts/uvicorn apps.api.src.main:app --reload --port 8000
```

Interactive docs: **http://127.0.0.1:8000/docs**

### Core Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check — reports RAG and OpenAI client status |
| `POST` | `/rag/retrieve` | Semantic search over the knowledge base |
| `POST` | `/generate` | RAG → prompt → LLM → generated Markdown |
| `POST` | `/feedback` | Submit a star rating and comments on a generation |
| `POST` | `/workflows` | Start a new content workflow |
| `GET` | `/workflows/{id}` | Get current workflow state and history |
| `POST` | `/workflows/{id}/transition` | Advance the workflow to a new state |
| `POST` | `/workflows/{id}/human-review` | Submit a human approve/reject decision |

---

## Advanced Orchestration

The orchestration layer sits in `libs/ai-workflows/` and `libs/llm/agents/` and implements a full multi-agent content pipeline with human oversight.

### Workflow State Machine

`libs/ai-workflows/states.py` defines a strict state machine. Each transition is validated against an explicit allowlist — invalid moves raise a `ValueError` before any LLM call is made.

```
INITIALIZED → PLANNING → DRAFTING → REVIEW → HUMAN_REVIEW → COMPLETED
                                  ↘          ↘             ↘
                                   REVISION ←──────────────┘
                                  ↘ FAILED (any state)
```

| State | Agent | Behaviour |
|---|---|---|
| `PLANNING` | `PlannerAgent` | Produces a structured content plan with audience analysis, outline, and keywords |
| `DRAFTING` | `WriterAgent` | Writes on-brand Markdown content using the plan as context |
| `REVIEW` | `ReviewerAgent` | Critically evaluates the draft against brand guidelines and compliance rules |
| `HUMAN_REVIEW` | — | Workflow **pauses**. No LLM call. Resumes via `POST /workflows/{id}/human-review` |
| `REVISION` | `WriterAgent` | Rewrites using human feedback stored in `metadata.human_review_feedback` |
| `COMPLETED` / `FAILED` | — | Terminal states |

### WorkflowEngine

`libs/ai-workflows/engine.py` — `WorkflowEngine` manages one workflow instance. It:

- Validates every transition against `STATE_TRANSITIONS` before committing it.
- Dispatches to the correct agent via `STATE_AGENT_MAP` after each transition.
- Calls `fail()` automatically if an agent raises an exception or exhausts all retries, recording `metadata.error.failed_at_state` and `metadata.error.reason` for diagnostics.
- Accumulates each agent's output in `metadata` (e.g. `planning_output`, `drafting_output`) so every downstream agent has full prior context.

### Agent Architecture

`libs/llm/agents/core.py` — `BaseAgent` provides the shared conversation loop:

- Maintains a running `conversation_history` seeded with the agent's role-specific system prompt.
- Passes `AVAILABLE_TOOLS` on every call so the model can invoke tools mid-response.
- Handles multi-turn tool calls inline — executes `TOOL_FUNCTIONS[name](**args)` and feeds results back until the model produces a final text response.
- `_call_llm` uses **tenacity** for automatic retry with exponential backoff (1 s → 2 s → 4 s, up to 3 attempts) on `RateLimitError`, `APIConnectionError`, `APITimeoutError`, and `InternalServerError`. Non-retryable errors (auth, bad request) fail immediately.

Specialised agents — `PlannerAgent`, `ResearcherAgent`, `WriterAgent`, `ReviewerAgent` — inherit `BaseAgent` and inject their role prompt from `libs/llm/agents/roles.py`.

### Tool Calling

`libs/llm/tools.py` — tool schemas (OpenAI function-calling format).  
`libs/llm/tool_functions.py` — callable implementations.

Currently registered:

| Tool | Description |
|---|---|
| `get_brand_info` | Returns tone of voice, key messaging, or target audience for `brand_a` / `brand_b` |

New tools can be added by appending a schema to `AVAILABLE_TOOLS` and a callable to `TOOL_FUNCTIONS`.

### End-to-End Workflow Example

```bash
# Start server from repo root
apps/api/.venv/Scripts/uvicorn apps.api.src.main:app --reload --port 8000

# 1. Create a workflow
RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/workflows" \
  -H "Content-Type: application/json" \
  -d '{"page_type":"blog_post","audience":"developers","brand":"brand_b","channel":"web","notes":"New API security features"}')
WF_ID=$(echo $RESPONSE | python -c "import sys,json; print(json.load(sys.stdin)['workflow_id'])")

# 2–4. Advance through AI stages (each triggers the mapped agent)
curl -s -X POST "http://127.0.0.1:8000/workflows/$WF_ID/transition" \
  -H "Content-Type: application/json" -d '{"new_state":"PLANNING"}'
curl -s -X POST "http://127.0.0.1:8000/workflows/$WF_ID/transition" \
  -H "Content-Type: application/json" -d '{"new_state":"DRAFTING"}'
curl -s -X POST "http://127.0.0.1:8000/workflows/$WF_ID/transition" \
  -H "Content-Type: application/json" -d '{"new_state":"REVIEW"}'

# 5. Enter human review — workflow pauses, no LLM call
curl -s -X POST "http://127.0.0.1:8000/workflows/$WF_ID/transition" \
  -H "Content-Type: application/json" -d '{"new_state":"HUMAN_REVIEW"}'

# 6. Approve → COMPLETED  (or reject with approved:false → REVISION)
curl -s -X POST "http://127.0.0.1:8000/workflows/$WF_ID/human-review" \
  -H "Content-Type: application/json" \
  -d '{"approved":true,"feedback":"On-brand and accurate. Approved."}'
```

---

## Running the Frontend

**Prerequisites:** Node.js 18+, pnpm

```bash
# Install dependencies
pnpm install

# Start dev server (from repo root)
pnpm nx run web:dev
```

Opens at **http://localhost:5173**

```bash
# Production build
pnpm nx run web:build
```
