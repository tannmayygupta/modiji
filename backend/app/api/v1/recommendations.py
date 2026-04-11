"""
Recommendation API Routes.
Serves AI-generated personalized internship recommendations.
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.internship import Internship
from app.models.recommendation import Recommendation
from app.schemas.schemas import (
    RecommendationCard, RecommendationListResponse,
    RecommendationExplanation, MatchReason, SkillAlignment, FeedbackCreate
)
from app.api.v1.auth import get_current_user

# Lazy import ML engine to avoid import errors during initial setup
_recommendation_service = None


def get_recommendation_service():
    """Lazy-load the recommendation service."""
    global _recommendation_service
    if _recommendation_service is None:
        try:
            from app.services.recommendation_service import RecommendationService
            _recommendation_service = RecommendationService()
        except ImportError:
            _recommendation_service = None
    return _recommendation_service


router = APIRouter()


@router.get("/", response_model=RecommendationListResponse)
def get_recommendations(
    top_k: int = 5,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get personalized internship recommendations for the current user.
    Uses the hybrid AI engine (content-based + collaborative filtering).
    """
    # Validate that the user has completed the wizard
    if not current_user.skills:
        raise HTTPException(
            status_code=400,
            detail="Please complete the onboarding wizard first to receive recommendations."
        )

    start_time = time.time()

    # Try to use the ML engine, fall back to content-based scoring
    service = get_recommendation_service()

    if service:
        recommendations = service.recommend(current_user, db, top_k=top_k)
    else:
        # Fallback: basic scoring without ML engine
        recommendations = _fallback_recommendations(current_user, db, top_k)

    latency_ms = (time.time() - start_time) * 1000

    return RecommendationListResponse(
        candidate_id=str(current_user.id),
        recommendations=recommendations,
        generated_at=datetime.utcnow(),
        engine_version="hybrid-v1" if service else "fallback-v1",
    )


def _fallback_recommendations(
    candidate: Candidate, db: Session, top_k: int
) -> list[RecommendationCard]:
    """
    Basic content-based recommendations without the ML engine.
    Used as fallback when ml/ module is not fully set up.
    """
    internships = db.query(Internship).filter(Internship.is_active == True).all()

    scored = []
    for internship in internships:
        score, reasons, skill_align = _basic_score(candidate, internship)
        scored.append((internship, score, reasons, skill_align))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    cards = []
    for rank, (internship, score, reasons, skill_align) in enumerate(scored[:top_k], 1):
        match_pct = min(99, max(1, int(score * 100)))

        # Save recommendation to DB for tracking
        rec = Recommendation(
            candidate_id=candidate.id,
            internship_id=internship.id,
            content_score=score,
            collaborative_score=0.0,
            affirmative_score=0.0,
            final_score=score,
            explanation={"reasons": [r.model_dump() for r in reasons]},
            display_rank=rank,
        )
        db.add(rec)

        cards.append(RecommendationCard(
            id=str(rec.id),
            internship_id=str(internship.id),
            company_name=internship.company_name,
            role_title=internship.role_title,
            match_percentage=match_pct,
            sector=internship.sector,
            city=internship.city,
            state=internship.state,
            stipend_amount=internship.stipend_amount,
            explanation=RecommendationExplanation(
                match_percentage=match_pct,
                reasons=reasons,
                skill_alignment=skill_align,
            ),
            display_rank=rank,
        ))

    db.commit()
    return cards


