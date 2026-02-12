"""
Fake Job Posting Detector — Backend API
FastAPI server that loads the trained ML model and serves predictions.
"""

import os
import sys
import io
import re
from dotenv import load_dotenv

load_dotenv()  # Load .env for MONGO_URI etc.
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Add ml_model to path for feature engineering imports
ML_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_model")
sys.path.insert(0, ML_MODEL_DIR)

from feature_engineering import (
    build_all_features,
    extract_scam_keyword_flags,
    combine_text_fields,
    count_missing_fields,
    parse_salary,
    detect_salary_anomaly,
)

# Import email domain analyzer (lives in backend/)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)
from email_analyzer import analyze_email_domain
from url_analyzer import analyze_url
from database import submit_report, get_community_reputation, get_top_reported, is_connected


# ── App Setup ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Fake Job Posting Detector API",
    description="AI-powered API to detect fraudulent job postings",
    version="1.0.0",
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Load Model ───────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(ML_MODEL_DIR, "saved_model", "model.pkl")
VECTORIZER_PATH = os.path.join(ML_MODEL_DIR, "saved_model", "vectorizer.pkl")

model = None
vectorizer = None


@app.on_event("startup")
async def load_model():
    """Load the trained model and vectorizer on server startup."""
    global model, vectorizer
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print(f"✅ Model loaded: {model.n_estimators} trees")
        print(f"✅ Vectorizer loaded: {len(vectorizer.vocabulary_)} terms")
    except FileNotFoundError:
        print("❌ Model files not found! Run train_model.py first.")
        print(f"   Expected: {MODEL_PATH}")
        print(f"   Expected: {VECTORIZER_PATH}")


# ── Request/Response Models ──────────────────────────────────────────────
class JobPostingRequest(BaseModel):
    """Input schema for job posting analysis."""
    title: str = Field(..., description="Job title", example="Senior Software Engineer")
    company_profile: Optional[str] = Field("", description="Company description")
    description: str = Field(..., description="Full job description")
    requirements: Optional[str] = Field("", description="Job requirements")
    benefits: Optional[str] = Field("", description="Listed benefits")
    salary_range: Optional[str] = Field("", description="e.g. '50000-80000'")
    location: Optional[str] = Field("", description="Job location")
    department: Optional[str] = Field("", description="Department name")
    employment_type: Optional[str] = Field("", description="Full-time, Part-time, etc.")
    required_experience: Optional[str] = Field("", description="Entry level, Mid-Senior, etc.")
    required_education: Optional[str] = Field("", description="Bachelor's, Master's, etc.")
    industry: Optional[str] = Field("", description="Industry sector")
    function: Optional[str] = Field("", description="Job function")
    telecommuting: Optional[int] = Field(0, description="1 if remote, 0 otherwise")
    has_company_logo: Optional[int] = Field(1, description="1 if company has logo")
    has_questions: Optional[int] = Field(1, description="1 if posting has screening questions")
    contact_email: Optional[str] = Field("", description="Recruiter/contact email address")
    job_url: Optional[str] = Field("", description="URL of the job posting")


class UrlRequest(BaseModel):
    """Input schema for URL-only analysis."""
    job_url: str = Field(..., description="URL of the job posting to analyze")
    company_name: Optional[str] = Field("", description="Company name for domain matching")


class ReportRequest(BaseModel):
    """Input schema for community scam reports."""
    entity_type: str = Field(..., description="Type: company, email, or url")
    entity_value: str = Field(..., description="Value to report")
    report_reason: str = Field("", description="Reason for reporting")


class EmailAnalysis(BaseModel):
    """Email domain verification results."""
    email_found: bool = False
    email: str = ""
    email_domain: str = ""
    free_provider: bool = False
    domain_matches_company: bool = True
    suspicious_pattern: bool = False


class UrlAnalysis(BaseModel):
    """URL legitimacy verification results."""
    url_provided: bool = False
    url: str = ""
    domain: str = ""
    ip_based: bool = False
    free_hosting: bool = False
    suspicious_keywords: List[str] = []
    domain_matches_company: bool = True
    excessive_subdomains: bool = False
    long_domain: bool = False
    numeric_substitutions: bool = False
    dns_resolves: bool = True
    ssl_error: bool = False
    reachable: bool = False


