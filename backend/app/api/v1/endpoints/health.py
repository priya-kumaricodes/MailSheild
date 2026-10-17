"""Health check endpoint verifying backend, database, and machine learning components.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.services.prediction_service import PredictionService

router = APIRouter()


@router.get("/health", response_model=dict[str, Any])
def health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    # Check database connectivity
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check ML model availability
    pred_svc = PredictionService.get_instance()
    ml_ok = pred_svc.is_loaded and len(pred_svc.models) > 0

    all_healthy = db_ok and ml_ok

    return {
        "status": "healthy" if all_healthy else "degraded",
        "backend": True,
        "database": db_ok,
        "model_loaded": ml_ok,
        "active_models": list(pred_svc.models.keys()) if ml_ok else [],
        "environment": settings.ENVIRONMENT,
        "mode": settings.MAILSHIELD_MODE,
        "version": settings.VERSION,
    }
