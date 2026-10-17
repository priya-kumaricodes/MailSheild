"""Registration of Pydantic schemas.
"""

from backend.app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse
from backend.app.schemas.history import (
    BulkDeleteRequest,
    DeleteResponse,
    HistoryDetail,
    HistoryItem,
    HistoryResponse,
)
from backend.app.schemas.models import (
    ModelInfo,
    ModelListResponse,
    ThresholdSimulationPoint,
    ThresholdSimulationResponse,
)
from backend.app.schemas.predict import (
    ExplanationSchema,
    FeatureContributionSchema,
    PredictRequest,
    PredictResponse,
)

__all__ = [
    "BulkDeleteRequest",
    "DeleteResponse",
    "ExplanationSchema",
    "FeatureContributionSchema",
    "FeedbackCreate",
    "FeedbackResponse",
    "HistoryDetail",
    "HistoryItem",
    "HistoryResponse",
    "ModelInfo",
    "ModelListResponse",
    "PredictRequest",
    "PredictResponse",
    "ThresholdSimulationPoint",
    "ThresholdSimulationResponse",
    "Token",
    "UserCreate",
    "UserLogin",
    "UserResponse",
]
