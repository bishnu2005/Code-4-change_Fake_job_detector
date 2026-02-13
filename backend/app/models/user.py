"""User model — simple username-based identity."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    reputation_score = Column(Float, nullable=False, default=50.0)
    report_count = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    reports = relationship("CommunityReport", back_populates="author")
    votes = relationship("Vote", back_populates="user")
