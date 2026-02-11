"""
Fake Job Posting Detector — FastAPI Application Entry Point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, MODEL_PATH, VECTORIZER_PATH
from app.models.model_loader import model_loader
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML model once at startup."""
    logger.info("Starting up — loading model artifacts...")
    loaded = model_loader.load(MODEL_PATH, VECTORIZER_PATH)
    if loaded:
        logger.info("✅ Model loaded successfully.")
    else:
        logger.warning("⚠️  Model artifacts not found. "
                        "Heuristic-only mode active. "
                        "Run 'python -m training.train' to generate artifacts.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Fake Job Posting Detector",
    description="ML + heuristic-based fraud detection for job postings",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────
app.include_router(router)
