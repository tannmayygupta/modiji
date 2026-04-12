import sys
import os
import json

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.internship import Internship

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ml", "data", "generated")

def safe_seed():
    db = SessionLocal()
    try:
        if db.query(Internship).count() > 0:
            print("Internships are already seeded. Skipping.")
            return

        internships_file = os.path.join(DATA_DIR, "internships.json")
        with open(internships_file, "r", encoding="utf-8") as f:
            internships_data = json.load(f)

        print(f"Loading {len(internships_data)} internships...")
        for i in internships_data:
            internship = Internship(
                id=i["id"],
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
                is_verified=True,
                fraud_risk_score=0.0
            )
            db.add(internship)

        db.commit()
        print("Database seeded with internships successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    safe_seed()
