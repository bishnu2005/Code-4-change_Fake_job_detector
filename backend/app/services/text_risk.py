"""
Text Risk Module: calibrated ML probability + SHAP explanations.
"""
import logging
import numpy as np

from app.models.model_loader import model_loader
from app.utils.helpers import clean_text
from app.config import SHAP_TOP_N

logger = logging.getLogger(__name__)

# Lazy SHAP import
_shap_explainer = None


def _get_shap_explainer():
    """Lazily create SHAP LinearExplainer from the uncalibrated model."""
    global _shap_explainer
    if _shap_explainer is not None:
        return _shap_explainer

    if not model_loader.is_loaded or model_loader.model is None:
        return None

    try:
        import shap
        _shap_explainer = shap.LinearExplainer(
            model_loader.model,
            masker=shap.maskers.Independent(
                data=np.zeros((1, len(model_loader.vectorizer.get_feature_names_out()))),
            ),
        )
        logger.info("SHAP LinearExplainer initialized.")
        return _shap_explainer
    except Exception as e:
        logger.warning(f"SHAP initialization failed: {e}")
        return None


def analyze_text_risk(raw_text: str) -> dict:
    """
    Run calibrated ML prediction + SHAP explanation on text.

    Returns:
        {
            "text_probability": float | None,
            "text_risk_score": float (0-100),
            "shap_risk_factors": [{"feature": str, "weight": float}],
            "shap_trust_factors": [{"feature": str, "weight": float}],
        }
    """
    result = {
        "text_probability": None,
        "text_risk_score": 0.0,
        "shap_risk_factors": [],
        "shap_trust_factors": [],
    }

    if not model_loader.is_loaded:
        return result

    cleaned = clean_text(raw_text)
    if not cleaned.strip():
        return result

    try:
        features = model_loader.vectorizer.transform([cleaned])

        # Calibrated probability
        prob = model_loader.predict_proba(features, calibrated=True)
        result["text_probability"] = round(prob, 4)
        # Risk score uses raw probability scaled 0-100
        result["text_risk_score"] = round(prob * 100, 1)
        # Classification uses tuned threshold
        result["exceeds_threshold"] = prob >= model_loader.optimal_threshold

        # SHAP explanations
        explainer = _get_shap_explainer()
        if explainer is not None:
            try:
                shap_values = explainer.shap_values(features)

                # For binary: shap_values may be (1, n_features) or list
                if isinstance(shap_values, list):
                    sv = shap_values[1][0]  # class 1 (fraud)
                else:
                    sv = shap_values[0]

                feature_names = model_loader.vectorizer.get_feature_names_out()

                # Top positive (risk) factors
                top_risk_idx = np.argsort(sv)[::-1][:SHAP_TOP_N]
                for idx in top_risk_idx:
                    if sv[idx] > 0:
                        result["shap_risk_factors"].append({
                            "feature": str(feature_names[idx]),
                            "weight": round(float(sv[idx]), 4),
                        })

                # Top negative (trust) factors
                top_trust_idx = np.argsort(sv)[:SHAP_TOP_N]
                for idx in top_trust_idx:
                    if sv[idx] < 0:
                        result["shap_trust_factors"].append({
                            "feature": str(feature_names[idx]),
                            "weight": round(float(sv[idx]), 4),
                        })
            except Exception as e:
                logger.warning(f"SHAP explanation failed: {e}")

    except Exception as e:
        logger.error(f"Text risk analysis failed: {e}")

    return result
