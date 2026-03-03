import unittest
from app.services.layer1_company import _normalize_domain, verify_company
from app.schemas.analyze import VerificationResult
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.company import Company
from app.database import Base

# Setup in-memory DB for testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

class TestDomainLogic(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        # Seed a company
        self.db.add(Company(name="Google", official_domain="google.com", verification_status="trusted"))
        self.db.commit()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_normalize(self):
        self.assertEqual(_normalize_domain("https://www.google.com/jobs"), "google.com")
        self.assertEqual(_normalize_domain("http://google.com"), "google.com")
        self.assertEqual(_normalize_domain("www.google.com"), "google.com")

    def test_exact_match(self):
        res, decisive = verify_company(self.db, "Google", "https://google.com/careers")
        self.assertEqual(res.status, "trusted")
        self.assertTrue(res.domain_match)
        self.assertFalse(res.deceptive)

    def test_subdomain_match(self):
        res, decisive = verify_company(self.db, "Google", "https://careers.google.com")
        self.assertEqual(res.status, "trusted")
        self.assertTrue(res.domain_match)
        self.assertFalse(res.deceptive)

    def test_deceptive_match(self):
        # google-careers.xyz should NOT match valid, but SHOULD be deceptive
        res, decisive = verify_company(self.db, "Google", "https://google-careers.xyz")
        self.assertEqual(res.status, "trusted") # Identifying the company is correct
        self.assertFalse(res.domain_match)      # But domain does NOT match
        self.assertTrue(res.deceptive)          # And it IS deceptive

    def test_no_match(self):
        res, decisive = verify_company(self.db, "Google", "https://example.com")
        self.assertEqual(res.status, "trusted")
        self.assertFalse(res.domain_match)
        self.assertFalse(res.deceptive)

if __name__ == '__main__':
    unittest.main()
