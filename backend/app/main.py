"""
Multi-Signal Fraud Intelligence System — FastAPI Application Entry Point.
"""
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # load .env before accessing config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    CORS_ORIGINS,
    MODEL_PATH,
    VECTORIZER_PATH,
    CALIBRATED_MODEL_PATH,
    THRESHOLD_PATH,
)
from app.models.model_loader import model_loader
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML model + calibrated model at startup."""
    logger.info("Starting up — loading model artifacts...")
    loaded = model_loader.load(
        model_path=MODEL_PATH,
        vectorizer_path=VECTORIZER_PATH,
        calibrated_model_path=CALIBRATED_MODEL_PATH,
        threshold_path=THRESHOLD_PATH,
    )
    if loaded:
        logger.info("✅ Model loaded successfully.")
        if model_loader.has_calibrated:
            logger.info("✅ Calibrated model available.")
        else:
            logger.info("ℹ️  Using uncalibrated model (calibrated_model.pkl not found).")
    else:
        logger.warning(
            "⚠️  Model artifacts not found. "
            "Endpoints will return 503. "
            "Run 'python -m training.train' to generate artifacts."
        )
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Multi-Signal Fraud Intelligence System",
    description=(
        "Calibrated ML + SHAP + URL verification + "
        "Google Safe Browsing + adaptive fusion"
    ),
    version="2.0.0",
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
