"""Vote model — prevents duplicate votes per user per report."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("community_reports.id"), nullable=False)
    vote_type = Column(String(10), nullable=False)  # "up" | "down"
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Prevent duplicate votes
    __table_args__ = (
        UniqueConstraint("user_id", "report_id", name="uq_user_report_vote"),
    )

    # Relationships
    user = relationship("User", back_populates="votes")
    report = relationship("CommunityReport", back_populates="votes")
