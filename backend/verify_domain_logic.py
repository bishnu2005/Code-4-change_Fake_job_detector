
from app.services.layer1_company import verify_company, _normalize_domain
from app.models.company import Company
from unittest.mock import MagicMock
import sys

def run_tests():
    print("Running domain verification tests...")
    
    # Test normalization
    assert _normalize_domain("https://www.google.com") == "google.com", "Normalization failed"
    assert _normalize_domain("http://google.com/") == "google.com", "Normalization failed"
    assert _normalize_domain("careers.google.com") == "careers.google.com", "Normalization failed"
    print("✅ Normalization tests passed")

    # Mock DB
    company = Company(name="Google", official_domain="google.com", verification_status="trusted")
    db = MagicMock()
    # Mock query.all()
    db.query.return_value.all.return_value = [company]

    # Test Exact Match
    result, decisive = verify_company(db, "Google", "https://google.com")
    if result.status == "trusted" and result.domain_match is True and decisive is True:
        print("✅ Exact match test passed")
    else:
        print(f"❌ Exact match failed: {result.status}, {result.domain_match}, {decisive}")
        sys.exit(1)

    # Test Subdomain Match
    result, decisive = verify_company(db, "Google", "https://careers.google.com/jobs")
    if result.domain_match is True and decisive is True:
        print("✅ Subdomain match test passed")
    else:
        print(f"❌ Subdomain match failed: {result.domain_match}, {decisive}")
        sys.exit(1)

    # Test Deceptive Domain
    result, decisive = verify_company(db, "Google", "https://google-careers.xyz")
    if result.domain_match is False and decisive is False:
        print("✅ Deceptive domain test passed")
    else:
        print(f"❌ Deceptive domain test failed: {result.domain_match}, {decisive}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        run_tests()
        print("\n🎉 ALL TESTS PASSED")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
