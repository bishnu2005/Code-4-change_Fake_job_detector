"""
Loads trained ML models and TF-IDF vectorizer from disk once at startup.
Supports calibrated model + uncalibrated model (for SHAP).
"""
import os
import json
import joblib
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton-style loader for fraud detection models."""

    def __init__(self):
        self.model = None               # uncalibrated LogisticRegression
        self.calibrated_model = None     # CalibratedClassifierCV
        self.vectorizer = None           # TfidfVectorizer
        self.optimal_threshold = 0.5     # default, overridden by threshold.json
        self._loaded = False

    def load(
        self,
        model_path: str,
        vectorizer_path: str,
        calibrated_model_path: str = "",
        threshold_path: str = "",
    ) -> bool:
        """
        Load model artifacts.
        Returns True if at least model + vectorizer loaded.
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

            # Load calibrated model if available
            if calibrated_model_path and os.path.exists(calibrated_model_path):
                self.calibrated_model = joblib.load(calibrated_model_path)
                logger.info("Calibrated model loaded successfully.")
            else:
                logger.warning(
                    "Calibrated model not found — using uncalibrated model."
                )

            # Load optimal threshold
            if threshold_path and os.path.exists(threshold_path):
                try:
                    with open(threshold_path, "r") as f:
                        data = json.load(f)
                    self.optimal_threshold = float(data.get("optimal_threshold", 0.5))
                    logger.info(
                        f"Optimal threshold loaded: {self.optimal_threshold}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to load threshold: {e}. Using 0.5.")
            else:
                logger.warning("threshold.json not found — using default 0.5.")

            return True
        except Exception as e:
            logger.error(f"Failed to load model artifacts: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def has_calibrated(self) -> bool:
        return self.calibrated_model is not None

    def predict_proba(self, text_features, calibrated: bool = True) -> float:
        """Return fraud probability for given TF-IDF features."""
        if not self._loaded:
            raise RuntimeError("Model not loaded. Train the model first.")

        model = (
            self.calibrated_model
            if calibrated and self.calibrated_model is not None
            else self.model
        )
        probas = model.predict_proba(text_features)
        return float(probas[0][1])


# Global singleton
model_loader = ModelLoader()
