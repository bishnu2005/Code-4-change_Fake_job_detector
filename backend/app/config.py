"""
Application configuration via environment variables.
"""
import os

# ── Database ─────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./hireliar.db"
)

# ── Model artifact paths ─────────────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join("artifacts", "model.pkl"))
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", os.path.join("artifacts", "vectorizer.pkl"))
CALIBRATED_MODEL_PATH = os.getenv(
    "CALIBRATED_MODEL_PATH", os.path.join("artifacts", "calibrated_model.pkl")
)
THRESHOLD_PATH = os.getenv(
    "THRESHOLD_PATH", os.path.join("artifacts", "threshold.json")
)

# ── CORS ─────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ── Google Safe Browsing ─────────────────────────────────────────
SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY", "")
SAFE_BROWSING_TIMEOUT = int(os.getenv("SAFE_BROWSING_TIMEOUT", "5"))

# ── Suspicious keywords ─────────────────────────────────────────
SUSPICIOUS_KEYWORDS = [
    "no interview", "urgent hiring", "registration fee",
    "work from home", "guaranteed income", "no experience needed",
    "easy money", "act now", "limited time offer", "wire transfer",
]

# ── Risk level thresholds ────────────────────────────────────────
RISK_THRESHOLD_HIGH = 70
RISK_THRESHOLD_SUSPICIOUS = 40

# ── Debug ────────────────────────────────────────────────────────
DEBUG_LOGGING = os.getenv("DEBUG_LOGGING", "false").lower() == "true"
