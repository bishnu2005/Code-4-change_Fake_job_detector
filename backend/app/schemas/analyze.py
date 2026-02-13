"""Pydantic schemas for the /analyze endpoint — layered response."""
from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    """Layer 1: Company verification."""
    status: str = "unknown"        # trusted | unknown | flagged
    company_name: str | None = None
    official_domain: str | None = None
    domain_match: bool | None = None


class CommunityResult(BaseModel):
    """Layer 2: Community intelligence."""
    total_reports: int = 0
    scam_count: int = 0
    legit_count: int = 0
    scam_ratio: float = 0.0
    credibility_score: float = 0.0


class DomainResult(BaseModel):
    """Layer 3: Domain intelligence."""
    extracted_domain: str | None = None
    age_days: int | None = None
    blacklist_hits: int = 0
    safe_browsing: str = "skipped"
    domain_mismatch: bool = False
    https: bool = False
    reachable: bool | None = None
    suspicious_tld: bool = False
    similarity_score: float = 0.0


class MLResult(BaseModel):
    """Layer 4: ML engine."""
    triggered: bool = False
    probability: float | None = None
    risk_score: float | None = None


class ContentAnalysisResult(BaseModel):
    """Layer 5: Deep content analysis."""
    triggered: bool = False
    heuristic_flags: list[str] = Field(default_factory=list)
    risk_boost: float = 0.0


class FinalRisk(BaseModel):
    """Final aggregated risk."""
    score: float = Field(0.0, ge=0, le=100)
    level: str = "Unknown"   # Safe | Suspicious | High Risk


class Confidence(BaseModel):
    """Confidence in the assessment."""
    score: int = Field(0, ge=0, le=95)
    level: str = "Low"   # Low | Medium | High | Very High


class AnalyzeRequest(BaseModel):
    """POST /analyze request (JSON body for non-image requests)."""
    company_name: str = ""
    job_description: str = ""
    url: str = ""
    user_id: int | None = None


class AnalyzeResponse(BaseModel):
    """Full layered analysis response."""
    verification: VerificationResult = Field(default_factory=VerificationResult)
    community: CommunityResult = Field(default_factory=CommunityResult)
    domain: DomainResult = Field(default_factory=DomainResult)
    ml: MLResult = Field(default_factory=MLResult)
    content_analysis: ContentAnalysisResult = Field(default_factory=ContentAnalysisResult)
    final_risk: FinalRisk = Field(default_factory=FinalRisk)
    confidence: Confidence = Field(default_factory=Confidence)
    reasons: list[str] = Field(default_factory=list)
