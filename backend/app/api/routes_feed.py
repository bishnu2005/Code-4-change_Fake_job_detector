"""
Feed API routes — community reports, voting, search.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.community_report import CommunityReport
from app.models.user import User
from app.models.vote import Vote
from app.schemas.feed import (
    CreateReportRequest, VoteRequest,
    FeedPost, FeedResponse, VoteResponse,
)
from app.services.layer2_community import compute_company_credibility_score

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feed", tags=["Community Feed"])


@router.get("", response_model=FeedResponse)
def get_feed(
    cursor: int | None = Query(default=None, description="Cursor for pagination (report ID)"),
    limit: int = Query(default=20, ge=1, le=50),
    filter: str = Query(default="all", pattern="^(all|scam|legit|suspicious|newest|credible)$"),
    search: str = Query(default="", description="Search by company or domain"),
    db: Session = Depends(get_db),
):
    """Get community feed with cursor-based pagination."""
    query = db.query(CommunityReport)

    # Search filter
    if search:
        from sqlalchemy import or_
        search_lower = search.lower()
        query = query.filter(
            or_(
                func.lower(CommunityReport.company_name).contains(search_lower),
                func.lower(CommunityReport.domain).contains(search_lower),
                func.lower(CommunityReport.title).contains(search_lower),
            )
        )

    # Verdict filter
    if filter in ("scam", "legit", "suspicious"):
        query = query.filter(CommunityReport.verdict == filter)

    # Cursor pagination
    if cursor is not None:
        query = query.filter(CommunityReport.id < cursor)

    # Ordering
    if filter == "credible":
        query = query.order_by(
            (CommunityReport.upvotes - CommunityReport.downvotes).desc()
        )
    else:
        query = query.order_by(CommunityReport.id.desc())

    total = query.count()
    posts = query.limit(limit).all()

    next_cursor = posts[-1].id if len(posts) == limit else None

    return FeedResponse(
        posts=[FeedPost.model_validate(p) for p in posts],
        next_cursor=next_cursor,
        total_count=total,
    )


@router.post("", response_model=FeedPost, status_code=201)
def create_report(
    body: CreateReportRequest,
    db: Session = Depends(get_db),
):
    """Create a new community report."""
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    report = CommunityReport(
        user_id=body.user_id,
        company_name=body.company_name,
        domain=body.domain,
        title=body.title,
        description=body.description,
        verdict=body.verdict,
    )
    db.add(report)

    # Update user report count
    user.report_count += 1

    db.commit()
    db.refresh(report)

    return FeedPost.model_validate(report)


@router.post("/{report_id}/vote", response_model=VoteResponse)
def vote_on_report(
    report_id: int,
    body: VoteRequest,
    db: Session = Depends(get_db),
):
    """Upvote or downvote a community report. Prevents duplicate votes."""
    report = db.query(CommunityReport).filter(CommunityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check for existing vote
    existing = db.query(Vote).filter(
        Vote.user_id == body.user_id,
        Vote.report_id == report_id,
    ).first()

    if existing:
        if existing.vote_type == body.vote_type:
            raise HTTPException(status_code=409, detail="Already voted")
        # Change vote direction
        if existing.vote_type == "up":
            report.upvotes = max(report.upvotes - 1, 0)
            report.downvotes += 1
        else:
            report.downvotes = max(report.downvotes - 1, 0)
            report.upvotes += 1
        existing.vote_type = body.vote_type
    else:
        # New vote
        db.add(Vote(
            user_id=body.user_id,
            report_id=report_id,
            vote_type=body.vote_type,
        ))
        if body.vote_type == "up":
            report.upvotes += 1
        else:
            report.downvotes += 1

    # Adjust author reputation
    author = db.query(User).filter(User.id == report.user_id).first()
    if author:
        if body.vote_type == "up":
            author.reputation_score = min(author.reputation_score + 0.5, 100)
        else:
            author.reputation_score = max(author.reputation_score - 0.3, 0)

    db.commit()
    db.refresh(report)

    return VoteResponse(
        report_id=report.id,
        upvotes=report.upvotes,
        downvotes=report.downvotes,
        user_vote=body.vote_type,
    )


@router.get("/search/company", response_model=dict)
def search_company_credibility(
    company: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    """Search and return company credibility score."""
    score = compute_company_credibility_score(db, company)
    from app.services.layer2_community import get_community_intelligence
    community = get_community_intelligence(db, company_name=company)

    return {
        "company_name": company,
        "credibility_score": score,
        "total_reports": community.total_reports,
        "scam_ratio": community.scam_ratio,
    }
