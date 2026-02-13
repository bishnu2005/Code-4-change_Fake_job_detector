"""
Layer 2 — Community Intelligence.
Searches community reports by company name or domain.
Returns aggregated credibility score.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.community_report import CommunityReport
from app.schemas.analyze import CommunityResult

logger = logging.getLogger(__name__)


def get_community_intelligence(
    db: Session,
    company_name: str = "",
    domain: str = "",
) -> CommunityResult:
    """
    Aggregate community reports for a company/domain.
    Returns credibility score based on scam/legit ratio and vote quality.
    """
    result = CommunityResult()

    if not company_name and not domain:
        return result

    # Build query: match company_name OR domain
    query = db.query(CommunityReport)
    conditions = []
    if company_name:
        conditions.append(
            func.lower(CommunityReport.company_name).contains(company_name.lower())
        )
    if domain:
        conditions.append(
            func.lower(CommunityReport.domain).contains(domain.lower())
        )

    if conditions:
        from sqlalchemy import or_
        query = query.filter(or_(*conditions))

    reports = query.all()

    if not reports:
        return result

    result.total_reports = len(reports)
    result.scam_count = sum(1 for r in reports if r.verdict == "scam")
    result.legit_count = sum(1 for r in reports if r.verdict == "legit")

    if result.total_reports > 0:
        result.scam_ratio = round(result.scam_count / result.total_reports, 2)

    # Credibility score:
    # High score = community trusts it (many legit votes, few scam)
    # Low score = community suspects it (many scam votes)
    # Factors: report ratio + weighted by upvotes
    total_weight = 0
    legit_weight = 0
    for r in reports:
        weight = max(r.upvotes - r.downvotes, 0) + 1  # min weight = 1
        total_weight += weight
        if r.verdict == "legit":
            legit_weight += weight
        elif r.verdict == "suspicious":
            legit_weight += weight * 0.5  # partial credit

    if total_weight > 0:
        result.credibility_score = round((legit_weight / total_weight) * 100, 1)

    return result


def compute_company_credibility_score(
    db: Session,
    company_name: str,
) -> float:
    """
    Compute aggregated company credibility score for search/company pages.
    0 = very suspicious, 100 = very credible.
    """
    community = get_community_intelligence(db, company_name=company_name)

    if community.total_reports == 0:
        return 50.0  # neutral when no data

    # Base: credibility from community
    score = community.credibility_score

    # Boost confidence with more reports
    report_factor = min(community.total_reports / 10, 1.0)  # max at 10 reports
    # Push score further from 50 based on report volume
    score = 50 + (score - 50) * report_factor

    return round(max(0, min(score, 100)), 1)
