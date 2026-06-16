import datetime
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PerformanceRecord(BaseModel):
    timestamp: str
    content_id: str
    content_type: str
    metrics: Dict[str, Any]


class FeedbackResult(BaseModel):
    content_id: str
    score: float
    status: str = "feedback_received"


class ContentAnalyticsService:
    """In-memory store for content performance metrics and LLM feedback simulation."""

    def __init__(self):
        self._store: List[PerformanceRecord] = []

    def record_performance(
        self, content_id: str, content_type: str, metrics: Dict[str, Any]
    ) -> PerformanceRecord:
        record = PerformanceRecord(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            content_id=content_id,
            content_type=content_type,
            metrics=metrics,
        )
        self._store.append(record)
        logger.info("Recorded analytics for %s: %s", content_id, metrics)
        return record

    def get_performance_data(
        self,
        content_id: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> List[PerformanceRecord]:
        if content_id:
            return [r for r in self._store if r.content_id == content_id]
        if content_type:
            return [r for r in self._store if r.content_type == content_type]
        return list(self._store)

    def provide_feedback_to_llm(
        self,
        content_id: str,
        feedback_score: float,
        feedback_text: Optional[str] = None,
    ) -> FeedbackResult:
        logger.info(
            "Feedback for %s: score=%.2f text=%r",
            content_id, feedback_score, feedback_text,
        )
        return FeedbackResult(content_id=content_id, score=feedback_score)
