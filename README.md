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
| Content transformation | Done | `transform_content()` — parses LLM JSON output into typed Pydantic schemas |
| Compliance validation | Done | `ComplianceService` — prohibited-word check, CTA presence, brand-guideline RAG |
| CMS-style publishing | Done | `CMSAdapter` interface with `MockCMSAdapter` (in-memory) and `ContentfulAdapter` |
| Content analytics | Done | `ContentAnalyticsService` — performance recording and feedback-to-LLM simulation |
| Design-system governance | Planned | Token pipeline, Storybook components, DS versioning |
| Workflow automation | Planned | GitHub Issues / Jira ticket generation |

## Repository Structure

```text
apps/api                  Python FastAPI backend — RAG, LLM, workflow, publish, and analytics endpoints
apps/web                  React + Vite frontend application shell
libs/ai-workflows         WorkflowEngine, ContentWorkflowState, STATE_TRANSITIONS
libs/llm                  BaseAgent, agent roles, prompts, tool schemas, tool functions
libs/rag                  Embedding pipeline, FAISS index, retrieval helpers
libs/content_transformer  Schema models (BlogPostSchema, LandingPageSchema) and transform_content()
libs/cms-adapter          CMSAdapter interface, MockCMSAdapter, ContentfulAdapter
libs/compliance           ComplianceService — prohibited word checks, CTA validation
libs/analytics            ContentAnalyticsService — performance recording and feedback simulation
libs/ui                   Shared UI components
libs/tokens               Design-token source and generated artifacts
docs                      Architecture, learning log, decisions, and interview notes
scripts                   Utility scripts for setup and validation
```

---

## Running the API

**Prerequisites:** Python 3.10+, `.env` file at repo root.

```dotenv
# Required
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Optional — omit to use MockCMSAdapter instead of Contentful
CONTENTFUL_SPACE_ID=...
CONTENTFUL_MANAGEMENT_TOKEN=...
CONTENTFUL_ENVIRONMENT=master
CONTENTFUL_LOCALE=en-US
CONTENTFUL_BLOG_POST_CONTENT_TYPE=blogPost
```

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
| `POST` | `/transform` | Parse and validate raw LLM JSON output into a typed schema |
| `POST` | `/publish` | Transform → compliance check → CMS publish → analytics record |
| `GET` | `/analytics` | Retrieve performance records (filterable by content_id or content_type) |
| `POST` | `/analytics/feedback` | Submit a feedback score for a published piece |

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
- Agent calls are offloaded via `asyncio.to_thread()` so the sync OpenAI SDK does not block the FastAPI event loop.

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

## Content Publishing Pipeline

`POST /publish` runs a sequential gate pipeline — each stage must pass before the next is invoked.

```
POST /publish
  └─ ContentTransformer   — parse LLM JSON → typed Pydantic schema (BlogPostSchema / LandingPageSchema)
       └─ ComplianceService  — prohibited-word scan + CTA check + brand-guideline RAG
            └─ CMSAdapter    — MockCMSAdapter (default) or ContentfulAdapter (when env vars set)
                 └─ ContentAnalyticsService  — record publish event with metrics
```

### Content Transformer

`libs/content_transformer/` — `transform_content(raw_llm_output, schema_cls)` JSON-parses and validates LLM output against a Pydantic v2 schema. Raises `ValueError` (propagated as a 422) on parse failure or schema mismatch.

Schemas: `BlogPostSchema`, `LandingPageSchema` (with nested `ContentSection`).

```bash
curl -s -X POST "http://127.0.0.1:8000/transform" \
  -H "Content-Type: application/json" \
  -d '{"content_type":"blog_post","raw_llm_output":"{\"title\":\"Test\",\"author\":\"Alice\",\"publish_date\":\"2025-01-01\",\"tags\":[\"ai\"],\"summary\":\"Short summary\",\"body\":\"Body text.\",\"seo_keywords\":[\"ai\"]}"}'
```

### Compliance Service

`libs/compliance/compliance_service.py` — `ComplianceService.validate(content, brand)` returns a `ValidationResult(is_compliant, details)`. A non-compliant result blocks the publish with a `422` response that includes each failing `ValidationFinding`.

Rules currently enforced:

| Rule | Check |
|---|---|
| Prohibited words | Rejects content containing `"revolutionary"`, `"groundbreaking"` |
| CTA presence | Warns when no call-to-action is set on a blog post |
| Brand guidelines | RAG retrieval over `brand_guidelines.txt` for the requested brand |

### CMS Adapter

`libs/cms-adapter/` — `CMSAdapter` abstract interface with `publish()`, `get_status()`, and `unpublish()`.

| Adapter | When used | Notes |
|---|---|---|
| `MockCMSAdapter` | `CONTENTFUL_*` env vars absent | Stores content in memory; returns a UUID `content_id` |
| `ContentfulAdapter` | `CONTENTFUL_*` env vars present | Calls the Contentful Management API to create and publish an entry |

### Content Analytics

`libs/analytics/analytics_service.py` — `ContentAnalyticsService` records a `PerformanceRecord` after each successful publish and accepts feedback scores to simulate a feedback loop back to the LLM.

```bash
# Retrieve all analytics records
curl -s "http://127.0.0.1:8000/analytics"

# Filter by content type
curl -s "http://127.0.0.1:8000/analytics?content_type=blog_post"

# Submit feedback
curl -s -X POST "http://127.0.0.1:8000/analytics/feedback" \
  -H "Content-Type: application/json" \
  -d '{"content_id":"<id>","feedback_score":4.5,"feedback_text":"Great tone, tighten the intro."}'
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

---

## Docker

Both services have multi-stage Dockerfiles. Build context for both is the **monorepo root**.

### API

```bash
# Build
docker build -f apps/api/Dockerfile -t ai-designs-copilot-api .

# Run — inject secrets at runtime, never bake them into the image
docker run --env-file .env -p 8000:8000 ai-designs-copilot-api
```

> `sentence-transformers` pulls in PyTorch (~2 GB). The first build takes several minutes; subsequent builds use the cached venv layer.

### Web

```bash
# Build
docker build -f apps/web/Dockerfile -t ai-designs-copilot-web .

# Run
docker run -p 3000:80 ai-designs-copilot-web
```

Opens at **http://localhost:3000**

The web image uses nginx with gzip compression and a 1-year cache policy on Vite's content-hashed `/assets/` files. All unmatched routes fall back to `index.html` for client-side routing.
