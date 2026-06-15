import json
import logging
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from libs.content_transformer.schema import BlogPostSchema

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def transform_content(raw_llm_output: str, target_schema: Type[T]) -> T:
    """Parse raw LLM JSON output and validate it against a Pydantic schema."""
    try:
        data = json.loads(raw_llm_output)
        result = target_schema.model_validate(data)
        logger.info("Transformed content to %s", target_schema.__name__)
        return result
    except json.JSONDecodeError as e:
        logger.error("JSON decode error for %s: %s", target_schema.__name__, e)
        raise ValueError(f"LLM output is not valid JSON: {e}") from e
    except ValidationError as e:
        logger.error("Validation error for %s: %s", target_schema.__name__, e)
        raise ValueError(f"LLM output does not match {target_schema.__name__}: {e}") from e


if __name__ == "__main__":
    sample_blog = '''
    {
      "title": "The Future of AI in DesignOps",
      "author": "AI DesignOps Bot",
      "publish_date": "2026-06-12",
      "tags": ["AI", "DesignOps", "Automation"],
      "summary": "How AI is reshaping Design Operations.",
      "body": "## Introduction\nAI is transforming DesignOps...",
      "image_url": "https://example.com/ai-designops.jpg",
      "seo_keywords": ["AI DesignOps", "Design Automation"],
      "call_to_action": "Learn more about our AI DesignOps solutions!"
    }
    '''

    try:
        post = transform_content(sample_blog, BlogPostSchema)
        print(post.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Transformation failed: {e}")

    missing_seo_keywords = '''
    {
      "title": "Missing Fields",
      "author": "Test",
      "publish_date": "2026-06-12",
      "tags": ["test"],
      "summary": "Missing seo_keywords.",
      "body": "Body text."
    }
    '''
    try:
        transform_content(missing_seo_keywords, BlogPostSchema)
    except ValueError as e:
        print(f"Expected validation error: {e}")
