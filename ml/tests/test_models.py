"""Tests verifying model predictions, probability calibration, and thresholding.
"""

import numpy as np
import pytest
from mailshield_ml.features import FeaturePipeline
from mailshield_ml.models import (
    LinearSVCWrapper,
    LogisticRegressionWrapper,
    MultinomialNBWrapper,
)


@pytest.fixture
def trained_models():
    texts = [
        "Urgent: your account has been suspended claim lottery money",
        "Exclusive cash prize guaranteed profit casino bitcoin",
        "Team sprint demo notes and code review comments",
        "Meeting agenda for database migration on friday",
    ]
    y = np.array([1, 1, 0, 0])

    pipeline = FeaturePipeline(min_df=1)
    X = pipeline.fit_transform(texts)

    lr = LogisticRegressionWrapper(random_state=42).fit(X, y)
    nb = MultinomialNBWrapper().fit(X, y)
    svm = LinearSVCWrapper(cv=2, random_state=42).fit(X, y)

    return pipeline, lr, nb, svm


def test_logistic_regression_probabilities(trained_models):
    pipeline, lr, _, _ = trained_models
    X_test = pipeline.transform(["Lottery prize cash"])

    pred = lr.predict_single(X_test)
    assert pred.score_type == "probability"
    assert pred.calibrated is True
    assert 0.0 <= pred.score <= 1.0
    assert pred.class_probabilities is not None
    assert abs(sum(pred.class_probabilities.values()) - 1.0) < 1e-4
    assert pred.predicted_label == "Spam"


def test_multinomial_nb_probabilities(trained_models):
    pipeline, _, nb, _ = trained_models
    X_test = pipeline.transform(["Sprint demo code review"])

    pred = nb.predict_single(X_test)
    assert pred.score_type == "probability"
    assert pred.calibrated is False  # Explicitly documented
    assert 0.0 <= pred.score <= 1.0
    assert pred.predicted_label == "Legitimate"


def test_linear_svm_calibrated_vs_uncalibrated(trained_models):
    pipeline, _, _, svm = trained_models
    X_test = pipeline.transform(["Cash prize lottery"])

    # Calibrated prediction
    cal_pred = svm.predict_single(X_test, use_calibration=True)
    assert cal_pred.score_type == "probability"
    assert cal_pred.calibrated is True
    assert 0.0 <= cal_pred.score <= 1.0

    # Uncalibrated decision margin prediction
    raw_pred = svm.predict_single(X_test, use_calibration=False)
    assert raw_pred.score_type == "decision_function"
    assert raw_pred.calibrated is False
    assert raw_pred.raw_decision_score is not None
    assert raw_pred.score == raw_pred.raw_decision_score


def test_threshold_effect_on_prediction(trained_models):
    pipeline, lr, _, _ = trained_models
    X_test = pipeline.transform(["Sprint meeting with cash prize"])

    # At threshold 0.1, spam is triggered easily
    pred_low = lr.predict_single(X_test, threshold=0.01)
    assert pred_low.is_spam is True

    # At threshold 0.99, requires overwhelming evidence to trigger spam
    pred_high = lr.predict_single(X_test, threshold=0.99)
    assert pred_high.is_spam is False


def test_model_artifact_save_and_load(tmp_path, trained_models):
    pipeline, lr, nb, svm = trained_models
    X_test = pipeline.transform(["Lottery prize cash"])

    # Test LogisticRegression save & load
    lr_file = str(tmp_path / "lr.joblib")
    lr.save(lr_file)
    lr_loaded = LogisticRegressionWrapper.load(lr_file)
    assert lr_loaded.is_trained is True
    assert lr_loaded.predict_single(X_test).score == lr.predict_single(X_test).score

    # Test NaiveBayes save & load
    nb_file = str(tmp_path / "nb.joblib")
    nb.save(nb_file)
    nb_loaded = MultinomialNBWrapper.load(nb_file)
    assert nb_loaded.is_trained is True
    assert nb_loaded.predict_single(X_test).score == nb.predict_single(X_test).score

    # Test LinearSVC save & load
    svm_file = str(tmp_path / "svm.joblib")
    svm.save(svm_file)
    svm_loaded = LinearSVCWrapper.load(svm_file)
    assert svm_loaded.is_trained is True
    assert svm_loaded.predict_single(X_test).score == svm.predict_single(X_test).score


def test_brier_score_loss_and_calibration_diagnostics():
    from mailshield_ml.evaluation import compute_metrics_at_threshold

    # Perfectly calibrated predictions
    y_true = [0, 0, 1, 1]
    y_scores_good = [0.05, 0.10, 0.90, 0.95]

    rep_cal = compute_metrics_at_threshold(
        y_true=y_true,
        y_scores=y_scores_good,
        threshold=0.5,
        score_type="probability",
        calibrated=True,
    )
    assert rep_cal.brier_score is not None
    assert rep_cal.brier_score < 0.05
    assert rep_cal.calibration_status == "evaluated_well_calibrated"

    # Uncalibrated Naive Bayes scores
    rep_uncal = compute_metrics_at_threshold(
        y_true=y_true,
        y_scores=y_scores_good,
        threshold=0.5,
        score_type="probability",
        calibrated=False,
    )
    assert rep_uncal.calibration_status == "uncalibrated_log_likelihood"

