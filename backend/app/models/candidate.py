"""
SQLAlchemy ORM Model: Candidate
Represents a student/applicant in the PM Internship Scheme.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, Enum, JSON, Text, Integer
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class EducationLevel(str, enum.Enum):
    TENTH = "10TH"
    TWELFTH = "12TH"
    ITI = "ITI"
    DIPLOMA = "DIPLOMA"
    GRADUATE = "GRADUATE"
    POST_GRADUATE = "PG"


class SocialCategory(str, enum.Enum):
    GENERAL = "GENERAL"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"


class LocationPreference(str, enum.Enum):
    HOME_STATE = "HOME_STATE"
    NEARBY = "NEARBY"
    PAN_INDIA = "PAN_INDIA"


class Candidate(Base):
    """A candidate seeking an internship through the PM Internship Scheme."""

    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aadhaar_hash = Column(String(64), unique=True, nullable=True, index=True)

    # ── 3-Step Auth Gate ──────────────────────────────
    # 1 = Registered (basic signup)
    # 2 = Aadhaar verified (identity confirmed)
    # 3 = Documents verified (admin approved 10th/12th/diploma)
    auth_step = Column(Integer, default=1, nullable=False, index=True)
    aadhaar_name = Column(String(255), nullable=True)  # Name as on Aadhaar, for cross-check

    # Personal Info
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(15), nullable=True)
    password_hash = Column(String(255), nullable=False)

    # Education
    education_level = Column(
        Enum(EducationLevel, name="education_level_enum"),
        nullable=False,
        default=EducationLevel.GRADUATE
    )
    field_of_study = Column(String(255), nullable=True)
    academic_score = Column(Float, nullable=True)  # Percentage or CGPA normalized to 0-100

    # Skills (stored as JSON array for flexibility)
    skills = Column(JSON, nullable=False, default=list)

    # Skill embedding vector (384-dim from sentence-transformers)
    # For pgvector: Column(Vector(384)) — using JSON for SQLite compatibility in prototype
    skill_embedding = Column(JSON, nullable=True)

    # Location
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    is_rural = Column(Boolean, default=False)
    is_aspirational_district = Column(Boolean, default=False)

    # Demographics
    social_category = Column(
        Enum(SocialCategory, name="social_category_enum"),
        nullable=True,
        default=SocialCategory.GENERAL
    )

    # Preferences
    sector_preferences = Column(JSON, nullable=False, default=list)
    location_preference = Column(
        Enum(LocationPreference, name="location_preference_enum"),
        nullable=True,
        default=LocationPreference.HOME_STATE
    )
    preferred_language = Column(String(20), default="en")

    # History
    has_past_participation = Column(Boolean, default=False)

    # Video introduction (optional — bonus signal for ML)
    video_uploaded       = Column(Boolean, default=False)
    video_url            = Column(String(500), nullable=True)
    video_transcript     = Column(Text, nullable=True)
    video_comm_score     = Column(Integer, nullable=True)      # 0–100
    video_conf_score     = Column(Integer, nullable=True)      # 0–100
    video_clarity_score  = Column(Integer, nullable=True)      # 0–100
    video_overall_score  = Column(Integer, nullable=True)      # 0–100
    video_skills_detected  = Column(Text, nullable=True)       # JSON string: ["Python", "Excel"]
    video_sectors_detected = Column(Text, nullable=True)       # JSON string: ["IT", "Finance"]
    video_is_bilingual   = Column(Boolean, default=False)
    video_pace           = Column(String(20), nullable=True)   # slow / moderate / fast

    # Metadata
    metadata_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="candidate", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="candidate", cascade="all, delete-orphan")
    documents = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate(name='{self.name}', auth_step={self.auth_step})>"
