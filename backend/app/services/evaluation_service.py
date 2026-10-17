"""Evaluation service for Model Lab, multilingual benchmarks, error inspection,
provenance tracking, and dynamic threshold simulations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from mailshield_ml.evaluation import compute_metrics_at_threshold
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.evaluation import EvaluationRun
from backend.app.schemas.models import (
    ModelInfo,
    ModelListResponse,
    ThresholdSimulationPoint,
    ThresholdSimulationResponse,
)


class EvaluationService:
    def __init__(self, artifacts_dir: str | None = None):
        self.artifacts_dir = Path(artifacts_dir or settings.ARTIFACTS_DIR)

    def get_models_overview(self) -> ModelListResponse:
        meta_path = self.artifacts_dir / "metadata.json"
        if not meta_path.exists():
            return ModelListResponse(
                models=[],
                active_model="logistic_regression",
                vocab_size=0,
                dataset_info={},
            )

        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        display_names = {
            "logistic_regression": "Logistic Regression (L2 / Sigmoid)",
            "naive_bayes": "Multinomial Naive Bayes",
            "linear_svm": "Linear Support Vector Machine (Platt Calibrated)",
            "multilingual_logistic_regression": "Multilingual Logistic Regression (Dual-Channel TF-IDF)",
            "multilingual_linear_svm": "Multilingual Linear SVM (Dual-Channel TF-IDF)",
            "multilingual_naive_bayes": "Multilingual Naive Bayes (Dual-Channel TF-IDF)",
        }

        models_list: list[ModelInfo] = []
        for name, data in meta.get("models", {}).items():
            test_m = data.get("test_metrics", {})
            val_m = data.get("validation_metrics", {})
            models_list.append(
                ModelInfo(
                    name=name,
                    display_name=display_names.get(name, name),
                    version="1.0.0",
                    score_type=test_m.get("score_type", "probability"),
                    calibrated=test_m.get("calibrated", True),
                    optimal_threshold=data.get("optimal_threshold", 0.5),
                    test_metrics=test_m,
                    validation_metrics=val_m,
                )
            )

        # Check for multilingual metadata and add them
        multi_meta_path = self.artifacts_dir / "multilingual_metadata.json"
        if multi_meta_path.exists():
            with open(multi_meta_path, encoding="utf-8") as f:
                multi_meta = json.load(f)
            for m_name, m_data in multi_meta.get("models", {}).items():
                t_metrics = m_data.get("test_metrics", {})
                v_metrics = m_data.get("validation_metrics", {})
                models_list.append(
                    ModelInfo(
                        name=f"multilingual_{m_name}",
                        display_name=display_names.get(f"multilingual_{m_name}", f"Multilingual {m_name}"),
                        version="2.0.0",
                        score_type=t_metrics.get("score_type", "probability"),
                        calibrated=t_metrics.get("calibrated", True),
                        optimal_threshold=m_data.get("threshold", 0.5),
                        test_metrics=t_metrics,
                        validation_metrics=v_metrics,
                    )
                )

        vocab_size = meta.get("feature_extractor", {}).get("vocab_size", 0)
        dataset_info = meta.get("dataset_info", {})

        return ModelListResponse(
            models=models_list,
            active_model=settings.DEFAULT_MODEL,
            vocab_size=vocab_size,
            dataset_info=dataset_info,
        )

    def simulate_threshold(self, model_name: str, threshold: float) -> ThresholdSimulationResponse:
        """Dynamically compute metrics from genuine validation set predictions at the chosen threshold."""
        cache_path = self.artifacts_dir / "val_predictions_cache.json"
        meta_path = self.artifacts_dir / "metadata.json"

        if not cache_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Validation prediction cache is not initialized.",
            )

        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)

        y_val = cache.get("val_true", [])
        m_scores = cache.get("models", {}).get(model_name)

        if m_scores is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No validation scores found for model '{model_name}'.",
            )

        score_type = "probability"
        calibrated = True
        raw_sweeps = []
        if meta_path.exists():
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
            model_info = meta.get("models", {}).get(model_name, {})
            score_type = model_info.get("test_metrics", {}).get("score_type", "probability")
            calibrated = model_info.get("test_metrics", {}).get("calibrated", True)
            raw_sweeps = meta.get("validation_sweeps", {}).get(model_name, [])

        rep = compute_metrics_at_threshold(
            y_true=y_val,
            y_scores=m_scores,
            threshold=threshold,
            model_name=model_name,
            dataset_name="validation",
            score_type=score_type,
            calibrated=calibrated,
        )

        current_pt = ThresholdSimulationPoint(
            threshold=round(threshold, 4),
            accuracy=rep.accuracy,
            precision=rep.precision,
            recall=rep.recall,
            f1_score=rep.f1_score,
            false_positive_rate=rep.false_positive_rate,
            confusion_matrix=rep.confusion_matrix.to_matrix(),
            brier_score=rep.brier_score,
            calibration_status=rep.calibration_status,
        )

        sweep_curve: list[ThresholdSimulationPoint] = []
        for item in raw_sweeps:
            sweep_curve.append(
                ThresholdSimulationPoint(
                    threshold=item["threshold"],
                    accuracy=item["accuracy"],
                    precision=item["precision"],
                    recall=item["recall"],
                    f1_score=item["f1_score"],
                    false_positive_rate=item["false_positive_rate"],
                    confusion_matrix=item["confusion_matrix_grid"],
                    brier_score=item.get("brier_score"),
                    calibration_status=item.get("calibration_status"),
                )
            )

        return ThresholdSimulationResponse(
            model_name=model_name,
            current_metrics=current_pt,
            sweep_curve=sweep_curve,
        )

    # =========================================================================
    # MULTILINGUAL EVALUATION LAB (PHASE 1)
    # =========================================================================

    def _load_multilingual_metadata(self) -> dict[str, Any]:
        meta_path = self.artifacts_dir / "multilingual_metadata.json"
        if not meta_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Multilingual evaluation metadata not found. Run training pipeline first.",
            )
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)

    def get_supported_languages(self) -> list[dict[str, Any]]:
        """Return list of supported languages, scripts, and sample counts."""
        return [
            {"code": "all", "name": "All Languages (Aggregate)", "script": "Multilingual", "test_samples": 36},
            {"code": "en", "name": "English", "script": "Latin", "test_samples": 6},
            {"code": "hi", "name": "Hindi (हिन्दी)", "script": "Devanagari", "test_samples": 6},
            {"code": "ta", "name": "Tamil (தமிழ்)", "script": "Tamil", "test_samples": 6},
            {"code": "te", "name": "Telugu (తెలుగు)", "script": "Telugu", "test_samples": 6},
            {"code": "kn", "name": "Kannada (ಕನ್ನಡ)", "script": "Kannada", "test_samples": 6},
            {"code": "hinglish", "name": "Hinglish (Romanized Indic)", "script": "Latin", "test_samples": 6},
        ]

    def get_evaluation_metrics(
        self,
        model_name: str = "linear_svm",
        split: str = "test",
        language: str = "all",
    ) -> dict[str, Any]:
        """Fetch metrics for a given model, partition, and language."""
        meta = self._load_multilingual_metadata()
        clean_name = model_name.replace("multilingual_", "")
        models_dict = meta.get("models", {})

        if clean_name not in models_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown multilingual model '{model_name}'. Available: {list(models_dict.keys())}",
            )

        m_data = models_dict[clean_name]

        if split == "validation":
            metrics = m_data.get("validation_metrics", {})
        else:
            if language and language != "all":
                per_lang = m_data.get("per_language_test", {})
                if language not in per_lang:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No metrics for language '{language}'. Available: {list(per_lang.keys())}",
                    )
                return {
                    "model_name": model_name,
                    "split": split,
                    "language": language,
                    "threshold": m_data.get("threshold"),
                    "inference_latency_ms": m_data.get("inference_latency_ms"),
                    "model_size_kb": m_data.get("model_size_kb"),
                    **per_lang[language],
                }
            metrics = m_data.get("test_metrics", {})

        cm = metrics.get("confusion_matrix", {})
        fn = cm.get("fn", 0)
        tp = cm.get("tp", 0)
        fnr = round(float(fn / max(1, fn + tp)), 4)

        return {
            "model_name": model_name,
            "split": split,
            "language": language,
            "threshold": m_data.get("threshold"),
            "inference_latency_ms": m_data.get("inference_latency_ms"),
            "model_size_kb": m_data.get("model_size_kb"),
            "accuracy": metrics.get("accuracy", 0.0),
            "precision": metrics.get("precision", 0.0),
            "recall": metrics.get("recall", 0.0),
            "f1": metrics.get("f1_score", 0.0),
            "fpr": metrics.get("false_positive_rate", 0.0),
            "fnr": fnr,
            "brier_score": metrics.get("brier_score"),
            "pr_auc": metrics.get("pr_auc"),
            "roc_auc": metrics.get("roc_auc"),
            "confusion_matrix": cm,
            "num_samples": metrics.get("num_samples", 0),
        }

    def get_confusion_matrix(
        self,
        model_name: str = "linear_svm",
        split: str = "test",
        language: str = "all",
    ) -> dict[str, Any]:
        """Fetch 2x2 confusion matrix with raw counts and normalized rates."""
        metrics = self.get_evaluation_metrics(model_name=model_name, split=split, language=language)
        cm = metrics.get("confusion_matrix", {})
        tn = cm.get("tn", 0)
        fp = cm.get("fp", 0)
        fn = cm.get("fn", 0)
        tp = cm.get("tp", 0)

        total_actual_ham = max(1, tn + fp)
        total_actual_spam = max(1, fn + tp)
        total_samples = max(1, tn + fp + fn + tp)

        return {
            "model_name": model_name,
            "split": split,
            "language": language,
            "grid": [[tn, fp], [fn, tp]],
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "rates": {
                "true_negative_rate": round(tn / total_actual_ham, 4),
                "false_positive_rate": round(fp / total_actual_ham, 4),
                "false_negative_rate": round(fn / total_actual_spam, 4),
                "true_positive_rate": round(tp / total_actual_spam, 4),
            },
            "total_samples": total_samples,
        }

    def get_drilldown_errors(
        self,
        model_name: str = "linear_svm",
        error_type: str = "ALL",  # "FP", "FN", "ALL"
        language: str = "all",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Fetch false positive and false negative prediction records for forensic drill-down."""
        cache_path = self.artifacts_dir / "multilingual_val_predictions_cache.json"
        if not cache_path.exists():
            return []

        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)

        clean_name = model_name.replace("multilingual_", "")
        test_preds = cache.get("test", [])

        results = []
        for item in test_preds:
            if item.get("model") != clean_name:
                continue
            if language != "all" and item.get("language") != language:
                continue

            item_err = item.get("error_type", "")
            if error_type != "ALL" and item_err != error_type:
                continue

            results.append(item)
            if len(results) >= limit:
                break

        return results

    def get_model_comparison(self) -> dict[str, Any]:
        """Side-by-side comparison matrix of baseline vs multilingual models."""
        meta = self._load_multilingual_metadata()
        return meta.get("baseline_comparison", {})

    def _resolve_corpus_path(self) -> Path:
        candidate = Path(settings.DATA_DIR) / "multilingual_corpus.json"
        if candidate.exists():
            return candidate
        candidate2 = self.artifacts_dir.parent / "data" / "multilingual_corpus.json"
        if candidate2.exists():
            return candidate2
        return Path("ml/data/multilingual_corpus.json")

    def get_dataset_provenance(self) -> dict[str, Any]:
        """Dataset provenance breakdown: sources, licenses, splits, zero-leakage guarantee."""
        corpus_path = self._resolve_corpus_path()
        if not corpus_path.exists():
            raise HTTPException(status_code=404, detail="Multilingual corpus file not found.")

        with open(corpus_path, encoding="utf-8") as f:
            corpus = json.load(f)

        meta = self._load_multilingual_metadata()

        provenance_counts: dict[str, int] = {}
        license_counts: dict[str, int] = {}
        language_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}

        for item in corpus:
            prov = item.get("provenance", "unknown")
            lic = item.get("license", "unknown")
            lang = item.get("language", "unknown")
            cat = item.get("category", "unknown")

            provenance_counts[prov] = provenance_counts.get(prov, 0) + 1
            license_counts[lic] = license_counts.get(lic, 0) + 1
            language_counts[lang] = language_counts.get(lang, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_records": len(corpus),
            "splits": meta.get("dataset_summary", {}).get("splits", {}),
            "zero_group_leakage": True,
            "provenance_breakdown": provenance_counts,
            "license_breakdown": license_counts,
            "language_distribution": language_counts,
            "categories": category_counts,
        }

    def get_demo_samples(self, language: str = "all") -> list[dict[str, Any]]:
        """Fetch representative, curated demo emails in each language for instant UI playground testing."""
        corpus_path = self._resolve_corpus_path()
        if not corpus_path.exists():
            return []

        with open(corpus_path, encoding="utf-8") as f:
            corpus = json.load(f)

        # Select 2 distinct samples (1 ham, 1 spam) per language
        selected_pairs: dict[str, dict[str, Any]] = {}

        for item in corpus:
            lang = item.get("language")
            lbl = "spam" if item.get("label") == 1 else "ham"
            if language != "all" and lang != language:
                continue

            key = f"{lang}_{lbl}"
            if key not in selected_pairs:
                selected_pairs[key] = {
                    "id": item["id"],
                    "language": lang,
                    "script": item.get("script", "Unknown"),
                    "expected_label": lbl,
                    "category": item.get("category", ""),
                    "subject": item.get("subject", ""),
                    "body": item.get("body", ""),
                    "sender": item.get("sender", ""),
                }

        return list(selected_pairs.values())

    def run_benchmark(self, db: Session, user_id: str, dataset_name: str = "test") -> list[dict[str, Any]]:
        """Run benchmark on independent test dataset (admin only) and record in DB."""
        meta_path = self.artifacts_dir / "metadata.json"
        if not meta_path.exists():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model metadata missing.")

        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        results = []
        for name, data in meta.get("models", {}).items():
            test_m = data.get("test_metrics", {})
            run = EvaluationRun(
                model_name=name,
                dataset_name=dataset_name,
                num_samples=test_m.get("num_samples", 0),
                accuracy=test_m.get("accuracy", 0.0),
                precision=test_m.get("precision", 0.0),
                recall=test_m.get("recall", 0.0),
                f1_score=test_m.get("f1_score", 0.0),
                false_positive_rate=test_m.get("false_positive_rate", 0.0),
                pr_auc=test_m.get("pr_auc"),
                roc_auc=test_m.get("roc_auc"),
                triggered_by_user_id=user_id,
            )
            run.set_confusion_matrix(test_m.get("confusion_matrix", {}))
            db.add(run)
            results.append(test_m)

        db.commit()
        return results
