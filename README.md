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
