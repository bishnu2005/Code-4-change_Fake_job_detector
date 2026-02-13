"""
Database engine and session factory.
Uses SQLite for development; swap DATABASE_URL for PostgreSQL in production.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    # SQLite needs check_same_thread=False; PostgreSQL ignores this
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """FastAPI dependency: yields a DB session, auto-closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Safe to call multiple times."""
    from app.models import company, scam_domain, community_report, user, domain_cache, vote  # noqa: F401
    Base.metadata.create_all(bind=engine)
