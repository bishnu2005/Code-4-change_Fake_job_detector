"""
MongoDB Community Reporting Module
Handles connection, report storage, and reputation queries.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ── MongoDB Client (lazy init) ───────────────────────────────────────────
_client = None
_db = None


def _get_db():
    """Lazy-init MongoDB connection from MONGO_URI env var."""
    global _client, _db
    if _db is not None:
        return _db

    uri = os.environ.get("MONGO_URI", "")
    if not uri:
        return None

    try:
        from pymongo import MongoClient
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Ping to verify connection
        _client.admin.command("ping")
        _db = _client["scam_reports_db"]

        # Ensure indexes
        _db["reports"].create_index("entity_value")
        _db["reports"].create_index("entity_type")
        _db["reports"].create_index("created_at")
        _db["reports"].create_index([("entity_value", 1), ("reporter_ip", 1)])

        print("✅ MongoDB connected: scam_reports_db")
        return _db
    except Exception as e:
        print(f"⚠️ MongoDB not available: {e}")
        _client = None
        _db = None
        return None


def is_connected() -> bool:
    """Check if MongoDB is available."""
    return _get_db() is not None


# ── Report Operations ────────────────────────────────────────────────────

def submit_report(
    entity_type: str,
    entity_value: str,
    report_reason: str,
    reporter_ip: str,
) -> Dict:
    """
    Submit a scam report. Returns status dict.
    Prevents duplicate from same IP within 24 hours.
    """
    db = _get_db()
    if db is None:
        return {"success": False, "message": "Database not available", "total_reports": 0}

    # Normalize
    entity_value = entity_value.strip().lower()
    entity_type = entity_type.strip().lower()
    report_reason = report_reason.strip()[:500]  # Cap at 500 chars

    # Validate entity_type
    if entity_type not in ("company", "email", "url"):
        return {"success": False, "message": "Invalid entity_type. Must be company, email, or url.", "total_reports": 0}

    if not entity_value:
        return {"success": False, "message": "entity_value is required.", "total_reports": 0}

    try:
        # Duplicate check — same IP + same entity within 24h
        cutoff = datetime.utcnow() - timedelta(hours=24)
        existing = db["reports"].find_one({
            "entity_value": entity_value,
            "entity_type": entity_type,
            "reporter_ip": reporter_ip,
            "created_at": {"$gte": cutoff},
        })

        if existing:
            total = db["reports"].count_documents({
                "entity_value": entity_value,
                "entity_type": entity_type,
            })
            return {
                "success": False,
                "message": "You have already reported this entity in the last 24 hours.",
                "total_reports": total,
            }

        # Insert report
        db["reports"].insert_one({
            "entity_type": entity_type,
            "entity_value": entity_value,
            "report_reason": report_reason,
            "reporter_ip": reporter_ip,
            "created_at": datetime.utcnow(),
        })

        total = db["reports"].count_documents({
            "entity_value": entity_value,
            "entity_type": entity_type,
        })

        return {
            "success": True,
            "message": "Report submitted successfully.",
            "total_reports": total,
        }
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}", "total_reports": 0}


# ── Reputation Queries ───────────────────────────────────────────────────

def get_report_count(entity_type: str, entity_value: str) -> int:
    """Get total reports for an entity."""
    db = _get_db()
    if db is None:
        return 0

    try:
        return db["reports"].count_documents({
            "entity_type": entity_type.strip().lower(),
            "entity_value": entity_value.strip().lower(),
        })
    except Exception:
        return 0


def get_community_reputation(
    company_name: str = "",
    email: str = "",
    url_domain: str = "",
) -> Dict:
    """
    Check community reports for all entities in a prediction.
    Returns dict with total_reports, flagged status, and risk boost.
    """
    total = 0

    if company_name and company_name.strip():
        total += get_report_count("company", company_name)

    if email and email.strip():
        total += get_report_count("email", email)

    if url_domain and url_domain.strip():
        total += get_report_count("url", url_domain)

    # Determine risk boost
    if total >= 10:
        risk_boost = 35
        flagged = True
    elif total >= 5:
        risk_boost = 20
        flagged = True
    elif total >= 3:
        risk_boost = 10
        flagged = True
    else:
        risk_boost = 0
        flagged = False

    return {
        "total_reports": total,
        "flagged_as_frequent_scam": flagged,
        "risk_boost_applied": risk_boost,
    }


# ── Top Reported ─────────────────────────────────────────────────────────

def get_top_reported(limit: int = 10) -> List[Dict]:
    """Aggregate top-reported entities."""
    db = _get_db()
    if db is None:
        return []

    try:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "entity_type": "$entity_type",
                        "entity_value": "$entity_value",
                    },
                    "total_reports": {"$sum": 1},
                }
            },
            {"$sort": {"total_reports": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "entity_type": "$_id.entity_type",
                    "entity_value": "$_id.entity_value",
                    "total_reports": 1,
                }
            },
        ]
        return list(db["reports"].aggregate(pipeline))
    except Exception:
        return []
