"""
Unified inference pipeline: orchestrates all signal modules.

Performance guard: total inference capped at INFERENCE_TIMEOUT seconds.
Each module timeout is handled individually; timed-out modules are skipped.
"""
import logging
import re
import time

from app.models.model_loader import model_loader
from app.utils.helpers import clean_text
from app.config import (
    RISK_THRESHOLD_HIGH,
    RISK_THRESHOLD_SUSPICIOUS,
    MIN_TEXT_LENGTH,
    MIN_WORD_COUNT,
    SUSPICIOUS_KEYWORDS,
    INFERENCE_TIMEOUT,
    DEBUG_LOGGING,
)
from app.services.text_risk import analyze_text_risk
from app.services.url_verification import verify_url
from app.services.safe_browsing import check_safe_browsing
from app.services.email_verification import verify_email
from app.services.fusion_engine import fuse_signals
from app.services.confidence_engine import compute_confidence

logger = logging.getLogger(__name__)


def classify_risk(score: float) -> str:
    """Map a 0-100 risk score to a risk level string."""
    if score >= RISK_THRESHOLD_HIGH:
        return "High Risk"
    elif score >= RISK_THRESHOLD_SUSPICIOUS:
        return "Suspicious"
    return "Safe"


def _extract_url_from_text(text: str) -> str | None:
    """Try to find a URL in the text."""
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


def _detect_keywords(text: str) -> list[str]:
    """Detect suspicious keywords in text."""
    found = []
    lower = text.lower()
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in lower:
            found.append(kw)
    return found


def _count_meaningful_words(text: str) -> int:
    """Count words that are >= 3 characters (filters out noise)."""
    if not text:
        return 0
    words = text.strip().split()
    return sum(1 for w in words if len(w) >= 3)


def _text_is_sufficient(text_len: int, word_count: int) -> bool:
    """Check if text meets both length and word count thresholds."""
    return text_len >= MIN_TEXT_LENGTH and word_count >= MIN_WORD_COUNT


def _compute_sufficiency(
    text_len: int,
    word_count: int,
    has_url: bool,
    has_image: bool,
    ocr_signal_strength: float,
    has_email: bool,
    email_signal_strength: float,
) -> tuple[int, str]:
    """
    Compute input sufficiency score and level.
      +1 if text >= MIN_TEXT_LENGTH AND >= MIN_WORD_COUNT
      +1 if URL present
      +1 if strong OCR (strength >= 1.0)
      +1 if email present AND signal_strength >= 0.5
    Levels: 0=None, 1=Weak, 2=Moderate, 3+=Strong
    """
    score = 0
    if _text_is_sufficient(text_len, word_count):
        score += 1
    if has_url:
        score += 1
    if has_image and ocr_signal_strength >= 1.0:
        score += 1
    if has_email and email_signal_strength >= 0.5:
        score += 1

    if score == 0:
        level = "None"
    elif score == 1:
        level = "Weak"
    elif score == 2:
        level = "Moderate"
    else:
        level = "Strong"

    return score, level


def _time_remaining(start: float) -> float:
    """Seconds remaining in the inference budget."""
    return max(0, INFERENCE_TIMEOUT - (time.time() - start))


