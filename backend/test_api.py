"""Concise verification of all API responses."""
import requests
import json

BASE = "http://localhost:8000"

# 1. Health
r = requests.get(f"{BASE}/health")
assert r.status_code == 200
assert r.json()["status"] == "healthy"
print("[PASS] Health check")

# 2. User create
r = requests.post(f"{BASE}/users/login", json={"username": "verify_user"})
assert r.status_code == 200
uid = r.json()["id"]
print(f"[PASS] User login (id={uid})")

# 3. Create report
r = requests.post(f"{BASE}/feed", json={
    "user_id": uid, "company_name": "BadCorp", "domain": "badcorp.xyz",
    "title": "Scam alert", "description": "Asked for money", "verdict": "scam"
})
assert r.status_code == 201
rid = r.json()["id"]
print(f"[PASS] Create report (id={rid})")

# 4. Feed
r = requests.get(f"{BASE}/feed")
assert r.status_code == 200
assert r.json()["total_count"] >= 1
print(f"[PASS] Feed ({r.json()['total_count']} posts)")

# 5. Vote
r = requests.post(f"{BASE}/feed/{rid}/vote", json={"user_id": uid, "vote_type": "up"})
assert r.status_code == 200
assert r.json()["upvotes"] >= 1
print(f"[PASS] Vote (upvotes={r.json()['upvotes']})")

# 6. Duplicate vote rejected
r = requests.post(f"{BASE}/feed/{rid}/vote", json={"user_id": uid, "vote_type": "up"})
assert r.status_code == 409
print("[PASS] Duplicate vote rejected")

# 7. Analyze - verified company
r = requests.post(f"{BASE}/analyze", data={
    "company_name": "Google", "url": "https://careers.google.com/jobs"
})
assert r.status_code == 200
d = r.json()
assert d["verification"]["status"] == "trusted"
assert d["verification"]["domain_match"] == True
assert d["final_risk"]["level"] == "Safe"
assert d["ml"]["triggered"] == False
print(f"[PASS] Analyze: Google verified (risk={d['final_risk']['score']}, ML skipped)")

# 8. Analyze - suspicious
r = requests.post(f"{BASE}/analyze", data={
    "company_name": "XYZ Corp",
    "job_description": "Urgent hiring no experience easy money guaranteed income registration fee",
    "url": "https://google-career-fastapply.xyz/apply"
})
assert r.status_code == 200
d = r.json()
assert d["domain"]["suspicious_tld"] == True
assert d["domain"]["blacklist_hits"] >= 1
assert d["ml"]["triggered"] == True
assert d["final_risk"]["score"] > 40
assert d["confidence"]["score"] <= 95
print(f"[PASS] Analyze: Suspicious (risk={d['final_risk']['score']}, ML={d['ml']['risk_score']}, conf={d['confidence']['score']})")

# 9. Company search
r = requests.get(f"{BASE}/feed/search/company", params={"company": "BadCorp"})
assert r.status_code == 200
assert "credibility_score" in r.json()
print(f"[PASS] Company credibility search (score={r.json()['credibility_score']})")

print("\n✅ ALL 9 TESTS PASSED")
