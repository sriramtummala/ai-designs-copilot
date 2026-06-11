## 1. Architecture Intent
 
The system is designed as a governed AI workflow rather than a single prompt. Each major responsibility is separated into a component so that request intake, retrieval, planning, compliance, approval, CMS output, and ticket automation can be tested and evolved independently.

## 2. High-Level System Diagram
 
```mermaid
flowchart TD
    U[User: Brand / Design / Content / Engineering] --> WEB[React Request UI]
    WEB --> API[FastAPI Workflow API]
    API --> WF[Agentic Workflow Orchestrator]
 
    WF --> RAG[RAG Retrieval Layer]
    RAG --> KB[(Approved Knowledge Base)]
    KB --> BG[Brand Guidelines]
    KB --> CR[Component Registry]
    KB --> DT[Design Tokens]
    KB --> AR[Accessibility Rules]
    KB --> CMSR[CMS Page Rules]
 
    WF --> PLAN[Layout Planner]
    PLAN --> COMP[Compliance Checker]
    COMP --> APPROVAL[Human Approval Gate]
    APPROVAL --> YAML[CMS-Style YAML Generator]
    APPROVAL --> TICKET[Ticket Automation]
 
    YAML --> CMS[CMS Adapter / Bloomreach-Style Simulation]
    TICKET --> JIRA[Jira or GitHub Issues]
 
    API --> LOGS[Trace Logs and Evaluation Evidence]
