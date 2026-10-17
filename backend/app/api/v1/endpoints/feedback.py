"""Feedback endpoint for user label corrections and review.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.analysis import AnalysisRecord
from backend.app.models.feedback import UserFeedback
from backend.app.models.user import User
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse
from backend.app.services.auth_service import get_optional_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_in: FeedbackCreate,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Submit user feedback regarding the accuracy of a prediction."""
    analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == feedback_in.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced analysis not found.")

    user_id = current_user.id if current_user else None

    # Cross-user authorization check
    if user_id is not None and analysis.user_id is not None and analysis.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced analysis not found.")

    feedback = UserFeedback(
        analysis_id=feedback_in.analysis_id,
        user_id=user_id,
        suggested_label=feedback_in.suggested_label,
        comments=feedback_in.comments,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback
