"""Feature extraction pipeline using specialized text tokenization and TF-IDF representation.
"""

from __future__ import annotations

import re
import unicodedata

import joblib
import numpy as np
from scipy.sparse import spmatrix
from sklearn.feature_extraction.text import TfidfVectorizer


def preprocess_email_text(text: str) -> str:
    """Preprocess email text by standardizing tokens for URLs, emails, currencies, and numbers."""
    if not text:
        return ""

    text = text.lower()

    # Replace URLs with normalized token
    text = re.sub(r"https?://\S+|www\.\S+", " http_url ", text)

    # Replace email addresses with normalized token
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", " email_addr ", text)

    # Replace currency symbols
    text = re.sub(r"[\$£€¥₹]", " curr_symbol ", text)

    # Replace standalone numbers and amounts with token
    text = re.sub(r"\b\d+([.,]\d+)?\b", " num_val ", text)

    # Replace repetitive exclamation and question marks
    text = re.sub(r"!{2,}", " multi_exclamation ", text)
    text = re.sub(r"\?{2,}", " multi_question ", text)

    # Replace punctuation and symbols with spaces while preserving letters, numbers, marks, and underscores
    text = "".join(
        c if (c == "_" or c.isspace() or not unicodedata.category(c).startswith(("P", "S"))) else " "
        for c in text
    )

    # Collapse spaces
    return re.sub(r"\s+", " ", text).strip()


class FeaturePipeline:
    """TF-IDF vectorizer wrapper enforcing strict fit-on-train and transform-on-eval."""

    def __init__(
        self,
        max_features: int = 5000,
        min_df: int = 2,
        ngram_range: tuple[int, int] = (1, 2),
        sublinear_tf: bool = True,
    ):
        self.max_features = max_features
        self.min_df = min_df
        self.ngram_range = ngram_range
        self.sublinear_tf = sublinear_tf
        self.vectorizer = TfidfVectorizer(
            preprocessor=preprocess_email_text,
            max_features=self.max_features,
            min_df=self.min_df,
            ngram_range=self.ngram_range,
            sublinear_tf=self.sublinear_tf,
            token_pattern=r"(?u)\S+",
        )
        self.is_fitted = False

    def fit(self, texts: list[str]) -> FeaturePipeline:
        """Fit the vectorizer strictly on the provided training texts."""
        self.vectorizer.fit(texts)
        self.is_fitted = True
        return self

    def transform(self, texts: list[str] | str) -> spmatrix:
        """Transform texts into TF-IDF sparse matrix representation."""
        if not self.is_fitted:
            raise RuntimeError("FeaturePipeline must be fitted before calling transform().")
        if isinstance(texts, str):
            texts = [texts]
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: list[str]) -> spmatrix:
        """Fit on training texts and return their TF-IDF representation."""
        self.fit(texts)
        return self.transform(texts)

    def get_feature_names(self) -> np.ndarray:
        """Return the learned vocabulary array."""
        if not self.is_fitted:
            raise RuntimeError("FeaturePipeline is not fitted yet.")
        return self.vectorizer.get_feature_names_out()

    def save(self, filepath: str) -> None:
        """Serialize fitted vectorizer artifact."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> FeaturePipeline:
        """Load serialized vectorizer artifact."""
        return joblib.load(filepath)
