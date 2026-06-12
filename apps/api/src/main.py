from enum import Enum
from typing import List, Optional
 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
 
app = FastAPI(
    title="AI DesignOps Copilot API",
    description="API for managing AI DesignOps workflows, page requests, and compliance.",
    version="0.1.0",
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
    rule_id: str = Field(..., description="Identifier for the compliance rule.")
    description: str = Field(..., description="Description of the compliance issue.")
    severity: str = Field(..., description="Severity of the finding (e.g., 'high', 'medium', 'low').")
    suggestion: Optional[str] = Field(None, description="Suggested fix for the compliance issue.")
 
class PagePlan(BaseModel):
    title: str = Field(..., description="Proposed title for the page.")
    sections: List[str] = Field(..., description="List of proposed sections for the page.")
    keywords: List[str] = Field(..., description="Relevant keywords for SEO.")
    estimated_word_count: int = Field(..., description="Estimated word count for the page.")
 
class WorkflowState(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the page request.")
    status: str = Field(..., description="Current status of the workflow (e.g., 'pending', 'validated', 'generating').")
    page_request: PageRequest = Field(..., description="The original page request details.")
    compliance_findings: List[ComplianceFinding] = Field(default_factory=list, description="List of compliance issues found.")
    page_plan: Optional[PagePlan] = Field(None, description="The generated page plan.")
    last_updated: str = Field(..., description="Timestamp of the last update.")
 
# --- Endpoints ---
 
@app.get("/health", summary="Health Check")
async def health_check():
    """Checks if the API is running."""
    return {"status": "ok", "message": "AI DesignOps Copilot API is healthy"}
 
@app.post("/page-request/validate", response_model=List[ComplianceFinding], summary="Validate Page Request")
async def validate_page_request(request: PageRequest):
    """Validates a page request against compliance rules.
 
    This endpoint simulates compliance checks. In a real scenario, this would
    involve calling the `libs/compliance` library.
    """
    # Placeholder for actual compliance logic
    findings = []
    if "urgent" in request.notes.lower() if request.notes else "":
        findings.append(ComplianceFinding(
            rule_id="URGENT_FLAG",
            description="'Urgent' keyword detected in notes. Requires special approval.",
            severity="high",
            suggestion="Route to manual review process."
        ))
    if request.page_type == PageType.blog_post and request.audience == Audience.developers:
        findings.append(ComplianceFinding(
            rule_id="BLOG_DEV_AUDIENCE",
            description="Blog post for developers might require technical review.",
            severity="medium",
            suggestion="Ensure technical accuracy and appropriate tone."
        ))
    return findings
 
@app.post("/workflow/mock-run", response_model=WorkflowState, summary="Mock Workflow Run")
async def mock_workflow_run(request: PageRequest):
    """Simulates a full AI DesignOps workflow run.
 
    This endpoint takes a page request and returns a mock workflow state,
    including simulated compliance findings and a basic page plan.
    """
    import datetime
    import uuid
 
    request_id = str(uuid.uuid4())
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
 
    # Simulate validation
    compliance_findings = await validate_page_request(request)
 
    # Simulate page plan generation
    mock_page_plan = PagePlan(
        title=f"Proposed {request.page_type.replace('_', ' ').title()} for {request.brand.title()} ({request.audience.title()})",
        sections=["Introduction", "Key Features", "Benefits", "Call to Action"],
        keywords=[request.page_type, request.audience, request.brand, "AI DesignOps"],
        estimated_word_count=500
    )
 
    return WorkflowState(
        request_id=request_id,
        status="mock_completed",
        page_request=request,
        compliance_findings=compliance_findings,
        page_plan=mock_page_plan,
        last_updated=current_time
    )
