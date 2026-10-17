"""Tests verifying prevention of train/val/test data leakage.
"""

import pytest
from mailshield_ml.features import FeaturePipeline


def test_leakage_prevention_vectorizer():
    train_texts = [
        "Quarterly planning meeting with engineering team",
        "Bug fix for distributed database transaction rollback",
        "Code review for authentication microservice pull request",
    ]
    test_texts = [
        "Unprecedented exclusive casino jackpot secret",  # Contains words never in train!
    ]

    pipeline = FeaturePipeline(min_df=1)
    pipeline.fit(train_texts)

    vocab = set(pipeline.get_feature_names())

    # Words in test_texts only must NOT be in the fitted vocabulary
    assert "casino" not in vocab
    assert "jackpot" not in vocab
    assert "unprecedented" not in vocab

    # Transform on test texts succeeds and produces expected shape without adding to vocab
    X_test = pipeline.transform(test_texts)
    assert X_test.shape[0] == 1
    assert X_test.shape[1] == len(vocab)
    assert set(pipeline.get_feature_names()) == vocab


def test_vectorizer_not_fitted_error():
    pipeline = FeaturePipeline()
    with pytest.raises(RuntimeError, match="must be fitted before"):
        pipeline.transform(["Some random email"])


def test_stratified_split_zero_hash_overlap():
    from mailshield_ml.dataset import deduplicate_records, stratified_split

    records = [
        {"subject": f"Sub {i}", "body": f"Body content {i}", "label": i % 2}
        for i in range(100)
    ]
    unique, _ = deduplicate_records(records)
    train, val, test = stratified_split(unique, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42)

    train_hashes = {r["content_hash"] for r in train}
    val_hashes = {r["content_hash"] for r in val}
    test_hashes = {r["content_hash"] for r in test}

    # Zero overlap across all partitions
    assert len(train_hashes & val_hashes) == 0
    assert len(train_hashes & test_hashes) == 0
    assert len(val_hashes & test_hashes) == 0
    assert len(train) + len(val) + len(test) == 100


def test_grouped_template_split_zero_group_overlap():
    import json
    from pathlib import Path

    from mailshield_ml.dataset import deduplicate_records, extract_template_group_id, grouped_template_split

    seed_path = Path("ml/data/seed_corpus.json")
    if not seed_path.exists():
        pytest.skip("Seed corpus not found")

    with open(seed_path, encoding="utf-8") as f:
        records = json.load(f)

    clean_records, _ = deduplicate_records(records)
    train_recs, val_recs, test_recs = grouped_template_split(clean_records)

    train_groups = {extract_template_group_id(r) for r in train_recs}
    val_groups = {extract_template_group_id(r) for r in val_recs}
    test_groups = {extract_template_group_id(r) for r in test_recs}

    # Strict partition guarantee: no group crosses splits
    assert len(train_groups & val_groups) == 0, f"Overlap between train and val: {train_groups & val_groups}"
    assert len(train_groups & test_groups) == 0, f"Overlap between train and test: {train_groups & test_groups}"
    assert len(val_groups & test_groups) == 0, f"Overlap between val and test: {val_groups & test_groups}"

    # Total sample conservation
    assert len(train_recs) + len(val_recs) + len(test_recs) == len(clean_records)

