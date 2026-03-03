"""
Layer 1 — Fast Company Verification.
Looks up company in trusted registry and checks domain match.
Can terminate pipeline early if company is verified or flagged.
"""
import logging
from difflib import SequenceMatcher
from urllib.parse import urlparse
import re

from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.analyze import VerificationResult

logger = logging.getLogger(__name__)


def verify_company(
    db: Session,
    company_name: str,
    url: str = "",
) -> tuple[VerificationResult, bool]:
    """
    Check company against trusted registry.

    Returns:
        (result, decisive) — decisive=True means pipeline can stop here.
    """
    result = VerificationResult()

    if not company_name or not company_name.strip():
        return result, False

    clean_name = company_name.strip()
    result.company_name = clean_name

    # Search by name (case-insensitive fuzzy match)
    companies = db.query(Company).all()
    best_match: Company | None = None
    best_score = 0.0

    for c in companies:
        score = SequenceMatcher(
            None, clean_name.lower(), c.name.lower()
        ).ratio()
        if score > best_score:
            best_score = score
            best_match = c

    # Require >70% name match to consider it a match
    if best_match is None or best_score < 0.7:
        result.status = "unknown"
        return result, False

    result.company_name = best_match.name
    result.official_domain = best_match.official_domain
    # Strip protocol and www from official domain for clean comparison
    official_clean = _normalize_domain(best_match.official_domain)
    
    result.status = best_match.verification_status

    # If flagged, return immediately
    if best_match.verification_status == "flagged":
        return result, True

    # Check domain match if URL provided
    if url and url.strip():
        url_input = url.strip()
        # Add protocol if missing for parsing
        if not url_input.startswith(("http://", "https://")):
            url_input = "http://" + url_input
            
        try:
            parsed = urlparse(url_input)
            # Get netloc (domain) and strip www.
            submitted_domain = parsed.netloc.split(":")[0].lower()
            if submitted_domain.startswith("www."):
                submitted_domain = submitted_domain[4:]
                
            # Match Logic:
            # 1. Exact match
            # 2. Valid subdomain (ends with .official_domain)
            is_valid_match = (
                submitted_domain == official_clean or 
                submitted_domain.endswith("." + official_clean)
            )
            
            result.domain_match = is_valid_match
            
            # Deceptive Domain Check
            # If the domain is NOT a valid match, but contains the company name or official domain parts,
            # it might be deceptive (e.g. google-careers.xyz).
            # Deceptive Domain Check
            # If the domain is NOT a valid match, but contains the company name or official domain parts,
            # it might be deceptive (e.g. google-careers.xyz).
            if not is_valid_match:
                # Simple heuristic: if official domain (without TLD) is present in submitted domain
                official_stem = official_clean.split('.')[0]
                if len(official_stem) > 3 and official_stem in submitted_domain:
                    result.deceptive = True
                    # We could also add a risk boost later in the pipeline based on this flag

        except Exception:
            result.domain_match = None

    # Decisive if trusted + domain matches
    decisive = (
        best_match.verification_status == "trusted"
        and result.domain_match is True
    )

    return result, decisive


def _normalize_domain(domain: str) -> str:
    """Strip protocol, www, and path."""
    if not domain:
        return ""
    d = domain.lower().strip()
    if d.startswith("http://"):
        d = d[7:]
    elif d.startswith("https://"):
        d = d[8:]
    if d.startswith("www."):
        d = d[4:]
    return d.split('/')[0]
