"""EvaluationRun model for recording model validation and test benchmarks.
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), index=True, nullable=False)
    
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(64), default="test", nullable=False)
    num_samples: Mapped[int] = mapped_column(Integer, nullable=False)
    
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float, nullable=False)
    recall: Mapped[float] = mapped_column(Float, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)
    false_positive_rate: Mapped[float] = mapped_column(Float, nullable=False)
    pr_auc: Mapped[float | None] = mapped_column(Float, nullable=True)
    roc_auc: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    confusion_matrix_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    triggered_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def get_confusion_matrix(self) -> dict[str, Any]:
        try:
            return json.loads(self.confusion_matrix_json)
        except Exception:
            return {}

    def set_confusion_matrix(self, data: dict[str, Any]) -> None:
        self.confusion_matrix_json = json.dumps(data)
