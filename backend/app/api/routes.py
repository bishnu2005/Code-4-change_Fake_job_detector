"""
API routes for the Fake Job Posting Detector.
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.api.schemas import AnalyzeTextRequest, AnalyzeResponse
from app.services.inference import analyze
from app.services.ocr_service import extract_text_from_image

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.models.model_loader import model_loader
    return {
        "status": "healthy",
        "model_loaded": model_loader.is_loaded,
    }


@router.post("/analyze_text", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeTextRequest):
    """
    Analyze a job posting from structured text fields.
    Returns risk score, risk level, and explanation reasons.
    """
    try:
        result = analyze(
            description=request.description,
            company=request.company,
            salary=request.salary,
            apply_link=request.apply_link,
        )
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze_image", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze a job posting from an uploaded image.
    Uses OCR to extract text, then runs the same analysis pipeline.
    """
    # Validate file type
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    try:
        image_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {e}")

    # OCR extraction
    try:
        extracted_text = extract_text_from_image(image_bytes)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not extracted_text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from the image")

    # Run through the same pipeline
    try:
        result = analyze(description=extracted_text)
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
