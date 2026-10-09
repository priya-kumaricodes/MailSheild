"""Pydantic schemas for user feedback.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    analysis_id: str
    suggested_label: str = Field(..., pattern="^(Spam|Legitimate)$")
    comments: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    suggested_label: str
    comments: str | None
    created_at: datetime
