"""
SQLAlchemy ORM Model: CandidateDocument
Stores uploaded education documents (10th, 12th, Diploma marksheets) 
for admin verification queue.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class CandidateDocument(Base):
    """
    An education document uploaded by a candidate for verification.
    Admin reviews these in a queue and approves/rejects.
    """

    __tablename__ = "candidate_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)

    # Document Info
    doc_type = Column(String(50), nullable=False)  # "10th_marksheet", "12th_marksheet", "diploma_certificate"
    file_path = Column(String(500), nullable=False)  # Path to stored file on disk
    original_filename = Column(String(255), nullable=False)

    # Verification
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)   # admin username
    reviewed_at = Column(DateTime, nullable=True)

    # OCR (Phase 2 automation)
    ocr_extracted_name = Column(String(255), nullable=True)
    ocr_confidence = Column(Integer, nullable=True)  # 0-100

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="documents")

    def __repr__(self):
        return f"<CandidateDocument(type='{self.doc_type}', status='{self.status}')>"
