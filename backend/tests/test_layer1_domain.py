
import pytest
from unittest.mock import MagicMock
from app.services.layer1_company import verify_company, _normalize_domain
from app.models.company import Company
from app.schemas.analyze import VerificationResult

def test_normalize_domain():
    assert _normalize_domain("https://www.google.com") == "google.com"
    assert _normalize_domain("http://google.com/") == "google.com"
    assert _normalize_domain("careers.google.com") == "careers.google.com"

def test_verify_company_exact_match(db_session):
    # Setup
    company = Company(name="Google", official_domain="google.com", verification_status="trusted")
    db = MagicMock()
    db.query.return_value.all.return_value = [company]
    
    # Execution
    result, decisive = verify_company(db, "Google", "https://google.com")
    
    # Assertion
    assert result.status == "trusted"
    assert result.domain_match is True
    assert decisive is True

def test_verify_company_subdomain_match(db_session):
    # Setup
    company = Company(name="Google", official_domain="google.com", verification_status="trusted")
    db = MagicMock()
    db.query.return_value.all.return_value = [company]
    
    # Execution: careers.google.com should match google.com
    result, decisive = verify_company(db, "Google", "https://careers.google.com/jobs")
    
    # Assertion
    assert result.domain_match is True
    assert decisive is True

def test_verify_company_deceptive_domain(db_session):
    # Setup
    company = Company(name="Google", official_domain="google.com", verification_status="trusted")
    db = MagicMock()
    db.query.return_value.all.return_value = [company]
    
    # Execution: google-careers.xyz should NOT match
    result, decisive = verify_company(db, "Google", "https://google-careers.xyz")
    
    # Assertion
    assert result.domain_match is False
    assert decisive is False
