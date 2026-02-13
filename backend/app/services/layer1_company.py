"""
Layer 1 — Fast Company Verification.
Looks up company in trusted registry and checks domain match.
Can terminate pipeline early if company is verified or flagged.
"""
import logging
from difflib import SequenceMatcher
from urllib.parse import urlparse

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
    result.status = best_match.verification_status

    # If flagged, return immediately
    if best_match.verification_status == "flagged":
        return result, True

    # Check domain match if URL provided
    if url and url.strip():
        url_clean = url.strip()
        if not url_clean.startswith(("http://", "https://")):
            url_clean = "http://" + url_clean
        try:
            parsed = urlparse(url_clean)
            submitted_domain = parsed.netloc.split(":")[0].lower()
            official = best_match.official_domain.lower()

            # Match: domain ends with official domain
            result.domain_match = (
                submitted_domain == official
                or submitted_domain.endswith("." + official)
            )
        except Exception:
            result.domain_match = None

    # Decisive if trusted + domain matches
    decisive = (
        best_match.verification_status == "trusted"
        and result.domain_match is True
    )

    return result, decisive
