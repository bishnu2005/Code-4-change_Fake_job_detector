"""
URL Verification Module: structural + reputation + WHOIS checks.
Returns None when no URL is provided.
"""
import ipaddress
import json
import os
import logging
from difflib import SequenceMatcher
from urllib.parse import urlparse

import requests

from app.config import SUSPICIOUS_TLDS, DOMAIN_BLACKLIST_PATH

logger = logging.getLogger(__name__)

# Load domain blacklist once
_blacklist: set[str] = set()
try:
    if os.path.exists(DOMAIN_BLACKLIST_PATH):
        with open(DOMAIN_BLACKLIST_PATH, "r") as f:
            _blacklist = set(json.load(f))
        logger.info(f"Loaded {len(_blacklist)} domains in blacklist.")
except Exception as e:
    logger.warning(f"Failed to load domain blacklist: {e}")


# ── Suspicious TLDs (strict inclusion list) ─────────────────────
SUSPICIOUS_TLD_SET = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".top", ".buzz", ".club", ".work", ".click",
    ".link", ".info", ".biz", ".icu", ".cam",
}

# ── Trusted TLDs ────────────────────────────────────────────────
TRUSTED_TLD_SET = {
    ".com", ".org", ".edu", ".gov", ".net", ".io",
    ".co", ".us", ".uk", ".ca", ".au", ".in",
}


