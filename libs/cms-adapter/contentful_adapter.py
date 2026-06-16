import logging
import os

from pydantic import BaseModel

try:
    import contentful_management as _cm  # type: ignore[import]
    Client = _cm.Client
    from contentful_management.errors import HTTPError as ContentfulManagementError  # type: ignore[import]
except (ImportError, AttributeError):  # package absent or Client/errors path changed
    Client = None  # type: ignore[assignment]
    ContentfulManagementError = Exception  # type: ignore[assignment,misc]

from interface import CMSAdapter, PublishResult
from libs.content_transformer.schema import BlogPostSchema

logger = logging.getLogger(__name__)


class ContentfulAdapter(CMSAdapter):
    """Contentful CMS adapter — publishes structured content via the Management API."""

    def __init__(self):
        space_id = os.getenv("CONTENTFUL_SPACE_ID")
        management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")
        environment_id = os.getenv("CONTENTFUL_ENVIRONMENT", "master")

        if not space_id or not management_token:
            raise ValueError("CONTENTFUL_SPACE_ID and CONTENTFUL_MANAGEMENT_TOKEN must be set.")

        self.locale = os.getenv("CONTENTFUL_LOCALE", "en-US")
        self.blog_post_content_type = os.getenv("CONTENTFUL_BLOG_POST_CONTENT_TYPE", "blogPost")
        client = Client(management_token)
        self.environment = client.spaces().find(space_id).environments().find(environment_id)
        logger.info(
            "ContentfulAdapter ready: space=%s env=%s locale=%s",
            space_id, environment_id, self.locale,
        )

    async def publish(self, content: BaseModel) -> PublishResult:
        if isinstance(content, BlogPostSchema):
            return await self._publish_blog_post(content)
        raise NotImplementedError(f"No Contentful mapping for {type(content).__name__}")

    async def _publish_blog_post(self, content: BlogPostSchema) -> PublishResult:
        loc = self.locale
        fields: dict = {
            "title": {loc: content.title},
            "author": {loc: content.author},
            "publishDate": {loc: content.publish_date.isoformat()},
            "tags": {loc: content.tags},
            "summary": {loc: content.summary},
            "body": {loc: content.body},
            "seoKeywords": {loc: content.seo_keywords},
        }
        if content.image_url:
            fields["imageUrl"] = {loc: str(content.image_url)}
        if content.call_to_action:
            fields["callToAction"] = {loc: content.call_to_action}

        logger.debug(
            "ContentfulAdapter: creating entry content_type=%s locale=%s fields=%s",
            self.blog_post_content_type, loc, list(fields.keys()),
        )
        try:
            entry = self.environment.entries.create(
                {"content_type_id": self.blog_post_content_type, "fields": fields}
            )
            entry.publish()
            logger.info("ContentfulAdapter: published blog post as %s", entry.id)
            return PublishResult(content_id=entry.id, status="published")
        except ContentfulManagementError as e:
            logger.error("Contentful API error publishing blog post: %s", e)
            raise ValueError(f"Contentful API error: {e}") from e

    async def get_status(self, content_id: str) -> PublishResult:
        try:
            entry = self.environment.entries.find(content_id)
            status = "published" if entry.sys.get("publishedVersion") else "draft"
            return PublishResult(content_id=content_id, status=status)
        except ContentfulManagementError as e:
            logger.warning("Contentful entry %s not found: %s", content_id, e)
            return PublishResult(content_id=content_id, status="not_found")

    async def unpublish(self, content_id: str) -> PublishResult:
        try:
            entry = self.environment.entries.find(content_id)
            entry.unpublish()
            logger.info("ContentfulAdapter: unpublished %s", content_id)
            return PublishResult(content_id=content_id, status="unpublished")
        except ContentfulManagementError as e:
            logger.error("Contentful API error unpublishing %s: %s", content_id, e)
            raise ValueError(f"Contentful API error: {e}") from e
