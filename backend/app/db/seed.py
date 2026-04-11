"""
Database Seeder Script

Loads synthetic data into the database for development and testing.
Run with: python -m app.db.seed
"""
import sys
import os
import json
import uuid

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal, engine, Base
from app.models.candidate import Candidate, EducationLevel, SocialCategory, LocationPreference
from app.models.internship import Internship
from app.models.interaction import Interaction, InteractionType
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "ml", "data", "generated")


def seed_database():
    """Load synthetic data into the database."""
    # Drop all tables first so we can recreate them with the new schema columns
    Base.metadata.drop_all(bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        existing_candidates = db.query(Candidate).count()
        if existing_candidates > 0:
            print(f"⚠️  Database already has {existing_candidates} candidates. Skipping seed.")
            return

        # Load generated data
        candidates_file = os.path.join(DATA_DIR, "candidates.json")
        internships_file = os.path.join(DATA_DIR, "internships.json")
        interactions_file = os.path.join(DATA_DIR, "interactions.json")

        if not os.path.exists(candidates_file):
            print("❌ No generated data found. Run the synthetic generator first:")
            print("   cd ml/data && python synthetic_generator.py")
            return

        with open(candidates_file, "r", encoding="utf-8") as f:
            candidates_data = json.load(f)
        with open(internships_file, "r", encoding="utf-8") as f:
            internships_data = json.load(f)
        with open(interactions_file, "r", encoding="utf-8") as f:
            interactions_data = json.load(f)

        print(f"📦 Loading {len(candidates_data)} candidates...")
        for c in candidates_data:
            candidate = Candidate(
                id=uuid.UUID(c["id"]),
                name=c["name"],
                email=c["email"],
                phone=c.get("phone"),
                password_hash=pwd_context.hash("password123"),  # Default password for testing
                education_level=EducationLevel(c["education_level"]),
                field_of_study=c.get("field_of_study"),
                academic_score=c.get("academic_score"),
                skills=c.get("skills", []),
                state=c.get("state"),
                district=c.get("district"),
                is_rural=c.get("is_rural", False),
                is_aspirational_district=c.get("is_aspirational_district", False),
                social_category=SocialCategory(c["social_category"]) if c.get("social_category") else None,
                sector_preferences=c.get("sector_preferences", []),
                location_preference=LocationPreference(c["location_preference"]) if c.get("location_preference") else None,
                preferred_language=c.get("preferred_language", "en"),
                has_past_participation=c.get("has_past_participation", False),
            )
            db.add(candidate)

        db.flush()
        print(f"✅ Loaded {len(candidates_data)} candidates")

        print(f"📦 Loading {len(internships_data)} internships...")
        for i in internships_data:
            internship = Internship(
                id=uuid.UUID(i["id"]),
                company_name=i["company_name"],
                company_description=i.get("company_description"),
                role_title=i["role_title"],
                description=i["description"],
                required_skills=i.get("required_skills", []),
                min_education=i.get("min_education", "GRADUATE"),
                preferred_fields=i.get("preferred_fields", []),
                sector=i["sector"],
                city=i["city"],
                state=i["state"],
                stipend_amount=i.get("stipend_amount", 5000),
                capacity=i.get("capacity", 10),
                filled_count=i.get("filled_count", 0),
                duration_months=i.get("duration_months", 12),
                is_active=i.get("is_active", True),
                is_verified=True,          # Assume existing synthetic data is clean
                fraud_risk_score=0.0       # Zero risk for synthetic data
            )
            db.add(internship)

        db.flush()
        print(f"✅ Loaded {len(internships_data)} internships")

        print(f"📦 Loading {len(interactions_data)} interactions...")
        for ix in interactions_data:
            interaction = Interaction(
                id=uuid.UUID(ix["id"]),
                candidate_id=uuid.UUID(ix["candidate_id"]),
                internship_id=uuid.UUID(ix["internship_id"]),
                interaction_type=InteractionType(ix["interaction_type"]),
            )
            db.add(interaction)

        db.commit()
        print(f"✅ Loaded {len(interactions_data)} interactions")
        print(f"\n🎉 Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
