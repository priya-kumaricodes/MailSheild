"""Tests verifying mathematical accuracy and direction of feature contributions.
"""

import numpy as np
from mailshield_ml.explainability import ExplainabilityEngine
from mailshield_ml.features import FeaturePipeline
from mailshield_ml.models import (
    LinearSVCWrapper,
    LogisticRegressionWrapper,
    MultinomialNBWrapper,
)


def test_logistic_regression_feature_contribution_math():
    train_texts = [
        "Congratulations you won one million dollars cash prize claim now",
        "Exclusive casino jackpot lottery payout wire transfer",
        "Team sprint planning architecture review meeting tomorrow morning",
        "Code review pull request for database query optimizer",
    ]
    train_y = np.array([1, 1, 0, 0])

    pipeline = FeaturePipeline(min_df=1)
    X_train = pipeline.fit_transform(train_texts)

    model = LogisticRegressionWrapper(random_state=42)
    model.fit(X_train, train_y)

    engine = ExplainabilityEngine(pipeline)

    # Test document: contains spam tokens and ham tokens
    test_doc = "Congratulations on your code review"
    X_test = pipeline.transform([test_doc])

    explanation = engine.explain_prediction(model, X_test)

    # Verify: net_decision_score == intercept + sum of all contributions
    sum_contribs = sum(c.contribution for c in explanation.all_contributions)
    expected_score = round(explanation.intercept + sum_contribs, 4)
    assert abs(explanation.net_decision_score - expected_score) < 1e-3

    # Verify sigmoid probability
    expected_prob = 1.0 / (1.0 + np.exp(-explanation.net_decision_score))
    assert abs(explanation.calibrated_probability - round(expected_prob, 4)) < 1e-3

    # Check that tokens categorized as 'Spam' have contribution >= 0
    for fc in explanation.top_spam_features:
        assert fc.contribution >= 0
        assert fc.direction == "Spam"

    # Check that tokens categorized as 'Legitimate' have contribution < 0
    for fc in explanation.top_legitimate_features:
        assert fc.contribution < 0
        assert fc.direction == "Legitimate"


def test_empty_document_explanation():
    pipeline = FeaturePipeline(min_df=1)
    pipeline.fit(["Sprint planning tomorrow morning"])

    model = LogisticRegressionWrapper()
    model.fit(pipeline.transform(["Sprint planning tomorrow morning", "Urgent lottery prize win"]), [0, 1])

    engine = ExplainabilityEngine(pipeline)
    # Document with completely out-of-vocabulary words
    X_empty = pipeline.transform(["Zilch qux quux"])

    exp = engine.explain_prediction(model, X_empty)
    assert len(exp.all_contributions) == 0
    assert "No active vocabulary tokens" in exp.attribution_notes


def test_linear_svm_feature_contribution_math():
    train_texts = [
        "Urgent lottery payout wire transfer cash money",
        "Exclusive casino jackpot claim prize winner",
        "Sprint planning engineering architecture review meeting",
        "Database migration code review pull request",
    ]
    train_y = np.array([1, 1, 0, 0])

    pipeline = FeaturePipeline(min_df=1)
    X_train = pipeline.fit_transform(train_texts)

    svm = LinearSVCWrapper(cv=2, random_state=42)
    svm.fit(X_train, train_y)

    engine = ExplainabilityEngine(pipeline)
    test_doc = "Urgent code review meeting"
    X_test = pipeline.transform([test_doc])

    exp = engine.explain_prediction(svm, X_test)

    # Verify: net_decision_score == intercept + sum of all contributions
    sum_contribs = sum(c.contribution for c in exp.all_contributions)
    expected_score = round(exp.intercept + sum_contribs, 4)
    assert abs(exp.net_decision_score - expected_score) < 1e-3

    # Decision function from sklearn matches net_decision_score within tolerance
    raw_decision = float(svm.model.decision_function(X_test)[0])
    assert abs(exp.net_decision_score - raw_decision) < 1e-3

    # Calibrated probability from Platt scaling is in [0, 1]
    assert exp.calibrated_probability is not None
    assert 0.0 <= exp.calibrated_probability <= 1.0


def test_multinomial_nb_feature_evidence_math():
    train_texts = [
        "Urgent lottery payout wire transfer cash money",
        "Exclusive casino jackpot claim prize winner",
        "Sprint planning engineering architecture review meeting",
        "Database migration code review pull request",
    ]
    train_y = np.array([1, 1, 0, 0])

    pipeline = FeaturePipeline(min_df=1)
    X_train = pipeline.fit_transform(train_texts)

    nb = MultinomialNBWrapper()
    nb.fit(X_train, train_y)

    engine = ExplainabilityEngine(pipeline)
    test_doc = "Urgent code review meeting"
    X_test = pipeline.transform([test_doc])

    exp = engine.explain_prediction(nb, X_test)

    # Net score matches log-prior odds + sum of log-likelihood ratio contributions
    sum_contribs = sum(c.contribution for c in exp.all_contributions)
    expected_score = round(exp.intercept + sum_contribs, 4)
    assert abs(exp.net_decision_score - expected_score) < 1e-3

    # For Naive Bayes, calibrated_probability must be None (uncalibrated posterior)
    assert exp.calibrated_probability is None

    # Attribution notes explicitly declare log-posterior odds / uncalibrated status
    assert "log-posterior odds" in exp.attribution_notes

    # Descriptions indicate log-likelihood evidence
    for fc in exp.top_spam_features:
        assert "log-likelihood evidence" in fc.description
        assert fc.contribution > 0


def test_unicode_and_repeated_tokens_explanation():
    train_texts = [
        "नमस्ते कल सुबह 10 बजे प्रोजेक्ट समीक्षा बैठक",
        "लॉटरी इनाम तत्काल नकद भुगतान जीतें",
        "Engineering sprint review architecture meeting",
        "Claim your lottery cash prize jackpot now",
    ]
    train_y = np.array([0, 1, 0, 1])

    pipeline = FeaturePipeline(min_df=1)
    X_train = pipeline.fit_transform(train_texts)

    model = LogisticRegressionWrapper(random_state=42).fit(X_train, train_y)
    engine = ExplainabilityEngine(pipeline)

    # Repeated tokens and Hindi mixed
    test_doc = "नमस्ते नमस्ते लॉटरी लॉटरी लॉटरी"
    X_test = pipeline.transform([test_doc])

    exp = engine.explain_prediction(model, X_test)
    assert len(exp.all_contributions) > 0

    # Relative impacts must be between 0 and 100
    for fc in exp.all_contributions:
        assert 0.0 <= fc.relative_impact <= 100.0

