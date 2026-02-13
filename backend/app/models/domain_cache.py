"""Domain intelligence cache model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class DomainCache(Base):
    __tablename__ = "domain_intelligence_cache"

    domain = Column(String(255), primary_key=True)
    age_days = Column(Integer, nullable=True)
    blacklist_hits = Column(Integer, nullable=False, default=0)
    safe_browsing_status = Column(String(20), nullable=False, default="unknown")
    last_checked = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
