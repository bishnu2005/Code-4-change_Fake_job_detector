"""
Database engine and session factory.
Uses SQLite for development; swap DATABASE_URL for PostgreSQL in production.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Use env var (PostgreSQL) or fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
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
    # Import all models to ensure they are registered with Base metadata
    from app.models import company, scam_domain, community_report, user, domain_cache, vote  # noqa: F401
    
    # FRESH START: Drop all tables to ensure clean schema (as per production demo requirements)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
