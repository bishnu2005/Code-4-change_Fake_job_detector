"""
Loads trained ML model and TF-IDF vectorizer from disk once at startup.
"""
import os
import joblib
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton-style loader for the fraud detection model and vectorizer."""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._loaded = False

    def load(self, model_path: str, vectorizer_path: str) -> bool:
        """
        Load model and vectorizer from the given paths.
        Returns True if both loaded successfully, False otherwise.
        """
        if self._loaded:
            return True

        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            return False

        if not os.path.exists(vectorizer_path):
            logger.warning(f"Vectorizer file not found: {vectorizer_path}")
            return False

        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self._loaded = True
            logger.info("Model and vectorizer loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load model artifacts: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict_proba(self, text_features):
        """Return fraud probability for the given TF-IDF features."""
        if not self._loaded:
            raise RuntimeError("Model not loaded. Train the model first.")
        probas = self.model.predict_proba(text_features)
        # Return probability of the positive (fraudulent) class
        return float(probas[0][1])


# Global singleton instance
model_loader = ModelLoader()
