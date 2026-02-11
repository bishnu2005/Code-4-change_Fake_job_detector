"""
Text processor: keyword detection, salary analysis, and URL/domain credibility.
"""
import re
import logging
import requests
from urllib.parse import urlparse

from app.config import SUSPICIOUS_KEYWORDS, SUSPICIOUS_TLDS, MAX_REASONABLE_SALARY, MIN_REASONABLE_SALARY
from app.utils.helpers import clean_text, extract_salary, extract_domain

logger = logging.getLogger(__name__)


def detect_suspicious_keywords(text: str) -> list[str]:
    """Return list of suspicious keywords found in the text."""
    text_lower = text.lower()
    found = []
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    return found


def analyze_salary(salary_text: str) -> dict:
    """
    Analyze salary field for anomalies.
    Returns dict with 'is_suspicious', 'reason', and 'amounts'.
    """
    result = {"is_suspicious": False, "reason": None, "amounts": []}

    if not salary_text:
        return result

    amounts = extract_salary(salary_text)
    result["amounts"] = amounts

    if not amounts:
        return result

    max_amount = max(amounts)
    min_amount = min(amounts)

    if max_amount > MAX_REASONABLE_SALARY:
        result["is_suspicious"] = True
        result["reason"] = f"Unrealistically high salary detected (${max_amount:,.0f})"
    elif min_amount < MIN_REASONABLE_SALARY and max_amount < MIN_REASONABLE_SALARY:
        result["is_suspicious"] = True
        result["reason"] = f"Suspiciously low salary detected (${min_amount:,.0f})"

    return result


def analyze_url(url: str) -> dict:
    """
    Analyze a URL/domain for credibility issues.
    Returns dict with 'is_suspicious', 'reasons'.
    """
    result = {"is_suspicious": False, "reasons": []}

    if not url:
        return result

    # Normalize
    url_lower = url.strip().lower()
    if not url_lower.startswith(("http://", "https://")):
        url_lower = "http://" + url_lower

    try:
        parsed = urlparse(url_lower)
    except Exception:
        result["is_suspicious"] = True
        result["reasons"].append("Malformed URL")
        return result

    domain = parsed.netloc

    # Check for raw IP address
    ip_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}(:\d+)?$")
    if ip_pattern.match(domain):
        result["is_suspicious"] = True
        result["reasons"].append("URL uses a raw IP address instead of a domain name")

    # Check for missing HTTPS
    if parsed.scheme != "https":
        result["reasons"].append("URL does not use HTTPS")

    # Check for suspicious TLDs
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            result["is_suspicious"] = True
            result["reasons"].append(f"Suspicious domain TLD: {tld}")
            break

    # Optional: quick reachability check
    try:
        resp = requests.head(url_lower, timeout=3, allow_redirects=True)
        if resp.status_code >= 400:
            result["is_suspicious"] = True
            result["reasons"].append(f"URL returned HTTP {resp.status_code}")
    except requests.RequestException:
        result["reasons"].append("URL is unreachable or timed out")

    if result["reasons"]:
        result["is_suspicious"] = True

    return result
