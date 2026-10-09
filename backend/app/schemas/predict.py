"""Pydantic schemas for prediction requests, responses, feature explainability,
language identification, and phishing risk analysis.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    subject: str | None = Field(default="", max_length=1000)
    body: str = Field(..., min_length=1, max_length=500000)
    sender: str | None = Field(default=None, max_length=500)
    model_name: str | None = Field(default="logistic_regression")
    threshold: float | None = Field(default=None, ge=0.01, le=0.99)
    store_content: bool = Field(default=False)


class FeatureContributionSchema(BaseModel):
    token: str
    weight: float
    tfidf_value: float
    contribution: float
    direction: str  # "Spam" or "Legitimate"
    relative_impact: float
    description: str


class ExplanationSchema(BaseModel):
    model_name: str
    intercept: float
    net_decision_score: float
    calibrated_probability: float | None
    top_spam_features: list[FeatureContributionSchema]
    top_legitimate_features: list[FeatureContributionSchema]
    all_contributions: list[FeatureContributionSchema]
    attribution_notes: str


class LanguageAnalysisSchema(BaseModel):
    detected_language: str = "en"
    confidence: float | None = None
    detection_method: str = "unknown"
    primary_script: str = "Latin"
    is_mixed: bool = False
    scripts_detected: dict[str, float] = Field(default_factory=dict)
    warning: str | None = None


class PhishingAnalysisSchema(BaseModel):
    risk_score: float = 0.0
    risk_level: str = "low"  # "low", "medium", "high", "critical"
    indicators_triggered: list[dict[str, Any]] = Field(default_factory=list)
    suspicious_urls: list[str] = Field(default_factory=list)
    has_credential_harvesting: bool = False
    has_urgency_threat: bool = False
    has_spoofed_brand: bool = False
    explanation: str = ""


class PredictResponse(BaseModel):
    id: str
    prediction: str  # "Spam" or "Legitimate"
    is_spam: bool
    score: float
    score_type: str  # "probability" or "decision_function"
    calibrated: bool
    raw_decision_score: float | None = None
    confidence_level: str
    model_name: str
    model_version: str
    threshold_used: float
    processing_time_ms: float
    explanations: ExplanationSchema
    created_at: datetime
    # MailShield 2.0 Multilingual & Phishing Additions
    language_analysis: LanguageAnalysisSchema = Field(default_factory=LanguageAnalysisSchema)
    phishing_analysis: PhishingAnalysisSchema = Field(default_factory=PhishingAnalysisSchema)
