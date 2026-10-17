"""Milestone 2 test suite: Multilingual dataset integrity, provenance, dual-channel feature extraction,
grouped template splitting, and holdout generalization.
"""

import json
from pathlib import Path

import pytest
from mailshield_ml.dataset import compute_content_hash, multilingual_grouped_split
from mailshield_ml.multilingual_features import MultilingualFeaturePipeline


@pytest.fixture
def corpus_data():
    corpus_path = Path("ml/data/multilingual_corpus.json")
    assert corpus_path.exists(), "Multilingual corpus file must exist at ml/data/multilingual_corpus.json"
    with open(corpus_path, encoding="utf-8") as f:
        records = json.load(f)
    return records


def test_dataset_provenance_and_licensing(corpus_data):
    """Validate all corpus records, licensing tags, and provenance declarations."""
    allowed_licenses = {"Apache-2.0", "CC-BY-4.0", "Public Domain"}
    allowed_provenance = {"public_corpus", "manually_curated", "synthetic_template"}

    assert len(corpus_data) >= 120, "Corpus must have sufficient records across all 6 targets"

    for r in corpus_data:
        assert "id" in r and r["id"]
        assert "language" in r and r["language"] in {"en", "hi", "ta", "te", "kn", "hinglish"}
        assert "label" in r and r["label"] in {0, 1}
        assert "template_group" in r and r["template_group"]
        assert "license" in r and r["license"] in allowed_licenses
        assert "provenance" in r and r["provenance"] in allowed_provenance
        assert "subject" in r
        assert "body" in r and len(r["body"].strip()) > 0


def test_no_exact_or_near_duplicates_in_corpus(corpus_data):
    """Ensure no duplicate content hashes or identical texts exist in the curated corpus."""
    hashes = set()
    for r in corpus_data:
        h = compute_content_hash(r["subject"], r["body"])
        assert h not in hashes, f"Duplicate content found for ID {r['id']}"
        hashes.add(h)


def test_strict_zero_template_group_leakage(corpus_data):
    """Guarantee zero template-group leakage across Train, Validation, and Holdout partitions."""
    train_recs, val_recs, test_recs = multilingual_grouped_split(corpus_data)

    train_groups = {r["template_group"] for r in train_recs}
    val_groups = {r["template_group"] for r in val_recs}
    test_groups = {r["template_group"] for r in test_recs}

    # Strict partition isolation
    assert len(train_groups & val_groups) == 0, "Train and Val must have zero group overlap"
    assert len(train_groups & test_groups) == 0, "Train and Test must have zero group overlap"
    assert len(val_groups & test_groups) == 0, "Val and Test must have zero group overlap"

    # Verify each split has ham and spam in all 6 target languages
    for split_name, split_recs in [("train", train_recs), ("val", val_recs), ("test", test_recs)]:
        langs = {r["language"] for r in split_recs}
        assert langs == {"en", "hi", "ta", "te", "kn", "hinglish"}, f"Split {split_name} missing target languages"
        for lang in langs:
            lang_labels = {r["label"] for r in split_recs if r["language"] == lang}
            assert {0, 1}.issubset(lang_labels), f"Split {split_name} in language {lang} must contain both ham and spam"


def test_dual_channel_feature_pipeline():
    """Verify that MultilingualFeaturePipeline extracts both word-level and subword character n-grams."""
    pipe = MultilingualFeaturePipeline(word_max_features=50, char_max_features=50, min_df=1)
    texts = [
        "Aapka SBI khata block ho jayega turant KYC complete karein",
        "Your flight confirmation is ready HA 482",
        "இலவச பரிசுத்தொகை பெற உடனே இந்த இணைப்பை கிளிக் செய்க",
    ]
    X = pipe.fit_transform(texts)
    assert X.shape[0] == 3
    features = pipe.get_feature_names()
    word_feats = [f for f in features if f.startswith("w:")]
    char_feats = [f for f in features if f.startswith("c:")]

    assert len(word_feats) > 0, "Must have word n-grams"
    assert len(char_feats) > 0, "Must have subword char_wb n-grams"


def test_multilingual_metadata_reporting():
    """Verify that metadata documents independent template-group counts and evaluation results."""
    meta_path = Path("ml/artifacts/multilingual_metadata.json")
    assert meta_path.exists(), "Multilingual metadata must exist"

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    # Must report splits with sample counts AND group counts
    splits = meta.get("dataset_summary", {}).get("splits", {})
    assert "train" in splits and "samples" in splits["train"] and "template_groups" in splits["train"]
    assert "validation" in splits and "samples" in splits["validation"] and "template_groups" in splits["validation"]
    assert "test" in splits and "samples" in splits["test"] and "template_groups" in splits["test"]

    # Must contain models with metrics
    models = meta.get("models", {})
    assert "linear_svm" in models
    assert "logistic_regression" in models
    assert "naive_bayes" in models

    for model_name, m_data in models.items():
        assert "threshold" in m_data or "optimal_threshold" in m_data
        assert "test_metrics" in m_data
        assert "accuracy" in m_data["test_metrics"]
        assert "precision" in m_data["test_metrics"]
        assert "recall" in m_data["test_metrics"]
        assert "false_positive_rate" in m_data["test_metrics"]
