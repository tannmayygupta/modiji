"""
Interaction Tracking API Routes.
Logs user interactions (view, save, apply) for collaborative filtering.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.internship import Internship
from app.models.interaction import Interaction, InteractionType
from app.models.recommendation import Recommendation
from app.schemas.schemas import InteractionCreate
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.post("/view")
def log_view(
    data: InteractionCreate,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log that a candidate viewed an internship."""
    return _log_interaction(current_user, data.internship_id, InteractionType.VIEW, db)


@router.post("/save")
def save_internship(
    data: InteractionCreate,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save an internship to the candidate's list."""
    return _log_interaction(current_user, data.internship_id, InteractionType.SAVE, db)


@router.post("/apply")
def apply_to_internship(
    data: InteractionCreate,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply to an internship. Also marks any related recommendation as applied."""
    result = _log_interaction(current_user, data.internship_id, InteractionType.APPLY, db)

    # Update recommendation tracking if this came from a recommendation
    rec = db.query(Recommendation).filter(
        Recommendation.candidate_id == current_user.id,
        Recommendation.internship_id == data.internship_id,
    ).first()
    if rec:
        rec.was_applied = True
        db.commit()

    return result


@router.get("/saved")
def get_saved_internships(
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of internships saved by the candidate."""
    saved = db.query(Interaction).filter(
        Interaction.candidate_id == current_user.id,
        Interaction.interaction_type == InteractionType.SAVE,
    ).all()

    internship_ids = list(set(s.internship_id for s in saved))
    internships = db.query(Internship).filter(Internship.id.in_(internship_ids)).all()

    return {
        "saved_count": len(internships),
        "internships": [
            {
                "id": str(i.id),
                "company_name": i.company_name,
                "role_title": i.role_title,
                "sector": i.sector,
                "city": i.city,
                "state": i.state,
                "stipend_amount": i.stipend_amount,
            }
            for i in internships
        ],
    }


@router.get("/applied")
def get_applied_internships(
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of internships applied to by the candidate."""
    applied = db.query(Interaction).filter(
        Interaction.candidate_id == current_user.id,
        Interaction.interaction_type == InteractionType.APPLY,
    ).all()

    internship_ids = list(set(s.internship_id for s in applied))
    internships = db.query(Internship).filter(Internship.id.in_(internship_ids)).all()

    return {
        "applied_count": len(internships),
        "internships": [
            {
                "id": str(i.id),
                "company_name": i.company_name,
                "role_title": i.role_title,
                "sector": i.sector,
                "city": i.city,
                "state": i.state,
                "stipend_amount": i.stipend_amount,
            }
            for i in internships
        ],
    }


@router.get("/history")
def get_interaction_history(
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the candidate's interaction history (applications, views, etc.)."""
    interactions = db.query(Interaction).filter(
        Interaction.candidate_id == current_user.id,
    ).order_by(Interaction.created_at.desc()).limit(50).all()

    return {
        "total": len(interactions),
        "interactions": [
            {
                "id": str(i.id),
                "internship_id": str(i.internship_id),
                "type": i.interaction_type.value,
                "created_at": i.created_at.isoformat(),
            }
            for i in interactions
        ],
    }


def _log_interaction(
    candidate: Candidate,
    internship_id: str,
    interaction_type: InteractionType,
    db: Session,
):
    """Helper to create an interaction record."""
    # Verify internship exists
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    interaction = Interaction(
        candidate_id=candidate.id,
        internship_id=internship_id,
        interaction_type=interaction_type,
    )
    db.add(interaction)
    db.commit()

    return {
        "status": "recorded",
        "interaction_type": interaction_type.value,
        "internship_id": internship_id,
    }
