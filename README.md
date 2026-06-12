# AI DesignOps Copilot

AI DesignOps Copilot is a portfolio project that demonstrates a governed, enterprise-style AI workflow for page generation, brand alignment, design-system compliance, CMS-style publishing, and workflow automation.

The project is intentionally framed as more than a chatbot. It models how an enterprise team could use retrieval-augmented generation, agentic workflow orchestration, design-token governance, CMS integration patterns, and ticket automation to reduce manual effort while maintaining approval gates and traceability.

## Target Capabilities

| Capability | Planned Implementation |
|---|---|
| Governed page request intake | React form and typed FastAPI request model. |
| Knowledge retrieval | RAG over brand rules, component registry, tokens, CMS rules, and accessibility guidance. |
| Agentic workflow | Explicit workflow stages for classification, retrieval, layout planning, compliance checking, human approval, YAML generation, and ticket creation. |
| Design-system governance | Token pipeline, Storybook components, DS 1.0/2.0 versioning, and CI drift checks. |
| CMS-style publishing | YAML page model and CMS adapter abstraction. |
| Workflow automation | GitHub Issues or Jira ticket generation from QA findings and page-generation context. |
| Production readiness | CI, documentation, monitoring notes, risk controls, and deployment path. |

## Repository Structure

```text
apps/web              Frontend application shell.
apps/api              Python API and workflow endpoints.
libs/ui               Shared UI components.
libs/tokens           Design-token source and generated artifacts.
libs/compliance       Brand, accessibility, and design-system validation rules.
libs/cms-adapter      CMS-style YAML and publishing adapter logic.
libs/ai-workflows     Agentic workflow orchestration and state models.
docs                  Architecture, learning log, decisions, screenshots, and interview notes.
scripts               Utility scripts for setup, validation, and automation.
```

## FastAPI Backend API Shell
 
Day 4 established the FastAPI backend API shell within `apps/api`. This includes defining explicit API contracts using Pydantic models for `PageRequest`, `ComplianceFinding`, `PagePlan`, and `WorkflowState`. Foundational endpoints (`/health`, `/page-request/validate`, `/workflow/mock-run`) were implemented to provide a structured interface for the frontend and future AI components.
 
### Verification Commands
 
```bash
cd apps/api
source .venv/bin/activate
uvicorn main:app --reload --port 8000
# In a new terminal:
curl http://127.0.0.1:8000/health
curl -X POST "http://127.0.0.1:8000/page-request/validate" -H "Content-Type: application/json" -d '{"page_type": "landing_page", "audience": "marketers", "brand": "brand_a", "channel": "web", "notes": "This is an urgent request."}'
curl -X POST "http://127.0.0.1:8000/workflow/mock-run" -H "Content-Type: application/json" -d '{"page_type": "blog_post", "audience": "developers", "brand": "brand_b", "channel": "web", "notes": "Technical article."}'
# Open http://127.0.0.1:8000/docs in browser
```

## Running the Frontend

**Prerequisites:** Node.js 18+, pnpm

Install dependencies from the repo root:

```bash
pnpm install
```

Start the dev server:

```bash
# From repo root
pnpm nx run web:dev

# Or directly from apps/web
cd apps/web
pnpm dev
```

Opens at **http://localhost:5173**

Build for production:

```bash
pnpm nx run web:build
```