class CommunityReports(BaseModel):
    """Community scam report summary."""
    total_reports: int = 0
    flagged_as_frequent_scam: bool = False
    risk_boost_applied: int = 0


class RiskBreakdown(BaseModel):
    """Detailed breakdown of risk factors."""
    scam_keywords_found: List[str]
    missing_fields_count: int
    has_salary: bool
    salary_anomaly: bool
    has_company_logo: bool
    has_questions: bool
    telecommuting: bool
    description_length: int
    risk_factors: List[str]
    email_analysis: EmailAnalysis = EmailAnalysis()
    url_analysis: UrlAnalysis = UrlAnalysis()
    community_reports: CommunityReports = CommunityReports()


class PredictionResponse(BaseModel):
    """Output schema for prediction results."""
    prediction: str  # "FRAUDULENT" or "LEGITIMATE"
    fraud_probability: float  # 0.0 to 1.0
    confidence: float  # Model confidence (max of both class probabilities)
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    risk_score: int  # 0-100
    risk_breakdown: RiskBreakdown
    recommendations: List[str]


# ── Risk Assessment Logic ────────────────────────────────────────────────
def compute_risk_level(risk_score: int) -> str:
    """Map risk score to human-readable level."""
    if risk_score <= 25:
        return "LOW"
    elif risk_score <= 50:
        return "MEDIUM"
    elif risk_score <= 75:
        return "HIGH"
    else:
        return "CRITICAL"


def generate_recommendations(risk_breakdown: dict, risk_score: int) -> List[str]:
    """Generate actionable recommendations based on risk factors."""
    recs = []

    if risk_score >= 75:
        recs.append("⛔ This posting has critical red flags. Do NOT share personal information.")
    elif risk_score >= 50:
        recs.append("⚠️ This posting has significant warning signs. Proceed with extreme caution.")

    if risk_breakdown["scam_keywords_found"]:
        recs.append(f"🔍 Suspicious keywords detected: {', '.join(risk_breakdown['scam_keywords_found'][:5])}")

    if risk_breakdown["missing_fields_count"] >= 5:
        recs.append("📝 Many important fields are missing — legitimate employers usually provide full details.")

    if not risk_breakdown["has_salary"]:
        recs.append("💰 No salary information provided — request salary details before proceeding.")

    if risk_breakdown["salary_anomaly"]:
        recs.append("💸 Salary range appears unrealistic — verify compensation with independent research.")

    if not risk_breakdown["has_company_logo"]:
        recs.append("🏢 No company logo — verify the company exists on LinkedIn or official website.")

    if not risk_breakdown["has_questions"]:
        recs.append("❓ No screening questions — most real employers use these to filter candidates.")

    if risk_breakdown["description_length"] < 100:
        recs.append("📄 Very short job description — legitimate postings usually have detailed descriptions.")

    # Email domain recommendations
    email_info = risk_breakdown.get("email_analysis", {})
    if email_info.get("free_provider"):
        recs.append(f"📧 Recruiter uses free email ({email_info['email_domain']}) — legitimate companies use corporate email.")
    if not email_info.get("domain_matches_company", True):
        recs.append("🔗 Email domain doesn't match company name — verify recruiter identity independently.")
    if email_info.get("suspicious_pattern"):
        recs.append(f"⚠️ Suspicious email domain pattern ({email_info['email_domain']}) — possible lookalike domain.")

    # URL recommendations
    url_info = risk_breakdown.get("url_analysis", {})
    if url_info.get("url_provided"):
        if url_info.get("ip_based"):
            recs.append("🌐 URL uses an IP address instead of a domain — major red flag for phishing.")
        if url_info.get("free_hosting"):
            recs.append(f"🏗️ URL hosted on free platform ({url_info.get('domain', '')}) — legitimate companies use their own domains.")
        if url_info.get("numeric_substitutions"):
            recs.append(f"🔢 URL domain contains number substitutions ({url_info.get('domain', '')}) — possible impersonation.")
        if not url_info.get("dns_resolves", True):
            recs.append("❌ URL domain does not resolve — the website may not exist.")
        if url_info.get("ssl_error"):
            recs.append("🔓 SSL certificate error — the site may be insecure or fraudulent.")
        if not url_info.get("domain_matches_company", True):
            recs.append("🔗 URL domain doesn't match the company name — verify the posting source.")

    # Community reports recommendations
    community = risk_breakdown.get("community_reports", {})
    if community.get("flagged_as_frequent_scam"):
        count = community.get("total_reports", 0)
        recs.append(f"🚨 This entity has been reported {count} times by community users — exercise extreme caution.")

    if risk_score <= 25:
        recs.append("✅ This posting appears legitimate, but always research the company independently.")

    return recs


