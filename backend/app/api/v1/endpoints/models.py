"""Model Lab endpoints for model comparison, evaluation metrics, and validation threshold simulation.
"""

from typing import Any

from fastapi import APIRouter, Query

from backend.app.core.config import settings
from backend.app.schemas.models import ModelListResponse, ThresholdSimulationResponse
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter(tags=["Models & Evaluation"])


@router.get("/models", response_model=ModelListResponse)
def get_models():
    """Retrieve comparative metrics, versions, and hyperparameter overviews for all models."""
    svc = EvaluationService()
    return svc.get_models_overview()


@router.get("/models/threshold-metrics", response_model=ThresholdSimulationResponse)
def simulate_threshold(
    model: str = Query(default="logistic_regression"),
    threshold: float = Query(default=0.5, ge=0.01, le=0.99),
):
    """Calculate exact classification metrics on genuine validation set predictions at the chosen threshold."""
    svc = EvaluationService()
    return svc.simulate_threshold(model_name=model, threshold=threshold)


@router.get("/metrics", response_model=dict[str, Any])
def get_active_model_metrics():
    """Retrieve latest test evaluation metrics for the active model."""
    svc = EvaluationService()
    overview = svc.get_models_overview()
    for m in overview.models:
        if m.name == settings.DEFAULT_MODEL:
            return {
                "model_name": m.name,
                "display_name": m.display_name,
                "version": m.version,
                "score_type": m.score_type,
                "calibrated": m.calibrated,
                "optimal_threshold": m.optimal_threshold,
                "metrics": m.test_metrics,
            }
    return {}
