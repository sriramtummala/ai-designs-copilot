import logging
import uuid

from pydantic import BaseModel

from interface import CMSAdapter, PublishResult

logger = logging.getLogger(__name__)


class MockCMSAdapter(CMSAdapter):
    """In-memory CMS adapter for testing and local development."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    async def publish(self, content: BaseModel) -> PublishResult:
        content_id = str(uuid.uuid4())
        content_type = type(content).__name__
        self._store[content_id] = {
            "type": content_type,
            "status": "published",
            "data": content.model_dump(),
        }
        logger.info("MockCMSAdapter: published %s as %s", content_type, content_id)
        return PublishResult(content_id=content_id, status="published")

    async def get_status(self, content_id: str) -> PublishResult:
        entry = self._store.get(content_id)
        if not entry:
            return PublishResult(content_id=content_id, status="not_found")
        return PublishResult(content_id=content_id, status=entry["status"])

    async def unpublish(self, content_id: str) -> PublishResult:
        if content_id not in self._store:
            return PublishResult(content_id=content_id, status="not_found")
        self._store[content_id]["status"] = "unpublished"
        logger.info("MockCMSAdapter: unpublished %s", content_id)
        return PublishResult(content_id=content_id, status="unpublished")
