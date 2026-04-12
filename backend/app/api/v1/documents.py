"""
Document Upload & Verification API.
Handles document uploads for 10th/12th/diploma marksheets
and the admin review queue.
"""
import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.document import CandidateDocument
from app.api.v1.auth import get_current_user
from app.services.supabase_storage import upload_file_to_supabase

router = APIRouter()

# Where uploaded documents are saved on disk
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_DOC_TYPES = ["10th_marksheet", "12th_marksheet", "diploma_certificate"]
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


# ── CANDIDATE ENDPOINTS ─────────────────────────────

@router.post("/upload")
async def upload_document(
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload an education document for admin verification.
    Candidate must be at auth_step >= 2 (Aadhaar verified).
    """
    # Allow upload from auth_step 1 onwards (OTP login is sufficient)
    if current_user.auth_step < 1:
        raise HTTPException(
            status_code=403,
            detail="Please login first before uploading documents."
        )

    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"doc_type must be one of: {ALLOWED_DOC_TYPES}"
        )

    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: {list(ALLOWED_EXTENSIONS)}"
        )

    # Upsert: if same doc_type already uploaded, delete old DB record
    existing = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == current_user.id,
        CandidateDocument.doc_type == doc_type,
    ).first()
    if existing:
        db.delete(existing)
        db.commit()

    # Upload file bytes to Supabase (with local disk fallback)
    file_bytes = await file.read()
    supabase_url = None
    try:
        supabase_url = upload_file_to_supabase(
            file_bytes=file_bytes,
            file_name=file.filename or "unknown.pdf",
            bucket_name="pmis-media",
            folder_name="documents",
            content_type=file.content_type or "application/pdf"
        )
    except ValueError as e:
        print(f"Supabase upload failed, falling back to local disk: {e}")

    # Fallback: save to local disk if Supabase not configured or failed
    if not supabase_url:
        safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename or 'upload'}"
        local_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(local_path, "wb") as f_out:
            f_out.write(file_bytes)
        supabase_url = f"local://{local_path}"

    # Create DB record with the cloud URL
    doc = CandidateDocument(
        candidate_id=current_user.id,
        doc_type=doc_type,
        file_path=supabase_url, # Now saving Cloud URL instead of C:/ path
        original_filename=file.filename or "unknown",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "message": f"{doc_type} uploaded successfully. Pending admin review.",
        "document_id": str(doc.id),
        "status": doc.status,
    }


@router.get("/my-documents")
def get_my_documents(
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all documents uploaded by the current user with their verification status."""
    docs = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == current_user.id
    ).order_by(CandidateDocument.created_at.desc()).all()

    return {
        "auth_step": current_user.auth_step,
        "documents": [
            {
                "id": str(d.id),
                "doc_type": d.doc_type,
                "original_filename": d.original_filename,
                "status": d.status,
                "reviewer_notes": d.reviewer_notes,
                "uploaded_at": d.created_at.isoformat() if d.created_at else None,
                "reviewed_at": d.reviewed_at.isoformat() if d.reviewed_at else None,
            }
            for d in docs
        ],
    }


# ── ADMIN ENDPOINTS ─────────────────────────────────

@router.get("/admin/queue")
def get_verification_queue(
    status_filter: str = "PENDING",
    db: Session = Depends(get_db),
):
    """
    Get the document verification queue for admin review.
    Returns documents alongside candidate names and Aadhaar names for cross-checking.
    """
    docs = (
        db.query(CandidateDocument, Candidate)
        .join(Candidate, Candidate.id == CandidateDocument.candidate_id)
        .filter(CandidateDocument.status == status_filter)
        .order_by(CandidateDocument.created_at.asc())
        .all()
    )

    return {
        "total": len(docs),
        "queue": [
            {
                "document_id": str(doc.id),
                "doc_type": doc.doc_type,
                "original_filename": doc.original_filename,
                "uploaded_at": doc.created_at.isoformat() if doc.created_at else None,
                # Candidate info for cross-check
                "candidate_id": str(candidate.id),
                "candidate_name": candidate.name,
                "aadhaar_name": candidate.aadhaar_name,
                "candidate_email": candidate.email,
                "auth_step": candidate.auth_step,
                # OCR data (will be populated in Phase 2)
                "ocr_extracted_name": doc.ocr_extracted_name,
                "ocr_confidence": doc.ocr_confidence,
            }
            for doc, candidate in docs
        ],
    }


@router.get("/admin/document-file/{document_id}")
def get_document_file(document_id: str, db: Session = Depends(get_db)):
    """Serve the actual uploaded document file for admin to view."""
    doc = db.query(CandidateDocument).filter(
        CandidateDocument.id == document_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File missing from storage")

    return FileResponse(doc.file_path, filename=doc.original_filename)


@router.post("/admin/review/{document_id}")
def review_document(
    document_id: str,
    action: str = Form(...),       # "APPROVED" or "REJECTED"
    notes: str = Form(""),
    reviewer: str = Form("admin"),
    db: Session = Depends(get_db),
):
    """
    Admin reviews a document: approve or reject.
    If ALL of a candidate's documents are approved, auto-advance them to auth_step 3.
    """
    if action not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="action must be APPROVED or REJECTED")

    doc = db.query(CandidateDocument).filter(
        CandidateDocument.id == document_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Update document status
    doc.status = action
    doc.reviewer_notes = notes
    doc.reviewed_by = reviewer
    doc.reviewed_at = datetime.utcnow()

    # If approved, check whether ALL documents for this candidate are now approved
    if action == "APPROVED":
        candidate = db.query(Candidate).filter(Candidate.id == doc.candidate_id).first()
        if candidate:
            all_docs = db.query(CandidateDocument).filter(
                CandidateDocument.candidate_id == candidate.id
            ).all()

            # Must have at least one doc, and all must be approved
            if all_docs and all(d.status == "APPROVED" for d in all_docs):
                candidate.auth_step = 3  # FULL ACCESS UNLOCKED

    db.commit()

    return {
        "message": f"Document {action.lower()} successfully.",
        "document_id": document_id,
        "status": action,
    }
