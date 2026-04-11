"""
SQLAlchemy ORM Model: Internship
Represents an internship opportunity posted by a company.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Date,
    Enum, JSON, Text
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class Internship(Base):
    """An internship opportunity within the PM Internship Scheme."""

    __tablename__ = "internships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Company Info
    company_name = Column(String(255), nullable=False, index=True)
    company_description = Column(Text, nullable=True)

    # Role Info
    role_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Requirements
    required_skills = Column(JSON, nullable=False, default=list)
    skill_embedding = Column(JSON, nullable=True)  # 384-dim vector
    min_education = Column(
        Enum("10TH", "12TH", "ITI", "DIPLOMA", "GRADUATE", "PG", name="min_education_enum"),
        nullable=False,
        default="GRADUATE"
    )
    preferred_fields = Column(JSON, nullable=True, default=list)

    # Classification
    sector = Column(String(100), nullable=False, index=True)

    # Location
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)

    # Compensation
    stipend_amount = Column(Float, nullable=True, default=5000.0)

    # Capacity
    capacity = Column(Integer, nullable=False, default=10)
    filled_count = Column(Integer, nullable=False, default=0)

    # Duration
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    duration_months = Column(Integer, default=12)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Fraud Detection & Reliability Tracking
    is_verified = Column(Boolean, default=False, index=True)
    fraud_risk_score = Column(Float, default=0.0)
    verification_notes = Column(String(500), nullable=True)

    # Metadata
    metadata_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="internship", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="internship", cascade="all, delete-orphan")

    @property
    def available_slots(self) -> int:
        return max(0, self.capacity - self.filled_count)

    @property
    def is_full(self) -> bool:
        return self.filled_count >= self.capacity

    def __repr__(self):
        return f"<Internship(role='{self.role_title}', company='{self.company_name}')>"
