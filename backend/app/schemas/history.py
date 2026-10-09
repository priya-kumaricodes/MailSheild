"""Pydantic schemas for analysis history, filtering, pagination, and bulk deletion.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.predict import ExplanationSchema


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    subject: str
    prediction: str
    is_spam: bool
    score: float
    score_type: str
    calibrated: bool
    confidence_level: str
    model_name: str
    model_version: str
    threshold_used: float
    processing_time_ms: float
    is_content_stored: bool
    has_feedback: bool = False


class HistoryDetail(HistoryItem):
    email_hash: str
    email_body: str | None = None
    explanations: ExplanationSchema | None = None


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class BulkDeleteRequest(BaseModel):
    ids: list[str] = Field(..., min_length=1)


class DeleteResponse(BaseModel):
    deleted_count: int
    message: str
