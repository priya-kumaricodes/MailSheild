"""Model wrappers and training routines for Logistic Regression, Naive Bayes, and Linear SVM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
from scipy.sparse import spmatrix
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC


@dataclass
class ModelPrediction:
    """Standardized prediction output with clear score semantics."""

    predicted_label: str  # "Spam" or "Legitimate"
    is_spam: bool
    score: float  # Display score: probability [0, 1] if calibrated, or raw decision score
    score_type: str  # "probability" or "decision_function"
    calibrated: bool  # True if validated probability calibration was applied
    raw_decision_score: float | None = None  # Raw uncalibrated decision function value if applicable
    class_probabilities: dict[str, float] | None = None  # {"Legitimate": p0, "Spam": p1}
    threshold_applied: float = 0.5


class BaseModelWrapper:
    """Abstract base wrapper for MailShield classifiers."""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.model: Any = None
        self.default_threshold: float = 0.5
        self.is_trained: bool = False

    def predict_single(
        self,
        X_single: spmatrix,
        threshold: float | None = None,
    ) -> ModelPrediction:
        raise NotImplementedError

    def save(self, filepath: str) -> None:
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> BaseModelWrapper:
        return joblib.load(filepath)


class LogisticRegressionWrapper(BaseModelWrapper):
    """Logistic Regression classifier with mathematically calibrated sigmoid probabilities."""

    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        super().__init__(name="logistic_regression")
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state
        self.model = LogisticRegression(
            C=self.C,
            max_iter=self.max_iter,
            random_state=self.random_state,
            solver="lbfgs",
        )

    def fit(self, X_train: spmatrix, y_train: list[int] | np.ndarray) -> LogisticRegressionWrapper:
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return self

    def predict_single(
        self,
        X_single: spmatrix,
        threshold: float | None = None,
    ) -> ModelPrediction:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")

        tau = threshold if threshold is not None else self.default_threshold
        probs = self.model.predict_proba(X_single)[0]
        prob_ham = float(probs[0])
        prob_spam = float(probs[1])

        raw_logit = float(self.model.decision_function(X_single)[0])
        is_spam = bool(prob_spam >= tau)
        predicted_label = "Spam" if is_spam else "Legitimate"

        return ModelPrediction(
            predicted_label=predicted_label,
            is_spam=is_spam,
            score=prob_spam,
            score_type="probability",
            calibrated=True,
            raw_decision_score=raw_logit,
            class_probabilities={"Legitimate": prob_ham, "Spam": prob_spam},
            threshold_applied=tau,
        )


class MultinomialNBWrapper(BaseModelWrapper):
    """Multinomial Naive Bayes classifier providing standard posterior log-likelihood estimates."""

    def __init__(self, alpha: float = 0.1):
        super().__init__(name="naive_bayes")
        self.alpha = alpha
        self.model = MultinomialNB(alpha=self.alpha)

    def fit(self, X_train: spmatrix, y_train: list[int] | np.ndarray) -> MultinomialNBWrapper:
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return self

    def predict_single(
        self,
        X_single: spmatrix,
        threshold: float | None = None,
    ) -> ModelPrediction:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")

        tau = threshold if threshold is not None else self.default_threshold
        probs = self.model.predict_proba(X_single)[0]
        prob_ham = float(probs[0])
        prob_spam = float(probs[1])

        is_spam = bool(prob_spam >= tau)
        predicted_label = "Spam" if is_spam else "Legitimate"

        return ModelPrediction(
            predicted_label=predicted_label,
            is_spam=is_spam,
            score=prob_spam,
            score_type="probability",
            calibrated=False,  # Naive Bayes probabilities are notorious for peakiness / lack of true calibration
            raw_decision_score=None,
            class_probabilities={"Legitimate": prob_ham, "Spam": prob_spam},
            threshold_applied=tau,
        )


class LinearSVCWrapper(BaseModelWrapper):
    """Linear Support Vector Classifier with optional cross-validated Platt probability calibration."""

    def __init__(self, C: float = 1.0, cv: int = 3, random_state: int = 42):
        super().__init__(name="linear_svm")
        self.C = C
        self.cv = cv
        self.random_state = random_state
        self.model = LinearSVC(C=self.C, random_state=self.random_state)
        self.calibrator = CalibratedClassifierCV(
            estimator=LinearSVC(C=self.C, random_state=self.random_state),
            method="sigmoid",
            cv=self.cv,
        )

    def fit(self, X_train: spmatrix, y_train: list[int] | np.ndarray) -> LinearSVCWrapper:
        self.model.fit(X_train, y_train)
        self.calibrator.fit(X_train, y_train)
        self.is_trained = True
        return self

    def predict_single(
        self,
        X_single: spmatrix,
        threshold: float | None = None,
        use_calibration: bool = True,
    ) -> ModelPrediction:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")

        tau = threshold if threshold is not None else self.default_threshold
        raw_dist = float(self.model.decision_function(X_single)[0])

        if use_calibration and self.calibrator is not None:
            probs = self.calibrator.predict_proba(X_single)[0]
            prob_ham = float(probs[0])
            prob_spam = float(probs[1])
            is_spam = bool(prob_spam >= tau)

            return ModelPrediction(
                predicted_label="Spam" if is_spam else "Legitimate",
                is_spam=is_spam,
                score=prob_spam,
                score_type="probability",
                calibrated=True,
                raw_decision_score=raw_dist,
                class_probabilities={"Legitimate": prob_ham, "Spam": prob_spam},
                threshold_applied=tau,
            )
        else:
            # Uncalibrated decision boundary: 0.0 is separating hyperplane
            is_spam = bool(raw_dist >= 0.0)
            return ModelPrediction(
                predicted_label="Spam" if is_spam else "Legitimate",
                is_spam=is_spam,
                score=raw_dist,
                score_type="decision_function",
                calibrated=False,
                raw_decision_score=raw_dist,
                class_probabilities=None,
                threshold_applied=0.0,
            )
