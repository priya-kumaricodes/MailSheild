"""Training and evaluation pipeline for MailShield 2.0 Multilingual Models.
Evaluates Dual-Channel TF-IDF against baseline on balanced multilingual corpus with zero group leakage.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import spmatrix

from mailshield_ml.dataset import multilingual_grouped_split
from mailshield_ml.evaluation import (
    compute_metrics_at_threshold,
    select_cost_sensitive_threshold,
    sweep_thresholds,
)
from mailshield_ml.models import (
    LinearSVCWrapper,
    LogisticRegressionWrapper,
    MultinomialNBWrapper,
)
from mailshield_ml.multilingual_features import MultilingualFeaturePipeline


def format_text(r: dict[str, Any]) -> str:
    sub = r.get("subject", "").strip()
    body = r.get("body", "").strip()
    if sub and body:
        return f"Subject: {sub}\n\n{body}"
    return sub or body


def get_model_scores(m: Any, name: str, X: spmatrix) -> tuple[np.ndarray, str, bool]:
    if name == "linear_svm" and getattr(m, "calibrator", None) is not None:
        return m.calibrator.predict_proba(X)[:, 1], "probability", True
    elif hasattr(m.model, "predict_proba"):
        return m.model.predict_proba(X)[:, 1], "probability", (name == "logistic_regression")
    else:
        return m.model.decision_function(X), "decision_function", False


class MultilingualTrainingPipeline:
    def __init__(
        self,
        data_path: str = "ml/data/multilingual_corpus.json",
        artifacts_dir: str = "ml/artifacts",
        reports_dir: str = "ml/reports",
        random_state: int = 42,
    ):
        self.data_path = Path(data_path)
        self.artifacts_dir = Path(artifacts_dir)
        self.reports_dir = Path(reports_dir)
        self.random_state = random_state

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict[str, Any]:
        print(f"Loading multilingual corpus from {self.data_path}...")
        with open(self.data_path, encoding="utf-8") as f:
            records = json.load(f)

        print(f"Total multilingual records: {len(records)}")

        # Partition by template group with zero leakage
        train_recs, val_recs, test_recs = multilingual_grouped_split(records)

        train_groups = {r["template_group"] for r in train_recs}
        val_groups = {r["template_group"] for r in val_recs}
        test_groups = {r["template_group"] for r in test_recs}

        # Programmatic verification of zero group overlap
        assert len(train_groups & val_groups) == 0, "Train-Val group overlap detected!"
        assert len(train_groups & test_groups) == 0, "Train-Test group overlap detected!"
        assert len(val_groups & test_groups) == 0, "Val-Test group overlap detected!"

        print(f"Train split: {len(train_recs)} samples across {len(train_groups)} template groups")
        print(f"Val split:   {len(val_recs)} samples across {len(val_groups)} template groups")
        print(f"Test split:  {len(test_recs)} samples across {len(test_groups)} template groups")

        train_texts = [format_text(r) for r in train_recs]
        train_y = np.array([r["label"] for r in train_recs], dtype=int)

        val_texts = [format_text(r) for r in val_recs]
        val_y = np.array([r["label"] for r in val_recs], dtype=int)

        test_texts = [format_text(r) for r in test_recs]
        test_y = np.array([r["label"] for r in test_recs], dtype=int)

        # Fit Dual-Channel Vectorizer strictly on train texts
        print("Fitting MultilingualFeaturePipeline on training texts...")
        feature_pipe = MultilingualFeaturePipeline(
            word_max_features=4000,
            char_max_features=4000,
            min_df=2,
        )
        X_train = feature_pipe.fit_transform(train_texts)
        X_val = feature_pipe.transform(val_texts)
        X_test = feature_pipe.transform(test_texts)

        vectorizer_path = self.artifacts_dir / "multilingual_tfidf_vectorizer.joblib"
        feature_pipe.save(str(vectorizer_path))
        print(f"Saved multilingual vectorizer to {vectorizer_path}")

        # Model Definitions
        log_reg = LogisticRegressionWrapper(C=2.0, max_iter=1000, random_state=self.random_state)
        linear_svm = LinearSVCWrapper(C=1.0, random_state=self.random_state, cv=3)
        naive_bayes = MultinomialNBWrapper(alpha=0.5)

        models_to_train = {
            "logistic_regression": log_reg,
            "linear_svm": linear_svm,
            "naive_bayes": naive_bayes,
        }

        model_eval_results = {}
        predictions_cache = {
            "validation": [],
            "test": [],
        }

        for model_name, m in models_to_train.items():
            print(f"\n--- Training {model_name} ---")
            t0 = time.perf_counter()
            m.fit(X_train, train_y)
            train_time_ms = (time.perf_counter() - t0) * 1000

            # Predict on validation set and run sweeps
            val_scores, score_type, calibrated = get_model_scores(m, model_name, X_val)
            sweeps = sweep_thresholds(
                y_true=val_y,
                y_scores=val_scores,
                model_name=model_name,
                dataset_name="validation",
                score_type=score_type,
                calibrated=calibrated,
            )

            # Cost-sensitive threshold tuning on validation
            best_tau, tau_meta = select_cost_sensitive_threshold(
                sweeps,
                fp_cost=5.0,
                fn_cost=1.0,
                max_fpr=0.05,
                fallback_threshold=0.5,
            )
            m.default_threshold = best_tau

            val_rep = compute_metrics_at_threshold(
                y_true=val_y,
                y_scores=val_scores,
                threshold=best_tau,
                model_name=model_name,
                dataset_name="validation",
                score_type=score_type,
                calibrated=calibrated,
            )

            # Evaluate on untouched holdout test split
            test_scores, _, _ = get_model_scores(m, model_name, X_test)
            test_rep = compute_metrics_at_threshold(
                y_true=test_y,
                y_scores=test_scores,
                threshold=best_tau,
                model_name=model_name,
                dataset_name="test",
                score_type=score_type,
                calibrated=calibrated,
            )

            # Benchmark inference latency
            passes = 50
            start_lat = time.perf_counter()
            for _ in range(passes):
                _ = get_model_scores(m, model_name, X_test)
            latency_ms = round(((time.perf_counter() - start_lat) / (passes * len(test_y))) * 1000.0, 4)

            print(f"Optimal threshold on Val: {best_tau:.4f} (Val F1: {val_rep.f1_score:.4f}, FPR: {val_rep.false_positive_rate:.4f})")
            print(f"Holdout Test Results: Acc: {test_rep.accuracy:.4f}, Prec: {test_rep.precision:.4f}, "
                  f"Recall: {test_rep.recall:.4f}, F1: {test_rep.f1_score:.4f}, FPR: {test_rep.false_positive_rate:.4f}, Brier: {test_rep.brier_score if test_rep.brier_score is not None else 0.0:.4f}")

            # Per-Language Breakdown on Holdout Test Set
            lang_breakdown = {}
            unique_langs = sorted(list({r["language"] for r in test_recs}))
            for lang in unique_langs:
                indices = [i for i, r in enumerate(test_recs) if r["language"] == lang]
                sub_y = test_y[indices]
                sub_scores = test_scores[indices]
                sub_rep = compute_metrics_at_threshold(
                    y_true=sub_y,
                    y_scores=sub_scores,
                    threshold=best_tau,
                    model_name=model_name,
                    dataset_name=f"test_{lang}",
                    score_type=score_type,
                    calibrated=calibrated,
                )
                lang_breakdown[lang] = {
                    "samples": len(indices),
                    "ham_samples": int(np.sum(sub_y == 0)),
                    "spam_samples": int(np.sum(sub_y == 1)),
                    "accuracy": sub_rep.accuracy,
                    "precision": sub_rep.precision,
                    "recall": sub_rep.recall,
                    "f1": sub_rep.f1_score,
                    "fpr": sub_rep.false_positive_rate,
                    "fnr": round(float(sub_rep.confusion_matrix.fn / max(1, sub_rep.confusion_matrix.fn + sub_rep.confusion_matrix.tp)), 4),
                    "confusion_matrix": {
                        "tn": sub_rep.confusion_matrix.tn,
                        "fp": sub_rep.confusion_matrix.fp,
                        "fn": sub_rep.confusion_matrix.fn,
                        "tp": sub_rep.confusion_matrix.tp,
                    },
                }

            # Save model artifact
            model_file = self.artifacts_dir / f"multilingual_model_{model_name}.joblib"
            m.save(str(model_file))
            model_size_kb = round(model_file.stat().st_size / 1024, 2)

            model_eval_results[model_name] = {
                "threshold": best_tau,
                "train_time_ms": round(train_time_ms, 2),
                "inference_latency_ms": latency_ms,
                "model_size_kb": model_size_kb,
                "threshold_metadata": tau_meta,
                "validation_metrics": val_rep.to_dict(),
                "test_metrics": test_rep.to_dict(),
                "per_language_test": lang_breakdown,
            }

            # Populate predictions cache for drill-down inspection
            for i, r in enumerate(test_recs):
                prob = float(test_scores[i])
                pred = int(prob >= best_tau)
                actual = int(test_y[i])
                is_error = (pred != actual)
                error_type = "FP" if (pred == 1 and actual == 0) else ("FN" if (pred == 0 and actual == 1) else "CORRECT")

                predictions_cache["test"].append({
                    "model": model_name,
                    "email_id": r["id"],
                    "subject": r["subject"],
                    "body_preview": r["body"][:120] + ("..." if len(r["body"]) > 120 else ""),
                    "sender": r["sender"],
                    "language": r["language"],
                    "script": r["script"],
                    "template_group": r["template_group"],
                    "provenance": r["provenance"],
                    "category": r["category"],
                    "actual_label": "spam" if actual == 1 else "ham",
                    "predicted_label": "spam" if pred == 1 else "ham",
                    "score": round(prob, 4),
                    "threshold": round(best_tau, 4),
                    "is_error": is_error,
                    "error_type": error_type,
                })

        # Save metadata and reports
        multilingual_metadata = {
            "version": "2.0.0-phase1",
            "feature_pipeline": {
                "type": "DualChannel-TFIDF",
                "word_ngrams": [1, 2],
                "char_ngrams": [3, 5],
                "char_analyzer": "char_wb",
                "total_vocabulary_size": len(feature_pipe.get_feature_names()),
            },
            "dataset_summary": {
                "total_records": len(records),
                "splits": {
                    "train": {"samples": len(train_recs), "template_groups": len(train_groups)},
                    "validation": {"samples": len(val_recs), "template_groups": len(val_groups)},
                    "test": {"samples": len(test_recs), "template_groups": len(test_groups)},
                },
                "languages": ["en", "hi", "ta", "te", "kn", "hinglish"],
                "zero_group_leakage": True,
            },
            "models": model_eval_results,
            "baseline_comparison": {
                "english_baseline": {
                    "model": "Linear SVM (English Baseline)",
                    "accuracy": 0.8333,
                    "recall": 0.7222,
                    "fpr": 0.0556,
                    "latency_ms": 0.05,
                    "size_kb": 12.4,
                },
                "multilingual_models": {
                    "logistic_regression": {
                        "accuracy": model_eval_results["logistic_regression"]["test_metrics"]["accuracy"],
                        "recall": model_eval_results["logistic_regression"]["test_metrics"]["recall"],
                        "fpr": model_eval_results["logistic_regression"]["test_metrics"]["false_positive_rate"],
                        "latency_ms": model_eval_results["logistic_regression"]["inference_latency_ms"],
                        "size_kb": model_eval_results["logistic_regression"]["model_size_kb"],
                    },
                    "linear_svm": {
                        "accuracy": model_eval_results["linear_svm"]["test_metrics"]["accuracy"],
                        "recall": model_eval_results["linear_svm"]["test_metrics"]["recall"],
                        "fpr": model_eval_results["linear_svm"]["test_metrics"]["false_positive_rate"],
                        "latency_ms": model_eval_results["linear_svm"]["inference_latency_ms"],
                        "size_kb": model_eval_results["linear_svm"]["model_size_kb"],
                    },
                    "naive_bayes": {
                        "accuracy": model_eval_results["naive_bayes"]["test_metrics"]["accuracy"],
                        "recall": model_eval_results["naive_bayes"]["test_metrics"]["recall"],
                        "fpr": model_eval_results["naive_bayes"]["test_metrics"]["false_positive_rate"],
                        "latency_ms": model_eval_results["naive_bayes"]["inference_latency_ms"],
                        "size_kb": model_eval_results["naive_bayes"]["model_size_kb"],
                    },
                },
            },
        }

        meta_path = self.artifacts_dir / "multilingual_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(multilingual_metadata, f, indent=2)
        print(f"Saved multilingual metadata to {meta_path}")

        cache_path = self.artifacts_dir / "multilingual_val_predictions_cache.json"
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(predictions_cache, f, indent=2)
        print(f"Saved multilingual predictions cache to {cache_path}")

        return multilingual_metadata


if __name__ == "__main__":
    pipeline = MultilingualTrainingPipeline()
    res = pipeline.run()
    print("\nMultilingual Training Complete!")
