"""
Email Verification Module: structural checks on email addresses.
Returns None when no email is found.

Signal strength levels:
  0.0  → no email found
  0.5  → free provider only
  0.75 → corporate domain but low similarity to company
  1.0  → disposable domain or strong mismatch
"""
import re
import logging
from difflib import SequenceMatcher
from functools import lru_cache

from app.config import MX_LOOKUP_TIMEOUT

logger = logging.getLogger(__name__)

# ── Disposable email domains ────────────────────────────────────
DISPOSABLE_DOMAINS = {
    "tempmail.com", "throwaway.email", "guerrillamail.com",
    "mailinator.com", "yopmail.com", "sharklasers.com",
    "guerrillamailblock.com", "grr.la", "dispostable.com",
    "trashmail.com", "10minutemail.com", "temp-mail.org",
    "fakeinbox.com", "mailnesia.com", "maildrop.cc",
    "discard.email", "tmpmail.net", "tmpmail.org",
    "getnada.com", "emailondeck.com", "burnermail.io",
}

# ── Free email providers ────────────────────────────────────────
FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "aol.com", "protonmail.com", "icloud.com", "mail.com",
    "zoho.com", "yandex.com", "gmx.com", "live.com",
    "rediffmail.com", "inbox.com",
}

# ── Email regex ─────────────────────────────────────────────────
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _extract_emails(text: str) -> list[str]:
    """Extract all email addresses from text."""
    if not text:
        return []
    return list(set(_EMAIL_RE.findall(text)))


@lru_cache(maxsize=128)
def _check_mx_record_cached(domain: str) -> bool | None:
    """Check if domain has MX records with timeout and caching."""
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.lifetime = MX_LOOKUP_TIMEOUT
        resolver.timeout = MX_LOOKUP_TIMEOUT
        answers = resolver.resolve(domain, "MX")
        return len(answers) > 0
    except dns.resolver.Timeout:
        logger.debug(f"MX lookup timeout for {domain}")
        return None  # neutral on timeout
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoAnswer:
        return False
    except Exception:
        return None  # neutral on unknown error


def _compute_email_signal_strength(
    disposable: bool,
    free_provider: bool,
    similarity: float,
    company_provided: bool,
) -> float:
    """
    Compute email signal strength:
      0.0 → no email (handled upstream)
      0.5 → free provider only (low signal)
      0.75 → corporate but low similarity to company
      1.0 → disposable or strong mismatch
    """
    if disposable:
        return 1.0
    if company_provided and not free_provider and similarity < 0.2:
        return 1.0  # strong mismatch
    if free_provider:
        return 0.5
    if company_provided and similarity < 0.4:
        return 0.75
    return 0.5  # default: moderate signal


def verify_email(text: str, company_name: str = "") -> dict | None:
    """
    Extract and verify email addresses from text.
    Returns None if no emails found.
    """
    emails = _extract_emails(text)
    if not emails:
        return None

    # Analyze first (most relevant) email
    email = emails[0]
    _, domain = email.rsplit("@", 1)
    domain_lower = domain.lower()
    company_provided = bool(company_name and company_name.strip())

    result = {
        "email_address": email,
        "email_domain": domain_lower,
        "email_risk_score": 0.0,
        "email_signal_strength": 0.0,
        "disposable_flag": False,
        "free_provider_flag": False,
        "domain_similarity_score": 0.0,
        "mx_record_exists": None,
    }

    risk_points = 0

    # 1. Disposable domain check
    if domain_lower in DISPOSABLE_DOMAINS:
        result["disposable_flag"] = True
        risk_points += 40

    # 2. Free provider check
    if domain_lower in FREE_PROVIDERS:
        result["free_provider_flag"] = True
        if company_provided:
            risk_points += 15

    # 3. Domain similarity with company name
    similarity = 0.0
    if company_provided:
        company_clean = company_name.strip().lower().replace(" ", "")
        domain_name = domain_lower.split(".")[0]
        similarity = SequenceMatcher(None, company_clean, domain_name).ratio()
        result["domain_similarity_score"] = round(similarity, 3)

        if similarity > 0.6:
            pass  # good match, no penalty
        elif similarity < 0.2 and not result["free_provider_flag"]:
            risk_points += 15

    # 4. MX record check (cached, with timeout)
    mx_exists = _check_mx_record_cached(domain_lower)
    result["mx_record_exists"] = mx_exists
    if mx_exists is False:  # explicitly False, not None (timeout)
        risk_points += 20

    # Clamp risk score
    result["email_risk_score"] = round(min(max(risk_points, 0), 100), 1)

    # Compute signal strength
    result["email_signal_strength"] = _compute_email_signal_strength(
        result["disposable_flag"],
        result["free_provider_flag"],
        similarity,
        company_provided,
    )

    return result
