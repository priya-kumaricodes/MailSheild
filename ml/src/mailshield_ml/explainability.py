"""Feature attribution and explainability engine for linear models and naive bayes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from scipy.sparse import spmatrix

from mailshield_ml.features import FeaturePipeline
from mailshield_ml.models import (
    BaseModelWrapper,
    LinearSVCWrapper,
    LogisticRegressionWrapper,
    MultinomialNBWrapper,
)


@dataclass
class FeatureContribution:
    """Detailed attribution of a specific token's influence on the classification decision."""

    token: str
    weight: float
    tfidf_value: float
    contribution: float  # Additive contribution to log-odds or decision margin
    direction: str  # "Spam" (pushes toward spam) or "Legitimate" (pushes toward ham)
    relative_impact: float  # Percentage of directional attribution mass [0, 100]
    description: str


@dataclass
class ExplanationResult:
    """Complete mathematical explanation of a model's prediction."""

    model_name: str
    intercept: float
    net_decision_score: float
    calibrated_probability: float | None
    top_spam_features: list[FeatureContribution]
    top_legitimate_features: list[FeatureContribution]
    all_contributions: list[FeatureContribution]
    attribution_notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExplainabilityEngine:
    """Computes exact, un-fabricated feature contributions based on model parameters."""

    def __init__(self, feature_pipeline: FeaturePipeline):
        self.feature_pipeline = feature_pipeline
        self.feature_names = self.feature_pipeline.get_feature_names()

    def explain_prediction(
        self,
        model_wrapper: BaseModelWrapper,
        X_single: spmatrix,
        top_k: int = 10,
    ) -> ExplanationResult:
        """Compute exact feature contributions for a single document sparse TF-IDF vector."""
        if not model_wrapper.is_trained:
            raise RuntimeError("Model must be trained before computing explanations.")

        # Extract active token indices and their TF-IDF values
        # X_single is a 1 x V sparse matrix
        coo = X_single.tocoo()
        active_indices = coo.col
        active_tfidf = coo.data

        if len(active_indices) == 0:
            # Document has no matching vocabulary words
            return ExplanationResult(
                model_name=model_wrapper.name,
                intercept=0.0,
                net_decision_score=0.0,
                calibrated_probability=0.5,
                top_spam_features=[],
                top_legitimate_features=[],
                all_contributions=[],
                attribution_notes="No active vocabulary tokens found in the email content.",
            )

        weights: np.ndarray
        intercept: float = 0.0

        if isinstance(model_wrapper, LogisticRegressionWrapper):
            weights = model_wrapper.model.coef_[0]
            intercept = float(model_wrapper.model.intercept_[0])
            score_desc = "log-odds"
        elif isinstance(model_wrapper, LinearSVCWrapper):
            weights = model_wrapper.model.coef_[0]
            intercept = float(model_wrapper.model.intercept_[0])
            score_desc = "decision margin distance"
        elif isinstance(model_wrapper, MultinomialNBWrapper):
            # For MultinomialNB, class-specific feature evidence via log-likelihood ratio:
            # log P(w|Spam) - log P(w|Ham)
            log_prob_spam = model_wrapper.model.feature_log_prob_[1]
            log_prob_ham = model_wrapper.model.feature_log_prob_[0]
            weights = log_prob_spam - log_prob_ham
            # Intercept is class log-prior odds: log P(Spam) - log P(Ham)
            intercept = float(model_wrapper.model.class_log_prior_[1] - model_wrapper.model.class_log_prior_[0])
            score_desc = "log-posterior odds (log-likelihood ratio evidence)"
        else:
            raise NotImplementedError(f"Explainability not implemented for {type(model_wrapper)}")

        contributions: list[FeatureContribution] = []
        spam_mass = 0.0
        legit_mass = 0.0

        raw_items = []
        for idx, tfidf_val in zip(active_indices, active_tfidf):
            token = self.feature_names[idx]
            w = float(weights[idx])
            contrib = float(w * tfidf_val)
            raw_items.append((token, w, float(tfidf_val), contrib))
            if contrib > 0:
                spam_mass += contrib
            elif contrib < 0:
                legit_mass += abs(contrib)

        # Sort all items by absolute contribution descending
        raw_items.sort(key=lambda x: abs(x[3]), reverse=True)

        spam_features: list[FeatureContribution] = []
        legit_features: list[FeatureContribution] = []

        is_nb = isinstance(model_wrapper, MultinomialNBWrapper)

        for token, w, tfidf_val, contrib in raw_items:
            if contrib > 0:
                rel_impact = (contrib / spam_mass * 100.0) if spam_mass > 0 else 0.0
                desc = (
                    f"'{token}' provides log-likelihood evidence toward spam (log-ratio: {w:+.3f}, tfidf: {tfidf_val:.3f}, log-evidence: {contrib:+.3f})"
                    if is_nb
                    else f"'{token}' has positive association with spam patterns (weight: {w:+.3f}, tfidf: {tfidf_val:.3f}, contribution: {contrib:+.3f})"
                )
                fc = FeatureContribution(
                    token=token,
                    weight=w,
                    tfidf_value=tfidf_val,
                    contribution=contrib,
                    direction="Spam",
                    relative_impact=round(rel_impact, 2),
                    description=desc,
                )
                spam_features.append(fc)
                contributions.append(fc)
            elif contrib < 0:
                rel_impact = (abs(contrib) / legit_mass * 100.0) if legit_mass > 0 else 0.0
                desc = (
                    f"'{token}' provides log-likelihood evidence toward legitimate email (log-ratio: {w:+.3f}, tfidf: {tfidf_val:.3f}, log-evidence: {contrib:+.3f})"
                    if is_nb
                    else f"'{token}' has positive association with legitimate email patterns (weight: {w:+.3f}, tfidf: {tfidf_val:.3f}, contribution: {contrib:+.3f})"
                )
                fc = FeatureContribution(
                    token=token,
                    weight=w,
                    tfidf_value=tfidf_val,
                    contribution=contrib,
                    direction="Legitimate",
                    relative_impact=round(rel_impact, 2),
                    description=desc,
                )
                legit_features.append(fc)
                contributions.append(fc)
            else:
                # Neutral contribution (weight == 0 or tfidf == 0)
                fc = FeatureContribution(
                    token=token,
                    weight=w,
                    tfidf_value=tfidf_val,
                    contribution=0.0,
                    direction="Neutral",
                    relative_impact=0.0,
                    description=f"'{token}' provides neutral evidence (zero contribution)",
                )
                contributions.append(fc)

        # Net decision score = intercept + sum of all contributions
        net_score = intercept + sum(c.contribution for c in contributions)

        calibrated_prob: float | None = None
        if isinstance(model_wrapper, LogisticRegressionWrapper):
            # Sigmoid of net logit represents calibrated probability for Logistic Regression
            calibrated_prob = float(1.0 / (1.0 + np.exp(-net_score)))
        elif isinstance(model_wrapper, LinearSVCWrapper) and model_wrapper.calibrator is not None:
            # Calibrated probability from cross-validated Platt scaling
            calibrated_prob = float(model_wrapper.predict_single(X_single, use_calibration=True).score)
        elif isinstance(model_wrapper, MultinomialNBWrapper):
            # MultinomialNB probabilities are uncalibrated log-likelihood ratios; calibrated_probability is None
            calibrated_prob = None

        notes = (
            f"Feature contributions represent linear mathematical attribution on {score_desc}. "
            "Evidence indicates statistical association with corpus patterns, not intrinsic causality."
        )

        return ExplanationResult(
            model_name=model_wrapper.name,
            intercept=round(intercept, 4),
            net_decision_score=round(net_score, 4),
            calibrated_probability=round(calibrated_prob, 4) if calibrated_prob is not None else None,
            top_spam_features=spam_features[:top_k],
            top_legitimate_features=legit_features[:top_k],
            all_contributions=contributions,
            attribution_notes=notes,
        )