def build_risk_factors(breakdown: dict) -> List[str]:
    """Build list of identified risk factor strings."""
    factors = []

    if breakdown["scam_keywords_found"]:
        factors.append(f"Contains {len(breakdown['scam_keywords_found'])} scam-related keywords")

    if breakdown["missing_fields_count"] >= 3:
        factors.append(f"{breakdown['missing_fields_count']} important fields are missing")

    if not breakdown["has_company_logo"]:
        factors.append("No company logo")

    if not breakdown["has_questions"]:
        factors.append("No screening questions")

    if breakdown["salary_anomaly"]:
        factors.append("Suspicious salary range")

    if not breakdown["has_salary"]:
        factors.append("No salary information")

    if breakdown["telecommuting"]:
        factors.append("Remote work (common in scams)")

    if breakdown["description_length"] < 100:
        factors.append("Very short description")

    # Email domain risk factors
    email_info = breakdown.get("email_analysis", {})
    if email_info.get("free_provider"):
        factors.append(f"Recruiter uses free email provider ({email_info.get('email_domain', '')})")
    if not email_info.get("domain_matches_company", True):
        factors.append("Email domain doesn't match company name")
    if email_info.get("suspicious_pattern"):
        factors.append(f"Suspicious lookalike domain ({email_info.get('email_domain', '')})")

    # URL risk factors
    url_info = breakdown.get("url_analysis", {})
    if url_info.get("url_provided"):
        if url_info.get("ip_based"):
            factors.append("URL uses IP address instead of domain")
        if url_info.get("free_hosting"):
            factors.append(f"URL hosted on free platform ({url_info.get('domain', '')})")
        if url_info.get("numeric_substitutions"):
            factors.append(f"URL contains lookalike characters ({url_info.get('domain', '')})")
        if url_info.get("excessive_subdomains"):
            factors.append("Excessive subdomains in URL")
        if not url_info.get("dns_resolves", True):
            factors.append("URL domain does not resolve (DNS failure)")
        if url_info.get("ssl_error"):
            factors.append("SSL certificate error on URL")
        if not url_info.get("domain_matches_company", True):
            factors.append("URL domain doesn't match company name")
        if url_info.get("suspicious_keywords"):
            factors.append(f"Suspicious keywords in URL: {', '.join(url_info['suspicious_keywords'][:3])}")

    # Community report factors
    community = breakdown.get("community_reports", {})
    if community.get("flagged_as_frequent_scam"):
        factors.append(f"Reported {community.get('total_reports', 0)} times by community")

    return factors


