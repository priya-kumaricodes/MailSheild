"""Evaluation endpoints for Evaluation Lab, multilingual model metrics,
confusion matrices, error drill-down, model comparisons, and dataset provenance.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.evaluation import EvaluationRun
from backend.app.models.user import User
from backend.app.services.auth_service import get_optional_current_user, require_admin_user
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/languages", response_model=list[dict[str, Any]])
def get_supported_languages(
    current_user: User | None = Depends(get_optional_current_user),
):
    """Retrieve supported languages, script types, and evaluation sample counts."""
    svc = EvaluationService()
    return svc.get_supported_languages()


@router.get("/metrics", response_model=dict[str, Any])
def get_evaluation_metrics(
    model_name: str = Query(default="linear_svm"),
    split: str = Query(default="test"),
    language: str = Query(default="all"),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Retrieve comprehensive performance metrics for a model on a dataset partition."""
    svc = EvaluationService()
    return svc.get_evaluation_metrics(model_name=model_name, split=split, language=language)


@router.get("/confusion-matrix", response_model=dict[str, Any])
def get_confusion_matrix(
    model_name: str = Query(default="linear_svm"),
    split: str = Query(default="test"),
    language: str = Query(default="all"),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Retrieve 2x2 confusion matrix (TN, FP, FN, TP) with normalized classification rates."""
    svc = EvaluationService()
    return svc.get_confusion_matrix(model_name=model_name, split=split, language=language)


@router.get("/errors", response_model=list[dict[str, Any]])
def get_drilldown_errors(
    model_name: str = Query(default="linear_svm"),
    error_type: str = Query(default="ALL"),  # "FP", "FN", "ALL"
    language: str = Query(default="all"),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Inspect misclassified examples (false positives and false negatives) with sanitized previews."""
    svc = EvaluationService()
    return svc.get_drilldown_errors(model_name=model_name, error_type=error_type, language=language, limit=limit)


@router.get("/compare", response_model=dict[str, Any])
def get_model_comparison(
    current_user: User | None = Depends(get_optional_current_user),
):
    """Retrieve side-by-side comparison of baseline English vs multilingual model variants."""
    svc = EvaluationService()
    return svc.get_model_comparison()


@router.get("/provenance", response_model=dict[str, Any])
def get_dataset_provenance(
    current_user: User | None = Depends(get_optional_current_user),
):
    """Retrieve dataset provenance summary, licensing terms, template group counts, and leakage verification."""
    svc = EvaluationService()
    return svc.get_dataset_provenance()


@router.get("/demo-samples", response_model=list[dict[str, Any]])
def get_demo_samples(
    language: str = Query(default="all"),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Fetch representative sample emails in each language for interactive testing in the playground."""
    svc = EvaluationService()
    return svc.get_demo_samples(language=language)


@router.post("/run", response_model=list[dict[str, Any]])
def run_evaluation_benchmark(
    admin_user: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """Execute evaluation benchmark across models using the independent test set. Restricted to administrators."""
    svc = EvaluationService()
    return svc.run_benchmark(db=db, user_id=admin_user.id)


@router.get("/runs/{run_id}", response_model=dict[str, Any])
def get_evaluation_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a historical evaluation benchmark run."""
    run = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation run not found.")

    return {
        "id": run.id,
        "timestamp": run.timestamp.isoformat(),
        "model_name": run.model_name,
        "dataset_name": run.dataset_name,
        "num_samples": run.num_samples,
        "accuracy": run.accuracy,
        "precision": run.precision,
        "recall": run.recall,
        "f1_score": run.f1_score,
        "false_positive_rate": run.false_positive_rate,
        "pr_auc": run.pr_auc,
        "roc_auc": run.roc_auc,
        "confusion_matrix": run.get_confusion_matrix(),
    }
