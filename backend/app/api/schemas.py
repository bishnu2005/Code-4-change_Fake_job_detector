"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    """Request body for POST /analyze_text."""
    company: str = Field(default="", description="Company name")
    salary: str = Field(default="", description="Salary information")
    description: str = Field(..., description="Job posting description text")
    apply_link: str = Field(default="", description="Application URL/link")


class ShapFactor(BaseModel):
    """Single SHAP risk or trust factor."""
    feature: str
    weight: float


class UrlAnalysis(BaseModel):
    """Structured URL verification results."""
    url_risk_score: float = 0.0
    url_trust_score: float = 0.0
    https_flag: bool = False
    ip_flag: bool = False
    reachable_flag: bool | None = None
    suspicious_tld_flag: bool = False
    domain_similarity_score: float = 0.0
    domain_age_days: int | None = None
    page_content_risk_score: float | None = None
    blacklisted: bool = False
    safe_browsing_status: str = "skipped"
    extracted_domain: str | None = None


class EmailAnalysis(BaseModel):
    """Structured email verification results."""
    email_address: str = ""
    email_domain: str = ""
    email_risk_score: float = 0.0
    email_signal_strength: float = 0.0
    disposable_flag: bool = False
    free_provider_flag: bool = False
    domain_similarity_score: float = 0.0
    mx_record_exists: bool | None = None


class SignalsUsed(BaseModel):
    """Which signal channels were active."""
    text: bool = False
    image: bool = False
    url: bool = False
    email: bool = False


class AnalyzeResponse(BaseModel):
    """Unified response for both analyze endpoints."""
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_level: str = Field(..., description="Safe | Suspicious | High Risk")
    confidence_score: int = Field(
        ..., ge=0, le=95, description="Confidence in assessment 0-95"
    )
    confidence_level: str = Field(
        ..., description="Low | Medium | High | Very High"
    )
    text_probability: float | None = Field(
        None, description="Calibrated ML fraud probability"
    )
    shap_risk_factors: list[ShapFactor] = Field(
        default_factory=list, description="Top SHAP features driving risk"
    )
    shap_trust_factors: list[ShapFactor] = Field(
        default_factory=list, description="Top SHAP features driving trust"
    )
    url_analysis: UrlAnalysis | None = Field(
        None, description="URL verification details, null when no URL"
    )
    email_analysis: EmailAnalysis | None = Field(
        None, description="Email verification details, null when no email"
    )
    sufficiency_level: str = Field(
        "Strong", description="None | Weak | Moderate | Strong"
    )
    data_sufficiency_flag: bool = Field(
        False, description="True if input data was insufficient"
    )
    signals_used: SignalsUsed = Field(
        default_factory=SignalsUsed, description="Which signals were used"
    )
    reasons: list[str] = Field(
        default_factory=list, description="Legacy explanation reasons"
    )
