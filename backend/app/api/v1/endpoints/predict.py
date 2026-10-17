"""Prediction endpoints for raw text and uploaded .txt/.eml files.
"""


from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.security import validate_file_upload
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.predict import PredictRequest, PredictResponse
from backend.app.services.auth_service import get_optional_current_user
from backend.app.services.prediction_service import PredictionService

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict_email(
    request: PredictRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Predict whether an email subject + body is Spam or Legitimate, with exact feature explanations."""
    svc = PredictionService.get_instance()
    user_id = current_user.id if current_user else None

    return svc.predict(
        subject=request.subject or "",
        body=request.body,
        sender=request.sender,
        model_name=request.model_name or "logistic_regression",
        threshold=request.threshold,
        store_content=request.store_content,
        user_id=user_id,
        db=db,
    )


@router.post("/predict/file", response_model=PredictResponse)
async def predict_email_file(
    file: UploadFile = File(...),
    model_name: str = Form(default="logistic_regression"),
    threshold: float | None = Form(default=None),
    store_content: bool = Form(default=False),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Safely process and classify uploaded .eml or .txt email file."""
    content = await file.read()
    validate_file_upload(file.filename or "uploaded.txt", len(content))

    svc = PredictionService.get_instance()
    user_id = current_user.id if current_user else None

    return svc.predict_file(
        content_bytes=content,
        filename=file.filename or "uploaded.txt",
        model_name=model_name,
        threshold=threshold,
        store_content=store_content,
        user_id=user_id,
        db=db,
    )
