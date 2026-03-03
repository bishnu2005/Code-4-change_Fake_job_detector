"""
Application configuration via environment variables.
"""
import os

# ── Model artifact paths (relative to backend/) ─────────────────
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
    "no interview",
    "urgent hiring",
    "registration fee",
    "work from home",
    "guaranteed income",
    "no experience needed",
    "easy money",
    "act now",
    "limited time offer",
    "wire transfer",
]

# ── Suspicious TLDs / free domains ───────────────────────────────
SUSPICIOUS_TLDS = [
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".top", ".buzz", ".club", ".work", ".click",
]

# ── Salary thresholds ────────────────────────────────────────────
MAX_REASONABLE_SALARY = 500000  # yearly USD
MIN_REASONABLE_SALARY = 10000   # yearly USD

# ── Risk level thresholds ────────────────────────────────────────
RISK_THRESHOLD_HIGH = 70
RISK_THRESHOLD_SUSPICIOUS = 40

# ── Fusion engine base weights ───────────────────────────────────
WEIGHT_TEXT = 0.45
WEIGHT_OCR = 0.20
WEIGHT_URL = 0.25
WEIGHT_EMAIL = 0.10

# ── OCR thresholds ───────────────────────────────────────────────
OCR_MIN_TEXT_LENGTH = 30      # characters
OCR_WEAK_SIGNAL_THRESHOLD = 0.3  # proportion considered weak

# ── Confidence parameters ────────────────────────────────────────
CONFIDENCE_BASE = 40

# ── Data sufficiency ─────────────────────────────────────────────
MIN_TEXT_LENGTH = 80  # characters for sufficient text
MIN_WORD_COUNT = 5    # minimum meaningful words for sufficiency

# ── Timeout guards ───────────────────────────────────────────────
MX_LOOKUP_TIMEOUT = 2           # seconds for MX DNS resolution
INFERENCE_TIMEOUT = 5           # seconds global inference cap
DEBUG_LOGGING = os.getenv("DEBUG_LOGGING", "false").lower() == "true"

# ── SHAP ─────────────────────────────────────────────────────────
SHAP_TOP_N = 5  # top N risk/trust factors to return

# ── Domain blacklist path ────────────────────────────────────────
DOMAIN_BLACKLIST_PATH = os.getenv(
    "DOMAIN_BLACKLIST_PATH", os.path.join("app", "data", "domain_blacklist.json")
)
