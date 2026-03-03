"""
Risk Scorer — computes final weighted risk and confidence from all layers.
"""
from app.schemas.analyze import (
    VerificationResult, CommunityResult, DomainResult,
    MLResult, ContentAnalysisResult, FinalRisk, Confidence,
)


def _classify(score: float) -> str:
    if score >= 70:
        return "High Risk"
    elif score >= 40:
        return "Suspicious"
    return "Safe"


def compute_final_risk(
    verification: VerificationResult,
    community: CommunityResult,
    domain: DomainResult,
    ml: MLResult,
    content: ContentAnalysisResult,
) -> FinalRisk:
    """
    Weighted risk scoring.
    Company verification → strongest (can override).
    Community → strong.
    Domain → strong.
    ML → medium.
    Content heuristics → additive.
    """
    # If company is verified + domain matches → very safe
    if verification.status == "trusted" and verification.domain_match is True:
        return FinalRisk(score=5.0, level="Safe")

    # If company is flagged → immediate high risk
    if verification.status == "flagged":
        return FinalRisk(score=85.0, level="High Risk")

    # Deceptive domain (e.g. google-careers.xyz) → High Risk Boost
    deceptive_risk = 0.0
    if verification.deceptive:
        deceptive_risk = 20.0

    # Collect weighted scores
    scores: list[tuple[float, float]] = []  # (score, weight)

    # Community signal
    if community.total_reports > 0:
        community_risk = community.scam_ratio * 100
        weight = min(community.total_reports / 5, 1.0) * 0.30  # max weight 0.30
        scores.append((community_risk, weight))

    # Domain signal
    if domain.extracted_domain:
        domain_risk = 0.0
        if domain.blacklist_hits > 0:
            domain_risk += 40
        if domain.age_days is not None:
            if domain.age_days < 60:
                domain_risk += 25
            elif domain.age_days < 180:
                domain_risk += 10
        if domain.suspicious_tld:
            domain_risk += 20
        if domain.safe_browsing == "malicious":
            domain_risk += 30
        if domain.domain_mismatch:
            domain_risk += 15
        if not domain.https:
            domain_risk += 5
        domain_risk = min(domain_risk, 100)
        scores.append((domain_risk, 0.30))

    # ML signal
    if ml.triggered and ml.risk_score is not None:
        scores.append((ml.risk_score, 0.25))

    # Content heuristics (additive)
    content_boost = content.risk_boost if content.triggered else 0

    # Compute weighted average
    if scores:
        total_weight = sum(w for _, w in scores)
        if total_weight > 0:
            weighted_sum = sum(s * w for s, w in scores)
            base_score = weighted_sum / total_weight
        else:
            base_score = 30.0  # neutral
    else:
        base_score = 30.0  # no signals

    final_score = round(min(base_score + content_boost + deceptive_risk, 100), 1)

    return FinalRisk(
        score=final_score,
        level=_classify(final_score),
    )


def compute_confidence(
    verification: VerificationResult,
    community: CommunityResult,
    domain: DomainResult,
    ml: MLResult,
    content: ContentAnalysisResult,
) -> Confidence:
    """
    Confidence based on number and strength of signals.
    Max = 95 (never 100).
    Never Very High on single weak signal.
    """
    score = 25  # base

    strong_signals = 0

    # Company verified → strong signal
    if verification.status == "trusted":
        score += 20
        strong_signals += 1

    # Community data → stronger with more reports
    if community.total_reports >= 3:
        score += 15
        strong_signals += 1
    elif community.total_reports > 0:
        score += 5

    # Domain intelligence
    if domain.extracted_domain:
        score += 10
        if domain.age_days is not None:
            score += 5
            strong_signals += 1
        if domain.safe_browsing in ("clean", "malicious"):
            score += 5

    # ML
    if ml.triggered:
        score += 10
        strong_signals += 1

    # Content analysis
    if content.triggered:
        score += 5

    # Single-signal cap: never Very High with 1 signal
    if strong_signals <= 1:
        score = min(score, 75)

    # Hard cap at 95
    score = max(0, min(score, 95))

    if score >= 86:
        level = "Very High"
    elif score >= 66:
        level = "High"
    elif score >= 41:
        level = "Medium"
    else:
        level = "Low"

    return Confidence(score=score, level=level)
