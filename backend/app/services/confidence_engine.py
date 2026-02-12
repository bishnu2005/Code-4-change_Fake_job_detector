"""
Confidence Engine: measures certainty of the assessment, NOT risk level.

Structured multi-step logic:
  Step 1: Base = 30
  Step 2: Signal count bonus (+20 for 2 strong, +35 for 3+ strong)
  Step 3: Signal strength bonuses
  Step 4: Agreement/contradiction via variance
  Step 5: Insufficient data cap (uses sufficiency_score)
  Step 6: Final clamp 0-95 (never 100, never Very High on single signal)
"""
import math
from app.config import MIN_TEXT_LENGTH, MIN_WORD_COUNT
from app.utils.helpers import clamp


def compute_confidence(
    has_text: bool = False,
    has_image: bool = False,
    has_url: bool = False,
    has_email: bool = False,
    ocr_signal_strength: float = 0.0,
    text_length: int = 0,
    word_count: int = 0,
    https_flag: bool = False,
    safe_browsing_status: str = "skipped",
    text_risk_score: float | None = None,
    ocr_risk_score: float | None = None,
    url_risk_score: float | None = None,
    email_risk_score: float | None = None,
    email_domain_matches_company: bool = False,
    sufficiency_score: int = 0,
) -> dict:
    """
    Compute confidence score reflecting certainty of the assessment.
    Maximum possible = 95. Never returns 100.
    """
    # Step 1: Base
    score = 30

    # Step 2: Signal count bonus (strong signals only)
    strong_signals = 0
    if has_text and text_length >= MIN_TEXT_LENGTH and word_count >= MIN_WORD_COUNT:
        strong_signals += 1
    if has_image and ocr_signal_strength >= 1.0:
        strong_signals += 1
    if has_url and url_risk_score is not None:
        strong_signals += 1
    if has_email and email_risk_score is not None:
        strong_signals += 1

    if strong_signals >= 3:
        score += 35
    elif strong_signals >= 2:
        score += 20

    # Step 3: Signal strength bonuses
    if has_url and url_risk_score is not None:
        score += 10
    if safe_browsing_status in ("clean", "malicious"):
        score += 10
    if has_image and ocr_signal_strength >= 1.0:
        score += 5
    if has_text and text_length >= MIN_TEXT_LENGTH and word_count >= MIN_WORD_COUNT:
        score += 5
    if has_email and email_risk_score is not None:
        score += 10
    if email_domain_matches_company:
        score += 5

    # Step 4: Agreement / contradiction
    active_scores: list[float] = []
    if has_text and text_risk_score is not None:
        active_scores.append(text_risk_score)
    if has_image and ocr_risk_score is not None and ocr_signal_strength > 0:
        active_scores.append(ocr_risk_score)
    if has_url and url_risk_score is not None:
        active_scores.append(url_risk_score)
    if has_email and email_risk_score is not None:
        active_scores.append(email_risk_score)

    if len(active_scores) >= 2:
        mean = sum(active_scores) / len(active_scores)
        variance = math.sqrt(
            sum((s - mean) ** 2 for s in active_scores) / len(active_scores)
        )
        if variance < 15:
            score += 10
        elif variance > 30:
            score -= 15

    # Step 5: Insufficient data cap
    if sufficiency_score <= 1:
        score = min(score, 60)

    # Step 5b: Never "Very High" on single signal
    if strong_signals <= 1:
        score = min(score, 80)  # caps below "Very High" threshold (86)

    # Step 6: Clamp 0–95 (NEVER 100)
    score = int(clamp(score, 0, 95))

    if score >= 86:
        level = "Very High"
    elif score >= 66:
        level = "High"
    elif score >= 41:
        level = "Medium"
    else:
        level = "Low"

    return {
        "confidence_score": score,
        "confidence_level": level,
    }
