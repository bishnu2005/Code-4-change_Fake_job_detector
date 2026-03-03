
"""
Analyze API route — unified /analyze endpoint using orchestrator.
"""
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analyze import AnalyzeResponse
from app.services.orchestrator import run_pipeline
from app.services.search_service import hybrid_search

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])


@router.get("/summary", response_model=dict)
def get_analysis_summary(query: str, db: Session = Depends(get_db)):
    """
    Get 3-layer intelligence summary: Verification, Community, Web.
    """
    return hybrid_search(db, query)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    company_name: str = Form(default=""),
    job_description: str = Form(default=""),
    url: str = Form(default=""),
    file: Annotated[UploadFile | None, File(description="Optional image of job posting")] = None,
    db: Session = Depends(get_db),
):
    """
    Unified multi-signal analysis endpoint.
    Runs the 5-layer intelligence pipeline.
    """
    # Read image if provided
    image_bytes = None
    if file is not None:
        try:
            image_bytes = await file.read()
            from PIL import Image
            from io import BytesIO
            Image.open(BytesIO(image_bytes)).verify()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file must be a valid image (JPEG, PNG, or WebP)",
            )

    # Need at least something to analyze
    has_input = bool(
        company_name.strip()
        or job_description.strip()
        or url.strip()
        or image_bytes
    )
    if not has_input:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least a company name, description, URL, or image.",
        )

    try:
        result = run_pipeline(
            db=db,
            company_name=company_name,
            job_description=job_description,
            url=url,
            image_bytes=image_bytes,
        )
        return result
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
