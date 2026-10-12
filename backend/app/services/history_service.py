"""History service for querying, paginating, filtering, deleting, and exporting analyses.
"""

from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from backend.app.core.security import sanitize_csv_value
from backend.app.models.analysis import AnalysisRecord
from backend.app.schemas.history import HistoryDetail, HistoryItem, HistoryResponse
from backend.app.schemas.predict import ExplanationSchema


class HistoryService:
    @staticmethod
    def get_history(
        db: Session,
        user_id: str | None = None,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        label_filter: str | None = None,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> HistoryResponse:
        query = db.query(AnalysisRecord)

        # Scoped strictly by user (or anonymous NULL)
        query = query.filter(AnalysisRecord.user_id == user_id)

        # Search filter
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(AnalysisRecord.subject.ilike(term))

        # Label filter
        if label_filter and label_filter.strip() in ("Spam", "Legitimate"):
            query = query.filter(AnalysisRecord.prediction == label_filter.strip())

        total = query.count()

        # Sorting
        order_col = AnalysisRecord.timestamp
        if sort_by == "score":
            order_col = AnalysisRecord.score
        elif sort_by == "subject":
            order_col = AnalysisRecord.subject

        query = query.order_by(desc(order_col) if sort_order == "desc" else asc(order_col))

        # Pagination
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()

        items = []
        for r in records:
            has_fb = len(r.feedback) > 0 if hasattr(r, "feedback") else False
            items.append(
                HistoryItem(
                    id=r.id,
                    timestamp=r.timestamp,
                    subject=r.subject or "(No Subject)",
                    prediction=r.prediction,
                    is_spam=r.is_spam,
                    score=r.score,
                    score_type=r.score_type,
                    calibrated=r.calibrated,
                    confidence_level=r.confidence_level,
                    model_name=r.model_name,
                    model_version=r.model_version,
                    threshold_used=r.threshold_used,
                    processing_time_ms=r.processing_time_ms,
                    is_content_stored=r.is_content_stored,
                    has_feedback=has_fb,
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return HistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def get_analysis_detail(db: Session, analysis_id: str, user_id: str | None = None) -> HistoryDetail:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

        # Strict user ownership check (User A cannot access User B or anonymous; anonymous cannot access user)
        if record.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

        exp_data = record.get_explanations()
        exp_schema = None
        if exp_data:
            try:
                exp_schema = ExplanationSchema(**exp_data)
            except Exception:
                pass

        has_fb = len(record.feedback) > 0 if hasattr(record, "feedback") else False

        return HistoryDetail(
            id=record.id,
            timestamp=record.timestamp,
            subject=record.subject or "(No Subject)",
            prediction=record.prediction,
            is_spam=record.is_spam,
            score=record.score,
            score_type=record.score_type,
            calibrated=record.calibrated,
            confidence_level=record.confidence_level,
            model_name=record.model_name,
            model_version=record.model_version,
            threshold_used=record.threshold_used,
            processing_time_ms=record.processing_time_ms,
            is_content_stored=record.is_content_stored,
            has_feedback=has_fb,
            email_hash=record.email_hash,
            email_body=record.email_body if record.is_content_stored else None,
            explanations=exp_schema,
        )

    @staticmethod
    def delete_analysis(db: Session, analysis_id: str, user_id: str | None = None) -> bool:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

        # Strict user ownership check
        if record.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

        db.delete(record)
        db.commit()
        return True

    @staticmethod
    def bulk_delete(db: Session, ids: list[str], user_id: str | None = None) -> int:
        query = db.query(AnalysisRecord).filter(AnalysisRecord.id.in_(ids), AnalysisRecord.user_id == user_id)

        records = query.all()
        count = len(records)
        for r in records:
            db.delete(r)
        db.commit()
        return count

    @staticmethod
    def export_csv(db: Session, user_id: str | None = None) -> str:
        """Export history with CSV formula injection defense."""
        query = db.query(AnalysisRecord).filter(AnalysisRecord.user_id == user_id)
        records = query.order_by(desc(AnalysisRecord.timestamp)).all()

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            "ID",
            "Timestamp",
            "Subject",
            "Prediction",
            "Score",
            "ScoreType",
            "Calibrated",
            "ConfidenceLevel",
            "ModelName",
            "ThresholdUsed",
            "ProcessingTimeMs",
        ])

        for r in records:
            writer.writerow([
                sanitize_csv_value(r.id),
                sanitize_csv_value(r.timestamp.isoformat()),
                sanitize_csv_value(r.subject),
                sanitize_csv_value(r.prediction),
                sanitize_csv_value(r.score),
                sanitize_csv_value(r.score_type),
                sanitize_csv_value(r.calibrated),
                sanitize_csv_value(r.confidence_level),
                sanitize_csv_value(r.model_name),
                sanitize_csv_value(r.threshold_used),
                sanitize_csv_value(r.processing_time_ms),
            ])

        return output.getvalue()

    @staticmethod
    def export_json(db: Session, user_id: str | None = None) -> list[dict[str, Any]]:
        query = db.query(AnalysisRecord).filter(AnalysisRecord.user_id == user_id)
        records = query.order_by(desc(AnalysisRecord.timestamp)).all()

        data = []
        for r in records:
            data.append({
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "subject": r.subject,
                "prediction": r.prediction,
                "is_spam": r.is_spam,
                "score": r.score,
                "score_type": r.score_type,
                "calibrated": r.calibrated,
                "confidence_level": r.confidence_level,
                "model_name": r.model_name,
                "threshold_used": r.threshold_used,
                "processing_time_ms": r.processing_time_ms,
                "explanations": r.get_explanations(),
            })
        return data
