"""Company model — trusted company registry."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    official_domain = Column(String(255), nullable=False)
    verification_status = Column(
        String(20), nullable=False, default="trusted"
    )  # trusted | unknown | flagged
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