# ── Shared Analysis Logic ────────────────────────────────────────────────
def analyze_job_data(data: dict) -> PredictionResponse:
    """
    Core analysis function shared by /predict and /predict-image.
    Accepts a dict with job posting fields, returns PredictionResponse.
    """
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please ensure model.pkl and vectorizer.pkl exist.",
        )

    df = pd.DataFrame([data])

    # Build features
    X, _, _ = build_all_features(df, tfidf_vectorizer=vectorizer)

    # Predict
    proba = model.predict_proba(X)[0]
    fraud_prob = float(proba[1])
    prediction = "FRAUDULENT" if fraud_prob >= 0.5 else "LEGITIMATE"
    confidence = float(max(proba))

    # Risk breakdown
    combined_text = combine_text_fields(df.iloc[0])
    scam_keywords = extract_scam_keyword_flags(combined_text)
    missing_count = count_missing_fields(df.iloc[0])
    sal_min, sal_max, has_sal = parse_salary(data.get("salary_range", ""))
    sal_anomaly = detect_salary_anomaly(sal_min, sal_max)

    # Email domain analysis
    email_result = analyze_email_domain(
        contact_email=data.get("contact_email", ""),
        raw_text=data.get("description", ""),
        company_name=data.get("company_profile", ""),
    )

    # URL analysis
    url_result = analyze_url(
        url=data.get("job_url", ""),
        company_name=data.get("company_profile", ""),
    )

    breakdown_dict = {
        "scam_keywords_found": scam_keywords,
        "missing_fields_count": missing_count,
        "has_salary": bool(has_sal),
        "salary_anomaly": bool(sal_anomaly),
        "has_company_logo": bool(data.get("has_company_logo", 1)),
        "has_questions": bool(data.get("has_questions", 1)),
        "telecommuting": bool(data.get("telecommuting", 0)),
        "description_length": len(data.get("description", "")),
        "email_analysis": {
            "email_found": email_result["email_found"],
            "email": email_result["email"],
            "email_domain": email_result["email_domain"],
            "free_provider": email_result["free_provider"],
            "domain_matches_company": email_result["domain_matches_company"],
            "suspicious_pattern": email_result["suspicious_pattern"],
        },
        "url_analysis": {
            "url_provided": url_result["url_provided"],
            "url": url_result["url"],
            "domain": url_result["domain"],
            "ip_based": url_result["ip_based"],
            "free_hosting": url_result["free_hosting"],
            "suspicious_keywords": url_result["suspicious_keywords"],
            "domain_matches_company": url_result["domain_matches_company"],
            "excessive_subdomains": url_result["excessive_subdomains"],
            "long_domain": url_result.get("long_domain", False),
            "numeric_substitutions": url_result["numeric_substitutions"],
            "dns_resolves": url_result["dns_resolves"],
            "ssl_error": url_result["ssl_error"],
            "reachable": url_result["reachable"],
        },
    }

    # Community reputation check
    community_rep = get_community_reputation(
        company_name=data.get("company_profile", ""),
        email=email_result.get("email", ""),
        url_domain=url_result.get("domain", ""),
    )
    breakdown_dict["community_reports"] = community_rep

    # Compute hybrid risk score (ML probability + rule-based factors)
    rule_score = 0
    if scam_keywords:
        rule_score += min(len(scam_keywords) * 8, 25)
    if missing_count >= 5:
        rule_score += 15
    elif missing_count >= 3:
        rule_score += 8
    if not has_sal:
        rule_score += 5
    if sal_anomaly:
        rule_score += 10
    if not data.get("has_company_logo", 1):
        rule_score += 10
    if not data.get("has_questions", 1):
        rule_score += 5
    if len(data.get("description", "")) < 100:
        rule_score += 10

    # Email domain risk contribution
    rule_score += email_result.get("domain_risk_score", 0)

    # URL risk contribution
    rule_score += url_result.get("url_risk_score", 0)

    # Community reputation risk contribution
    rule_score += community_rep.get("risk_boost_applied", 0)

    # Hybrid score: 60% ML, 40% rules
    risk_score = int(fraud_prob * 60 + min(rule_score, 40))
    risk_score = min(risk_score, 100)

    risk_factors = build_risk_factors(breakdown_dict)
    breakdown_dict["risk_factors"] = risk_factors

    recommendations = generate_recommendations(breakdown_dict, risk_score)

    return PredictionResponse(
        prediction=prediction,
        fraud_probability=round(fraud_prob, 4),
        confidence=round(confidence, 4),
        risk_level=compute_risk_level(risk_score),
        risk_score=risk_score,
        risk_breakdown=RiskBreakdown(**breakdown_dict),
        recommendations=recommendations,
    )


# ── Prediction Endpoint ─────────────────────────────────────────────────
@app.post("/predict", response_model=PredictionResponse)
async def predict(job: JobPostingRequest):
    """
    Analyze a job posting and return fraud prediction with risk breakdown.
    """
    data = {
        "title": job.title,
        "company_profile": job.company_profile or "",
        "description": job.description,
        "requirements": job.requirements or "",
        "benefits": job.benefits or "",
        "salary_range": job.salary_range or "",
        "location": job.location or "",
        "department": job.department or "",
        "employment_type": job.employment_type or "",
        "required_experience": job.required_experience or "",
        "required_education": job.required_education or "",
        "industry": job.industry or "",
        "function": job.function or "",
        "telecommuting": job.telecommuting or 0,
        "has_company_logo": job.has_company_logo if job.has_company_logo is not None else 1,
        "has_questions": job.has_questions if job.has_questions is not None else 1,
        "contact_email": job.contact_email or "",
        "job_url": job.job_url or "",
        "fraudulent": 0,
    }
    return analyze_job_data(data)


