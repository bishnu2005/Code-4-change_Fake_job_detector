"""
Email Domain Verification Module
Analyzes recruiter email domains for fraud indicators.
"""

import re
from typing import Optional, Dict

# ── Free email providers (high risk for recruiters) ──────────────────────
FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "protonmail.com", "icloud.com", "aol.com", "mail.com",
    "yandex.com", "zoho.com", "gmx.com", "inbox.com",
    "live.com", "msn.com", "fastmail.com", "tutanota.com",
    "yahoo.co.in", "rediffmail.com",
}

# ── Leet-speak substitutions for lookalike detection ─────────────────────
LEET_MAP = {
    "0": "o", "1": "l", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "9": "g",
}

# ── Suspicious domain keywords ──────────────────────────────────────────
SUSPICIOUS_DOMAIN_WORDS = {
    "careers", "jobs", "hiring", "apply", "recruit",
    "employment", "vacancy", "opportunity", "fast", "now",
    "urgent", "immediate", "work", "income", "earn",
}

# ── Company name stopwords to remove during matching ─────────────────────
COMPANY_STOPWORDS = {
    "inc", "ltd", "llc", "corp", "corporation", "company",
    "co", "group", "holdings", "international", "pvt",
    "private", "limited", "the", "and", "&",
}

# ── Email regex ──────────────────────────────────────────────────────────
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def extract_email(text: str, contact_email: str = "") -> Optional[str]:
    """Extract email from structured field or raw text."""
    if contact_email and contact_email.strip():
        email = contact_email.strip().lower()
        if EMAIL_REGEX.fullmatch(email):
            return email

    if text:
        match = EMAIL_REGEX.search(text)
        if match:
            return match.group(0).lower()

    return None


def get_domain(email: str) -> str:
    """Extract domain from email address."""
    return email.split("@")[1].strip().lower()


def is_free_provider(domain: str) -> bool:
    """Check if domain is a known free email provider."""
    return domain in FREE_EMAIL_PROVIDERS


def normalize_company_name(name: str) -> str:
    """Normalize company name for comparison."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    words = [w for w in name.split() if w not in COMPANY_STOPWORDS]
    return "".join(words)


def normalize_domain_for_matching(domain: str) -> str:
    """Extract root domain and strip TLD, hyphens, filler words."""
    # Remove TLD (.com, .net, .org, etc.)
    base = domain.rsplit(".", 1)[0] if "." in domain else domain
    # Remove common filler words
    for word in SUSPICIOUS_DOMAIN_WORDS:
        base = base.replace(word, "")
    # Remove hyphens and dots
    base = base.replace("-", "").replace(".", "")
    return base


def decode_leet(text: str) -> str:
    """Convert leet-speak back to normal letters."""
    return "".join(LEET_MAP.get(ch, ch) for ch in text)


def check_domain_company_match(domain: str, company_name: str) -> bool:
    """Check if email domain matches company name."""
    if not company_name or not company_name.strip():
        return True  # Can't verify without company name

    norm_company = normalize_company_name(company_name)
    norm_domain = normalize_domain_for_matching(domain)
    decoded_domain = decode_leet(norm_domain)

    if not norm_company or not norm_domain:
        return True

    # Direct substring match
    if norm_company in norm_domain or norm_domain in norm_company:
        return True

    # Decoded leet match
    if norm_company in decoded_domain or decoded_domain in norm_company:
        return True

    # Partial match (first 4+ chars)
    if len(norm_company) >= 4 and len(norm_domain) >= 4:
        if norm_company[:4] == norm_domain[:4]:
            return True
        if norm_company[:4] == decoded_domain[:4]:
            return True

    return False


def detect_lookalike(domain: str) -> bool:
    """Detect suspicious lookalike domain patterns."""
    base = domain.rsplit(".", 1)[0] if "." in domain else domain

    # Check for leet-speak: only flag mixed alpha+digit segments
    segments = re.split(r"[.\-]", base)
    has_leet = False
    for seg in segments:
        if seg.isdigit() or seg.isalpha():
            continue
        if seg and any(c.isdigit() for c in seg) and any(c.isalpha() for c in seg):
            has_leet = True
            break

    if has_leet:
        decoded = decode_leet(base)
        if decoded != base:
            return True

    # Excessive hyphens (e.g., google-careers-jobs-apply.com)
    if base.count("-") >= 3:
        return True

    # Count suspicious filler words in domain
    suspicious_count = sum(1 for word in SUSPICIOUS_DOMAIN_WORDS if word in base)
    if suspicious_count >= 2:
        return True

    # Very long domains are suspicious
    if len(base) > 30:
        return True

    return False


def analyze_email_domain(
    contact_email: str = "",
    raw_text: str = "",
    company_name: str = "",
) -> Dict:
    """
    Full email domain analysis. Returns dict with:
      - email_found, email, email_domain
      - free_provider, domain_matches_company, suspicious_pattern
      - domain_risk_score (0–25 contribution to rule engine)
    """
    result = {
        "email_found": False,
        "email": "",
        "email_domain": "",
        "free_provider": False,
        "domain_matches_company": True,
        "suspicious_pattern": False,
        "domain_risk_score": 0,
    }

    email = extract_email(raw_text, contact_email)
    if not email:
        return result

    domain = get_domain(email)
    result["email_found"] = True
    result["email"] = email
    result["email_domain"] = domain

    # Free provider check
    if is_free_provider(domain):
        result["free_provider"] = True
        result["domain_risk_score"] += 15

    # Company-domain match
    if not check_domain_company_match(domain, company_name):
        result["domain_matches_company"] = False
        result["domain_risk_score"] += 12

    # Lookalike detection
    if detect_lookalike(domain):
        result["suspicious_pattern"] = True
        result["domain_risk_score"] += 10

    # Cap domain risk contribution
    result["domain_risk_score"] = min(result["domain_risk_score"], 25)

    return result
