"""Health check route."""
from fastapi import APIRouter
from app.models.model_loader import model_loader

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model_loader.is_loaded,
        "calibrated": model_loader.has_calibrated,
    }
