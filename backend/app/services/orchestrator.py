"""
Orchestrator — Strict layered intelligence pipeline.
Runs layers 1→5 in order. Can terminate early if decisive.
"""
import logging
from sqlalchemy.orm import Session

from app.services.layer1_company import verify_company
from app.services.layer2_community import get_community_intelligence
from app.services.layer3_domain import analyze_domain
from app.services.layer4_ml import run_ml
from app.services.layer5_content import analyze_content
from app.services.risk_scorer import compute_final_risk, compute_confidence
from app.schemas.analyze import AnalyzeResponse

logger = logging.getLogger(__name__)


def run_pipeline(
    db: Session,
    company_name: str = "",
    job_description: str = "",
    url: str = "",
    image_bytes: bytes | None = None,
) -> AnalyzeResponse:
    """
    Execute layered intelligence pipeline:
      1. Company Verification
      2. Community Intelligence
      3. Domain Intelligence
      4. ML Engine (conditional)
      5. Deep Content Analysis (conditional)
    """
    reasons: list[str] = []
    ml_skip = False

    # ── Layer 1: Company Verification ────────────────────────────
    verification, decisive = verify_company(db, company_name, url)

    if decisive and verification.status == "trusted" and verification.domain_match:
        reasons.append(
            f"✅ {verification.company_name} is a verified company and the domain matches."
        )
        # Still run community for enrichment, but ML is skipped
        ml_skip = True

    if verification.status == "flagged":
        reasons.append(
            f"⚠️ {verification.company_name} has been flagged in our registry."
        )

    # ── Layer 2: Community Intelligence ──────────────────────────
    # Extract domain from URL for community search
    domain_for_search = ""
    if url:
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url if url.startswith("http") else "http://" + url)
            domain_for_search = parsed.netloc.split(":")[0]
        except Exception:
            pass

    community = get_community_intelligence(
        db, company_name=company_name, domain=domain_for_search
    )

    if community.total_reports > 0:
        if community.scam_ratio > 0.7:
            reasons.append(
                f"⚠️ Community reports: {community.scam_count}/{community.total_reports} "
                f"flagged as scam ({int(community.scam_ratio * 100)}% scam ratio)."
            )
        elif community.scam_ratio < 0.3 and community.total_reports >= 3:
            reasons.append(
                f"✅ Community reports mostly positive: {community.legit_count}/{community.total_reports} legit."
            )

    # ── Layer 3: Domain Intelligence ─────────────────────────────
    domain = analyze_domain(db, url, company_name)

    if domain.extracted_domain:
        if domain.blacklist_hits > 0:
            reasons.append("⚠️ Domain found in scam/phishing blacklist.")
        if domain.age_days is not None and domain.age_days < 60:
            reasons.append(f"⚠️ Domain is very new ({domain.age_days} days old).")
        if domain.suspicious_tld:
            reasons.append("⚠️ Domain uses a suspicious TLD.")
        if domain.safe_browsing == "malicious":
            reasons.append("⚠️ Google Safe Browsing flagged this domain.")
        if domain.domain_mismatch and company_name:
            reasons.append("⚠️ Domain does not match the company name.")
        if not domain.https:
            reasons.append("Domain does not use HTTPS.")

        # Count red flags for ML skip decision
        red_flags = sum([
            domain.blacklist_hits > 0,
            domain.age_days is not None and domain.age_days < 60,
            domain.suspicious_tld,
            domain.safe_browsing == "malicious",
            domain.domain_mismatch,
        ])
        if red_flags >= 2:
            ml_skip = False  # Force ML to confirm

    # ── Layer 4: Conditional ML ──────────────────────────────────
    ml = run_ml(job_description, skip=ml_skip)

    if ml.triggered:
        if ml.risk_score is not None and ml.risk_score > 60:
            reasons.append(f"ML model fraud probability: {ml.probability:.1%}")
        elif ml.risk_score is not None and ml.risk_score < 20:
            reasons.append("ML model indicates low fraud probability.")

    # ── Layer 5: Deep Content Analysis ───────────────────────────
    content = analyze_content(url, domain)

    if content.triggered and content.heuristic_flags:
        reasons.append(
            f"Page content flags: {', '.join(content.heuristic_flags[:5])}"
        )

    # ── Final scoring ────────────────────────────────────────────
    if not reasons:
        reasons.append("No significant signals detected.")

    final_risk = compute_final_risk(
        verification=verification,
        community=community,
        domain=domain,
        ml=ml,
        content=content,
    )

    confidence = compute_confidence(
        verification=verification,
        community=community,
        domain=domain,
        ml=ml,
        content=content,
    )

    return AnalyzeResponse(
        verification=verification,
        community=community,
        domain=domain,
        ml=ml,
        content_analysis=content,
        final_risk=final_risk,
        confidence=confidence,
        reasons=reasons,
    )
