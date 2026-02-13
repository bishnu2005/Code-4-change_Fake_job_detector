"""
Layer 5 — Conditional Deep Content Analysis.
Only fires if suspicious signals found in Layers 1-3.
Fetches page content and scans for fraud heuristic keywords.
"""
import logging
import requests
from app.schemas.analyze import ContentAnalysisResult, DomainResult

logger = logging.getLogger(__name__)

# Heuristic red-flag keywords
HEURISTIC_FLAGS = {
    "telegram": "Telegram channel reference",
    "crypto": "Cryptocurrency mention",
    "bitcoin": "Bitcoin mention",
    "upfront payment": "Requests upfront payment",
    "registration fee": "Asks for registration fee",
    "gift card": "Gift card payment request",
    "bank details": "Asks for bank details",
    "wire transfer": "Wire transfer request",
    "guaranteed income": "Guaranteed income claim",
    "whatsapp": "WhatsApp contact (not official channel)",
    "no interview": "No interview required",
    "act now": "Urgency pressure tactic",
    "limited time": "Artificial scarcity",
    "easy money": "Unrealistic income promise",
    "work from home guaranteed": "Guaranteed WFH claim",
}


def _should_trigger(domain: DomainResult) -> bool:
    """Only run deep analysis if domain has suspicious signals."""
    if domain.age_days is not None and domain.age_days < 180:
        return True
    if domain.suspicious_tld:
        return True
    if domain.domain_mismatch:
        return True
    if domain.blacklist_hits > 0:
        return True
    if domain.safe_browsing == "malicious":
        return True
    return False


def analyze_content(
    url: str,
    domain_result: DomainResult,
) -> ContentAnalysisResult:
    """
    Fetch page content and run heuristic keyword scan.
    Only triggers if domain has suspicious signals.
    """
    result = ContentAnalysisResult()

    if not url or not url.strip():
        return result

    if not _should_trigger(domain_result):
        return result

    url_clean = url.strip()
    if not url_clean.startswith(("http://", "https://")):
        url_clean = "http://" + url_clean

    try:
        resp = requests.get(
            url_clean, timeout=5,
            headers={"User-Agent": "HireLiar/1.0"},
            allow_redirects=True,
        )
        if resp.status_code >= 400:
            return result

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return result

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text[:50000], "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        visible = soup.get_text(separator=" ", strip=True)[:5000].lower()

        result.triggered = True

        # Scan for heuristic flags
        for keyword, label in HEURISTIC_FLAGS.items():
            if keyword in visible:
                result.heuristic_flags.append(label)

        # Risk boost: 5 per flag, max 25
        result.risk_boost = min(len(result.heuristic_flags) * 5, 25)

    except Exception as e:
        logger.debug(f"Deep content analysis failed: {e}")

    return result
