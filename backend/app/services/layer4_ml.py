"""
Layer 4 — Conditional ML Engine.
Only fires if previous layers are not decisive.
Uses existing calibrated Logistic Regression model.
"""
import logging
from app.models.model_loader import model_loader
from app.schemas.analyze import MLResult
from app.utils.helpers import clean_text

logger = logging.getLogger(__name__)


def run_ml(
    job_description: str,
    skip: bool = False,
) -> MLResult:
    """
    Run ML model on job description text.

    Args:
        job_description: The raw job posting text.
        skip: If True, layer is skipped (previous layers were decisive).

    Returns:
        MLResult with triggered=False if skipped or no text.
    """
    result = MLResult()

    if skip:
        return result

    if not job_description or len(job_description.strip()) < 30:
        return result

    if not model_loader.is_loaded:
        logger.warning("ML model not loaded, skipping Layer 4")
        return result

    try:
        cleaned = clean_text(job_description)
        X = model_loader.vectorizer.transform([cleaned])

        if model_loader.calibrated_model:
            prob = model_loader.calibrated_model.predict_proba(X)[0][1]
        else:
            prob = model_loader.model.predict_proba(X)[0][1]

        result.triggered = True
        result.probability = round(float(prob), 4)
        result.risk_score = round(float(prob) * 100, 1)

    except Exception as e:
        logger.error(f"ML inference failed: {e}")

    return result
