"""AnalysisRecord SQLAlchemy model for persisting prediction history and explanations.
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), index=True, nullable=False)
    
    subject: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    email_hash: Mapped[str] = mapped_column(String(64), index=True, default="", nullable=False)
    
    prediction: Mapped[str] = mapped_column(String(32), nullable=False)  # "Spam" or "Legitimate"
    is_spam: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    score_type: Mapped[str] = mapped_column(String(32), default="probability", nullable=False)
    calibrated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(32), default="Medium", nullable=False)
    
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    threshold_used: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    feature_explanations_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    
    is_content_stored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="analyses")
    feedback = relationship("UserFeedback", back_populates="analysis", cascade="all, delete-orphan")

    def get_explanations(self) -> dict[str, Any]:
        try:
            return json.loads(self.feature_explanations_json)
        except Exception:
            return {}

    def set_explanations(self, data: dict[str, Any]) -> None:
        self.feature_explanations_json = json.dumps(data)
