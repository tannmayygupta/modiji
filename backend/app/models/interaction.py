"""
SQLAlchemy ORM Model: Interaction
Tracks user interactions with internships (view, save, apply, etc.)
Used as input for the collaborative filtering engine.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class InteractionType(str, enum.Enum):
    VIEW = "VIEW"
    SAVE = "SAVE"
    APPLY = "APPLY"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    COMPLETE = "COMPLETE"


# Interaction weights for collaborative filtering
INTERACTION_WEIGHTS = {
    InteractionType.VIEW: 1.0,
    InteractionType.SAVE: 2.0,
    InteractionType.APPLY: 3.0,
    InteractionType.ACCEPT: 5.0,
    InteractionType.REJECT: -1.0,
    InteractionType.COMPLETE: 5.0,
}


class Interaction(Base):
    """A record of a candidate interacting with an internship."""

    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    candidate_id = Column(
        String(36),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    internship_id = Column(
        String(36),
        ForeignKey("internships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    interaction_type = Column(
        Enum(InteractionType, name="interaction_type_enum"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="interactions")
    internship = relationship("Internship", back_populates="interactions")

    def __repr__(self):
        return f"<Interaction(candidate={self.candidate_id}, type={self.interaction_type})>"
