"""User model — Google OAuth2 identity."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    username = Column(String(100), nullable=False)  # Display name from Google
    avatar_url = Column(String(500), nullable=True)
    
    reputation_score = Column(Float, nullable=False, default=50.0)
    report_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reports = relationship("CommunityReport", back_populates="author")
    votes = relationship("Vote", back_populates="user")
