"""
Application configuration via environment variables.
"""
import os

# Paths to trained model artifacts (relative to backend/)
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join("artifacts", "model.pkl"))
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", os.path.join("artifacts", "vectorizer.pkl"))

# CORS origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Suspicious keywords used in heuristic analysis
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

# Suspicious TLDs / free domains
SUSPICIOUS_TLDS = [
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".top", ".buzz", ".club", ".work", ".click",
]

# Salary thresholds
MAX_REASONABLE_SALARY = 500000  # yearly USD
MIN_REASONABLE_SALARY = 10000   # yearly USD

# Risk level thresholds
RISK_THRESHOLD_HIGH = 70
RISK_THRESHOLD_SUSPICIOUS = 40
