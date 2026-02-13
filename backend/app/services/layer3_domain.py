"""
Layer 3 — Domain Intelligence.
WHOIS age, blacklist, Safe Browsing, similarity, TLD check.
Results cached in domain_intelligence_cache table.
"""
import ipaddress
import logging
from datetime import datetime, timezone
from difflib import SequenceMatcher
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Session

from app.models.scam_domain import ScamDomain
from app.models.domain_cache import DomainCache
from app.schemas.analyze import DomainResult
from app.config import SAFE_BROWSING_API_KEY, SAFE_BROWSING_TIMEOUT

logger = logging.getLogger(__name__)

SUSPICIOUS_TLDS = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".top", ".buzz", ".club", ".work", ".click",
    ".link", ".info", ".biz", ".icu", ".cam",
}
TRUSTED_TLDS = {
    ".com", ".org", ".edu", ".gov", ".net", ".io",
    ".co", ".us", ".uk", ".ca", ".au", ".in",
}


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _get_tld(domain: str) -> str:
    parts = domain.rsplit(".", 1)
    return f".{parts[1]}" if len(parts) == 2 else ""


def _whois_age(domain: str) -> int | None:
    try:
        import whois
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation is None:
            return None
        if creation.tzinfo is None:
            creation = creation.replace(tzinfo=timezone.utc)
        return max((datetime.now(timezone.utc) - creation).days, 0)
    except Exception:
        return None


def _check_reachable(url: str) -> bool | None:
    try:
        resp = requests.get(
            url, timeout=3, allow_redirects=True,
            headers={"User-Agent": "HireLiar/1.0"}, stream=True,
        )
        resp.close()
        return resp.status_code < 400
    except Exception:
        return False


def _safe_browsing_check(url: str) -> str:
    if not SAFE_BROWSING_API_KEY:
        return "skipped"
    try:
        api_url = (
            "https://safebrowsing.googleapis.com/v4/threatMatches:find"
            f"?key={SAFE_BROWSING_API_KEY}"
        )
        payload = {
            "client": {"clientId": "hireliar", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        resp = requests.post(api_url, json=payload, timeout=SAFE_BROWSING_TIMEOUT)
        if resp.status_code == 200:
            return "malicious" if resp.json().get("matches") else "clean"
        return "error"
    except Exception:
        return "skipped"


def analyze_domain(
    db: Session,
    url: str,
    company_name: str = "",
) -> DomainResult:
    """Full domain intelligence analysis with DB caching."""
    result = DomainResult()
    if not url or not url.strip():
        return result

    url_clean = url.strip()
    if not url_clean.startswith(("http://", "https://")):
        url_clean = "http://" + url_clean

    try:
        parsed = urlparse(url_clean)
        domain = parsed.netloc.split(":")[0].lower()
    except Exception:
        return result

    if not domain:
        return result

    result.extracted_domain = domain
    result.https = parsed.scheme == "https"

    # Check IP
    if _is_ip(domain):
        result.domain_mismatch = True
        return result

    # Check cache first
    cached = db.query(DomainCache).filter(DomainCache.domain == domain).first()
    cache_fresh = False
    if cached:
        age = (datetime.now(timezone.utc) - cached.last_checked.replace(tzinfo=timezone.utc)).total_seconds()
        if age < 86400:  # 24 hour cache
            cache_fresh = True
            result.age_days = cached.age_days
            result.blacklist_hits = cached.blacklist_hits
            result.safe_browsing = cached.safe_browsing_status

    if not cache_fresh:
        # WHOIS
        result.age_days = _whois_age(domain)

        # Blacklist check
        result.blacklist_hits = db.query(ScamDomain).filter(
            ScamDomain.domain == domain
        ).count()

        # Safe Browsing
        result.safe_browsing = _safe_browsing_check(url_clean)

        # Update cache
        if cached:
            cached.age_days = result.age_days
            cached.blacklist_hits = result.blacklist_hits
            cached.safe_browsing_status = result.safe_browsing
            cached.last_checked = datetime.now(timezone.utc)
        else:
            db.add(DomainCache(
                domain=domain,
                age_days=result.age_days,
                blacklist_hits=result.blacklist_hits,
                safe_browsing_status=result.safe_browsing,
            ))
        db.commit()

    # Reachability (not cached — cheap)
    result.reachable = _check_reachable(url_clean)

    # TLD check
    tld = _get_tld(domain)
    result.suspicious_tld = tld in SUSPICIOUS_TLDS

    # Domain similarity
    if company_name:
        company_clean = company_name.strip().lower().replace(" ", "")
        domain_stem = domain.split(".")[0]
        result.similarity_score = round(
            SequenceMatcher(None, company_clean, domain_stem).ratio(), 3
        )
        result.domain_mismatch = result.similarity_score < 0.3

    return result
