"""
Shared utility functions.
"""
import re
from urllib.parse import urlparse


def clean_text(text: str) -> str:
    """Lowercase, strip HTML, collapse whitespace."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)       # strip HTML tags
    text = re.sub(r"http\S+", " ", text)        # strip URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text) # keep alphanumeric
    text = re.sub(r"\s+", " ", text).strip()    # collapse whitespace
    return text.lower()


def extract_salary(text: str) -> list[float]:
    """Extract numeric salary figures from text via regex."""
    patterns = [
        r"\$\s?([\d,]+(?:\.\d+)?)",                        # $120,000
        r"([\d,]+(?:\.\d+)?)\s*(?:per\s+year|\/yr|\/year)", # 120000 per year
        r"([\d,]+(?:\.\d+)?)\s*(?:per\s+month|\/mo|\/month)",  # 10000 per month
        r"([\d,]+)\s*-\s*([\d,]+)",                          # 80,000 - 120,000
    ]
    amounts: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            for group in match.groups():
                if group:
                    try:
                        val = float(group.replace(",", ""))
                        amounts.append(val)
                    except ValueError:
                        continue
    return amounts


def extract_domain(url: str) -> str | None:
    """Extract domain from a URL string."""
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    try:
        parsed = urlparse(url)
        return parsed.netloc or None
    except Exception:
        return None


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Clamp a value between low and high."""
    return max(low, min(high, value))
