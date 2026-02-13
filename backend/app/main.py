"""
HireLiar — Layered Intelligence Fraud Detection System.
FastAPI Application Entry Point.
"""
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    CORS_ORIGINS, MODEL_PATH, VECTORIZER_PATH,
    CALIBRATED_MODEL_PATH, THRESHOLD_PATH,
)
from app.database import init_db, SessionLocal
from app.seed import run_seed
from app.models.model_loader import model_loader
from app.api.routes_analyze import router as analyze_router
from app.api.routes_feed import router as feed_router
from app.api.routes_users import router as users_router
from app.api.routes_health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB, seed data, load ML model at startup."""
    # 1. Create tables
    logger.info("Initializing database...")
    init_db()

    # 2. Seed data
    logger.info("Seeding database...")
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()

    # 3. Load ML model
    logger.info("Loading ML model artifacts...")
    loaded = model_loader.load(
        model_path=MODEL_PATH,
        vectorizer_path=VECTORIZER_PATH,
        calibrated_model_path=CALIBRATED_MODEL_PATH,
        threshold_path=THRESHOLD_PATH,
    )
    if loaded:
        logger.info("✅ ML model loaded.")
    else:
        logger.warning("⚠️ ML model not found — Layer 4 will be skipped.")

    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="HireLiar — Layered Intelligence Fraud Detection",
    description=(
        "5-layer intelligence pipeline: Company Verification → "
        "Community Intelligence → Domain Intelligence → "
        "Conditional ML → Deep Content Analysis"
    ),
    version="3.0.0",
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
app.include_router(analyze_router)
app.include_router(feed_router)
app.include_router(users_router)
app.include_router(health_router)
