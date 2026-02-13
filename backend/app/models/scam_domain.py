"""Known scam domains model."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database import Base


class ScamDomain(Base):
    __tablename__ = "known_scam_domains"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    source = Column(String(100), nullable=False, default="seed")
    risk_score = Column(Float, nullable=False, default=90.0)
    first_seen = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
