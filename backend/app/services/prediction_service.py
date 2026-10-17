"""Prediction service integrating ML inference, feature explainability,
multilingual language identification, phishing risk evaluation, and database persistence.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from mailshield_ml.dataset import compute_content_hash, parse_rfc822_email
from mailshield_ml.explainability import ExplainabilityEngine
from mailshield_ml.features import FeaturePipeline
from mailshield_ml.language import LanguageIdentifier
from mailshield_ml.models import (
    BaseModelWrapper,
    LinearSVCWrapper,
    LogisticRegressionWrapper,
    MultinomialNBWrapper,
)
from mailshield_ml.multilingual_features import MultilingualFeaturePipeline
from mailshield_ml.phishing_risk import PhishingRiskEngine
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.analysis import AnalysisRecord
from backend.app.schemas.predict import (
    ExplanationSchema,
    FeatureContributionSchema,
    LanguageAnalysisSchema,
    PhishingAnalysisSchema,
    PredictResponse,
)


class PredictionService:
    _instance: PredictionService | None = None

    def __init__(self, artifacts_dir: str | None = None):
        self.artifacts_dir = Path(artifacts_dir or settings.ARTIFACTS_DIR)
        self.vectorizer: FeaturePipeline | None = None
        self.multilingual_vectorizer: MultilingualFeaturePipeline | None = None
        self.models: dict[str, BaseModelWrapper] = {}
        self.explainer: ExplainabilityEngine | None = None
        self.multilingual_explainer: ExplainabilityEngine | None = None
        self.metadata: dict[str, Any] = {}
        self.language_identifier = LanguageIdentifier()
        self.phishing_engine = PhishingRiskEngine()
        self.is_loaded = False
        self.load_artifacts()

    @classmethod
    def get_instance(cls) -> PredictionService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_artifacts(self) -> None:
        """Load fitted vectorizer, models, and metadata into memory."""
        vec_path = self.artifacts_dir / "tfidf_vectorizer.joblib"
        multi_vec_path = self.artifacts_dir / "multilingual_tfidf_vectorizer.joblib"
        meta_path = self.artifacts_dir / "metadata.json"

        if not vec_path.exists() and not multi_vec_path.exists():
            print(f"Warning: Model artifacts not found at {self.artifacts_dir}. Predictions will be unavailable until trained.")
            return

        try:
            # 1. Load English Baseline pipeline if available
            if vec_path.exists():
                self.vectorizer = FeaturePipeline.load(str(vec_path))
                self.explainer = ExplainabilityEngine(self.vectorizer)

                lr_path = self.artifacts_dir / "model_logistic_regression.joblib"
                nb_path = self.artifacts_dir / "model_naive_bayes.joblib"
                svm_path = self.artifacts_dir / "model_linear_svm.joblib"

                if lr_path.exists():
                    self.models["logistic_regression"] = LogisticRegressionWrapper.load(str(lr_path))
                if nb_path.exists():
                    self.models["naive_bayes"] = MultinomialNBWrapper.load(str(nb_path))
                if svm_path.exists():
                    self.models["linear_svm"] = LinearSVCWrapper.load(str(svm_path))

            # 2. Load Multilingual pipeline if available
            if multi_vec_path.exists():
                self.multilingual_vectorizer = MultilingualFeaturePipeline.load(str(multi_vec_path))
                self.multilingual_explainer = ExplainabilityEngine(self.multilingual_vectorizer)

                m_lr_path = self.artifacts_dir / "multilingual_model_logistic_regression.joblib"
                m_nb_path = self.artifacts_dir / "multilingual_model_naive_bayes.joblib"
                m_svm_path = self.artifacts_dir / "multilingual_model_linear_svm.joblib"

                if m_lr_path.exists():
                    self.models["multilingual_logistic_regression"] = LogisticRegressionWrapper.load(str(m_lr_path))
                if m_nb_path.exists():
                    self.models["multilingual_naive_bayes"] = MultinomialNBWrapper.load(str(m_nb_path))
                if m_svm_path.exists():
                    self.models["multilingual_linear_svm"] = LinearSVCWrapper.load(str(m_svm_path))

            if meta_path.exists():
                with open(meta_path, encoding="utf-8") as f:
                    self.metadata = json.load(f)

            self.is_loaded = True
            print(f"PredictionService loaded {len(self.models)} models successfully.")
        except Exception as e:
            print(f"Error loading ML artifacts: {e}")
            self.is_loaded = False

    def get_model(self, model_name: str) -> BaseModelWrapper:
        if not self.is_loaded or not self.models:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Machine learning models are not initialized or still training.",
            )
        name = model_name.lower().strip()
        if name not in self.models:
            available = list(self.models.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown model '{model_name}'. Available models: {', '.join(available)}",
            )
        return self.models[name]

    @staticmethod
    def calculate_confidence_level(score: float, score_type: str) -> str:
        """Derive meaningful confidence tier based on score type."""
        if score_type == "probability":
            dist = abs(score - 0.5)
            if dist >= 0.35:
                return "High"
            elif dist >= 0.15:
                return "Medium"
            return "Low"
        else:
            abs_dist = abs(score)
            if abs_dist >= 1.0:
                return "High"
            elif abs_dist >= 0.4:
                return "Medium"
            return "Low"

    def predict(
        self,
        subject: str,
        body: str,
        sender: str | None = None,
        model_name: str = "logistic_regression",
        threshold: float | None = None,
        store_content: bool = False,
        user_id: str | None = None,
        db: Session | None = None,
    ) -> PredictResponse:
        start_time = time.perf_counter()

        if not body or not body.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email body cannot be empty.",
            )

        # Format input representation
        norm_sub = subject.strip() if subject else ""
        norm_body = body.strip()
        combined_text = f"Subject: {norm_sub}\n\n{norm_body}" if norm_sub else norm_body

        content_hash = compute_content_hash(norm_sub, norm_body)

        # 1. Language Identification
        lang_res = self.language_identifier.identify_language(combined_text)

        # 2. Phishing Risk Evaluation
        phishing_res = self.phishing_engine.evaluate_phishing_risk(
            text=norm_body,
            sender=sender,
            subject=norm_sub,
        )

        # 3. Model and Vectorizer Selection
        is_multilingual_model = model_name.startswith("multilingual_")

        # If a standard model was requested but text is non-English Indic or Hinglish,
        # route to the multilingual version if available
        effective_model_name = model_name
        if not is_multilingual_model and lang_res.language in ("hi", "ta", "te", "kn", "hinglish"):
            candidate = f"multilingual_{model_name}"
            if candidate in self.models:
                effective_model_name = candidate
                is_multilingual_model = True

        model = self.get_model(effective_model_name)

        if is_multilingual_model and self.multilingual_vectorizer is not None:
            active_vectorizer = self.multilingual_vectorizer
            active_explainer = self.multilingual_explainer
        else:
            active_vectorizer = self.vectorizer or self.multilingual_vectorizer
            active_explainer = self.explainer or self.multilingual_explainer

        assert active_vectorizer is not None
        assert active_explainer is not None

        # Feature transformation
        X_vec = active_vectorizer.transform([combined_text])

        # Run inference
        pred = model.predict_single(X_vec, threshold=threshold)

        # Compute feature explainability
        exp = active_explainer.explain_prediction(model, X_vec, top_k=8)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        confidence = self.calculate_confidence_level(pred.score, pred.score_type)
        now = datetime.now(UTC)

        # Format explanation schema
        top_spam = [
            FeatureContributionSchema(
                token=fc.token,
                weight=round(fc.weight, 4),
                tfidf_value=round(fc.tfidf_value, 4),
                contribution=round(fc.contribution, 4),
                direction=fc.direction,
                relative_impact=fc.relative_impact,
                description=fc.description,
            )
            for fc in exp.top_spam_features
        ]
        top_legit = [
            FeatureContributionSchema(
                token=fc.token,
                weight=round(fc.weight, 4),
                tfidf_value=round(fc.tfidf_value, 4),
                contribution=round(fc.contribution, 4),
                direction=fc.direction,
                relative_impact=fc.relative_impact,
                description=fc.description,
            )
            for fc in exp.top_legitimate_features
        ]
        all_contribs = [
            FeatureContributionSchema(
                token=fc.token,
                weight=round(fc.weight, 4),
                tfidf_value=round(fc.tfidf_value, 4),
                contribution=round(fc.contribution, 4),
                direction=fc.direction,
                relative_impact=fc.relative_impact,
                description=fc.description,
            )
            for fc in exp.all_contributions
        ]

        exp_schema = ExplanationSchema(
            model_name=exp.model_name,
            intercept=exp.intercept,
            net_decision_score=exp.net_decision_score,
            calibrated_probability=exp.calibrated_probability,
            top_spam_features=top_spam,
            top_legitimate_features=top_legit,
            all_contributions=all_contribs,
            attribution_notes=exp.attribution_notes,
        )

        lang_schema = LanguageAnalysisSchema(
            detected_language=lang_res.language,
            confidence=lang_res.confidence,
            detection_method=lang_res.detection_method,
            primary_script=lang_res.primary_script,
            is_mixed=lang_res.is_mixed,
            scripts_detected=lang_res.scripts_detected,
            warning=lang_res.warning,
        )

        phishing_schema = PhishingAnalysisSchema(
            risk_score=phishing_res.risk_score,
            risk_level=phishing_res.risk_level,
            indicators_triggered=phishing_res.indicators_triggered,
            suspicious_urls=phishing_res.suspicious_urls,
            has_credential_harvesting=phishing_res.has_credential_harvesting,
            has_urgency_threat=phishing_res.has_urgency_threat,
            has_spoofed_brand=phishing_res.has_spoofed_brand,
            explanation=phishing_res.explanation,
        )

        # Save to database if session is provided
        analysis_id = ""
        if db is not None:
            record = AnalysisRecord(
                user_id=user_id,
                timestamp=now,
                subject=norm_sub[:500],
                email_hash=content_hash,
                prediction=pred.predicted_label,
                is_spam=pred.is_spam,
                score=round(pred.score, 4),
                score_type=pred.score_type,
                calibrated=pred.calibrated,
                confidence_level=confidence,
                model_name=model.name,
                model_version=model.version,
                threshold_used=round(pred.threshold_applied, 4),
                processing_time_ms=elapsed_ms,
                is_content_stored=store_content,
                email_body=norm_body if store_content else None,
            )
            db_exp = exp_schema.model_dump()
            db_exp["language_analysis"] = lang_schema.model_dump()
            db_exp["phishing_analysis"] = phishing_schema.model_dump()
            record.set_explanations(db_exp)
            db.add(record)
            db.commit()
            db.refresh(record)
            analysis_id = record.id

        return PredictResponse(
            id=analysis_id or "ephemeral",
            prediction=pred.predicted_label,
            is_spam=pred.is_spam,
            score=round(pred.score, 4),
            score_type=pred.score_type,
            calibrated=pred.calibrated,
            raw_decision_score=round(pred.raw_decision_score, 4) if pred.raw_decision_score is not None else None,
            confidence_level=confidence,
            model_name=model.name,
            model_version=model.version,
            threshold_used=round(pred.threshold_applied, 4),
            processing_time_ms=elapsed_ms,
            explanations=exp_schema,
            created_at=now,
            language_analysis=lang_schema,
            phishing_analysis=phishing_schema,
        )

    def predict_file(
        self,
        content_bytes: bytes,
        filename: str,
        model_name: str = "logistic_regression",
        threshold: float | None = None,
        store_content: bool = False,
        user_id: str | None = None,
        db: Session | None = None,
    ) -> PredictResponse:
        """Parse uploaded .txt or .eml file and execute prediction."""
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        sender = None

        if ext == ".eml":
            parsed = parse_rfc822_email(content_bytes)
            subject = parsed.subject
            body = parsed.body
            sender = parsed.headers.get("from")
        else:
            try:
                text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = content_bytes.decode("latin-1", errors="replace")

            lines = text.strip().splitlines()
            if lines and lines[0].lower().startswith("subject:"):
                subject = lines[0][8:].strip()
                body = "\n".join(lines[1:]).strip()
            else:
                subject = filename
                body = text

        return self.predict(
            subject=subject,
            body=body,
            sender=sender,
            model_name=model_name,
            threshold=threshold,
            store_content=store_content,
            user_id=user_id,
            db=db,
        )
