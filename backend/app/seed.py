"""Seed database with initial companies and known scam domains."""
import json
import os
import logging

from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.scam_domain import ScamDomain

logger = logging.getLogger(__name__)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def seed_companies(db: Session) -> int:
    """Seed trusted companies. Returns count added."""
    if db.query(Company).count() > 0:
        logger.info("Companies already seeded, skipping.")
        return 0

    path = os.path.join(_DATA_DIR, "seed_companies.json")
    if not os.path.exists(path):
        logger.warning(f"Seed file not found: {path}")
        return 0

    with open(path, "r") as f:
        data = json.load(f)

    count = 0
    for item in data:
        db.add(Company(
            name=item["name"],
            official_domain=item["domain"],
            verification_status="trusted",
        ))
        count += 1

    db.commit()
    logger.info(f"Seeded {count} trusted companies.")
    return count


def seed_scam_domains(db: Session) -> int:
    """Seed known scam domains. Returns count added."""
    if db.query(ScamDomain).count() > 0:
        logger.info("Scam domains already seeded, skipping.")
        return 0

    path = os.path.join(_DATA_DIR, "seed_scam_domains.json")
    if not os.path.exists(path):
        logger.warning(f"Seed file not found: {path}")
        return 0

    with open(path, "r") as f:
        data = json.load(f)

    count = 0
    for item in data:
        db.add(ScamDomain(
            domain=item["domain"],
            source=item.get("source", "seed"),
            risk_score=item.get("risk_score", 90.0),
        ))
        count += 1

    db.commit()
    logger.info(f"Seeded {count} known scam domains.")
    return count


def run_seed(db: Session):
    """Run all seeders."""
    seed_companies(db)
    seed_scam_domains(db)
