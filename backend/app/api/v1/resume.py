from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
import sys
import os

# Add ML engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from ml.engine.resume_parser import ResumeParser

router = APIRouter()

@router.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parses a PDF resume file to extract the candidate's skills, 
    education level, and automatically align them to our ML engine format.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        contents = await file.read()
        
        # Send raw bytes to our new Resume Parser model
        extracted_data = ResumeParser.process_resume(contents)
        
        if not extracted_data["success"]:
            raise HTTPException(status_code=422, detail="Could not extract readable text from this PDF.")
            
        return {
            "message": "Resume successfully parsed",
            "data": {
                "education_level": extracted_data["extracted_education"],
                "skills": extracted_data["extracted_skills"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
