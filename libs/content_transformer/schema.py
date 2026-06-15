from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ContentSection(BaseModel):
    section_type: str = Field(..., description="e.g. 'features', 'testimonials', 'faq'")
    heading: Optional[str] = None
    body: str = Field(..., description="Section body in Markdown.")
    cta_text: Optional[str] = None
    cta_url: Optional[HttpUrl] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BlogPostSchema(BaseModel):
    title: str
    author: str
    publish_date: date
    tags: List[str]
    summary: str
    body: str = Field(..., description="Main content in Markdown.")
    image_url: Optional[HttpUrl] = None
    seo_keywords: List[str]
    call_to_action: Optional[str] = None


class LandingPageSchema(BaseModel):
    page_title: str
    hero_headline: str
    hero_subheadline: str
    sections: List[ContentSection]
    seo_keywords: List[str]
    cta_text: Optional[str] = None
    cta_url: Optional[HttpUrl] = None
