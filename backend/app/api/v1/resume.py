import sys
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.models.candidate import Candidate
from app.models.document import CandidateDocument
from app.services.supabase_storage import upload_file_to_supabase

# Add ML engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from ml.engine.resume_parser import ResumeParser

router = APIRouter()

@router.post("/parse")
async def parse_resume(
    file: UploadFile = File(...),
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Uploads the candidate's PDF resume to Supabase cloud storage.
    2. Saves a 'resume' document record mapping to the user's profile.
    3. Parses the PDF to extract AI skills & education for profile injection.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        contents = await file.read()
        
        # 1. Save Resume to Supabase Cloud Storage
        supabase_url = upload_file_to_supabase(
            file_bytes=contents,
            file_name=file.filename or "resume.pdf",
            bucket_name="pmis-media",
            folder_name="resumes",
            content_type="application/pdf"
        )
        
        # 2. Upsert: Delete old resume record if it exists
        existing = db.query(CandidateDocument).filter(
            CandidateDocument.candidate_id == current_user.id,
            CandidateDocument.doc_type == "resume"
        ).first()
        if existing:
            db.delete(existing)
            db.flush()

        # 3. Link this document into our database natively
        doc = CandidateDocument(
            candidate_id=current_user.id,
            doc_type="resume",
            file_path=supabase_url,
            original_filename=file.filename or "resume.pdf",
            status="PENDING",  # Admin must manually approve resumes just like marksheets
        )
        db.add(doc)
        db.commit()

        # 4. Send raw bytes to our new Resume Parser model
        extracted_data = ResumeParser.process_resume(contents)
        
        if not extracted_data["success"]:
            # Even if ML fails, we saved the document, warn user softly
            return {
                "message": "Resume saved, but AI could not perfectly extract text.",
                "data": {"education_level": None, "skills": []}
            }
            
        return {
            "message": "Resume successfully parsed and saved",
            "data": {
                "education_level": extracted_data["extracted_education"],
                "skills": extracted_data["extracted_skills"]
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
