"""
Hybrid Search Service.
Combines internal DB search, community reports, and external web intelligence (mocked/API).
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.company import Company
from app.models.community_report import CommunityReport
# from app.utils.web_intelligence import fetch_web_mentions  # Future implementation

logger = logging.getLogger(__name__)

def hybrid_search(db: Session, query: str, limit: int = 10) -> dict:
    """
    Perform 3-layer search:
    1. Internal Verified Companies (Official Registry)
    2. Community Reports (Crowdsourced)
    3. Web Intelligence (Fallback/Supplement)
    
    Returns structured results.
    """
    if not query or len(query.strip()) < 2:
        return {"companies": [], "reports": [], "web_mentions": []}

    q = query.strip().lower()
    
    # Layer A: Internal DB Search
    # Exact or like match on company name or domain
    companies = db.query(Company).filter(
        or_(
            Company.name.ilike(f"%{q}%"),
            Company.official_domain.ilike(f"%{q}%")
        )
    ).limit(limit).all()
    
    company_results = [
        {
            "name": c.name,
            "domain": c.official_domain,
            "status": c.verification_status,
            "logo": c.logo_url
        }
        for c in companies
    ]
    
    # Layer B: Community Reports Search
    # Search in user-submitted reports for this company/domain
    reports = db.query(CommunityReport).filter(
        or_(
            CommunityReport.company_name.ilike(f"%{q}%"),
            CommunityReport.domain.ilike(f"%{q}%")
        )
    ).limit(limit).all()
    
    report_results = [
        {
            "company": r.company_name,
            "domain": r.domain,
            "verdict": r.verdict,
            # "scam_type": r.scam_type, # Removed as it doesn't exist on model
            "title": r.title,
            "upvotes": r.upvotes,
            "created_at": r.created_at.isoformat()
        }
        for r in reports
    ]
    
    # Layer C: Web Intelligence (Mocked for now)
    # If internal results are low, we'd trigger a web scrape or API call.
    web_mentions = []
    if len(company_results) + len(report_results) < 3:
        # Mock web results for "Google" etc if not found internally
        # In production, call Serper.dev or similar
        web_mentions = [
            {
                "source": "Reddit",
                "signal": "No major scam reports found recently."
            },
            {
                "source": "News",
                "signal": "Company mentioned in recent tech news positively."
            }
        ]

    return {
        "companies": company_results,
        "reports": report_results,
        "web_mentions": web_mentions,
        "meta": {
            "total_internal": len(company_results),
            "total_community": len(report_results)
        }
    }