def analyze(
    description: str,
    company: str = "",
    salary: str = "",
    apply_link: str = "",
    image_bytes: bytes | None = None,
) -> dict:
    """
    Run the full multi-signal analysis pipeline.
    Returns the unified response dict matching AnalyzeResponse schema.
    """
    start_time = time.time()
    timeout_notes: list[str] = []

    full_text = f"{company} {salary} {description}"
    text_len = len(description.strip()) if description else 0
    word_count = _count_meaningful_words(description)
    has_text = bool(description.strip())

    # ── 1. Text Risk Module ──────────────────────────────────────
    text_result = analyze_text_risk(full_text)
    text_risk_score = text_result["text_risk_score"]

    # Keyword boost
    keywords = _detect_keywords(full_text)
    keyword_boost = min(len(keywords) * 6, 20)
    text_risk_score = min(text_risk_score + keyword_boost, 100)

    # ── 2. OCR Risk Module ───────────────────────────────────────
    ocr_result = None
    has_image = image_bytes is not None
    ocr_signal_strength = 0.0
    ocr_extracted_text = ""
    if has_image and _time_remaining(start_time) > 0.5:
        try:
            from app.services.ocr_risk import analyze_ocr_risk
            ocr_result = analyze_ocr_risk(image_bytes)
            ocr_signal_strength = ocr_result.get("ocr_signal_strength", 0.0)
            ocr_extracted_text = ocr_result.get("extracted_text", "")
        except Exception as e:
            logger.warning(f"OCR module failed: {e}")
            has_image = False
    elif has_image:
        timeout_notes.append("OCR")
        has_image = False

    # ── 3. URL Verification Module ───────────────────────────────
    url_to_check = apply_link.strip() if apply_link else _extract_url_from_text(full_text)
    url_result = None
    has_url = False
    safe_browsing_status = "skipped"

    if url_to_check and _time_remaining(start_time) > 0.5:
        url_result = verify_url(url_to_check, company_name=company)
        has_url = url_result is not None

        if has_url and _time_remaining(start_time) > 0.5:
            safe_browsing_status = check_safe_browsing(url_to_check)
            url_result["safe_browsing_status"] = safe_browsing_status

            if safe_browsing_status == "malicious":
                url_result["url_risk_score"] = min(
                    url_result["url_risk_score"] + 40, 100
                )
            elif safe_browsing_status == "clean":
                url_result["url_trust_score"] = min(
                    url_result["url_trust_score"] + 20, 100
                )
        elif has_url:
            timeout_notes.append("Safe Browsing")
    elif url_to_check:
        timeout_notes.append("URL verification")

    # ── 4. Email Verification Module ─────────────────────────────
    email_result = None
    has_email = False
    email_signal_strength = 0.0
    email_domain_matches = False

    if _time_remaining(start_time) > 0.3:
        combined_text_for_email = f"{full_text} {ocr_extracted_text}"
        email_result = verify_email(combined_text_for_email, company_name=company)
        has_email = email_result is not None

        if has_email and email_result:
            email_signal_strength = email_result.get("email_signal_strength", 0.5)
            email_domain_matches = email_result.get("domain_similarity_score", 0) > 0.6
    else:
        timeout_notes.append("Email verification")

    # ── 5. Sufficiency Check ─────────────────────────────────────
    sufficiency_score, sufficiency_level = _compute_sufficiency(
        text_len, word_count, has_url, has_image, ocr_signal_strength,
        has_email, email_signal_strength,
    )

    if DEBUG_LOGGING:
        active_signals = [s for s in ["text", "url", "image", "email"]
                          if {"text": has_text, "url": has_url,
                              "image": has_image, "email": has_email}[s]]
        logger.info(f"[INFERENCE] Signals used: {', '.join(active_signals) or 'none'}")
        logger.info(f"[INFERENCE] Sufficiency level: {sufficiency_level}")

    # Block prediction if NO meaningful input
    if sufficiency_score == 0:
        return {
            "risk_score": 0.0,
            "risk_level": "Safe",
            "confidence_score": 0,
            "confidence_level": "Low",
            "text_probability": None,
            "shap_risk_factors": [],
            "shap_trust_factors": [],
            "url_analysis": None,
            "email_analysis": None,
            "sufficiency_level": sufficiency_level,
            "data_sufficiency_flag": True,
            "signals_used": {
                "text": False, "image": False, "url": False, "email": False,
            },
            "reasons": [
                "Insufficient input data. Please provide text, image, or URL.",
            ],
        }

    # ── 6. Fusion Engine ─────────────────────────────────────────
    fusion = fuse_signals(
        text_risk_score=text_risk_score if has_text else None,
        ocr_risk_score=ocr_result["ocr_risk_score"] if ocr_result else None,
        url_risk_score=url_result["url_risk_score"] if url_result else None,
        email_risk_score=email_result["email_risk_score"] if email_result else None,
        ocr_signal_strength=ocr_signal_strength,
        email_signal_strength=email_signal_strength,
        has_text=has_text,
        has_url=has_url,
        has_image=has_image,
        has_email=has_email,
    )

    risk_score = fusion["final_risk_score"]
    risk_level = classify_risk(risk_score)

    # ── 7. Data Sufficiency Flag ─────────────────────────────────
    data_sufficiency_flag = sufficiency_score <= 1

    # ── 8. Confidence Engine ─────────────────────────────────────
    confidence = compute_confidence(
        has_text=has_text,
        has_image=has_image,
        has_url=has_url,
        has_email=has_email,
        ocr_signal_strength=ocr_signal_strength,
        text_length=text_len,
        word_count=word_count,
        https_flag=url_result["https_flag"] if url_result else False,
        safe_browsing_status=safe_browsing_status,
        text_risk_score=text_risk_score if has_text else None,
        ocr_risk_score=ocr_result["ocr_risk_score"] if ocr_result else None,
        url_risk_score=url_result["url_risk_score"] if url_result else None,
        email_risk_score=email_result["email_risk_score"] if email_result else None,
        email_domain_matches_company=email_domain_matches,
        sufficiency_score=sufficiency_score,
    )

    # ── 9. Build legacy reasons list ─────────────────────────────
    reasons = []
    if text_result["text_probability"] is not None:
        prob_pct = round(text_result["text_probability"] * 100, 1)
        reasons.append(f"ML model fraud probability: {prob_pct}%")
    if keywords:
        reasons.append(f"Suspicious keywords detected: {', '.join(keywords)}")
    if url_result:
        if url_result.get("ip_flag"):
            reasons.append("URL uses raw IP address instead of domain")
        if not url_result.get("https_flag"):
            reasons.append("URL does not use HTTPS")
        if url_result.get("suspicious_tld_flag"):
            reasons.append("Domain uses a suspicious TLD")
        if url_result.get("blacklisted"):
            reasons.append("Domain is on the local blacklist")
        age = url_result.get("domain_age_days")
        if age is not None and age < 60:
            reasons.append(f"⚠️ Domain is very new ({age} days old)")
        elif age is not None and age < 180:
            reasons.append(f"Domain is relatively new ({age} days old)")
        pcr = url_result.get("page_content_risk_score")
        if pcr is not None and pcr > 50:
            reasons.append(f"Page content ML risk score: {pcr}%")
        if safe_browsing_status == "malicious":
            reasons.append("⚠️ Google Safe Browsing flagged this URL as malicious")
    if email_result:
        if email_result.get("disposable_flag"):
            reasons.append("⚠️ Email uses a disposable email provider")
        if email_result.get("free_provider_flag") and company:
            reasons.append("Email uses a free provider despite company being specified")
    if data_sufficiency_flag:
        reasons.append("⚠️ Limited data provided. Assessment may be unreliable.")
    if timeout_notes:
        reasons.append(
            f"Some verification checks skipped due to timeout: {', '.join(timeout_notes)}."
        )
    if not reasons:
        if risk_score < RISK_THRESHOLD_SUSPICIOUS:
            reasons.append("No significant fraud signals detected")
        else:
            reasons.append("Multiple heuristic signals contributed to the risk score")

    # ── 10. Assemble response (with sanity clamps) ────────────────
    final_risk = round(max(0, min(risk_score, 100)), 1)
    final_confidence = max(0, min(confidence["confidence_score"], 95))

    return {
        "risk_score": final_risk,
        "risk_level": risk_level,
        "confidence_score": final_confidence,
        "confidence_level": confidence["confidence_level"],
        "text_probability": text_result["text_probability"],
        "shap_risk_factors": text_result["shap_risk_factors"],
        "shap_trust_factors": text_result["shap_trust_factors"],
        "url_analysis": url_result,
        "email_analysis": email_result,
        "sufficiency_level": sufficiency_level,
        "data_sufficiency_flag": data_sufficiency_flag,
        "signals_used": {
            "text": has_text,
            "image": has_image,
            "url": has_url,
            "email": has_email,
        },
        "reasons": reasons,
    }
