import datetime
import json
import os
import sys
import uuid
from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

# Allow importing from the monorepo root
sys.path.append(".")
load_dotenv(override=True)
from libs.rag.create_embeddings import get_index, get_model, retrieve
from libs.llm.prompts import PromptContext, build_system_prompt, build_user_prompt


# --- Lifespan ---

openai_client: OpenAI | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global openai_client
    print("Starting up: Loading RAG components...")
    get_model()
    get_index()
    print("RAG components loaded successfully.")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set.")
    else:
        openai_client = OpenAI(api_key=api_key)
        print("OpenAI client initialized.")
    yield
    print("Shutting down...")
    openai_client = None


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

class GenerationRequest(BaseModel):
    page_type: PageType
    audience: Audience
    brand: Brand
    channel: Channel
    notes: Optional[str] = None
    llm_model: Optional[str] = None

class GenerationResponse(BaseModel):
    generated_content: str
    retrieved_context: List[dict]
    llm_model_used: str


# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "rag_loaded": True,
        "openai_client_ready": openai_client is not None,
    }


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


@app.post("/generate", response_model=GenerationResponse, summary="Generate content via LLM")
async def generate_content(request: GenerationRequest):
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI client not initialized. Check OPENAI_API_KEY.")

    # 1. Retrieve relevant context from the knowledge base
    retrieval_query = (
        f"Guidelines for {request.page_type.value} for {request.brand.value} "
        f"targeting {request.audience.value}. {request.notes or ''}"
    )
    try:
        raw_results = retrieve(retrieval_query, k=5)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG retrieval failed: {e}")

    # Apply metadata filters; fall back to unfiltered results if nothing matches
    filters = {
        "brand": request.brand.value,
        "channel": request.channel.value,
        "page_type": request.page_type.value,
    }
    filtered = [r for r in raw_results if all(r["metadata"].get(k) == v for k, v in filters.items())]
    results = filtered if filtered else raw_results

    # 2. Format context string for the prompt
    context_text = (
        "\n\n".join(json.dumps(r["metadata"]) + "\n" + r["content"] for r in results)
        if results
        else "No specific context found in the knowledge base. Rely on general knowledge."
    )

    # 3. Build prompts via PromptContext
    ctx = PromptContext(
        page_type=request.page_type.value,
        audience=request.audience.value,
        brand=request.brand.value,
        channel=request.channel.value,
        retrieved_context=context_text,
        notes=request.notes or "",
    )

    # 4. Call the LLM
    model = request.llm_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        chat_completion = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": build_system_prompt(ctx)},
                {"role": "user", "content": build_user_prompt(ctx)},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        generated_content = chat_completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation error: {e}")

    return GenerationResponse(
        generated_content=generated_content,
        retrieved_context=[{"metadata": r["metadata"], "content": r["content"]} for r in results],
        llm_model_used=model,
    )
