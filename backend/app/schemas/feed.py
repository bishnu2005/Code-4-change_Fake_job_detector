"""Pydantic schemas for community feed endpoints."""
from pydantic import BaseModel, Field
from datetime import datetime


# ── Request schemas ──────────────────────────────────────────────

class CreateReportRequest(BaseModel):
    """POST /feed — create a community report."""
    user_id: int
    company_name: str = Field(..., min_length=1, max_length=255)
    domain: str | None = Field(default=None, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    verdict: str = Field(
        default="suspicious",
        pattern="^(scam|legit|suspicious)$",
    )


class VoteRequest(BaseModel):
    """POST /feed/{id}/vote."""
    user_id: int
    vote_type: str = Field(..., pattern="^(up|down)$")


# ── Response schemas ─────────────────────────────────────────────

class ReportAuthor(BaseModel):
    id: int
    username: str
    reputation_score: float

    class Config:
        from_attributes = True


class FeedPost(BaseModel):
    """Single feed post in response."""
    id: int
    company_name: str
    domain: str | None
    title: str
    description: str
    verdict: str
    upvotes: int
    downvotes: int
    created_at: datetime
    author: ReportAuthor

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    """GET /feed response with cursor pagination."""
    posts: list[FeedPost]
    next_cursor: int | None = None
    total_count: int = 0


class VoteResponse(BaseModel):
    """Response after voting."""
    report_id: int
    upvotes: int
    downvotes: int
    user_vote: str
