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


class AnalyzeResponse(BaseModel):
    """Unified response for both analyze endpoints."""
    risk_score: float = Field(..., ge=0, le=100, description="Risk score from 0-100")
    risk_level: str = Field(..., description="Safe | Suspicious | High Risk")
    reasons: list[str] = Field(..., description="Explanation reasons for the score")
