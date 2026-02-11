"""
Fake Job Posting Detector — Backend API
FastAPI server that loads the trained ML model and serves predictions.
"""

import os
import sys
import io
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
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

    breakdown_dict = {
        "scam_keywords_found": scam_keywords,
        "missing_fields_count": missing_count,
        "has_salary": bool(has_sal),
        "salary_anomaly": bool(sal_anomaly),
        "has_company_logo": bool(data.get("has_company_logo", 1)),
        "has_questions": bool(data.get("has_questions", 1)),
        "telecommuting": bool(data.get("telecommuting", 0)),
        "description_length": len(data.get("description", "")),
    }

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


# ── Health Check ─────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
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
            "GET /health": "Health check",
            "GET /docs": "Interactive API docs (Swagger)",
        },
    }
