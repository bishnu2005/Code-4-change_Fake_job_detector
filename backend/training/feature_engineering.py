"""
Feature engineering: TF-IDF vectorization.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)


def create_tfidf_vectorizer(max_features: int = 5000) -> TfidfVectorizer:
    """Create a configured TF-IDF vectorizer."""
    return TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )


def fit_transform(vectorizer: TfidfVectorizer, texts):
    """Fit the vectorizer and transform texts."""
    logger.info(f"Fitting TF-IDF on {len(texts)} documents...")
    X = vectorizer.fit_transform(texts)
    logger.info(f"TF-IDF matrix shape: {X.shape}")
    return X


def transform(vectorizer: TfidfVectorizer, texts):
    """Transform texts using an already-fitted vectorizer."""
    return vectorizer.transform(texts)
