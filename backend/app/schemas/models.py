"""Pydantic schemas for Model Lab metrics, comparisons, and threshold simulations.
"""

from typing import Any

from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    display_name: str
    version: str
    score_type: str
    calibrated: bool
    optimal_threshold: float
    test_metrics: dict[str, Any]
    validation_metrics: dict[str, Any]


class ModelListResponse(BaseModel):
    models: list[ModelInfo]
    active_model: str
    vocab_size: int
    dataset_info: dict[str, Any]


class ThresholdSimulationPoint(BaseModel):
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    confusion_matrix: list[list[int]]
    brier_score: float | None = None
    calibration_status: str | None = None


class ThresholdSimulationResponse(BaseModel):
    model_name: str
    current_metrics: ThresholdSimulationPoint
    sweep_curve: list[ThresholdSimulationPoint]