# ── OCR Image Prediction Endpoint ────────────────────────────────────────
@app.post("/predict-image", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    """
    Accept an image of a job posting, extract text via OCR,
    and return the same fraud prediction response.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"]
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Accepted: PNG, JPEG, WEBP, BMP, TIFF.",
        )

    # Read and convert to PIL Image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the uploaded file as an image.")

    # OCR extraction
    try:
        raw_text = pytesseract.image_to_string(image)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {str(e)}. Ensure Tesseract is installed and accessible.",
        )

    # Validate extracted text
    raw_text = raw_text.strip()
    if not raw_text or len(raw_text) < 10:
        raise HTTPException(
            status_code=422,
            detail="OCR could not extract meaningful text from the image. Try a clearer image.",
        )

    # Build job data with OCR text as description, defaults for everything else
    data = {
        "title": "",
        "company_profile": "",
        "description": raw_text,
        "requirements": "",
        "benefits": "",
        "salary_range": "",
        "location": "",
        "department": "",
        "employment_type": "",
        "required_experience": "",
        "required_education": "",
        "industry": "",
        "function": "",
        "telecommuting": 0,
        "has_company_logo": 0,
        "has_questions": 0,
        "fraudulent": 0,
    }
    return analyze_job_data(data)


# ── URL Prediction Endpoint ──────────────────────────────────────────────
@app.post("/predict-url", response_model=PredictionResponse)
async def predict_url(req: UrlRequest):
    """
    Analyze a job posting URL for legitimacy.
    Performs URL analysis + optional scrape, then runs ML prediction on scraped text.
    """
    from url_analyzer import analyze_url as _analyze_url, normalize_url
    import requests as req_lib

    url = normalize_url(req.job_url)
    if not url:
        raise HTTPException(status_code=400, detail="job_url is required.")

    # Scrape page text for ML analysis
    scraped_text = ""
    try:
        resp = req_lib.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0 FakeJobDetector/1.0"})
        if resp.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text[:50000], "html.parser")
            # Remove script/style
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            scraped_text = soup.get_text(separator=" ", strip=True)[:5000]
    except Exception:
        pass

    description = scraped_text if len(scraped_text) > 20 else "Job posting URL submitted for analysis."

    data = {
        "title": "",
        "company_profile": req.company_name or "",
        "description": description,
        "requirements": "",
        "benefits": "",
        "salary_range": "",
        "location": "",
        "department": "",
        "employment_type": "",
        "required_experience": "",
        "required_education": "",
        "industry": "",
        "function": "",
        "telecommuting": 0,
        "has_company_logo": 0,
        "has_questions": 0,
        "contact_email": "",
        "job_url": req.job_url,
        "fraudulent": 0,
    }
    return analyze_job_data(data)


# ── Community Report Endpoint ────────────────────────────────────────────
@app.post("/report")
async def report_entity(req: ReportRequest, request: Request):
    """
    Submit a community scam report.
    """
    # Get reporter IP
    reporter_ip = request.client.host if request.client else "unknown"

    result = submit_report(
        entity_type=req.entity_type,
        entity_value=req.entity_value,
        report_reason=req.report_reason,
        reporter_ip=reporter_ip,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ── Top Reported Endpoint ────────────────────────────────────────────────
@app.get("/top-reported")
async def top_reported():
    """Get top 10 most reported entities."""
    return get_top_reported(limit=10)


# ── Health Check ─────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "db_connected": is_connected(),
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "app": "Fake Job Posting Detector API",
        "version": "1.0.0",
        "endpoints": {
            "POST /predict": "Analyze a job posting (JSON)",
            "POST /predict-image": "Analyze a job posting screenshot (OCR)",
            "POST /predict-url": "Analyze a job posting URL",
            "POST /report": "Submit a community scam report",
            "GET /top-reported": "Top 10 most reported entities",
            "GET /health": "Health check",
            "GET /docs": "Interactive API docs (Swagger)",
        },
    }
