"""
Unified inference pipeline: text → clean → features → ML + heuristics → risk score.
"""
import logging

from app.models.model_loader import model_loader
from app.utils.helpers import clean_text, clamp
from app.services.text_processor import detect_suspicious_keywords, analyze_salary, analyze_url
from app.services.explainer import generate_reasons
from app.config import RISK_THRESHOLD_HIGH, RISK_THRESHOLD_SUSPICIOUS

logger = logging.getLogger(__name__)


def classify_risk(score: float) -> str:
    """Map a 0-100 risk score to a risk level string."""
    if score >= RISK_THRESHOLD_HIGH:
        return "High Risk"
    elif score >= RISK_THRESHOLD_SUSPICIOUS:
        return "Suspicious"
    return "Safe"


def analyze(
    description: str,
    company: str = "",
    salary: str = "",
    apply_link: str = "",
) -> dict:
    """
    Run the full analysis pipeline on a job posting.

    Returns:
        {
            "risk_score": float (0-100),
            "risk_level": "Safe" | "Suspicious" | "High Risk",
            "reasons": [str]
        }
    """
    # ── 1. Combine and clean text ────────────────────────────────
    raw_text = f"{company} {salary} {description} {apply_link}"
    cleaned = clean_text(raw_text)

    # ── 2. ML probability ────────────────────────────────────────
    ml_prob = None
    if model_loader.is_loaded:
        try:
            features = model_loader.vectorizer.transform([cleaned])
            ml_prob = model_loader.predict_proba(features)
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
    else:
        logger.warning("Model not loaded — using heuristics only.")

    # ── 3. Heuristic signals ─────────────────────────────────────
    # Keyword detection (run on original text for accuracy)
    full_text = f"{company} {salary} {description}"
    suspicious_keywords = detect_suspicious_keywords(full_text)

    # Salary analysis
    salary_result = analyze_salary(salary)

    # URL / domain analysis
    url_result = analyze_url(apply_link)

    # ── 4. Compute final risk score ──────────────────────────────
    # Start with ML probability (scaled to 0-100) or a neutral 25
    if ml_prob is not None:
        base_score = ml_prob * 100
    else:
        base_score = 25.0  # neutral baseline when no model

    # Heuristic boosts
    keyword_boost = min(len(suspicious_keywords) * 8, 30)   # up to +30
    salary_boost = 15 if salary_result["is_suspicious"] else 0
    url_boost = min(len(url_result.get("reasons", [])) * 7, 25)  # up to +25

    risk_score = clamp(base_score + keyword_boost + salary_boost + url_boost)
    risk_level = classify_risk(risk_score)

    # ── 5. Generate explanations ─────────────────────────────────
    reasons = generate_reasons(ml_prob, suspicious_keywords, salary_result, url_result)

    return {
        "risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "reasons": reasons,
    }