def _is_ip_address(host: str) -> bool:
    """Check if host is an IP address using the ipaddress module."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _get_tld(domain: str) -> str:
    """Extract the TLD from a domain name."""
    parts = domain.rsplit(".", 1)
    if len(parts) == 2:
        return f".{parts[1]}"
    return ""


def _check_reachable(url: str) -> bool | None:
    """Check if URL is reachable using GET with redirects (3s timeout)."""
    try:
        resp = requests.get(
            url, timeout=3, allow_redirects=True,
            headers={"User-Agent": "FakeJobDetector/1.0"},
            stream=True,  # don't download full body
        )
        resp.close()
        return resp.status_code < 400
    except requests.RequestException:
        return False
    except Exception:
        return None


def _get_domain_age_days(domain: str) -> int | None:
    """
    Get domain age in days using python-whois.
    Returns None if WHOIS lookup fails.
    """
    try:
        import whois
        from datetime import datetime, timezone
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation is None:
            return None
        if creation.tzinfo is None:
            creation = creation.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return max((now - creation).days, 0)
    except Exception as e:
        logger.debug(f"WHOIS lookup failed for {domain}: {e}")
        return None


def _fetch_page_content(url: str) -> dict | None:
    """
    Lightweight page content analysis.
    Fetches HTML (3s timeout), extracts title, meta, visible text.
    Returns None on any failure.
    """
    try:
        resp = requests.get(
            url, timeout=3,
            headers={"User-Agent": "FakeJobDetector/1.0"},
            allow_redirects=True,
        )
        if resp.status_code >= 400:
            return None

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return None

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text[:50000], "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()[:200]

        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()[:500]

        # Extract visible text (max 5000 chars)
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        visible_text = soup.get_text(separator=" ", strip=True)[:5000]

        return {
            "title": title,
            "meta_description": meta_desc,
            "visible_text": visible_text,
        }
    except Exception as e:
        logger.debug(f"Page content fetch failed for {url}: {e}")
        return None


def verify_url(url: str, company_name: str = "") -> dict | None:
    """
    Perform structural + reputation URL verification.
    Returns None if no URL is provided — caller must treat as absent signal.
    """
    if not url or not url.strip():
        return None

    url_clean = url.strip()
    if not url_clean.startswith(("http://", "https://")):
        url_clean = "http://" + url_clean

    # Parse URL
    try:
        parsed = urlparse(url_clean)
    except Exception:
        return {
            "url_risk_score": 60.0,
            "url_trust_score": 0.0,
            "https_flag": False,
            "ip_flag": False,
            "reachable_flag": None,
            "suspicious_tld_flag": False,
            "domain_similarity_score": 0.0,
            "domain_age_days": None,
            "page_content_risk_score": None,
            "blacklisted": False,
            "extracted_domain": None,
        }

    domain = parsed.netloc
    if not domain:
        return {
            "url_risk_score": 60.0,
            "url_trust_score": 0.0,
            "https_flag": False,
            "ip_flag": False,
            "reachable_flag": None,
            "suspicious_tld_flag": False,
            "domain_similarity_score": 0.0,
            "domain_age_days": None,
            "page_content_risk_score": None,
            "blacklisted": False,
            "extracted_domain": None,
        }

    # Remove port if present
    domain_no_port = domain.split(":")[0]

    result = {
        "url_risk_score": 0.0,
        "url_trust_score": 0.0,
        "https_flag": False,
        "ip_flag": False,
        "reachable_flag": None,
        "suspicious_tld_flag": False,
        "domain_similarity_score": 0.0,
        "domain_age_days": None,
        "page_content_risk_score": None,
        "blacklisted": False,
        "extracted_domain": domain_no_port,
    }

    risk_points = 0
    trust_points = 0

    # ── HTTPS check ──────────────────────────────────────────────
    if parsed.scheme == "https":
        result["https_flag"] = True
        trust_points += 15
    else:
        risk_points += 10

    # ── Raw IP detection (using ipaddress module) ────────────────
    if _is_ip_address(domain_no_port):
        result["ip_flag"] = True
        risk_points += 25

    # ── HTTP reachability (GET + redirects) ──────────────────────
    reachable = _check_reachable(url_clean)
    result["reachable_flag"] = reachable
    if reachable is True:
        trust_points += 10
    elif reachable is False:
        risk_points += 10

    # ── Suspicious TLD (strict set) ──────────────────────────────
    tld = _get_tld(domain_no_port)
    if tld in SUSPICIOUS_TLD_SET:
        result["suspicious_tld_flag"] = True
        risk_points += 20
    elif tld in TRUSTED_TLD_SET:
        trust_points += 10

    # ── Domain similarity with company name ──────────────────────
    if company_name and company_name.strip():
        company_clean = company_name.strip().lower().replace(" ", "")
        domain_clean = domain_no_port.split(".")[0].lower()
        similarity = SequenceMatcher(None, company_clean, domain_clean).ratio()
        result["domain_similarity_score"] = round(similarity, 3)

        if similarity > 0.6:
            trust_points += 15
        elif similarity < 0.2:
            risk_points += 10

    # ── Blacklist check ──────────────────────────────────────────
    if domain_no_port in _blacklist:
        result["blacklisted"] = True
        risk_points += 30

    # ── WHOIS domain age scoring ─────────────────────────────────
    if not result["ip_flag"]:
        age_days = _get_domain_age_days(domain_no_port)
        result["domain_age_days"] = age_days
        if age_days is not None:
            if age_days < 60:
                risk_points += 25
            elif age_days < 180:
                risk_points += 10
            else:
                trust_points += 5

    # ── Lightweight page content analysis ────────────────────────
    if reachable is True:
        page = _fetch_page_content(url_clean)
        if page and page["visible_text"]:
            try:
                from app.models.model_loader import model_loader
                if model_loader.is_loaded:
                    from app.utils.helpers import clean_text
                    cleaned = clean_text(page["visible_text"])
                    X = model_loader.vectorizer.transform([cleaned])
                    if model_loader.calibrated_model:
                        prob = model_loader.calibrated_model.predict_proba(X)[0][1]
                    else:
                        prob = model_loader.model.predict_proba(X)[0][1]
                    page_risk = round(prob * 100, 1)
                    result["page_content_risk_score"] = page_risk
                    if page_risk > 50:
                        risk_points += 15
                    elif page_risk < 20:
                        trust_points += 10
            except Exception as e:
                logger.debug(f"Page content ML scoring failed: {e}")

    # ── Compute scores ───────────────────────────────────────────
    result["url_risk_score"] = round(min(risk_points, 100), 1)
    result["url_trust_score"] = round(min(trust_points, 100), 1)

    return result
