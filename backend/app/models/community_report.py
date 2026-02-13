"""Community report model — Reddit-style posts."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    verdict = Column(
        String(20), nullable=False, default="suspicious"
    )  # scam | legit | suspicious
    upvotes = Column(Integer, nullable=False, default=0)
    downvotes = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
    author = relationship("User", back_populates="reports")
    votes = relationship("Vote", back_populates="report", cascade="all, delete-orphan")
