"""Seed database with initial companies and known scam domains."""
import json
import os
import logging

from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.scam_domain import ScamDomain
from app.models.user import User
from app.models.community_report import CommunityReport

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


def seed_users(db: Session) -> dict:
    """Seed initial users and return a map of username -> user_id."""
    users = [
        {"username": "SecurityHawk", "reputation_score": 85.0, "google_id": "seed_1"},
        {"username": "JobSeeker_Pro", "reputation_score": 60.0, "google_id": "seed_2"},
        {"username": "AnonUser", "reputation_score": 40.0, "google_id": "seed_3"},
    ]

    user_map = {}
    for u_data in users:
        existing = db.query(User).filter_by(username=u_data["username"]).first()
        if not existing:
            new_user = User(**u_data)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_map[u_data["username"]] = new_user.id
        else:
            user_map[u_data["username"]] = existing.id
    
    logger.info(f"Seeded {len(user_map)} users.")
    return user_map


def seed_reports(db: Session, user_map: dict) -> int:
    """Seed realistic community reports."""
    if db.query(CommunityReport).count() > 0:
        logger.info("Reports already seeded, skipping.")
        return 0

    reports = [
        {
            "company_name": "Stripe",
            "domain": "stripe.com",
            "title": "Legit senior engineer role",
            "description": "Applied through official site. Interview process was professional and standard. Recruiter reached out via LinkedIn first.",
            "verdict": "legit",
            "user_id": user_map.get("SecurityHawk"),
            "upvotes": 45,
            "downvotes": 2
        },
        {
            "company_name": "TechFlow Solutions",
            "domain": "techflow-jobs.xyz",
            "title": "Fake job offer via Telegram",
            "description": "They asked for money for equipment before starting. The domain is extremely new. Be careful!",
            "verdict": "scam",
            "user_id": user_map.get("JobSeeker_Pro"),
            "upvotes": 120,
            "downvotes": 1
        },
        {
            "company_name": "Amazon Web Services",
            "domain": "aws.amazon.com",
            "title": "Standard hiring process",
            "description": "No red flags. Online assessment followed by loop interviews.",
            "verdict": "legit",
            "user_id": user_map.get("SecurityHawk"),
            "upvotes": 30,
            "downvotes": 0
        },
        {
            "company_name": "CryptoWealth Inc",
            "domain": "cryptowealth-instant.net",
            "title": "Ponzi scheme recruiting",
            "description": "Promising 200% returns for 'investment managers'. Complete scam.",
            "verdict": "scam",
            "user_id": user_map.get("AnonUser"),
            "upvotes": 88,
            "downvotes": 5
        },
        {
            "company_name": "Deloitte",
            "domain": "deloitte.com",
            "title": "Verifying recruiter email",
            "description": "Received email from @deloitte.com. Checked headers, seems authentic.",
            "verdict": "legit",
            "user_id": user_map.get("SecurityHawk"),
            "upvotes": 15,
            "downvotes": 0
        }
    ]

    count = 0
    for r_data in reports:
        if r_data["user_id"]:
            db.add(CommunityReport(**r_data))
            count += 1

    db.commit()
    logger.info(f"Seeded {count} community reports.")
    return count


def run_seed(db: Session):
    """Run all seeders."""
    seed_companies(db)
    seed_scam_domains(db)
    user_map = seed_users(db)
    seed_reports(db, user_map)
