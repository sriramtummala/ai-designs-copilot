import logging
from typing import List

from pydantic import BaseModel

from libs.content_transformer.schema import BlogPostSchema, LandingPageSchema
from libs.rag.create_embeddings import retrieve

logger = logging.getLogger(__name__)

_PROHIBITED_WORDS = ["revolutionary", "groundbreaking"]

_CONTENT_TYPE_MAP = {
    "blog_post": BlogPostSchema,
    "landing_page": LandingPageSchema,
}


class ValidationFinding(BaseModel):
    rule: str
    status: str  # "PASS" or "FAIL"
    message: str
    context: str = ""


class ValidationResult(BaseModel):
    is_compliant: bool
    details: List[ValidationFinding]


class ComplianceService:
    """Validates structured content against brand and compliance rules."""

    def validate(self, content: BaseModel, brand: str) -> ValidationResult:
        if isinstance(content, BlogPostSchema):
            return self._validate_blog_post(content, brand)
        if isinstance(content, LandingPageSchema):
            return ValidationResult(
                is_compliant=True,
                details=[ValidationFinding(
                    rule="Landing page validation",
                    status="PASS",
                    message="Landing page validation not yet implemented.",
                )],
            )
        return ValidationResult(
            is_compliant=False,
            details=[ValidationFinding(
                rule="Unsupported content type",
                status="FAIL",
                message=f"No validation rules defined for {type(content).__name__}.",
            )],
        )

    def validate_by_type(self, content_type: str, content_data: dict, brand: str) -> ValidationResult:
        schema_cls = _CONTENT_TYPE_MAP.get(content_type)
        if not schema_cls:
            return ValidationResult(
                is_compliant=False,
                details=[ValidationFinding(
                    rule="Unsupported content type",
                    status="FAIL",
                    message=f"'{content_type}' is not a supported content type.",
                )],
            )
        return self.validate(schema_cls.model_validate(content_data), brand)

    def _validate_blog_post(self, content: BlogPostSchema, brand: str) -> ValidationResult:
        raw = retrieve(f"Brand guidelines for {brand}", k=1)
        guideline = raw[0]["content"] if raw else ""

        findings: List[ValidationFinding] = []
        content_text = f"{content.title} {content.summary} {content.body}".lower()

        for word in _PROHIBITED_WORDS:
            if word in content_text:
                findings.append(ValidationFinding(
                    rule=f"Avoid prohibited word: {word}",
                    status="FAIL",
                    message=f'Content contains the prohibited word "{word}".',
                    context=guideline,
                ))
            else:
                findings.append(ValidationFinding(
                    rule=f"Avoid prohibited word: {word}",
                    status="PASS",
                    message=f'Content does not contain "{word}".',
                ))

        if not content.call_to_action:
            findings.append(ValidationFinding(
                rule="Include a Call to Action",
                status="FAIL",
                message="Blog post is missing a Call to Action.",
                context="All blog posts must include a call to action.",
            ))
        else:
            findings.append(ValidationFinding(
                rule="Include a Call to Action",
                status="PASS",
                message="Blog post includes a Call to Action.",
            ))

        return ValidationResult(
            is_compliant=all(f.status == "PASS" for f in findings),
            details=findings,
        )
