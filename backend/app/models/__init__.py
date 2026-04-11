"""
Models package - imports all ORM models for Alembic and session use.
"""
from app.models.candidate import Candidate, EducationLevel, SocialCategory, LocationPreference
from app.models.internship import Internship
from app.models.interaction import Interaction, InteractionType, INTERACTION_WEIGHTS
from app.models.recommendation import Recommendation
from app.models.document import CandidateDocument

__all__ = [
    "Candidate", "EducationLevel", "SocialCategory", "LocationPreference",
    "Internship",
    "Interaction", "InteractionType", "INTERACTION_WEIGHTS",
    "Recommendation",
    "CandidateDocument",
]
