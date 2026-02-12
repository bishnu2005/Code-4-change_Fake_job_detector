"""
API routes for the Fake Job Posting Detector.
"""
import logging
from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.api.schemas import AnalyzeResponse
from app.services.inference import analyze
from app.models.model_loader import model_loader

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model_loader.is_loaded,
        "calibrated": model_loader.has_calibrated,
    }


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_unified(
    description: str = Form(default=""),
    company: str = Form(default=""),
    salary: str = Form(default=""),
    apply_link: str = Form(default=""),
    file: Annotated[UploadFile | None, File(description="Optional image of job posting")] = None,
):
    """
    Unified multi-signal analysis endpoint.
    Accepts text fields and an optional image in a single request.
    """
    if not model_loader.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Train the model first.",
        )

    # Validate and read image if provided
    image_bytes = None
    if file is not None:
        try:
            image_bytes = await file.read()
            # Content-based validation using Pillow
            from PIL import Image
            from io import BytesIO
            Image.open(BytesIO(image_bytes)).verify()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file must be a valid image (JPEG, PNG, or WebP)",
            )

    try:
        result = analyze(
            description=description,
            company=company,
            salary=salary,
            apply_link=apply_link,
            image_bytes=image_bytes,
        )
        return AnalyzeResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {str(e)}"
        )


# ── Legacy endpoints (kept for backward compatibility) ──────────

@router.post("/analyze_text", response_model=AnalyzeResponse)
async def analyze_text_legacy(
    description: str = Form(default=""),
    company: str = Form(default=""),
    salary: str = Form(default=""),
    apply_link: str = Form(default=""),
):
    """Legacy text-only endpoint. Redirects to unified pipeline."""
    return await analyze_unified(
        description=description,
        company=company,
        salary=salary,
        apply_link=apply_link,
    )


@router.post("/analyze_image", response_model=AnalyzeResponse)
async def analyze_image_legacy(file: UploadFile = File(...)):
    """Legacy image-only endpoint. Redirects to unified pipeline."""
    return await analyze_unified(file=file)
