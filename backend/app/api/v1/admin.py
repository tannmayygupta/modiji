"""
Admin & Analytics API Routes.
Dashboard metrics, model performance, and system management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.internship import Internship
from app.models.interaction import Interaction, InteractionType
from app.models.recommendation import Recommendation

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall system statistics for the admin dashboard."""
    total_candidates = db.query(func.count(Candidate.id)).scalar() or 0
    total_internships = db.query(func.count(Internship.id)).scalar() or 0
    total_applications = db.query(func.count(Interaction.id)).filter(
        Interaction.interaction_type == InteractionType.APPLY
    ).scalar() or 0
    total_recommendations = db.query(func.count(Recommendation.id)).scalar() or 0

    # Average match score
    avg_score = db.query(func.avg(Recommendation.final_score)).scalar() or 0.0

    # Conversion rate: recommendations that led to applications
    recs_clicked = db.query(func.count(Recommendation.id)).filter(
        Recommendation.was_applied == True
    ).scalar() or 0
    conversion_rate = (recs_clicked / total_recommendations * 100) if total_recommendations > 0 else 0.0

    # Category distribution
    category_dist = {}
    category_counts = db.query(
        Candidate.social_category, func.count(Candidate.id)
    ).group_by(Candidate.social_category).all()
    for cat, count in category_counts:
        category_dist[cat.value if cat else "UNKNOWN"] = count

    # Top sectors by application count
    top_sectors = db.query(
        Internship.sector, func.count(Interaction.id)
    ).join(
        Interaction, Interaction.internship_id == Internship.id
    ).filter(
        Interaction.interaction_type == InteractionType.APPLY
    ).group_by(Internship.sector).order_by(func.count(Interaction.id).desc()).limit(10).all()

    return {
        "total_candidates": total_candidates,
        "total_internships": total_internships,
        "total_applications": total_applications,
        "total_recommendations_generated": total_recommendations,
        "avg_match_score": round(avg_score, 4),
        "conversion_rate": round(conversion_rate, 2),
        "category_distribution": category_dist,
        "top_sectors": [{"sector": s, "applications": c} for s, c in top_sectors],
        "active_internships": db.query(func.count(Internship.id)).filter(
            Internship.is_active == True
        ).scalar() or 0,
    }


@router.get("/model-performance")
def get_model_metrics(db: Session = Depends(get_db)):
    """
    Get ML model performance metrics.
    In production, these would be computed by the evaluation pipeline.
    """
    total_recs = db.query(func.count(Recommendation.id)).scalar() or 0
    clicked_recs = db.query(func.count(Recommendation.id)).filter(
        Recommendation.was_clicked == True
    ).scalar() or 0
    applied_recs = db.query(func.count(Recommendation.id)).filter(
        Recommendation.was_applied == True
    ).scalar() or 0

    return {
        "total_recommendations": total_recs,
        "click_through_rate": round(clicked_recs / total_recs * 100, 2) if total_recs > 0 else 0,
        "application_rate": round(applied_recs / total_recs * 100, 2) if total_recs > 0 else 0,
        "avg_score": round(
            db.query(func.avg(Recommendation.final_score)).scalar() or 0, 4
        ),
        "score_distribution": {
            "90-100%": db.query(func.count(Recommendation.id)).filter(Recommendation.final_score >= 0.9).scalar() or 0,
            "70-89%": db.query(func.count(Recommendation.id)).filter(Recommendation.final_score >= 0.7, Recommendation.final_score < 0.9).scalar() or 0,
            "50-69%": db.query(func.count(Recommendation.id)).filter(Recommendation.final_score >= 0.5, Recommendation.final_score < 0.7).scalar() or 0,
            "<50%": db.query(func.count(Recommendation.id)).filter(Recommendation.final_score < 0.5).scalar() or 0,
        },
        "engine_version": "hybrid-v1",
        "note": "Full precision@5, NDCG, fairness metrics available after evaluation pipeline setup"
    }


@router.get("/candidates/demographics")
def get_demographics(db: Session = Depends(get_db)):
    """Get candidate demographic breakdown for affirmative action reporting."""
    # By social category
    by_category = dict(
        db.query(Candidate.social_category, func.count(Candidate.id))
        .group_by(Candidate.social_category).all()
    )

    # Aspirational districts
    aspirational = db.query(func.count(Candidate.id)).filter(
        Candidate.is_aspirational_district == True
    ).scalar() or 0
    rural = db.query(func.count(Candidate.id)).filter(
        Candidate.is_rural == True
    ).scalar() or 0
    total = db.query(func.count(Candidate.id)).scalar() or 0

    # By education level
    by_education = dict(
        db.query(Candidate.education_level, func.count(Candidate.id))
        .group_by(Candidate.education_level).all()
    )

    return {
        "total_candidates": total,
        "by_social_category": {(k.value if k else "UNKNOWN"): v for k, v in by_category.items()},
        "aspirational_district_candidates": aspirational,
        "aspirational_percentage": round(aspirational / total * 100, 1) if total > 0 else 0,
        "rural_candidates": rural,
        "rural_percentage": round(rural / total * 100, 1) if total > 0 else 0,
        "by_education_level": {(k.value if k else "UNKNOWN"): v for k, v in by_education.items()},
    }