def _basic_score(candidate: Candidate, internship: Internship):
    """
    Simple content-based scoring using exact matching.
    Returns (score, reasons, skill_alignment).
    """
    score = 0.0
    reasons = []

    candidate_skills = set(s.lower() for s in (candidate.skills or []))
    required_skills = set(s.lower() for s in (internship.required_skills or []))

    # ── Skill matching (weight: 0.35) ──
    if required_skills:
        matched = candidate_skills & required_skills
        partial = set()  # Would use semantic similarity in full engine
        missing = required_skills - candidate_skills
        skill_score = len(matched) / len(required_skills) if required_skills else 0
        score += 0.35 * skill_score

        if matched:
            reasons.append(MatchReason(
                icon="💻",
                text=f"{len(matched)} of your skills match: {', '.join(list(matched)[:3])}",
                category="skills"
            ))
    else:
        matched, partial, missing = set(), set(), set()
        skill_score = 0.5
        score += 0.35 * 0.5

    skill_alignment = SkillAlignment(
        matched=list(matched),
        partial=list(partial),
        missing=list(missing),
    )

    # ── Education matching (weight: 0.20) ──
    edu_hierarchy = {"10TH": 1, "12TH": 2, "ITI": 2, "DIPLOMA": 3, "GRADUATE": 4, "PG": 5}
    candidate_edu_rank = edu_hierarchy.get(candidate.education_level.value if candidate.education_level else "GRADUATE", 4)
    required_edu_rank = edu_hierarchy.get(internship.min_education, 4)

    if candidate_edu_rank >= required_edu_rank:
        edu_score = 1.0
        reasons.append(MatchReason(
            icon="🎓",
            text=f"Your {candidate.education_level.value if candidate.education_level else 'education'} meets the requirements",
            category="education"
        ))
    else:
        edu_score = max(0.3, candidate_edu_rank / required_edu_rank)
    score += 0.20 * edu_score

    # ── Location matching (weight: 0.20) ──
    loc_score = 0.5
    if candidate.state and internship.state:
        if candidate.state.lower() == internship.state.lower():
            loc_score = 1.0
            reasons.append(MatchReason(
                icon="📍",
                text=f"{internship.city} is in your home state",
                category="location"
            ))
        elif candidate.location_preference and candidate.location_preference.value == "PAN_INDIA":
            loc_score = 0.8
            reasons.append(MatchReason(
                icon="📍",
                text=f"You're open to pan-India locations",
                category="location"
            ))
        else:
            loc_score = 0.4
    score += 0.20 * loc_score

    # ── Sector matching (weight: 0.15) ──
    candidate_sectors = set(s.lower() for s in (candidate.sector_preferences or []))
    if internship.sector and internship.sector.lower() in candidate_sectors:
        sector_score = 1.0
        reasons.append(MatchReason(
            icon="🏢",
            text=f"{internship.sector} matches your sector interest",
            category="sector"
        ))
    elif candidate_sectors:
        sector_score = 0.3
    else:
        sector_score = 0.5
    score += 0.15 * sector_score

    # ── Field of study matching (weight: 0.10) ──
    if candidate.field_of_study and internship.preferred_fields:
        if candidate.field_of_study.lower() in [f.lower() for f in internship.preferred_fields]:
            score += 0.10 * 1.0
        else:
            score += 0.10 * 0.4
    else:
        score += 0.10 * 0.5

    return score, reasons, skill_alignment


@router.post("/{recommendation_id}/feedback")
def submit_feedback(
    recommendation_id: str,
    feedback: FeedbackCreate,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit thumbs up/down feedback on a recommendation."""
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.candidate_id == current_user.id,
    ).first()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.was_clicked = True
    db.commit()

    return {"status": "feedback recorded", "is_positive": feedback.is_positive}


@router.get("/explain/{recommendation_id}")
def explain_recommendation(
    recommendation_id: str,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed explanation for a specific recommendation."""
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.candidate_id == current_user.id,
    ).first()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Mark as clicked
    rec.was_clicked = True
    db.commit()

    return {
        "recommendation_id": str(rec.id),
        "internship_id": str(rec.internship_id),
        "scores": {
            "content_based": round(rec.content_score, 4),
            "collaborative": round(rec.collaborative_score, 4),
            "affirmative_action": round(rec.affirmative_score, 4),
            "final": round(rec.final_score, 4),
        },
        "match_percentage": rec.match_percentage,
        "explanation": rec.explanation,
    }
