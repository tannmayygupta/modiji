"""
Recommendation Service — Bridge between FastAPI backend and ML engine.
Translates ORM models ↔ ML engine dicts for clean separation of concerns.
"""
import logging
from sqlalchemy.orm import Session

# Import models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.models.candidate import Candidate
from app.models.internship import Internship
from app.models.interaction import Interaction
from app.models.recommendation import Recommendation
from app.schemas.schemas import (
    RecommendationCard, RecommendationExplanation, MatchReason, SkillAlignment
)

logger = logging.getLogger(__name__)

# Lazy-load ML engine to handle import errors gracefully
_hybrid_engine = None


def _get_engine():
    global _hybrid_engine
    if _hybrid_engine is None:
        try:
            from ml.engine.hybrid_scorer import load_models, recommend
            load_models()
            _hybrid_engine = recommend  # Store the function itself
            logger.info("Trained ML Hybrid Scorer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ML engine: {e}")
    return _hybrid_engine


class RecommendationService:
    """Bridges FastAPI routes with the ML recommendation engine."""

    def recommend(
        self,
        candidate: Candidate,
        db: Session,
        top_k: int = 5,
    ) -> list[RecommendationCard]:
        """
        Generate recommendations for a candidate using the hybrid engine.

        Falls back to basic scoring if the ML engine is not available.
        """
        engine = _get_engine()
        if not engine:
            logger.warning("ML engine unavailable, using API-level fallback")
            return []

        # Convert ORM candidate to dict
        candidate_dict = self._candidate_to_dict(candidate)

        # Get active internships
        internships = db.query(Internship).filter(Internship.is_active == True).all()
        internship_dicts = [self._internship_to_dict(i) for i in internships]

        if not internship_dicts:
            logger.info("Database internships empty! Falling back to ML Cache for MVP.")
            internship_dicts = None

        # Count candidate interactions for cold-start weight
        interaction_count = db.query(Interaction).filter(
            Interaction.candidate_id == candidate.id
        ).count()

        # Run trained hybrid scorer
        recommend_fn = engine
        recommendations = recommend_fn(
            candidate_dict, internships=internship_dicts, top_n=top_k,
        )

        # Convert to response models and save to DB
        cards = []
        for rec_data in recommendations:
            # Save to DB for tracking
            rec_record = Recommendation(
                candidate_id=candidate.id,
                internship_id=rec_data["internship_id"],
                content_score=rec_data.get("content_score", 0),
                collaborative_score=rec_data.get("collaborative_score", 0),
                affirmative_score=rec_data.get("affirmative_score", 0),
                final_score=rec_data.get("final_score", 0),
                explanation=rec_data.get("explanation", {}),
                display_rank=rec_data.get("display_rank", 0),
            )
            if internship_dicts is not None:
                db.add(rec_record)

            explanation_data = rec_data.get("explanation", {})
            reasons = [
                MatchReason(**r) for r in explanation_data.get("reasons", [])
                if isinstance(r, dict) and "icon" in r and "text" in r
            ]
            skill_align = explanation_data.get("skill_alignment", {})

            card = RecommendationCard(
                id=str(rec_record.id),
                internship_id=rec_data["internship_id"],
                company_name=rec_data.get("company_name", ""),
                role_title=rec_data.get("role_title", ""),
                match_percentage=rec_data.get("match_percentage", 50),
                sector=rec_data.get("sector", ""),
                city=rec_data.get("city", ""),
                state=rec_data.get("state", ""),
                stipend_amount=rec_data.get("stipend_amount"),
                explanation=RecommendationExplanation(
                    match_percentage=rec_data.get("match_percentage", 50),
                    reasons=reasons,
                    skill_alignment=SkillAlignment(**skill_align) if skill_align else None,
                ),
                display_rank=rec_data.get("display_rank", 0),
            )
            cards.append(card)

        if internship_dicts is not None:
            try:
                db.commit()
            except Exception as e:
                logger.error(f"Failed to save recommendations: {e}")
                db.rollback()
        return cards

    def _candidate_to_dict(self, c: Candidate) -> dict:
        """Convert Candidate ORM model to dict for ML engine."""
        return {
            "id": str(c.id),
            "name": c.name,
            "education_level": c.education_level.value if c.education_level else "GRADUATE",
            "field_of_study": c.field_of_study,
            "academic_score": c.academic_score,
            "skills": c.skills or [],
            "state": c.state,
            "district": c.district,
            "is_rural": c.is_rural,
            "is_aspirational_district": c.is_aspirational_district,
            "social_category": c.social_category.value if c.social_category else "GENERAL",
            "sector_preferences": c.sector_preferences or [],
            "location_preference": c.location_preference.value if c.location_preference else "HOME_STATE",
            "has_past_participation": c.has_past_participation,
        }

    def _internship_to_dict(self, i: Internship) -> dict:
        """Convert Internship ORM model to dict for ML engine."""
        return {
            "id": str(i.id),
            "company_name": i.company_name,
            "role_title": i.role_title,
            "description": i.description,
            "required_skills": i.required_skills or [],
            "min_education": i.min_education or "GRADUATE",
            "preferred_fields": i.preferred_fields or [],
            "sector": i.sector,
            "city": i.city,
            "state": i.state,
            "stipend_amount": i.stipend_amount,
            "capacity": i.capacity,
            "filled_count": i.filled_count,
        }
