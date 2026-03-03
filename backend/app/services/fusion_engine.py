"""
Multi-Signal Fusion Engine: adaptive weighted combination of risk signals.

Rules:
  - Only include signals that exist and have non-zero strength.
  - Single signal -> weight = 1.0, no normalization.
  - Weak signals: reduce weight proportionally BEFORE normalization.
  - Email weight scaled by email_signal_strength.
  - Always enforce sum(weights) == 1.0.
  - Clamp final risk score 0-100.
"""
import logging

from app.config import WEIGHT_TEXT, WEIGHT_OCR, WEIGHT_URL, WEIGHT_EMAIL, DEBUG_LOGGING
from app.utils.helpers import clamp

logger = logging.getLogger(__name__)


def fuse_signals(
    text_risk_score: float | None = None,
    ocr_risk_score: float | None = None,
    url_risk_score: float | None = None,
    email_risk_score: float | None = None,
    ocr_signal_strength: float = 0.0,
    email_signal_strength: float = 0.0,
    has_text: bool = False,
    has_url: bool = False,
    has_image: bool = False,
    has_email: bool = False,
) -> dict:
    """
    Adaptively combine risk signals into a final risk score.
    """
    signals: list[tuple[str, float, float]] = []

    # Text signal
    if has_text and text_risk_score is not None:
        signals.append(("text", text_risk_score, WEIGHT_TEXT))

    # OCR signal — only if image present AND strength > 0
    if has_image and ocr_risk_score is not None and ocr_signal_strength > 0:
        adjusted_weight = WEIGHT_OCR * ocr_signal_strength
        signals.append(("ocr", ocr_risk_score, adjusted_weight))

    # URL signal — only if url_analysis is not None
    if has_url and url_risk_score is not None:
        signals.append(("url", url_risk_score, WEIGHT_URL))

    # Email signal — scale weight by signal strength
    if has_email and email_risk_score is not None and email_signal_strength > 0:
        adjusted_weight = WEIGHT_EMAIL * email_signal_strength
        signals.append(("email", email_risk_score, adjusted_weight))

    # Handle edge cases
    weights_used = {"text": 0.0, "ocr": 0.0, "url": 0.0, "email": 0.0}

    if not signals:
        return {
            "final_risk_score": 0.0,
            "weights_used": weights_used,
        }

    # Single signal -> weight = 1.0
    if len(signals) == 1:
        name, score, _ = signals[0]
        weights_used[name] = 1.0
        return {
            "final_risk_score": round(clamp(score), 1),
            "weights_used": weights_used,
        }

    # Multiple signals: normalize weights to sum = 1
    total_weight = sum(w for _, _, w in signals)
    if total_weight <= 0:
        total_weight = 1.0

    final_score = 0.0
    for name, score, weight in signals:
        normalized = weight / total_weight
        weights_used[name] = round(normalized, 3)
        final_score += normalized * score

    if DEBUG_LOGGING:
        active = {k: v for k, v in weights_used.items() if v > 0}
        logger.info(f"[FUSION] Weights: {active}")

    return {
        "final_risk_score": round(clamp(final_score), 1),
        "weights_used": weights_used,
    }
