"""End-to-end Machine Learning pipeline: training, calibration, threshold tuning, and artifact serialization.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from mailshield_ml.dataset import (
    deduplicate_records,
    grouped_template_split,
    stratified_split,
)
from mailshield_ml.evaluation import (
    compute_metrics_at_threshold,
    select_cost_sensitive_threshold,
    sweep_thresholds,
)
from mailshield_ml.explainability import ExplainabilityEngine
from mailshield_ml.features import FeaturePipeline
from mailshield_ml.models import (
    LinearSVCWrapper,
    LogisticRegressionWrapper,
    MultinomialNBWrapper,
)


def format_email_for_vectorizer(record: dict[str, Any]) -> str:
    """Format an email record into combined Subject + Body text."""
    sub = record.get("subject", "").strip()
    body = record.get("body", "").strip()
    if sub and body:
        return f"Subject: {sub}\n\n{body}"
    return sub or body


class TrainingPipeline:
    """Manages data preparation, feature extraction, model fitting, validation tuning, and testing."""

    def __init__(
        self,
        data_path: str = "ml/data/seed_corpus.json",
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
        """Execute full training and evaluation workflow."""
        print(f"Loading dataset from {self.data_path}...")
        with open(self.data_path, encoding="utf-8") as f:
            raw_records = json.load(f)

        total_raw = len(raw_records)
        clean_records, dupes = deduplicate_records(raw_records)
        print(f"Loaded {total_raw} records; deduplicated {dupes} duplicate entries.")
        print(f"Remaining clean records: {len(clean_records)}")

        # Step 1: Stratified train / val / test split
        train_recs, val_recs, test_recs = stratified_split(
            clean_records,
            train_ratio=0.70,
            val_ratio=0.15,
            test_ratio=0.15,
            random_state=self.random_state,
        )

        print(f"Split sizes - Train: {len(train_recs)}, Validation: {len(val_recs)}, Test: {len(test_recs)}")

        # Extract text representations and labels
        train_texts = [format_email_for_vectorizer(r) for r in train_recs]
        train_y = np.array([r["label"] for r in train_recs], dtype=int)

        val_texts = [format_email_for_vectorizer(r) for r in val_recs]
        val_y = np.array([r["label"] for r in val_recs], dtype=int)

        test_texts = [format_email_for_vectorizer(r) for r in test_recs]
        test_y = np.array([r["label"] for r in test_recs], dtype=int)

        # Step 2: Fit TF-IDF Vectorizer strictly on train split
        print("Fitting TF-IDF FeaturePipeline strictly on training texts (leakage prevention)...")
        feature_pipeline = FeaturePipeline(
            max_features=5000,
            min_df=2,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        X_train = feature_pipeline.fit_transform(train_texts)
        X_val = feature_pipeline.transform(val_texts)
        X_test = feature_pipeline.transform(test_texts)

        vocab_size = len(feature_pipeline.get_feature_names())
        print(f"Learned vocabulary size: {vocab_size} tokens.")

        # Step 3: Train Models
        print("Training Logistic Regression classifier...")
        log_reg = LogisticRegressionWrapper(C=1.0, max_iter=1000, random_state=self.random_state)
        log_reg.fit(X_train, train_y)

        print("Training Multinomial Naive Bayes classifier...")
        nb_model = MultinomialNBWrapper(alpha=0.1)
        nb_model.fit(X_train, train_y)

        print("Training Linear Support Vector Machine (with cross-validated Platt scaling)...")
        svm_model = LinearSVCWrapper(C=1.0, cv=3, random_state=self.random_state)
        svm_model.fit(X_train, train_y)

        models = {
            "logistic_regression": log_reg,
            "naive_bayes": nb_model,
            "linear_svm": svm_model,
        }

        # Step 4: Validation evaluation and threshold sweeps
        validation_reports = {}
        validation_sweeps = {}
        optimal_thresholds = {}
        threshold_selection_meta = {}

        for name, m in models.items():
            # Get validation probabilities or decision scores
            if name == "linear_svm" and m.calibrator is not None:
                val_probs = m.calibrator.predict_proba(X_val)[:, 1]
                score_type = "probability"
                calibrated = True
            elif hasattr(m.model, "predict_proba"):
                val_probs = m.model.predict_proba(X_val)[:, 1]
                score_type = "probability"
                calibrated = (name == "logistic_regression")
            else:
                val_probs = m.model.decision_function(X_val)
                score_type = "decision_function"
                calibrated = False

            # Threshold sweep
            sweeps = sweep_thresholds(
                y_true=val_y,
                y_scores=val_probs,
                model_name=name,
                dataset_name="validation",
                score_type=score_type,
                calibrated=calibrated,
            )
            validation_sweeps[name] = sweeps

            # Cost-sensitive threshold selection: Utility = TP - 5*FP - FN subject to FPR <= 0.05
            best_tau, tau_meta = select_cost_sensitive_threshold(
                sweeps,
                fp_cost=5.0,
                fn_cost=1.0,
                max_fpr=0.05,
                fallback_threshold=0.5,
            )
            optimal_thresholds[name] = best_tau
            threshold_selection_meta[name] = tau_meta

            # Metrics at default 0.5 threshold
            rep = compute_metrics_at_threshold(
                y_true=val_y,
                y_scores=val_probs,
                threshold=0.5,
                model_name=name,
                dataset_name="validation",
                score_type=score_type,
                calibrated=calibrated,
            )
            validation_reports[name] = rep.to_dict()

        # Step 5: Final Evaluation on Independent Test Set
        test_reports = {}
        for name, m in models.items():
            tau = optimal_thresholds[name]
            if name == "linear_svm" and m.calibrator is not None:
                test_probs = m.calibrator.predict_proba(X_test)[:, 1]
                score_type = "probability"
                calibrated = True
            elif hasattr(m.model, "predict_proba"):
                test_probs = m.model.predict_proba(X_test)[:, 1]
                score_type = "probability"
                calibrated = (name == "logistic_regression")
            else:
                test_probs = m.model.decision_function(X_test)
                score_type = "decision_function"
                calibrated = False

            rep = compute_metrics_at_threshold(
                y_true=test_y,
                y_scores=test_probs,
                threshold=tau,
                model_name=name,
                dataset_name="test",
                score_type=score_type,
                calibrated=calibrated,
            )

            # Benchmark inference latency
            start_lat = time.perf_counter()
            passes = 100
            for _ in range(passes):
                if name == "linear_svm" and m.calibrator is not None:
                    _ = m.calibrator.predict_proba(X_test)
                elif hasattr(m.model, "predict_proba"):
                    _ = m.model.predict_proba(X_test)
                else:
                    _ = m.model.decision_function(X_test)
            latency_ms = round(((time.perf_counter() - start_lat) / (passes * len(test_y))) * 1000.0, 4)

            d_rep = rep.to_dict()
            d_rep["inference_latency_ms"] = latency_ms
            test_reports[name] = d_rep

            print(f"Model [{name}] Test Performance at threshold {tau}:")
            print(f"  Accuracy: {rep.accuracy:.4f}, Precision: {rep.precision:.4f}, Recall: {rep.recall:.4f}, F1: {rep.f1_score:.4f}, FPR: {rep.false_positive_rate:.4f}, Latency: {latency_ms:.4f} ms/sample")

        # Step 5b: Out-of-Template Generalization Benchmark (Strict Grouped Split)
        print("\nRunning out-of-template generalization benchmark (strict grouped template split)...")
        str_train_recs, str_val_recs, str_test_recs = grouped_template_split(clean_records)

        str_train_texts = [format_email_for_vectorizer(r) for r in str_train_recs]
        str_train_y = np.array([r["label"] for r in str_train_recs], dtype=int)
        str_val_texts = [format_email_for_vectorizer(r) for r in str_val_recs]
        str_val_y = np.array([r["label"] for r in str_val_recs], dtype=int)
        str_test_texts = [format_email_for_vectorizer(r) for r in str_test_recs]
        str_test_y = np.array([r["label"] for r in str_test_recs], dtype=int)

        str_feature_pipeline = FeaturePipeline(
            max_features=5000,
            min_df=2,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        X_str_train = str_feature_pipeline.fit_transform(str_train_texts)
        X_str_val = str_feature_pipeline.transform(str_val_texts)
        X_str_test = str_feature_pipeline.transform(str_test_texts)

        str_models = {
            "logistic_regression": LogisticRegressionWrapper(C=1.0, max_iter=1000, random_state=self.random_state).fit(X_str_train, str_train_y),
            "naive_bayes": MultinomialNBWrapper(alpha=0.1).fit(X_str_train, str_train_y),
            "linear_svm": LinearSVCWrapper(C=1.0, cv=3, random_state=self.random_state).fit(X_str_train, str_train_y),
        }

        strict_reports: dict[str, Any] = {}
        for name, m in str_models.items():
            if name == "linear_svm" and m.calibrator is not None:
                s_val_probs = m.calibrator.predict_proba(X_str_val)[:, 1]
                s_test_probs = m.calibrator.predict_proba(X_str_test)[:, 1]
                s_score_type = "probability"
                s_calibrated = True
            elif hasattr(m.model, "predict_proba"):
                s_val_probs = m.model.predict_proba(X_str_val)[:, 1]
                s_test_probs = m.model.predict_proba(X_str_test)[:, 1]
                s_score_type = "probability"
                s_calibrated = (name == "logistic_regression")
            else:
                s_val_probs = m.model.decision_function(X_str_val)
                s_test_probs = m.model.decision_function(X_str_test)
                s_score_type = "decision_function"
                s_calibrated = False

            s_sweeps = sweep_thresholds(
                y_true=str_val_y,
                y_scores=s_val_probs,
                model_name=name,
                dataset_name="strict_validation",
                score_type=s_score_type,
                calibrated=s_calibrated,
            )
            s_best_tau, s_tau_meta = select_cost_sensitive_threshold(
                s_sweeps,
                fp_cost=5.0,
                fn_cost=1.0,
                max_fpr=0.05,
                fallback_threshold=0.5,
            )

            s_rep = compute_metrics_at_threshold(
                y_true=str_test_y,
                y_scores=s_test_probs,
                threshold=s_best_tau,
                model_name=name,
                dataset_name="strict_holdout_test",
                score_type=s_score_type,
                calibrated=s_calibrated,
            )
            d_srep = s_rep.to_dict()
            d_srep["threshold_selection"] = s_tau_meta
            strict_reports[name] = d_srep
            print(f"  [Strict Benchmark] {name} (tau={s_best_tau}): Acc={s_rep.accuracy:.4f}, Prec={s_rep.precision:.4f}, Rec={s_rep.recall:.4f}, F1={s_rep.f1_score:.4f}, FPR={s_rep.false_positive_rate:.4f}, Brier={s_rep.brier_score}")

        strict_generalization_report = {
            "evaluation_type": "grouped_template_holdout",
            "description": "Strict partition grouping template families and campaigns to prevent cross-split leakage",
            "dataset_split": {
                "total_samples": len(clean_records),
                "train_samples": len(str_train_recs),
                "validation_samples": len(str_val_recs),
                "test_samples": len(str_test_recs),
                "train_spam_ratio": float(np.mean(str_train_y)),
                "val_spam_ratio": float(np.mean(str_val_y)),
                "test_spam_ratio": float(np.mean(str_test_y)),
            },
            "models": strict_reports,
        }

        with open(self.reports_dir / "strict_generalization_report.json", "w", encoding="utf-8") as f:
            json.dump(strict_generalization_report, f, indent=2)

        # Step 6: Verify Explainability Engine
        print("Testing explainability engine on sample test document...")
        explainer = ExplainabilityEngine(feature_pipeline)
        sample_x = X_test[0]
        sample_exp = explainer.explain_prediction(log_reg, sample_x, top_k=5)
        print(f"Sample explanation: top spam tokens={len(sample_exp.top_spam_features)}, top ham tokens={len(sample_exp.top_legitimate_features)}")

        # Step 7: Serialize Artifacts
        print(f"Saving artifacts to {self.artifacts_dir}...")
        feature_pipeline.save(str(self.artifacts_dir / "tfidf_vectorizer.joblib"))
        log_reg.save(str(self.artifacts_dir / "model_logistic_regression.joblib"))
        nb_model.save(str(self.artifacts_dir / "model_naive_bayes.joblib"))
        svm_model.save(str(self.artifacts_dir / "model_linear_svm.joblib"))

        # Save metadata and reports
        pipeline_metadata = {
            "version": "1.0.0",
            "feature_extractor": {
                "type": "TfidfVectorizer",
                "max_features": 5000,
                "ngram_range": [1, 2],
                "sublinear_tf": True,
                "vocab_size": vocab_size,
            },
            "dataset_info": {
                "source": str(self.data_path),
                "total_samples": len(clean_records),
                "duplicates_removed": dupes,
                "train_samples": len(train_recs),
                "validation_samples": len(val_recs),
                "test_samples": len(test_recs),
                "class_distribution": {
                    "train_spam_ratio": float(np.mean(train_y)),
                    "val_spam_ratio": float(np.mean(val_y)),
                    "test_spam_ratio": float(np.mean(test_y)),
                },
            },
            "models": {
                name: {
                    "optimal_threshold": optimal_thresholds[name],
                    "threshold_selection": threshold_selection_meta[name],
                    "validation_metrics": validation_reports[name],
                    "test_metrics": test_reports[name],
                }
                for name in models
            },
            "validation_sweeps": validation_sweeps,
            "strict_generalization_benchmark": strict_generalization_report,
        }

        with open(self.artifacts_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(pipeline_metadata, f, indent=2)

        with open(self.reports_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(test_reports, f, indent=2)

        # Also save validation predictions for fast API retrieval in Model Lab
        val_cache = {
            "val_true": val_y.tolist(),
            "models": {
                "logistic_regression": log_reg.model.predict_proba(X_val)[:, 1].tolist(),
                "naive_bayes": nb_model.model.predict_proba(X_val)[:, 1].tolist(),
                "linear_svm": svm_model.calibrator.predict_proba(X_val)[:, 1].tolist() if svm_model.calibrator else svm_model.model.decision_function(X_val).tolist(),
            }
        }
        with open(self.artifacts_dir / "val_predictions_cache.json", "w", encoding="utf-8") as f:
            json.dump(val_cache, f)

        print("ML training pipeline completed successfully!")
        return pipeline_metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MailShield ML Training Pipeline")
    parser.add_argument("--data", default="ml/data/seed_corpus.json", help="Path to input data JSON")
    parser.add_argument("--artifacts", default="ml/artifacts", help="Path to artifacts directory")
    parser.add_argument("--reports", default="ml/reports", help="Path to reports directory")
    args = parser.parse_args()

    pipeline = TrainingPipeline(
        data_path=args.data,
        artifacts_dir=args.artifacts,
        reports_dir=args.reports,
    )
    pipeline.run()
