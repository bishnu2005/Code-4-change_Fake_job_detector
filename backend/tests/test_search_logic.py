import unittest
from app.services.search_service import hybrid_search
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.company import Company
from app.models.community_report import CommunityReport
from app.models.user import User
from app.models import scam_domain, domain_cache, vote # Ensure all models loaded
from app.database import Base

# Setup in-memory DB for testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

class TestSearchLogic(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        # Seed user first (FK dependency)
        user = User(username="tester", google_id="123", email="test@test.com")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Seed data
        self.db.add(Company(name="Stripe", official_domain="stripe.com", verification_status="trusted"))
        self.db.add(CommunityReport(company_name="Stripe", domain="stripe.com", verdict="legit", title="Great", description=".", upvotes=10, downvotes=0, user_id=user.id))
        self.db.commit()

    def tearDown(self):
        self.db.rollback()
        self.db.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_hybrid_search_found(self):
        results = hybrid_search(self.db, "Stripe")
        self.assertEqual(len(results["companies"]), 1)
        self.assertEqual(len(results["reports"]), 1)
        # Should be enough to NOT trigger web mentions (1+1 >= 3? No, 2 < 3, so web mentions SHOULD trigger)
        # Wait, 1 company + 1 report = 2. 2 < 3. So Web SHOULD be present (mocked).
        self.assertTrue(len(results["web_mentions"]) > 0)
        self.assertEqual(results["web_mentions"][0]["source"], "Reddit")

    def test_hybrid_search_empty(self):
        results = hybrid_search(self.db, "NonExistent")
        self.assertEqual(len(results["companies"]), 0)
        self.assertEqual(len(results["reports"]), 0)
        # 0 < 3, so web mentions should trigger
        self.assertTrue(len(results["web_mentions"]) > 0)

if __name__ == '__main__':
    unittest.main()
