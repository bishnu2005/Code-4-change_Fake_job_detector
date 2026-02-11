"""
Explainer: generates human-readable reason strings from analysis signals.
"""


def generate_reasons(
    ml_probability: float | None,
    suspicious_keywords: list[str],
    salary_analysis: dict,
    url_analysis: dict,
) -> list[str]:
    """
    Build a list of explanation strings based on all analysis signals.
    """
    reasons: list[str] = []

    # ML model signal
    if ml_probability is not None:
        pct = ml_probability * 100
        if pct >= 70:
            reasons.append(f"ML model indicates high fraud probability ({pct:.0f}%)")
        elif pct >= 40:
            reasons.append(f"ML model indicates moderate fraud probability ({pct:.0f}%)")
        else:
            reasons.append(f"ML model indicates low fraud probability ({pct:.0f}%)")

    # Suspicious keywords
    if suspicious_keywords:
        kw_list = ", ".join(f'"{kw}"' for kw in suspicious_keywords)
        reasons.append(f"Suspicious keywords detected: {kw_list}")

    # Salary anomaly
    if salary_analysis.get("is_suspicious"):
        reasons.append(f"Salary anomaly: {salary_analysis['reason']}")

    # URL/domain issues
    if url_analysis.get("is_suspicious"):
        for r in url_analysis.get("reasons", []):
            reasons.append(f"Domain credibility issue: {r}")

    # If nothing flagged
    if not reasons:
        reasons.append("No significant risk signals detected")

    return reasons
