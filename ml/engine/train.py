"""
ml/engine/train.py
Master training script. Run this once to train the complete ML pipeline.

Usage: python -m ml.engine.train
"""

import sys
import os
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)


def main():
    print("=" * 60)
    print("PMIS ML Training Pipeline")
    print("=" * 60)

    # Step 1: Generate dataset
    print("\n[1/4] Generating dataset from real PMIS anchors...")
    t = time.time()
    from ml.data.pipeline import run_pipeline
    run_pipeline()
    print(f"Done in {time.time()-t:.1f}s")

    # Step 2: Build skill taxonomy
    print("\n[2/4] Building skill taxonomy (TF-IDF co-occurrence)...")
    t = time.time()
    from ml.engine.skill_taxonomy import build_skill_taxonomy
    build_skill_taxonomy()
    print(f"Done in {time.time()-t:.1f}s")

    # Step 3: Train collaborative filter
    print("\n[3/4] Training SVD collaborative filter...")
    t = time.time()
    from ml.engine.train_cf import train_collaborative_filter
    train_collaborative_filter()
    print(f"Done in {time.time()-t:.1f}s")

    # Step 4: Smoke test
    print("\n[4/4] Running smoke test...")
    t = time.time()
    from ml.engine.hybrid_scorer import load_models, recommend
    load_models()

    test_candidate = {
        "id": "smoke-test-001",
        "education_level": "GRADUATE",
        "field_of_study": "Computer Science",
        "skills": ["Python", "SQL", "Data Analysis"],
        "sector_preferences": ["IT & Software Development"],
        "state": "Maharashtra",
        "location_preference": "HOME_STATE",
        "social_category": "SC",
        "is_rural": True,
        "is_aspirational_district": False,
        "has_past_participation": False,
        "video_overall_score": 78,
        "video_skills_detected": ["Python", "Communication"],
    }

    results = recommend(test_candidate, top_n=5)

    print(f"\nSmoke test: Rural SC Graduate from Maharashtra (Python + SQL + Data Analysis)")
    print(f"Top 5 recommendations:")
    for r in results:
        boost_parts = []
        if r["affirmative_score"] > 0:
            boost_parts.append(f"+{int(r['affirmative_score']*100)}% diversity")
        if r.get("explanation", {}).get("reasons"):
            for reason in r["explanation"]["reasons"]:
                if reason.get("category") == "video":
                    boost_parts.append(reason["text"])
        boost_str = " | ".join(boost_parts)
        boost_display = f" ({boost_str})" if boost_str else ""
        print(f"  {r['display_rank']}. {r['company_name']} - {r['role_title']}")
        print(f"     {r['match_percentage']}% match | Rs.{r['stipend_amount']}/mo | {r['city']}, {r['state']}{boost_display}")

    print(f"\nDone in {time.time()-t:.1f}s")
    print("\n" + "=" * 60)
    print("Training complete. Models saved to ml/models/")
    print("Next: cd backend && python -m app.db.seed")
    print("=" * 60)


if __name__ == "__main__":
    main()
