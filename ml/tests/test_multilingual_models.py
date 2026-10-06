"""Unit tests for multilingual feature pipeline, grouped splitting, and trained model artifacts."""

import json
from pathlib import Path

import pytest
from mailshield_ml.dataset import multilingual_grouped_split
from mailshield_ml.models import BaseModelWrapper
from mailshield_ml.multilingual_features import MultilingualFeaturePipeline


@pytest.fixture
def corpus_records():
    path = Path("ml/data/multilingual_corpus.json")
    assert path.exists(), "Multilingual corpus file must exist"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_multilingual_grouped_split_zero_leakage(corpus_records):
    train_recs, val_recs, test_recs = multilingual_grouped_split(corpus_records)

    train_groups = {r["template_group"] for r in train_recs}
    val_groups = {r["template_group"] for r in val_recs}
    test_groups = {r["template_group"] for r in test_recs}

    # Strict zero group overlap assertion
    assert len(train_groups & val_groups) == 0
    assert len(train_groups & test_groups) == 0
    assert len(val_groups & test_groups) == 0

    # Ensure all 6 target languages are represented in all splits
    target_langs = {"en", "hi", "ta", "te", "kn", "hinglish"}
    assert {r["language"] for r in train_recs} == target_langs
    assert {r["language"] for r in val_recs} == target_langs
    assert {r["language"] for r in test_recs} == target_langs


def test_multilingual_feature_pipeline_dual_channel():
    texts = [
        "Aapka SBI account suspend hone wala hai turant KYC karein",
        "Dear Customer, your monthly salary of Rs 65000 is credited",
        "அன்புள்ள வாடிக்கையாளரே, உங்கள் மின் கட்டணம் பெறப்பட்டது",
        "ఖాతా లావాదేవీ హెచ్చరిక: రూ. 2450 డ్రా చేయబడింది",
    ]
    pipe = MultilingualFeaturePipeline(word_max_features=100, char_max_features=100, min_df=1)
    X = pipe.fit_transform(texts)
    assert X.shape[0] == 4
    assert X.shape[1] > 10

    names = pipe.get_feature_names()
    assert any(n.startswith("w:") for n in names)
    assert any(n.startswith("c:") for n in names)


def test_trained_multilingual_artifacts_exist_and_predict():
    vec_path = Path("ml/artifacts/multilingual_tfidf_vectorizer.joblib")
    lr_path = Path("ml/artifacts/multilingual_model_logistic_regression.joblib")
    svm_path = Path("ml/artifacts/multilingual_model_linear_svm.joblib")

    assert vec_path.exists()
    assert lr_path.exists()
    assert svm_path.exists()

    vectorizer = MultilingualFeaturePipeline.load(str(vec_path))
    lr_model = BaseModelWrapper.load(str(lr_path))
    svm_model = BaseModelWrapper.load(str(svm_path))

    # Test sample in Hindi
    test_hi = "Subject: बिजली बिल अलर्ट\n\nआज रात आपका बिजली कनेक्शन काट दिया जाएगा। तुरंत भुगतान करें http://fake-pay.biz"
    x_hi = vectorizer.transform(test_hi)
    pred_lr = lr_model.predict_single(x_hi)
    assert pred_lr.is_spam is True

    # Test sample in English ham
    test_en_ham = "Subject: AWS Invoice #9821\n\nYour monthly cloud infrastructure bill of $120 is paid successfully."
    x_en = vectorizer.transform(test_en_ham)
    pred_svm = svm_model.predict_single(x_en)
    assert pred_svm.is_spam is False
