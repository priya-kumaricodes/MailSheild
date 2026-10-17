"""Evaluation metrics computation, probability calibration assessment, and dynamic threshold simulation on genuine data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class ConfusionMatrixData:
    tn: int
    fp: int
    fn: int
    tp: int

    def to_matrix(self) -> list[list[int]]:
        return [[self.tn, self.fp], [self.fn, self.tp]]


@dataclass
class ModelEvaluationReport:
    """Rigorous evaluation metrics calculated from genuine test or validation predictions."""

    model_name: str
    dataset_name: str
    num_samples: int
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    pr_auc: float | None
    roc_auc: float | None
    brier_score: float | None
    confusion_matrix: ConfusionMatrixData
    score_type: str
    calibrated: bool
    calibration_status: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["confusion_matrix_grid"] = self.confusion_matrix.to_matrix()
        return d


def compute_metrics_at_threshold(
    y_true: list[int] | np.ndarray,
    y_scores: list[float] | np.ndarray,
    threshold: float = 0.5,
    model_name: str = "model",
    dataset_name: str = "validation",
    score_type: str = "probability",
    calibrated: bool = True,
) -> ModelEvaluationReport:
    """Calculate exact classification and calibration metrics at a given decision threshold."""
    y_t = np.array(y_true, dtype=int)
    y_s = np.array(y_scores, dtype=float)

    # Class 1 is Spam, Class 0 is Legitimate
    y_pred = (y_s >= threshold).astype(int)

    cm = confusion_matrix(y_t, y_pred, labels=[0, 1])
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    acc = float(accuracy_score(y_t, y_pred))
    prec = float(precision_score(y_t, y_pred, zero_division=0.0))
    rec = float(recall_score(y_t, y_pred, zero_division=0.0))
    f1 = float(f1_score(y_t, y_pred, zero_division=0.0))

    denom_fpr = fp + tn
    fpr = float(fp / denom_fpr) if denom_fpr > 0 else 0.0

    pr_auc: float | None = None
    roc_auc: float | None = None
    brier_score: float | None = None
    cal_status: str = "uncalibrated"

    # Evaluate Brier score loss if score represents probabilities
    if score_type == "probability" and np.all(y_s >= 0.0) and np.all(y_s <= 1.0):
        try:
            brier_score = float(brier_score_loss(y_t, y_s))
            if calibrated:
                cal_status = "evaluated_well_calibrated" if brier_score <= 0.15 else "evaluated_moderate_calibration"
            else:
                cal_status = "uncalibrated_log_likelihood"
        except Exception:
            pass
    elif score_type == "decision_function":
        cal_status = "raw_decision_margin"

    # Calculate curve AUCs if scores are continuous and both classes are present
    if len(np.unique(y_t)) > 1:
        try:
            pr_auc = float(average_precision_score(y_t, y_s))
            roc_auc = float(roc_auc_score(y_t, y_s))
        except Exception:
            pass

    return ModelEvaluationReport(
        model_name=model_name,
        dataset_name=dataset_name,
        num_samples=len(y_t),
        threshold=round(threshold, 4),
        accuracy=round(acc, 4),
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1_score=round(f1, 4),
        false_positive_rate=round(fpr, 4),
        pr_auc=round(pr_auc, 4) if pr_auc is not None else None,
        roc_auc=round(roc_auc, 4) if roc_auc is not None else None,
        brier_score=round(brier_score, 4) if brier_score is not None else None,
        confusion_matrix=ConfusionMatrixData(tn=tn, fp=fp, fn=fn, tp=tp),
        score_type=score_type,
        calibrated=calibrated,
        calibration_status=cal_status,
    )


def sweep_thresholds(
    y_true: list[int] | np.ndarray,
    y_scores: list[float] | np.ndarray,
    thresholds: list[float] | None = None,
    model_name: str = "model",
    dataset_name: str = "validation",
    score_type: str = "probability",
    calibrated: bool = True,
) -> list[dict[str, Any]]:
    """Sweep thresholds across predictions to populate interactive threshold simulators."""
    if thresholds is None:
        thresholds = [round(t, 2) for t in np.linspace(0.05, 0.95, 19)]

    results = []
    for tau in thresholds:
        rep = compute_metrics_at_threshold(
            y_true=y_true,
            y_scores=y_scores,
            threshold=tau,
            model_name=model_name,
            dataset_name=dataset_name,
            score_type=score_type,
            calibrated=calibrated,
        )
        results.append(rep.to_dict())

    return results


def select_cost_sensitive_threshold(
    sweeps: list[dict[str, Any]],
    fp_cost: float = 5.0,
    fn_cost: float = 1.0,
    max_fpr: float = 0.05,
    fallback_threshold: float = 0.5,
) -> tuple[float, dict[str, Any]]:
    """Select the optimal operating threshold using cost-sensitive utility on validation data.

    Utility(tau) = TP(tau) - fp_cost * FP(tau) - fn_cost * FN(tau)
    Subject to constraint: FPR(tau) <= max_fpr

    If the constraint is unmet across all evaluated thresholds, it selects the threshold
    maximizing unconstrained utility and explicitly records that the constraint was unmet.
    """
    eligible = [s for s in sweeps if s.get("false_positive_rate", 1.0) <= max_fpr]
    constraint_met = len(eligible) > 0
    candidate_pool = eligible if constraint_met else sweeps

    best_utility = -float("inf")
    best_tau = fallback_threshold
    best_entry = None

    for item in candidate_pool:
        cm = item.get("confusion_matrix")
        if isinstance(cm, dict):
            tp = cm.get("tp", 0)
            fp = cm.get("fp", 0)
            fn = cm.get("fn", 0)
        elif hasattr(cm, "tp"):
            tp = cm.tp
            fp = cm.fp
            fn = cm.fn
        else:
            grid = item.get("confusion_matrix_grid", [[0, 0], [0, 0]])
            fp = grid[0][1]
            fn = grid[1][0]
            tp = grid[1][1]

        utility = float(tp - (fp_cost * fp) - (fn_cost * fn))
        tau = float(item["threshold"])

        if utility > best_utility:
            best_utility = utility
            best_tau = tau
            best_entry = item
        elif abs(utility - best_utility) < 1e-6:
            # Tie-break: prefer threshold closer to fallback_threshold (0.5), or higher if equidistant
            curr_dist = abs(tau - fallback_threshold)
            best_dist = abs(best_tau - fallback_threshold)
            if curr_dist < best_dist or (abs(curr_dist - best_dist) < 1e-6 and tau > best_tau):
                best_utility = utility
                best_tau = tau
                best_entry = item

    meta = {
        "fp_cost": fp_cost,
        "fn_cost": fn_cost,
        "max_fpr": max_fpr,
        "constraint_met": constraint_met,
        "selected_threshold": best_tau,
        "utility": best_utility if best_entry is not None else None,
        "validation_fpr": best_entry.get("false_positive_rate") if best_entry is not None else None,
        "validation_f1": best_entry.get("f1_score") if best_entry is not None else None,
        "warning": None if constraint_met else f"Validation FPR constraint (<= {max_fpr}) was unmet. Best unconstrained threshold selected.",
    }
    return best_tau, meta
