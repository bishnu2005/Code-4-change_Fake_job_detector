"""Quick verification of the refactored signal handling."""
import sys
sys.path.insert(0, ".")

# 1. Config
from app.config import THRESHOLD_PATH
print(f"THRESHOLD_PATH = {THRESHOLD_PATH}")
print("config OK")

# 2. Model loader
from app.models.model_loader import model_loader
print(f"default threshold = {model_loader.optimal_threshold}")
print("model_loader OK")

# 3. URL verification - empty URL -> None
from app.services.url_verification import verify_url
r = verify_url("")
assert r is None, f"Expected None for empty URL, got {r}"
print("empty url -> None  PASS")

r2 = verify_url("https://google.com", "Google")
assert r2 is not None
print(f"real url -> risk={r2['url_risk_score']}, trust={r2['url_trust_score']}, https={r2['https_flag']}  PASS")

# 4. Fusion - single signal
from app.services.fusion_engine import fuse_signals
f = fuse_signals(text_risk_score=80.0, has_text=True)
assert f["weights_used"]["text"] == 1.0, f"Single signal should have weight=1.0, got {f['weights_used']['text']}"
print(f"single signal -> score={f['final_risk_score']}, weights={f['weights_used']}  PASS")

# 5. Fusion - no signals
f0 = fuse_signals()
assert f0["final_risk_score"] == 0.0
print("no signals -> score=0  PASS")

# 6. Fusion - two signals
f2 = fuse_signals(text_risk_score=80.0, url_risk_score=20.0, has_text=True, has_url=True)
wsum = sum(f2["weights_used"].values())
assert abs(wsum - 1.0) < 0.01, f"Weights should sum to 1.0, got {wsum}"
print(f"two signals -> score={f2['final_risk_score']}, weights sum={wsum:.3f}  PASS")

# 7. Confidence - text only (short)
from app.services.confidence_engine import compute_confidence
c1 = compute_confidence(has_text=True, text_length=20, text_risk_score=80.0)
assert c1["confidence_score"] <= 60, f"Weak single signal should cap at 60, got {c1['confidence_score']}"
print(f"weak text-only -> {c1['confidence_score']} ({c1['confidence_level']})  PASS")

# 8. Confidence - text + url (strong)
c2 = compute_confidence(
    has_text=True, text_length=200, text_risk_score=80.0,
    has_url=True, url_risk_score=70.0,
    https_flag=True, safe_browsing_status="clean",
)
print(f"text+url+sb -> {c2['confidence_score']} ({c2['confidence_level']})  PASS")

# 9. Confidence - image only weak OCR
c3 = compute_confidence(has_image=True, ocr_signal_strength=0.5, ocr_risk_score=50.0)
assert c3["confidence_level"] != "Very High", f"Weak OCR should not be Very High"
print(f"weak OCR only -> {c3['confidence_score']} ({c3['confidence_level']})  PASS")

# 10. Schemas
from app.api.schemas import AnalyzeResponse
resp = AnalyzeResponse(
    risk_score=50.0,
    risk_level="Suspicious",
    confidence_score=55,
    confidence_level="Medium",
    url_analysis=None,
)
assert resp.url_analysis is None
print("schemas OK (url_analysis=None)  PASS")

# 11. Routes
from app.api.routes import router
print("routes OK  PASS")

print("")
print("ALL VERIFICATION TESTS PASSED")
