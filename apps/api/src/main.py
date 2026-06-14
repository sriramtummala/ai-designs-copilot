import datetime
import sys
import uuid
from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Allow importing from the monorepo root
sys.path.append(".")
from libs.rag.create_embeddings import get_index, get_model, retrieve


# --- Lifespan ---

@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_model()
    get_index()
    yield


app = FastAPI(
    title="AI DesignOps Copilot API",
    description="API for managing AI DesignOps workflows, page requests, and compliance.",
    version="0.1.0",
    lifespan=lifespan,
)


# --- Pydantic Models ---

class PageType(str, Enum):
    landing_page = "landing_page"
    product_page = "product_page"
    blog_post = "blog_post"
    help_article = "help_article"

class Audience(str, Enum):
    developers = "developers"
    designers = "designers"
    marketers = "marketers"
    end_users = "end_users"

class Brand(str, Enum):
    brand_a = "brand_a"
    brand_b = "brand_b"

class Channel(str, Enum):
    web = "web"
    mobile = "mobile"
    email = "email"

class PageRequest(BaseModel):
    page_type: PageType = Field(..., description="Type of page to generate.")
    audience: Audience = Field(..., description="Target audience for the page.")
    brand: Brand = Field(..., description="Brand guidelines to follow.")
    channel: Channel = Field(..., description="Delivery channel for the page.")
    notes: Optional[str] = Field(None, description="Additional notes or requirements.")

class ComplianceFinding(BaseModel):
    rule_id: str
    description: str
    severity: str
    suggestion: Optional[str] = None

class PagePlan(BaseModel):
    title: str
    sections: List[str]
    keywords: List[str]
    estimated_word_count: int

class WorkflowState(BaseModel):
    request_id: str
    status: str
    page_request: PageRequest
    compliance_findings: List[ComplianceFinding] = []
    page_plan: Optional[PagePlan] = None
    last_updated: str

class RetrievalRequest(BaseModel):
    query: str = Field(..., description="Natural language query to search the knowledge base.")
    k: int = Field(5, ge=1, le=20, description="Number of results to return.")
    filters: Optional[dict] = Field(None, description="Optional metadata filters (e.g. source_type).")

class RetrievalResult(BaseModel):
    score: float
    content: str
    source_path: Optional[str] = None
    source_type: Optional[str] = None
    metadata: dict

class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievalResult]


# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AI DesignOps Copilot API is healthy"}


@app.post("/rag/retrieve", response_model=RetrievalResponse, summary="RAG Retrieval")
async def retrieve_knowledge(request: RetrievalRequest):
    """Search the knowledge base using semantic similarity."""
    try:
        raw = retrieve(request.query, k=request.k)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Retrieval failed: {e}")

    # Apply optional metadata filters post-retrieval
    if request.filters:
        raw = [
            r for r in raw
            if all(r["metadata"].get(k) == v for k, v in request.filters.items())
        ]

    results = [
        RetrievalResult(
            score=r["score"],
            content=r["content"],
            source_path=r["metadata"].get("source_path"),
            source_type=r["metadata"].get("source_type"),
            metadata=r["metadata"],
        )
        for r in raw
    ]
    return RetrievalResponse(query=request.query, results=results)


@app.post("/page-request/validate", response_model=List[ComplianceFinding])
async def validate_page_request(request: PageRequest):
    findings = []
    if request.notes and "urgent" in request.notes.lower():
        findings.append(ComplianceFinding(
            rule_id="URGENT_FLAG",
            description="'Urgent' keyword detected in notes. Requires special approval.",
            severity="high",
            suggestion="Route to manual review process.",
        ))
    if request.page_type == PageType.blog_post and request.audience == Audience.developers:
        findings.append(ComplianceFinding(
            rule_id="BLOG_DEV_AUDIENCE",
            description="Blog post for developers might require technical review.",
            severity="medium",
            suggestion="Ensure technical accuracy and appropriate tone.",
        ))
    return findings


@app.post("/workflow/mock-run", response_model=WorkflowState)
async def mock_workflow_run(request: PageRequest):
    request_id = str(uuid.uuid4())
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    compliance_findings = await validate_page_request(request)

    mock_page_plan = PagePlan(
        title=f"Proposed {request.page_type.replace('_', ' ').title()} for {request.brand.title()} ({request.audience.title()})",
        sections=["Introduction", "Key Features", "Benefits", "Call to Action"],
        keywords=[request.page_type, request.audience, request.brand, "AI DesignOps"],
        estimated_word_count=500,
    )

    return WorkflowState(
        request_id=request_id,
        status="mock_completed",
        page_request=request,
        compliance_findings=compliance_findings,
        page_plan=mock_page_plan,
        last_updated=current_time,
    )
