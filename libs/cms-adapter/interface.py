from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class PublishResult(BaseModel):
    content_id: str
    status: str
    url: Optional[str] = None


class CMSAdapter(ABC):
    """Abstract interface for CMS publishing backends."""

    @abstractmethod
    async def publish(self, content: BaseModel) -> PublishResult:
        ...

    @abstractmethod
    async def get_status(self, content_id: str) -> PublishResult:
        ...

    @abstractmethod
    async def unpublish(self, content_id: str) -> PublishResult:
        ...
