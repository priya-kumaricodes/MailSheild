"""Dual-channel (Word + Subword char_wb) TF-IDF feature pipeline for multilingual email classification.
"""

from __future__ import annotations

import joblib
import numpy as np
from scipy.sparse import spmatrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

from mailshield_ml.features import preprocess_email_text


class MultilingualFeaturePipeline:
    """Combines word-level n-grams (1-2) with character subword n-grams (3-5 char_wb)

    to achieve high robustness across Indic scripts, transliterated Hinglish, and English.
    """

    def __init__(
        self,
        word_max_features: int = 4000,
        char_max_features: int = 4000,
        min_df: int = 2,
    ):
        self.word_max_features = word_max_features
        self.char_max_features = char_max_features
        self.min_df = min_df

        self.word_vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=self.word_max_features,
            min_df=self.min_df,
            sublinear_tf=True,
            preprocessor=preprocess_email_text,
            token_pattern=r"(?u)\S+",
        )

        self.char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            max_features=self.char_max_features,
            min_df=self.min_df,
            sublinear_tf=True,
            preprocessor=preprocess_email_text,
        )

        self.union = FeatureUnion([
            ("word", self.word_vectorizer),
            ("char", self.char_vectorizer),
        ])
        self.is_fitted = False

    def fit(self, texts: list[str]) -> MultilingualFeaturePipeline:
        """Fit strictly on training split texts to avoid data leakage."""
        self.union.fit(texts)
        self.is_fitted = True
        return self

    def transform(self, texts: list[str] | str) -> spmatrix:
        """Transform texts into combined sparse feature matrix."""
        if not self.is_fitted:
            raise RuntimeError("MultilingualFeaturePipeline must be fitted before transform().")
        if isinstance(texts, str):
            texts = [texts]
        return self.union.transform(texts)

    def fit_transform(self, texts: list[str]) -> spmatrix:
        self.fit(texts)
        return self.transform(texts)

    def get_feature_names(self) -> np.ndarray:
        """Return the combined vocabulary feature names."""
        if not self.is_fitted:
            raise RuntimeError("MultilingualFeaturePipeline is not fitted yet.")
        word_names = np.array([f"w:{name}" for name in self.word_vectorizer.get_feature_names_out()])
        char_names = np.array([f"c:{name}" for name in self.char_vectorizer.get_feature_names_out()])
        return np.concatenate([word_names, char_names])

    def save(self, filepath: str) -> None:
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> MultilingualFeaturePipeline:
        return joblib.load(filepath)
